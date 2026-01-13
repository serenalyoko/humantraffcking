import pandas as pd

path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/labeled_jd_downsampled.csv"
df = pd.read_csv(path)
print("Rows where label = save:", (df['label'] == 'safe').sum())
print("Rows where label = risk:", (df['label'] == 'risk').sum())