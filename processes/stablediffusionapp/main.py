from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings

from diffusionpipeline import get_model_refiner, make_scheduler
from diffusers.utils import load_image
from helpers import image_to_string

import sys
from pathlib import Path
from lib.config import get_config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent
STACK_DIR = BASE_DIR.parent.parent
sys.path.append(str(STACK_DIR))


config = get_config()


# SETTINGS
class Settings(BaseSettings):
    DEBUG: bool = config.processes.core.stablediffusionxl.run.env.debug
    CROSS_ALLOW_ORIGINS: list = [config.processes.core.backend.computed.url]
    MODEL: str = config.processes.core.stablediffusionxl.run.env.model


# INIT
app = FastAPI()
settings = Settings()
model, model_img, refiner = get_model_refiner(settings.MODEL)

# CORS
origins = settings.CROSS_ALLOW_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def process_data(request: Request):
    data = await request.json()
    prompt = data.pop('prompt', None)
    refine = data.pop('refine', None)
    high_noise_frac = data.pop('high_noise_frac', None)
    num_outputs = data.pop('num_outputs', 1)
    scheduler = data.pop('scheduler', None)
    img_url = data.pop('image', False)
    mask_url = data.pop('mask_image', False)

    return data, prompt, refine, high_noise_frac, num_outputs, scheduler, img_url, mask_url


def process_refiner_data(refine, high_noise_frac):
    refiner_data = {'refiner': {}, 'model': {}}
    if refine and high_noise_frac:
        refiner_data['refiner']['denoising_start'] = high_noise_frac
        refiner_data['model']['denoising_end'] = high_noise_frac
    return refiner_data


def process_scheduler(scheduler, model):
    if scheduler:
        model.scheduler = make_scheduler(scheduler, model.scheduler.config)


def process_images(img_url, mask_url, data):
    model_type = 'base'
    if img_url:
        model_type = 'image'
        data['image'] = load_image(img_url)
        if mask_url:
            data['mask_image'] = load_image(mask_url)
        data['strength'] = 0.75
    return model_type


def process_output(model_type, prompt, num_outputs, data, refiner_data):
    if model_type == 'image':
        output = model_img(
            prompt=[prompt] * num_outputs if prompt is not None else '',
            **data,
            **refiner_data['model'],
        )
    else:
        output = model(
            prompt=[prompt] * num_outputs if prompt is not None else '',
            **data,
            **refiner_data['model'],
        )
    return output


def process_refine(refine, refiner, prompt, num_outputs, output, data, refiner_data):
    if refine and refiner:
        if data.get('image', None):
            del data['image']
        output = refiner(
            prompt=[prompt] * num_outputs if prompt is not None else '',
            image=output.images,
            **data,
            **refiner_data['refiner'],
        )
    return output


@app.post("/process")
async def process(request: Request):
    # Process data from request
    data, prompt, refine, high_noise_frac, num_outputs, scheduler, img_url, mask_url = await process_data(request)

    # Process refiner data
    refiner_data = process_refiner_data(refine, high_noise_frac)

    # Process scheduler
    process_scheduler(scheduler, model)

    # Process images
    model_type = process_images(img_url, mask_url, data)

    # Process output
    output = process_output(model_type, prompt, num_outputs, data, refiner_data)

    # Refine output if necessary
    output = process_refine(refine, refiner, prompt, num_outputs, output, data, refiner_data)

    # Convert images to string format
    images = [image_to_string(sample) for sample in output.images]

    return {"images": images}