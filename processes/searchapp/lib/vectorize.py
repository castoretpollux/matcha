import torch
from sentence_transformers import SentenceTransformer  # type: ignore
from django.conf import settings


if settings.USE_GPU:
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
else:
    device = "cpu"


# Load model
model = None


def get_model():
    global model
    if model is None:
        model = SentenceTransformer("antoinelouis/biencoder-camembert-base-mmarcoFR")
        model.to(device)
    return model


def vectorize(text):
    # Embed content
    embeddings = get_model().encode([text], convert_to_tensor=True)

    # Extract only vestors
    return embeddings[0].tolist()
