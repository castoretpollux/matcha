import os
import requests

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Check if needed models are available, else download them
MODEL_FILES_ROOT_URL = 'https://iamodels.preview2.castoretpollux.com/'
current_path = os.path.dirname(os.path.abspath(__file__))
for model_name in ['boolean_classifier', 'pipeline_classifier']:
    model_dirpath = os.path.join(current_path, 'models', model_name)
    if not os.path.exists(model_dirpath):
        print('Downloading', model_name, 'files')
        os.makedirs(model_dirpath, exist_ok=True)
        for file_name in ['config.json', 'model.safetensors', 'training_args.bin']:
            file_url = MODEL_FILES_ROOT_URL + f'{model_name}/{file_name}'
            file_content = requests.get(file_url).content
            file_path = os.path.join(model_dirpath, file_name)
            open(file_path, 'wb').write(file_content)
            print(f"- {file_name} downloaded")

app = FastAPI()


# SETTINGS
class Settings(BaseSettings):
    DEBUG: bool = False
    CORS_ALLOW_ORIGINS: str = "*"

    class Config:
        env_file = ".env"


settings = Settings()


# CORS
origins = settings.CORS_ALLOW_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DEFINE MODEL
device = torch.device('cpu')
model_name = 'camembert-base'
tokenizer = AutoTokenizer.from_pretrained(model_name, do_lower_case=True)

boolean_model_path = 'models/boolean_classifier'
boolean_model = AutoModelForSequenceClassification.from_pretrained(boolean_model_path, local_files_only=True)
boolean_model = boolean_model.to(device)

model_path = 'models/pipeline_classifier'
model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)
model = model.to(device)

# METHOD TO RETURN LABEL

boolean_labels = ['autre', 'normal']
labels = ['image', 'music', 'seo', 'sound', 'summary', 'text']


def predict_prompt_handler(input_text):
    result = []
    tokenized_text = tokenizer(
        input_text,
        truncation=True,
        is_split_into_words=False,
        return_tensors='pt'
    )
    tokenized_text = tokenized_text.to(device)
    # 1st : use boolean model to check if prompt is "normal" or "other" :
    boolean_outputs = boolean_model(tokenized_text["input_ids"])
    boolean_predicted_label = boolean_labels[boolean_outputs.logits.argmax(-1)]
    if boolean_predicted_label == 'autre':
        result.append('text')
    outputs = model(tokenized_text["input_ids"])
    predicted_label = labels[outputs.logits.argmax(-1)]
    if predicted_label not in result:
        result.append(predicted_label)
    return result


@app.post("/suggestion")
async def suggestion(request: Request):
    data = await request.json()
    labels_predicted = predict_prompt_handler(data['prompt'])
    return {"suggestions": labels_predicted}
