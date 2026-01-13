import json
import re
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd

# ----------------------------
# 1) Language gate: mostly Russian?
# ----------------------------
CYRILLIC_RE = re.compile(r"[\u0400-\u04FF\u0500-\u052F]")
LATIN_RE    = re.compile(r"[A-Za-z]")

def is_mostly_russian(text: Optional[str], threshold: float = 0) -> bool:
    if not text:
        return False
    cyr = len(CYRILLIC_RE.findall(text))
    lat = len(LATIN_RE.findall(text))
    total = cyr + lat
    return (total > 0) and (cyr / total >= threshold)

def _norm(s: str) -> str:
    #return s.casefold()
    s = s.replace(",", "")
    return s

# --- Build index from ONE JSON ---
def build_variant_index(us_states: Dict[str, List[str]]) -> List[Tuple[str, str, str]]:
    index = []
    for state, variants in us_states.items():
        for v in variants:
            if not v or not str(v).strip():
                continue
            v = str(v).strip()
            v_norm = _norm(v)

            is_short_latin_abbrev = (
                len(v_norm) <= 3 and re.fullmatch(r"[a-zA-Z]{1,3}", v_norm) is not None
            )
            match_type = "boundary" if is_short_latin_abbrev else "substring"
            index.append((v_norm, state, match_type))

    index.sort(key=lambda x: len(x[0]), reverse=True)  # longest first
    #print(index)
    return index

# --- Collect ALL matched states ---
def extract_states_from_text(
    text: Optional[str],
    variant_index,
    max_states: Optional[int] = None
) -> List[str]:
    if not text:
        return []

    t = _norm(text)
    found = []
    seen = set()

    for v_norm, state, match_type in variant_index:
        if state in seen:
            continue

        matched = False
        if match_type == "boundary":
            pattern = rf"(?<!\w){re.escape(v_norm)}(?!\w)"
            matched = re.search(pattern, t) is not None
        else:
            matched = (v_norm in t)

        if matched:
            return [state]
            #found.append(state)
            #seen.add(state)
            #if max_states is not None and len(found) >= max_states:
            #    break

    return found

def get_state(description):
    states = []
    for state, variants in us_states.items():
        all_variants = [state] + variants
        for variant in all_variants:
            if variant.casefold() in description.casefold():
                states.append(state)
    return states

# --- Main function: RU-only + multi-state output ---
def assign_locations_ru_only(
    description: Optional[str],
    variant_index,
    ru_threshold: float = 0,
    output: str = "list",          # "list" or "string"
    sep: str = "; ",
    max_states: Optional[int] = None
) -> Union[List[str], str]:
    if not is_mostly_russian(description, threshold=ru_threshold):
        return [] if output == "list" else "unspecified"

    states = extract_states_from_text(description, variant_index, max_states=max_states)
    #states = get_state(description)

    if output == "list":
        return states  # empty list means unspecified
    else:
        return sep.join(states) if states else "unspecified"
    
dict_path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/us_states.json"
data_path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/rusrek.xlsx"
datta_to_fix_path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_df_2.0.csv"
with open(dict_path, "r", encoding="utf-8") as f:
    us_states = json.load(f)
variant_index = build_variant_index(us_states)
df = pd.read_excel(data_path)
df_data_to_fix = pd.read_csv(datta_to_fix_path, low_memory=False)
descriptions = df["job_description"].tolist()
locations = []
for desc in descriptions:
    loc = assign_locations_ru_only(
        desc,
        variant_index,
        ru_threshold=0.10,
        output="string",
        sep=", ",
        max_states=None
    )
    locations.append(loc)
df["location"] = locations
# Replace location in df_data_to_fix with the location in df if job_description matches
location_map = dict(zip(df["job_description"], df["location"]))
df_data_to_fix["location"] = df_data_to_fix["job_description"].map(location_map).fillna(df_data_to_fix["location"])
df.to_csv("/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/rusrek_labeled.csv", index=False, encoding='utf-8-sig')
df_data_to_fix.to_csv("/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_df_2.1.csv", index=False, encoding='utf-8-sig')