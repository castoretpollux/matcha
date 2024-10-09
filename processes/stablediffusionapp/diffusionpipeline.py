import torch
import torchvision.transforms as T

from diffusers import (
    AutoPipelineForText2Image,
    AutoPipelineForImage2Image,
    DiffusionPipeline,
    # StableDiffusionXLInpaintPipeline,
    PNDMScheduler,
    LMSDiscreteScheduler,
    DDIMScheduler,
    EulerDiscreteScheduler,
    EulerAncestralDiscreteScheduler,
    DPMSolverMultistepScheduler,
)

transform = T.ToPILImage()


def get_model_refiner(model_id):
    torch.cuda.empty_cache()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    params = {
        'torch_dtype': torch_dtype,
        'use_safetensors': True,
    }

    model = AutoPipelineForText2Image.from_pretrained(
        model_id,
        **params
    )
    model.to(device)

    try:
        params['text_encoder_2'] = model.text_encoder_2
    except AttributeError:
        params['text_encoder'] = model.text_encoder

    refiner = DiffusionPipeline.from_pretrained(
        'stabilityai/stable-diffusion-xl-refiner-1.0',
        vae=model.vae,
        variant="fp16",
        **params
    )
    refiner.to(device)

    model_img = AutoPipelineForImage2Image.from_pipe(model).to(device)

    return model, model_img, refiner


def make_scheduler(name, config):
    return {
        "PNDM": PNDMScheduler.from_config(config),
        "KLMS": LMSDiscreteScheduler.from_config(config),
        "DDIM": DDIMScheduler.from_config(config),
        "K_EULER": EulerDiscreteScheduler.from_config(config),
        "K_EULER_ANCESTRAL": EulerAncestralDiscreteScheduler.from_config(config),
        "DPMSolverMultistep": DPMSolverMultistepScheduler.from_config(config),
    }[name]
