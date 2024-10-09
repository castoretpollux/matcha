from django.utils.translation import gettext as _
from django.conf import settings

from lib.uischema import UISchemaBaseModel
from lib.uifields import UIAutocompleteField


class SearchFactorySchema(UISchemaBaseModel):
    # FIXME model should be transmited to searchapp
    # model: str = UISelectField(label=_("Embedding Model"), options=ALL_LLM['ollama'], default=ALL_LLM['ollama'][0][0], required=True)(None)
    namespace: str = UIAutocompleteField(
        label=_("Folder path"),
        options_api_url=settings.SITE_ROOT + "/api/folders/research/",
        required=True,
    )(None)

    @staticmethod
    def layout():
        return [
            # ['model', 'namespace']
            ['namespace']
        ]
