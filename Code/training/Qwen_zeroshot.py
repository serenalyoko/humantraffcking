# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM
from pydantic import BaseModel
import pandas as pd

class Labels (BaseModel):
    message: str
    label: str
    model: str



def zeroshot_thinker_4b(model, message):
    tokenizer = AutoTokenizer.from_pretrained(model)
    model = AutoModelForCausalLM.from_pretrained(model)
    messages = [
        {"role": "system", "content": "You are labeler who only labels text as 'safe' or 'risk' based on whether the job description contains potential human trafficking risk factors. Respond with only one word with label."},
        {"role": "user", "content": message}
    ]
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)

    outputs = model.generate(**inputs, max_new_tokens=40)
    res = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:])
    print("Raw output:", res)
    return res


if __name__ == "__main__":
    dataPath = ["/scratch1/zhousiyi/human_trafficking/Data/balanced_data.csv", "/scratch1/zhousiyi/human_trafficking/Data/labeled_jd_downsampled.csv"]
    models = ["Qwen/Qwen3-8B", "Qwen/Qwen3-4B-Thinking-2507"]
    for model in models:
        for path in dataPath:
            df = pd.read_csv(path)
            labels =[] 
            for index, row in df.iterrows():
                print(f"Processing row {index} from {path} using model {model}")
                jd = "label this job " + row['description']
                result = zeroshot_thinker_4b(model, jd)
                print(f"Result: {result}")
                labels.append(result.strip().lower())
            df[model.split("/")[-1] + "_label"] = labels
        outpath = f"/scratch1/zhousiyi/human_trafficking/Data/{path.split('/')[-1].split('.')[0]}_zeroshot_{model.split('/')[-1]}_labels.csv"
        df.to_csv(outpath, index=False)            
        print(f"Saved results to {outpath}")