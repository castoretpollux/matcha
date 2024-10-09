from django.utils.translation import gettext as _

from typing import Optional

from lib.uischema import UISchemaBaseModel
from lib.uifields import UIInputField, UICheckboxField, UITextareaField, UISelectField, UINumberField


class StableDiffusionSchema(UISchemaBaseModel):
    prompt: Optional[str] = UIInputField(
        default="",
        label=_("Prompt"),
        description=_("Prompt"),
        required=True,
    )(None)

    negative_prompt: Optional[str] = UITextareaField(
        rows=4,
        label=_("Negative Prompt"),
        description=_("Input Negative Prompt"),
    )(None)

    num_outputs: Optional[int] = UINumberField(
        slider=True,
        default=1,
        label=_("Num. Outputs"),
        description=_("Number of images to output."),
        minimum=1,
        maximum=4,
        step=1
    )(None)

    image: Optional[str] = UISelectField(
        default="",
        label=_("Image"),
        description=_("Input image for img2img or inpaint mode"),
        required=False,
        required_if={'mask_image': ""},
        has_media=True,
    )(None)

    mask_image: Optional[str] = UISelectField(
        default="",
        label=_("Mask"),
        description=_("Input mask for inpaint mode. Black areas will be preserved,white areas will be inpainted."),
        required_if={'image': ""},
        has_media=True,
    )(None)

    width: Optional[int] = UINumberField(
        default=1024,
        step=8,
        minimum=8,
        maximum=1024,
        label=_("Width"),
        description=_("Width of output image"),
        slider=True,
    )(None)

    height: Optional[int] = UINumberField(
        default=1024,
        step=8,
        minimum=8,
        maximum=1024,
        label=_("Height"),
        description=_("Height of output image"),
        slider=True,
    )(None)

    high_noise_frac: float = UINumberField(
        slider=True,
        default=0.8,
        step=0.1,
        label=_("High Noise Frac"),
        description=_("For expert_ensemble_refiner, the fraction of noise to use"),
        minimum=0,
        maximum=1,
    )(None)

    num_inference_steps: Optional[int] = UINumberField(
        default=50,
        step=1,
        label=_("Num. Inference Steps"),
        description=_("Number of inference steps"),
        minimum=1,
        maximum=500,
        slider=True
    )(None)

    guidance_scale: Optional[float] = UINumberField(
        slider=True,
        default=7.5,
        label=_("Guidance Scale"),
        description=_("Scale for classifier-free guidance"),
        minimum=1,
        maximum=50,
        step=0.5,
    )(None)

    refine: bool = UICheckboxField(
        default=False,
        toggle=True,
        label=_("Use refine ?"),
        description=_("Use refine ?"),
    )(None)
    # refine: str = UISelectField(
    #     default="no_refiner",
    #     label="Refine",
    #     description="Which refine style to use",
    #     options=[('no_refiner', 'no_refiner'), ('expert_ensemble_refiner', 'expert_ensemble_refiner'), ('base_image_refiner', 'base_image_refiner')]
    # )

    seed: Optional[int] = UINumberField(
        label=_("Seed"),
        description=_("Random seed. Leave blank to randomize the seed"),
        slider=True
    )(None)

    scheduler: str = UISelectField(
        default="K_EULER",
        label=_("Scheduler"),
        required=True,
        description=_("Scheduler"),
        options=[('DDIM', 'DDIM'), ('DPMSolverMultistep', 'DPMSolverMultistep'), ('K_EULER_ANCESTRAL', 'K_EULER_ANCESTRAL'), ('K_EULER', 'K_EULER'), ('PNDM', 'PNDM')]
    )(None)

    # lora_scale: float = UINumberField(
    #     default=0.6,
    #     label="Lora Scale",
    #     description="LoRA additive scale. Only applicable on trained models.",
    #     minimum=0,
    #     maximum=1,
    #     slider=True
    # )

    # apply_watermark: bool = UICheckboxField(
    #     default=True,
    #     toggle=True,
    #     label="Apply Watermark",
    #     description="Applies a watermark to enable determining if an image is generated in downstream applications. If you have other provisions for generating or deploying images safely,you can use this to disable watermarking.",
    # )

    # prompt_strength: float = UIInputField(
    #     default=0.8,
    #     label="Prompt Strength",
    #     description="Prompt strength when using img2img / inpaint. 1.0 corresponds to full destruction of information in image",
    #     minimum=0,
    #     maximum=1,
    #     step=0.1
    # )

    # replicate_weights: str = UIInputField(
    #     label="Replicate Weights",
    #     description="Replicate LoRA weights to use. Leave blank to use the default weights.",
    # )

    # disable_safety_checker: bool = UICheckboxField(
    #     default=False,
    #     toggle=True,
    #     label="Disable Safety Checker",
    #     description="Disable safety checker for generated images.",
    # )

    @staticmethod
    def layout():
        return [
            ['negative_prompt'],
            ['num_outputs', 'width', 'height'],
            ['high_noise_frac', 'num_inference_steps', 'guidance_scale', 'seed'],
            ['mask_image', 'image', 'scheduler', 'refine'],
        ]
