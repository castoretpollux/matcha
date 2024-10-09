import math
import uuid

from django.conf import settings
from django.utils.translation import gettext as _

from langchain_community.document_loaders import UnstructuredFileLoader  # type: ignore
from ollama import Client  # noqa


def cluster(it, count):
    items = [item for item in it]
    remaining = len(items)
    result = []
    while remaining:
        subresult = []
        for _ in range(count):
            try:
                subresult.append(items.pop(0))
            except IndexError:
                remaining = False
        if len(subresult):
            result.append(subresult)
    return result


def groups(it, count):
    if count <= 0:
        return []
    items = [item for item in it]
    item_count = len(items)
    if item_count % count == 0:
        cluster_count = item_count / count
    else:
        cluster_count = item_count / count + 1
    return cluster(items, math.floor(cluster_count))


def save_file(file):
    # generate unique folder name
    folder_name = str(uuid.uuid4())
    # relative path from media folder
    relative_path = f"uploads/{folder_name}/{file.name}"
    # save the file to media/uploads folder within unique folder name
    path = f"{settings.MEDIA_ROOT}/{relative_path}"
    # create folder if it does not exist
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return relative_path


def convert_to_text(path):
    # # remove the file from the path
    # path = path.split('/')[0:-1]
    # # convert path to string
    # path = '/'.join(path)
    # path = f"{settings.MEDIA_ROOT}/{path}"
    loader = UnstructuredFileLoader(path)
    documents = loader.load()
    return documents[0].page_content


def delete_file(path):
    import os
    path = f"{settings.MEDIA_ROOT}/{path}"
    # remove the file from the path
    os.remove(path)
    # remove the folder from the path
    path = path.split('/')[0:-1]
    # convert path to string
    path = '/'.join(path)
    os.rmdir(path)


def generate_summary(text):
    MODEL = settings.SUMMARY_MODEL
    client = Client(host=settings.OLLAMA_BACKEND_URL, timeout=60)
    preprompt = _("Generates a concise english summary of the following text in up to 50 words, gives the summary directly, do not add a commentary or introduction:")
    prompt_tpl = _('{preprompt}\n\n{text} \n\nConcise summary:')
    prompt = prompt_tpl.format(preprompt=preprompt, text=text)
    response = client.generate(model=MODEL, prompt=prompt, stream=False)
    summary = response['response']
    return summary
