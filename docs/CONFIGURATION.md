# Introduction

Matcha configuration is aimed to be centralised in a single file : config.yaml

By default, when you clone Matcha repository, this file is **not available**.

**But** we provide a config.yaml.sample that can be copied to config.yaml and fitted to your needs

# config.yaml

config.yaml, as its extension indicates, is a file that *essentially* follows the yaml syntax.
But, for practicality, **we have extended this syntax to allow us to use Python format strings** (More on this later).

The config.yaml file has 5 main sections:

- common : which contains transversal configuration parameters
- processes : which defines processes that must be launched and their configurations.
- pipelines : which defines pipelines (see [TERMINOLOGY](/docs/TERMINOLOGY.md)) that will be available when Matcha starts
- factory instances : which defines pipelines that are created from factories and that will also be available when Matcha starts
- factories : which defines factories that are useable to create new pipelines thru a frontend interfaces.

We'll go into more detail below

## common

This section contains global configuration parameters.

Let's look at the parameters in this section in config.yaml.sample :

- timezone: Europe/Paris  # See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for existing timezones
-   language_code: fr-fr    # Your main language. It will be used to localize Matcha front interface
-   datetime_format: '%d/%m/%Y %H:%M:%S'  # How date should be displayed (especially message dates). Format MUST follow Python date format : https://docs.python.org/3/library/datetime.html#format-codes
- venv_dir: Your python virtual environments root directory, it will mostly be used for reference later in the configuration (search for occurences...)
- nvm_dir: Your node virtualenv environments root directory
- nvm_version: Must be at least 18.19
- redis: redis configuration (thru sub parameters), Redis is used mainly to run django redis queue workers for asynchronous tasks
- big_llm: used as a reference, defines what you're considering as a "BIG" LLM (which means both powerful and - often - slow). This depends a lot on your hardware configuration (GPU number/power/vram)
- small_llm: used as a reference, defines what you're considering as a "Small" LLM
- title_llm: which LLM should be used to define chat session title ?
- embedding_model: Ollama embedding model alias. Advice : choose an embedding model that has been tuned for your native language (we use camembert because we are french... and like cheeses)
- django_secret: set a string that is long and difficult to guess. A [GUID](https://guidgenerator.com/) can be a good choice
- cookie_age: How long (in sec) must cookie last by default. We use 86400 (1 day)

## processes

This section contains configuration of processes that must be launched for Matcha to work.

**IMPORTANT** : This processes section is especially needed to run Matcha in "dev" mode. For production, what is important is the settings sub-section of each process

Note : processes defines a list of process. For each process, "run" sub-section is the only subsection that is needed for Matcha to run in dev mode. This run sub-section defines :

- workdir
- environment variables
- "pre command"
- the cmd itself

Let's look at all the parameters in this section in config.yaml.sample :

- alias: core.backend &larr; This process is important : it servers API and handles websockets that are used by the front - we advice you to not change this alias
    - settings: &core_backend_settings &larr; settings that will be read by matcha django project
        - protocol &larr;  http or http
        - hostname &larr;  can be an IP or host name
        - port &larr;  by default, 8000
        - replicate_api_token &larr;  if you use Replicate in your pipeline, set your token here
        - openai_api_key &larr;  if you use OpenAI API, set your key here
        - db_name &larr; PostgreSQL database name
        - db_user &larr; PostgreSQL username
        - db_password &larr;  PostgreSQL password
        - ollama_protocol &larr; http or https
        - ollama_hostname &larr; can be an IP or host name
        - ollama_port &larr; ollama port
    - computed &larr; You should not change following values as those are computed values that will be used as references
        - url: "{process.settings.protocol}://{process.settings.hostname}:{process.settings.port}"
        - ollama_url: "{process.settings.ollama_protocol}://{process.settings.ollama_hostname}:{process.settings.ollama_port}"
    - run &larr; except if you change backend virtualenv name (matcha by default), you don't need to change following values
        - workdir: ./
        - env: *core_backend_settings
        - precmd: . {common.venv_dir}/matcha/bin/activate
        - cmd: python3 manage.py runserver {process.settings.hostname}:{process.settings.port}

- alias: core.defaultworker1 &larr; 1st Django RQ worker process, it is used to call pipelines asynchronously
    - run &larr; except if you change backend virtualenv name (matcha by default), you don't need to change following values
        - workdir: ./
        - env: *core_backend_settings
        - precmd: . {common.venv_dir}/matcha/bin/activate
        - cmd: python3 manage.py rqworker default

- alias: core.defaultworker2 &larr; Another Django RQ worker process. You could add more workers if you have a lot of core (more that 16) but you shouldn't have less than 2
    - run &larr; except if you change backend virtualenv name (matcha by default), you don't need to change following values
        - workdir: ./
        - env: *core_backend_settings
        - precmd: . {common.venv_dir}/matcha/bin/activate
        - cmd: python3 manage.py rqworker default

- alias: core.populateworker1 &larr; 1st Django RQ popupate process, it is used to do long term computation such as converting documents to text and extracting informations from those texts
    - run &larr; except if you change backend virtualenv name (matcha by default), you don't need to change following values
        - workdir: ./
        - env: *core_backend_settings
        - precmd: . {common.venv_dir}/matcha/bin/activate
        - cmd: python3 manage.py rqworker populate

- alias: core.populateworker2 &larr; 1st Django RQ popupate process. As for worker process, you could add more workers if you have a lot of core (more that 16) but you shouldn't have less than 2
    - run &larr; except if you change backend virtualenv name (matcha by default), you don't need to change following values
        - workdir: ./
        - env: *core_backend_settings
        - precmd: . {common.venv_dir}/matcha/bin/activate
        - cmd: python3 manage.py rqworker populate

- alias: core.frontend &larr; Matcha frontend is a Vue3 appplication. Change values below to fit your need
    - settings:
        - protocol: http
        - hostname: localhost
        - port: 3000
    - computed &larr; You should not change following values as those are computed values that will be used as references
        - url: "{process.settings.protocol}://{process.settings.hostname}:{process.settings.port}"
    - run &larr; you shouldn't have the need to change the following values :
        - workdir: ./frontend
        - precmd: . {common.nvm_dir}/nvm.sh && nvm use {common.nvm_version}
        - cmd: npm run dev
        - env:
            - VITE_BACKEND_URL: "{processes.core.backend.computed.url}"
            - VITE_BASE_URL: "{process.computed.url}"
            - VITE_PORT: "{process.settings.port}"
            - NVM_DIR: "{common.nvm_dir}"

- alias: core.search &larr; search is used to handle file upload/vectorization/indexation & search
    - settings: &core_search_settings &larr; settings that will be read by searchapp django project
        - protocol &larr; http or https
        - hostname &larr; can be an IP or host name
        - port &larr;  by default, 8081
        - db_name &larr; PostgreSQL database name
        - db_user &larr; PostgreSQL username
        - db_password &larr;  PostgreSQL password
        - use_gpu: 0 # use 0 if you want to use CPU and 1 to use GPU (but don't forget that most pipelines also use GPUs)
        - part_size &larr; 1024 by default. Each documents is splitted in chunks that are also vectorized, in some cases, this leads to fast response time.
        - part_overlap &larr; 128. Document chunks can overlap, overlapping is usually considered as a good practice in RAG as "concepts" in chunks could be splitted, thus ~destroyed if there was no overlap.
        - summary_model: &larr; by default it reference *big_llm and we advice you to not change this
        - embedding_model: *embedding_model &larr; we advice you to not change this value

    - computed &larr; we advice you to not change the following values
        - url: "{process.settings.protocol}://{process.settings.hostname}:{process.settings.port}"
    - run &larr; you shouldn't have the need to change the following values :
        - workdir: processes/searchapp
        - precmd: . {common.venv_dir}/searchapp/bin/activate
        - cmd: python3 manage.py runserver {process.settings.hostname}:{process.settings.port}
        - env: *core_search_settings

- alias: core.searchworker1 &larr; 1st Django RQ search process, it is used to convert document to text, split them in chunks and vectorize them to make them searchable
    - run  &larr; except if you change backend virtualenv name (searchapp by default), you don't need to change following values
        - workdir: processes/searchapp
        - env: *core_search_settings
        - precmd: . {common.venv_dir}/searchapp/bin/activate
        - cmd: python3 manage.py rqworker search

- alias: core.searchworker2 &larr; Another Django RQ search process. You could add more workers if you have a lot of core (more that 16) but you shouldn't have less than 2
    - run:
        - workdir: processes/searchapp
        - env: *core_search_settings
        - precmd: . {common.venv_dir}/searchapp/bin/activate
        - cmd: python3 manage.py rqworker search


## pipelines : introduction

Pipelines are a core concept of Matcha : they are the tools visible in the frontend interface that enable users to transform data.

There are multiple parts of config.yaml that deals with pipelines :

- default_pipeline: which defines the default pipepines to be used when no pipelines have been chosen explicitely
- pipelines : which define "static" pipelines that are available immediately
- factory_instances : which define pipelines that are instanciated for factories and whose parameters are defined in the configuration file
- factories : which define factories that can be used in the interface to create "dynamic" pipelines

## default_pipeline

default_pipeline: instance.instance.ollama_llama3 &larr; this pipeline is a classical txt2txt pipeline that uses Llama3 as backend, it is a good default value.

## pipelines

- alias: core.searchupload &larr; core.searchupload is a pipeline that allows to search among uploaded documents, it uses a RAG
    - backend: machinery.pipelines.featureextractor.searchupload.SearchUploadPipeline &larr; class that implements searchupload
    - settings:
        - model: *big_llm &larr; by default, it uses a "big" LLM to generate text.

- alias: core.demo &larr; core demo is mainly useful to understand how new pipelines can be created
    - description: Demo
    - backend: machinery.pipelines.demo.demo.EchoPipeline &larr; Demo pipeline implementation


## factory instances

- alias: instance.ollama_llama3 &larr; instance.ollama_llama3 is a pipeline that allow txt2txt conversion, it's a classical LLM based on Llama3
    - factory: machinery.factories.ollama.factory.OllamaRunnerFactory &larr; this pipeline uses Ollama as backend
    - params:
      - model: llama3 &larr; this is the most important parameter for this pipeline : it defines the model, using its alias, that must be used by Ollama to answer requests
      - system: You're a nice assistant and you have to answer in French. &larr; pre-prompt, fit it to your needs

## factories

- alias: factory.search &larr; this factory allows to create instances that search among a given folder
    - backend: machinery.factories.search.factory.SearchFactory &larr; Factory backend

- alias: factory.ollama &larr; this factory allows to create instances that uses Ollama backend
    - backend: machinery.factories.ollama.factory.OllamaRunnerFactory &larr; Factory backend

- alias: factory.translation &larr; this factory allows to create instances of text translations
    - backend: machinery.factories.translation.factory.TranslationFactory &larr; Factory backend

# Parsing utilities

The config.yaml file parser is defined within [/lib/config.py](/lib/config.py)

This parser used PyYAML and custom parsing code to parse clauses that mixes yaml syntax and Python [formatted string literals](https://docs.python.org/3/tutorial/inputoutput.html).

This allows to define variables once and use them in multiple part of the config.yaml