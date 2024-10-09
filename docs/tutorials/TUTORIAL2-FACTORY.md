# Introduction

Factories allows users to create pipelines dynamically.

They are quite useful in a lot of cases, for instances :

- create translation pipelines by only requesting the user to specify the target language.
- create some wrapper to existing and future model available in Ollama/Huggingface or Replicate
- create some gpts-like pipeline by providing preprmpts

Conceptually, you'll need first to define what is expected from the user and create a schema (Pydantic schema with additionnal stuff)

# Factory example

We advice you tu study the code of the translation factory which is available in [machinery/factories/translation](/machinery/factories/translation).

Here is the schema (available in [machinery/factories/translation/schema.py](/machinery/factories/translation/schema.py)):

```
class TranslationFactorySchema(UISchemaBaseModel):

    model: str = UISelectField(label=_("Translation Model"), options=ALL_LLM['ollama'], default=ALL_LLM['ollama'][0][0], required=True)(None)
    language: str = UISelectField(label=_("Language"), options=LANGUAGE_CHOICES, default=LANGUAGE_ENGLISH, required=True)(None)

    @staticmethod
    def layout():
        return [
            ['model', 'language']
        ]
```

This allows the user to define the following parameters :

- model : to select the LLM that will be used to power the translation
- language : to define the target language

And here is the factory implementation (available in [machinery/factories/translation/factory.py](/machinery/factories/translation/factory.py)):

```
class TranslationFactory(BasePipelineFactory):

    @classproperty
    def pydantic_model(cls):
        return TranslationFactorySchema

    @classmethod
    def get_default_label(cls):
        return _("Translate a text")

    @classmethod
    def get_default_description(cls):
        return _("Translate a text using a neural network")

    @classmethod
    def produce(cls, **kwargs) -> Type[ReferenceTranslationPipeline]:
        model = kwargs.get('model', None)
        language = kwargs.get('language', None)
        capitalized_language = language.capitalize()
        new_class_name = f'Translate{capitalized_language}Pipeline'
        return type(new_class_name, (ReferenceTranslationPipeline,), {
            'MODEL': model,
            'LANGUAGE': language
        })
```

The most import method of the factory is the produce method which will dynamically instantiate a new Python Pipeline class using typical Python code to create class on the fly

In this case, the factory use a "reference" Pipeline as a model to create a new class dynamically, only specifying MODEL and LANGUAGE class properties.

This translation factory is a good example of how little effort it takes to create a factory, basically you'll have to :

- Define parameters list and create the schema
- Create the "reference" pipeline
- Create the factory class and use the reference pipeline to create some new classes

# "Installing" this factory

Factories can be installed in 2 different ways:

- Instanciated on the start, in the [factory_instances] section of config.yaml, see [docs/CONFIGURATION.md](/docs/CONFIGURATION.md) for futher information
- Be declared as factory, to be used by users thru the frontend interfaces, this need to be done in the [factories] section of config.yaml, see [docs/CONFIGURATION.md](/docs/CONFIGURATION.md) for futher information


# Going further

It's a good idea to see how other factories are implemented, for instance :

- [machinery/factories/ollama/factory.py](/machinery/factories/ollama/factory.py) : shows a factory that helps to create pipeline by providing a model and a system prompt that will use Ollama server as backend
- [machinery/factories/replicate/factory.py](/machinery/factories/replicate/factory.py) : shows a factory that helps to create pipelines that use Replicate API

