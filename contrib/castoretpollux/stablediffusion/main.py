from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings

from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
import torch
import requests
from PIL import Image
from io import BytesIO
import base64

app = FastAPI()


# SETTINGS
class Settings(BaseSettings):
    DEBUG: bool = False
    CORS_ALLOW_ORIGINS: str
    MODEL: str

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

model_id = settings.MODEL


@app.post("/txt2img")
async def txt2img(request: Request):
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe = pipe.to("cuda")
    data = await request.json()
    prompt = data['prompt']
    image = pipe(prompt).images[0]
    # convert image to BASE64 and add it to the response
    img_str = image_to_string(image)
    response = {"image": img_str}
    return response


@app.post("/img2img")
async def img2img(request: Request):
    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe = pipe.to("cuda")
    data = await request.json()
    prompt = data['prompt']
    img_response = requests.get(data['image'])
    init_image = Image.open(BytesIO(img_response.content)).convert("RGB")
    init_image = init_image.resize((768, 512))
    images = pipe(prompt=prompt, image=init_image, strength=0.75, guidance_scale=7.5).images
    # convert image to BASE64 and add it to the response
    img_str = image_to_string(images[0])
    response = {"image": img_str}
    return response


def image_to_string(image):
    img_byte_array = BytesIO()
    image.save(img_byte_array, format='JPEG')
    img_str = base64.b64encode(img_byte_array.getvalue()).decode()
    return img_str