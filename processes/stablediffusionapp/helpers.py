from diffusionpipeline import transform

from io import BytesIO
import base64


def image_to_string(image):
    img_byte_array = BytesIO()
    image.save(img_byte_array, format='PNG')
    img_str = base64.b64encode(img_byte_array.getvalue()).decode()
    return img_str
