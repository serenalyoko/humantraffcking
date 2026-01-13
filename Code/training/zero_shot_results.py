import pickle

paths = ["/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/zero_shot_result_DeepSeek.pkl",
         "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/zero_shot_result_gemini_refined.pkl"]
for path in paths:
    print(f"Results from {path.split('/')[-1]}:")
    with open(path, "rb") as f:
        results = pickle.load(f)
    print(results)