
from django.conf import settings
import ollama


class LlmTitleGeneratorMixin(object):

    @classmethod
    def generate_title(cls, new_prompt):
        title_generator = ollama.Client(host=settings.OLLAMA_BACKEND_URL)
        title = title_generator.generate(model=settings.TITLE_LLM, prompt=new_prompt)
        # remove "
        title['response'] = title['response'].replace('"', '')
        # cut the string to 250 characters
        title['response'] = title['response'][:250]
        return title['response']
