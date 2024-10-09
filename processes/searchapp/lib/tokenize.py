
from nltk.tokenize import word_tokenize  # type: ignore

from django.utils.translation import gettext as _

from .utils import cluster


def tokenize(content):
    return word_tokenize(content)


def extract_parts(content, size=1024, overlap=128):
    if size <= overlap:
        raise ValueError(_("Overlap must be smaller than chunk size"))
    all_tokens = tokenize(content)
    non_overlapping_chunk_size = size - overlap
    non_overlapping_chunks = cluster(all_tokens, non_overlapping_chunk_size)
    result = []
    for current_chunk, next_chunk in zip(non_overlapping_chunks, non_overlapping_chunks[1:] + [[]]):
        tokens = current_chunk + next_chunk[:overlap]
        part = ' '.join(tokens)
        result.append(part)
    return result
