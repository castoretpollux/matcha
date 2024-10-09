import os
import random
import uuid
import requests
import base64
from urllib.parse import urlparse
from collections import defaultdict

from django.conf import settings
from django.core.cache import caches

from .app_requests import SearchRequest


def get_site_root():
    return settings.SITE_ROOT


def download_url(url):
    # prepare downloaded file name
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    ext = ext or ''
    ext = ext.lower()
    file_name = str(uuid.uuid4()) + ext
    folder_name = str(random.randint(1000, 9999))  # NOSONAR
    folder_path = os.path.join(settings.MEDIA_ROOT, 'downloaded', folder_name)
    try:
        os.makedirs(folder_path)
    except OSError:
        pass
    file_path = os.path.join(folder_path, file_name)
    file_relative_path = os.path.join(settings.MEDIA_URL, 'downloaded', folder_name, file_name)
    # file_url = get_site_root() + file_relative_path
    # download and save the file :
    resp = requests.get(url, allow_redirects=True)
    open(file_path, 'wb').write(resp.content)
    # return the relative file path :
    return file_relative_path


def save_image_from_base64(base64_string):
    # prepare downloaded file name
    file_name = str(uuid.uuid4()) + '.jpg'
    folder_name = str(random.randint(1000, 9999))  # NOSONAR
    folder_path = os.path.join(settings.MEDIA_ROOT, 'downloaded', folder_name)
    try:
        os.makedirs(folder_path)
    except OSError:
        pass
    file_path = os.path.join(folder_path, file_name)
    file_relative_path = os.path.join(settings.MEDIA_URL, 'downloaded', folder_name, file_name)
    # file_url = get_site_root() + file_relative_path
    # download and save the file :
    img_data = base64.b64decode(base64_string)
    with open(file_path, 'wb') as f:
        f.write(img_data)
    # return the relative file path :
    return file_relative_path


def get_upload_path(instance, filename):
    session_uuid = str(instance.session.id).split('-')
    path_folder = f'uploaded/{session_uuid[0]}/{session_uuid[1]}/{session_uuid[2]}/{session_uuid[3]}/{session_uuid[4]}/'

    file_uuid = str(uuid.uuid4())
    _, ext = os.path.splitext(filename)
    path_file = f'{file_uuid}{ext}'

    fullpath = os.path.join(path_folder, path_file)

    return fullpath


def get_best_suggestion(suggestions, user):
    # check aggregation
    cache = caches['diskcache']
    thema_aggregation = cache.get('suggestion_thema_aggregation')

    if not thema_aggregation:
        json_dict = {
            "filters": {'namespace': 'ROOT/SEARCH/CORE/SUGGESTIONAPP'},
            "aggregate": "context__thema",
        }
        sr = SearchRequest(user)
        output = sr.post("/api/aggregate/", json=json_dict)
        thema_aggregation = output.json()
        cache.set('suggestion_thema_aggregation', thema_aggregation)

    # get count by theme
    count_by_theme = defaultdict(int)
    for item in suggestions:
        theme = item['context']['thema']
        count_by_theme[theme] += 1

    # get ratio by theme
    ratio_suggestion_list = []
    for theme, count in count_by_theme.items():
        ratio = count / thema_aggregation[theme]
        ratio_suggestion_list.append({theme: ratio})

    # get theme with best ratio
    if len(ratio_suggestion_list):
        best_suggestion_ratio = max(ratio_suggestion_list, key=lambda x: list(x.values())[0])
        best_suggestion = list(best_suggestion_ratio.keys())[0]
    else:
        best_suggestion = None

    return best_suggestion


def generate_pipeline_dict(cls_, alias):
    return {
        'pipeline': alias,
        'pipeline_type': f'{cls_.input} -> {cls_.output}',
        'pipeline_label': cls_.label,
        'pipeline_schema': cls_.json_schema,
        'pipeline_uischema': cls_.ui_schema,
    }


def get_data_type(value):
    if isinstance(value, str):
        return 'string'
    elif isinstance(value, list):
        return 'list'
    elif isinstance(value, dict):
        return 'dict'
    else:
        return 'other'
