# Introduction

As seen in [TERMINOLOGY](/docs/TERMINOLOGY.md), pipelines are a core concept of Matcha.

They are in charge of transforming a given input into an output, which is a central concept in computing, often materialized by *functions*

Pipelines are "functions", accessible thru a frontend interface that can deal with asynchronous requests and responses, able to call backend tools such as LLM or API

# Simple pipeline

The base pipeline class is available in [machinery/pipelines/base.py](/machinery/pipelines/base.py).

We can use this base pipeline class to implement a very simple pipeline that echoes user input :

```
class EchoPipeline(BasePipeline):

    LABEL = _("Echo pipeline") # <-- This is the label that will be used to display the pipeline button in frontend
    DESCRIPTION = _("Returns the message sent by the user") # <-- This is a description that is aimed to be displayed when hovering the pipeline button
    GENERATE_MEDIA = False # <-- False is a good default value, it means that no media will be generated when generating output
    INPUT = KIND_TEXT # <-- The expected input is a text
    OUTPUT = KIND_TEXT # <-- This pipeline returns text

    @classmethod
    def get_title(cls, request_message: core_models.ChatSessionMessage, response_message: core_models.ChatSessionMessage) -> str: # <-- When this pipeline is the first used in a session, this will be the session's title
        title = _("Echo")
        return title

    def process(self, request_message: core_models.ChatSessionMessage, response_message: core_models.ChatSessionMessage) -> None: # <-- the main method
        user_prompt = request_message.data['prompt']
        result = user_prompt
        response_message.data['result'] = result

```

The most important method is the process method.

It gives access to 2 objects :

- request_message : which gives access to every data that have been sent by the user
- response_message : which allows to set the result

# "Installing" this pipeline

The echo pipeline is available in [machinery/pipelines/demo/demo.py](/machinery/pipelines/demo/demo.py)

To use it, you must modify your config.yaml file to add the following lines in the [pipelines] section :

```
  - alias: core.demo
    description: Demo
    backend: machinery.pipelines.demo.demo.EchoPipeline
```

- alias is used by the frontend to indicate which pipeline must be used by the backend <=> it's use to "route" the request
- description : This is optionnal, if defined, it will override the description provided by the pipeline class
- backend : this is the most important line : it defines the import path to access the pipeline class. In this case, the file path is [machinery/pipelines/demo/demo.py](/machinery/pipelines/demo/demo.py) and the class name is EchoPipeline

# Going further

It's a good idea to see how other pipelines are implemented :

- [machinery/pipelines/featureextractor/searchupload.py](/machinery/pipelines/featureextractor/searchupload.py) : shows a more complicated example where documents can be uploaded before RAG and LLM helps to search data within the documents
- [machinery/pipelines/speech2txt/whisper.py](/machinery/pipelines/speech2txt/whisper.py) : shows how to interface with a backend process which can be accessed locally or thru an API


# Creating dynamic pipelines on the fly

You want to let user create its own pipeline by providing only a few parameters, this is the purpose of factories !

And this topic is covered in [TUTORIAL2-FACTORY](/docs/tutorials/TUTORIAL2-FACTORY.md)
