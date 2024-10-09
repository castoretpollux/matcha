import os
import string
from collections import defaultdict

import yaml
from yaml import SafeLoader

from .exceptions import UnhandledConfigTypeException



class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def propertize(value):
    t = type(value)
    if t in [bool, str, float, int, bytes, dotdict]:
        return value
    if t == list:
        return [propertize(item) for item in value]
    if t == dict:
        return dotdict(dict((key, propertize(val)) for key, val in value.items()))
    raise UnhandledConfigTypeException(str(t))


def format_string(value, context):
    try:
        result = value.format(**context)
        return result
    except Exception:
        print(f"Error while formatting {value} with context: {context}")


# Function to load YAML file
def load_yaml(filepath):
    with open(filepath, 'r') as f:
        return yaml.load(f, SafeLoader)


# Function to process 'computed' fields in the process configuration
def process_computed_fields(process, local_flatvars):
    computed = process.get('computed', {})
    for key, value in computed.items():
        computed[key] = format_string(value, local_flatvars)
    return propertize(computed)


# Function to process 'run' fields in the process configuration
def process_run_fields(run, local_flatvars):
    cmd = format_string(run['cmd'], local_flatvars)
    precmd = format_string(run.get('precmd', ''), local_flatvars) if run.get('precmd') else None
    workdir = format_string(run.get('workdir', ''), local_flatvars) if run.get('workdir') else None
    env = {k: format_string(v, local_flatvars) if isinstance(v, (str, bytes)) else str(v) for k, v in run.get('env', {}).items()}
    return {'workdir': workdir, 'env': env, 'precmd': precmd, 'cmd': cmd}


# Function to process individual process item and return its configuration
def process_item(process, common_vars, namespaced_processes):
    local_flatvars = propertize({'common': common_vars, 'process': process, 'processes': dict(namespaced_processes)})
    item = {
        'alias': process['alias'],
        'settings': process.get('settings', {}),
        'computed': process_computed_fields(process, local_flatvars),
        'run': process_run_fields(process['run'], local_flatvars)
    }
    return item


# Function to namespace items based on their alias
def namespace_items(item_list):
    namespaced_items = defaultdict(dict)
    for item in item_list:
        alias = item['alias']
        namespace, name = alias.split('.')
        namespaced_items[namespace][name] = item
    return dict(namespaced_items)


# Main function to get configuration from the YAML file
def get_config(filepath=None):
    # Set default filepath if not provided
    if filepath is None:
        parent_file_dir = os.path.dirname(os.path.dirname(__file__))
        filepath = os.path.join(parent_file_dir, 'config.yaml')

    # Load data from the YAML file
    data = load_yaml(filepath)

    # Initialize result dictionary with common variables and default pipeline
    result = {
        'common': data['common'],
        'default_pipeline': data['default_pipeline'],
        'process_list': [],
        'pipeline_list': data['pipelines'],
        'factory_instance_list': data['factory_instances'],
        'factory_list': data['factories']
    }

    # Process and namespace each process item
    namespaced_processes = defaultdict(dict)
    for process in data['processes']:
        item = process_item(process, data['common'], namespaced_processes)
        result['process_list'].append(item)
        namespace, name = item['alias'].split('.')
        namespaced_processes[namespace][name] = item

    # Add namespaced processes to the result
    result['processes'] = dict(namespaced_processes)

    # Namespace and add pipelines, factory instances, and factories to the result
    result['pipelines'] = namespace_items(result['pipeline_list'])
    result['factory_instances'] = namespace_items(result['factory_instance_list'])
    result['factories'] = namespace_items(result['factory_list'])

    # Return the final configuration, properly formatted
    return propertize(result)
