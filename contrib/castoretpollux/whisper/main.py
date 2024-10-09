import sys
from pathlib import Path

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


APP_DIR = Path(__file__).resolve().parent
STACK_DIR = APP_DIR.parent.parent.parent

sys.path.append(str(STACK_DIR))

from lib.config import get_config
config = get_config()

MODEL = config.processes.contrib.whisper.settings.model
DEBUG = config.processes.contrib.whisper.settings.debug in [1, '1']
USE_GPU = config.processes.contrib.whisper.settings.use_gpu in [1, '1']
CORS_ALLOW_ORIGINS = config.processes.contrib.whisper.settings.cors_allow_origins
LANGUAGE = config.processes.contrib.whisper.settings.language or 'english'

app = FastAPI()

# CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the model and the processor
if USE_GPU:
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
else:
    device = "cpu"
    torch_dtype = torch.float32


model = AutoModelForSpeechSeq2Seq.from_pretrained(
    MODEL, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(MODEL)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=30,
    batch_size=16,
    return_timestamps=True,
    torch_dtype=torch_dtype,
    device=device,
)


@app.post("/transcript")
async def transcript(request: Request):
    data = await request.json()
    audio_file = data['audio']
    result = pipe(audio_file, generate_kwargs={"language": LANGUAGE})
    return result


