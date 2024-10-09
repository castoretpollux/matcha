from __future__ import annotations
import importlib
import logging
from collections import defaultdict
from typing import Type

from django.contrib.auth.models import User
from django.db.models import Q

from lib.config import get_config

logger = logging.getLogger("django")

import machinery.pipelines.base as pipelines_base



# Don't use this value directy, use get_* methods instead
PIPELINE_DICT = None
FACTORY_DICT = None
PIPELINE_ALIASES = None

PIPELINE_META_ATTR_NAMES = ['alias', 'label', 'description', 'generate_media', 'input', 'output']
FACTORY_META_ATTR_NAMES = ['alias', 'label', 'description']


def extract_meta_infos(definition, attr_names):
    return dict([(attr_name, definition.get(attr_name)) for attr_name in attr_names])


def override_meta_info(cls, **infos):
    for key, value in infos.items():
        try:
            current = getattr(cls, key)
        except Exception:
            current = None
        setattr(cls, key.upper(), value or current)


def get_pipeline_dict(user: User, use_cache=True):
    global PIPELINE_DICT
    if use_cache and PIPELINE_DICT is not None:
        return PIPELINE_DICT
    from core.models import DynamicPipeline
    result = {}
    config = get_config()
    # Handle normal pipelines :
    for pipeline_defn in config.pipeline_list:
        backend = pipeline_defn['backend']
        path, classname = backend.rsplit('.', 1)
        module = importlib.import_module(path)
        cls = getattr(module, classname)
        infos = extract_meta_infos(pipeline_defn, PIPELINE_META_ATTR_NAMES)
        override_meta_info(cls, **infos)
        alias = pipeline_defn['alias']
        result[alias] = cls
    # Handle build pipelines :
    for factory_instance_defn in config.factory_instance_list:
        factory = factory_instance_defn['factory']
        path, classname = factory.rsplit('.', 1)
        module = importlib.import_module(path)
        factory_kls = getattr(module, classname)
        params = factory_instance_defn['params']
        cls = factory_kls.produce(**params)
        infos = extract_meta_infos(factory_instance_defn, PIPELINE_META_ATTR_NAMES)
        override_meta_info(cls, **infos)
        alias = factory_instance_defn['alias']
        result[alias] = cls
    # Handle dynamic pipelines
    # there's 3 conditions for a user to access DynamicPipeline :
    # - DynamicPipeline user and group are None
    # - DynamicPipeline user is current user
    # - user belongs to DynamicPipeline group
    q_public = Q(user__isnull=True) & Q(group__isnull=True)
    q_user = Q(user=user)
    q_group = Q(group_id__in=user.groups.values_list('id', flat=True))
    clause = q_public | q_user | q_group
    for item in DynamicPipeline.objects.filter(clause):
        cls = item.pipeline_class  # Info : no need to "override" meta info, it's already done in pipeline_class method
        result[cls.ALIAS] = cls
    PIPELINE_DICT = result
    return result


def get_pipeline_class(pipeline_alias: str, user: User) -> Type[pipelines_base.BasePipeline]:
    # 1st : try with cache :
    pipeline_dict = get_pipeline_dict(user, use_cache=True)
    result = pipeline_dict.get(pipeline_alias)
    if result is not None:
        return result
    # result is None, try without the cache :
    pipeline_dict = get_pipeline_dict(user, use_cache=False)
    return pipeline_dict.get(pipeline_alias)


def get_pipeline_aliases(user: User) -> list[str]:
    pipeline_dict = get_pipeline_dict(user, use_cache=False)
    PIPELINE_ALIASES = pipeline_dict.keys()
    return PIPELINE_ALIASES


def get_output_kind_to_pipeline_dict(user: User) -> dict:
    result = defaultdict(list)
    pipeline_dict = get_pipeline_dict(user, use_cache=False)
    for _, kls in pipeline_dict.items():
        output = kls.output
        if output:
            result[output].append(kls)
    return dict(result)


def get_factory_dict() -> dict:
    global FACTORY_DICT
    if FACTORY_DICT is not None:
        return FACTORY_DICT
    result = {}
    config = get_config()
    # Handle normal pipelines :
    for factory_defn in config.factory_list:
        backend = factory_defn['backend']
        path, classname = backend.rsplit('.', 1)
        module = importlib.import_module(path)
        cls = getattr(module, classname)
        infos = extract_meta_infos(factory_defn, FACTORY_META_ATTR_NAMES)
        override_meta_info(cls, **infos)
        alias = factory_defn['alias']
        result[alias] = cls
    FACTORY_DICT = result
    return result


def get_factory_class(factory_alias: str):
    factory_dict = get_factory_dict()
    return factory_dict.get(factory_alias)
