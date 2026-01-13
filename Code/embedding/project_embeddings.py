# project_to_768.py
import argparse, os, sys, numpy as np
import pandas as pd

def save_npy(path, arr):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    np.save(path, arr)

def load_linear(path_w, path_b=None):
    W = np.load(path_w)           # shape: (D, 768)
    b = np.load(path_b) if path_b else None  # shape: (768,)
    return W, b

def project_linear(X, W, b=None, batch=65536):
    # X: (N, D) -> (N, 768)
    out = np.empty((X.shape[0], W.shape[1]), dtype=np.float32)
    start = 0
    while start < X.shape[0]:
        end = min(start + batch, X.shape[0])
        chunk = X[start:end]      # (B, D)
        Y = chunk @ W             # (B, 768)
        if b is not None:
            Y += b
        out[start:end] = Y.astype(np.float32, copy=False)
        start = end
    return out

def method_pca_npy(in_path, out_path, dim=768, batch=65536):
    # Incremental PCA: two passes
    from sklearn.decomposition import IncrementalPCA

    X = np.load(in_path, mmap_mode="r")   # (N, D) float32
    N, D = X.shape
    ipca = IncrementalPCA(n_components=dim)

    # pass 1: fit
    for start in range(0, N, batch):
        end = min(start + batch, N)
        ipca.partial_fit(X[start:end])

    # pass 2: transform
    out = np.empty((N, dim), dtype=np.float32)
    for start in range(0, N, batch):
        end = min(start + batch, N)
        out[start:end] = ipca.transform(X[start:end]).astype(np.float32, copy=False)

    save_npy(out_path, out)

    # optionally save components to reuse later
    base = os.path.splitext(out_path)[0]
    np.save(base + "_pca_components.npy", ipca.components_.astype(np.float32))
    np.save(base + "_pca_mean.npy", ipca.mean_.astype(np.float32))
    print(f"[OK] Saved: {out_path}\n[OK] PCA components: {base+'_pca_components.npy'}")

def method_linear_npy(in_path, out_path, w_path, b_path=None, batch=65536):
    X = np.load(in_path, mmap_mode="r")   # (N, D)
    W, B = load_linear(w_path, b_path)    # W: (D, 768)
    Y = project_linear(X, W, B, batch=batch)
    save_npy(out_path, Y)
    print(f"[OK] Saved: {out_path}")

def method_pca_parquet(in_path, out_path, col="emb", dim=768, batch_rows=20000, passthrough_cols=("description", "label")):
    """
    Projects list-like embedding column `col` -> `<col>_768` via IncrementalPCA,
    and writes a new parquet containing the projected column PLUS the requested
    passthrough columns (default: 'description', 'label').

    - in_path: input parquet path
    - out_path: output parquet path
    - col: name of embedding column (list/array per row)
    - dim: PCA output dimension (default 768)
    - batch_rows: rows per batch
    - passthrough_cols: tuple/list of extra columns to keep in the output
    """
    import os
    import numpy as np
    import pyarrow.dataset as ds
    import pyarrow as pa
    import pyarrow.parquet as pq
    from sklearn.decomposition import IncrementalPCA

    dataset = ds.dataset(in_path, format="parquet")

    # Validate columns
    existing_cols = set(dataset.schema.names)
    missing = [c for c in (col, *passthrough_cols) if c not in existing_cols]
    if missing:
        print(f"[WARN] Missing columns in input parquet: {missing}. They will be skipped in output.")
        passthrough_cols = tuple(c for c in passthrough_cols if c in existing_cols)

    # --- probe first batch to get D ---
    first = next(dataset.to_batches(columns=[col], batch_size=batch_rows))
    D = len(first.column(0)[0].as_py())
    ipca = IncrementalPCA(n_components=dim)

    # --- pass 1: fit PCA on embedding column only ---
    for batch in dataset.to_batches(columns=[col], batch_size=batch_rows):
        arr = np.stack([np.array(v.as_py(), dtype=np.float32) for v in batch.column(0)])
        ipca.partial_fit(arr)

    # --- prepare output schema: passthrough + new projected column ---
    # Build a schema for the new column as list<float32>
    proj_field = pa.field(f"{col}_768", pa.list_(pa.float32()))
    # We will infer passthrough field types from the dataset schema
    passthrough_fields = [dataset.schema.field(c) for c in passthrough_cols]
    out_schema = pa.schema(passthrough_fields + [proj_field])

    # --- pass 2: transform + write batches with passthrough columns ---
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    writer = pq.ParquetWriter(out_path, out_schema)
    try:
        # Read *both* emb col and passthrough cols to avoid double scans
        read_cols = list(passthrough_cols) + [col]
        for batch in dataset.to_batches(columns=read_cols, batch_size=batch_rows):
            # Convert to a table to easily pick columns by name
            tbl = pa.Table.from_batches([batch])

            # Project embeddings
            X = np.stack([np.array(v, dtype=np.float32) for v in tbl[col].to_pylist()])
            proj = ipca.transform(X).astype(np.float32)
            proj_arr = pa.array(proj.tolist(), type=pa.list_(pa.float32()))

            # Build output table: passthrough columns + new projected column
            out_cols = {c: tbl[c] for c in passthrough_cols}
            out_cols[f"{col}_768"] = proj_arr
            out_tbl = pa.table(out_cols, schema=out_schema)

            writer.write_table(out_tbl)
    finally:
        writer.close()

    # Save PCA parts (optional)
    base = os.path.splitext(out_path)[0]
    np.save(base + "_pca_components.npy", ipca.components_.astype(np.float32))
    np.save(base + "_pca_mean.npy", ipca.mean_.astype(np.float32))
    print(f"[OK] Saved: {out_path}")
    print(f"[OK] PCA components: {base+'_pca_components.npy'}")


def method_linear_parquet(in_path, out_path, w_path, b_path=None, in_col="emb", out_col="emb_768", batch_rows=20000):
    import pyarrow.dataset as ds
    import pyarrow as pa
    import pyarrow.parquet as pq

    W, B = load_linear(w_path, b_path)
    dataset = ds.dataset(in_path, format="parquet")

    writer = None
    try:
        for batch in dataset.to_batches(columns=[in_col], batch_size=batch_rows):
            X = np.stack([np.array(v.as_py(), dtype=np.float32) for v in batch.column(0)])
            Y = project_linear(X, W, B, batch=batch_rows)
            table = pa.table({out_col: Y.tolist()})
            if writer is None:
                os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
                writer = pq.ParquetWriter(out_path, table.schema)
            writer.write_table(table)
    finally:
        if writer is not None:
            writer.close()
    print(f"[OK] Saved: {out_path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help=".npy or .parquet path")
    ap.add_argument("--output", required=True, help="output .npy or .parquet path")
    ap.add_argument("--method", choices=["pca","linear"], default="pca")
    ap.add_argument("--dim", type=int, default=768)
    ap.add_argument("--batch", type=int, default=65536, help="batch size (rows) for .npy or per pass")
    ap.add_argument("--parquet_col", default="emb", help="column name containing embeddings (parquet)")
    ap.add_argument("--w", help="path to .npy weight matrix (D,dim) for method=linear")
    ap.add_argument("--b", help="path to .npy bias (dim,) for method=linear")
    args = ap.parse_args()

    if args.input.endswith(".npy") and args.output.endswith(".npy"):
        if args.method == "pca":
            method_pca_npy(args.input, args.output, dim=args.dim, batch=args.batch)
        else:
            if not args.w:
                sys.exit("ERROR: --w required for method=linear")
            method_linear_npy(args.input, args.output, args.w, args.b, batch=args.batch)
    elif args.input.endswith(".parquet") and args.output.endswith(".parquet"):
        df= pd.read_parquet(args.input)
        print(df.head())
        if args.method == "pca":
            method_pca_parquet(args.input, args.output, col=args.parquet_col, dim=args.dim, batch_rows=args.batch)
        else:
            if not args.w:
                sys.exit("ERROR: --w required for method=linear")
            method_linear_parquet(args.input, args.output, args.w, args.b, in_col=args.parquet_col, out_col=args.parquet_col+"_768", batch_rows=args.batch)
    else:
        sys.exit("ERROR: Input and output must both be .npy OR both be .parquet")

if __name__ == "__main__":
    main()
