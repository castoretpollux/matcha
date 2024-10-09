from django.utils.translation import gettext as _

# Document states

DOCUMENT_STATE_INIT = 'init'
DOCUMENT_STATE_STARTPROCESS = 'startprocess'
DOCUMENT_STATE_TEXTCONVERTED = 'textconverted'
DOCUMENT_STATE_VECTORIZED = 'vectorized'
DOCUMENT_STATE_FINALIZED = 'finalized'
DOCUMENT_STATE_ERROR = 'error'

DOCUMENT_STATES = (
    (DOCUMENT_STATE_INIT, _('Initial')),
    (DOCUMENT_STATE_STARTPROCESS, _('Processing started')),
    (DOCUMENT_STATE_TEXTCONVERTED, _('Converted to text')),
    (DOCUMENT_STATE_VECTORIZED, _('Vectorized')),
    (DOCUMENT_STATE_FINALIZED, _('Finalized')),
    (DOCUMENT_STATE_ERROR, _('Error')),
)
DOCUMENT_STATE_TO_LABEL = dict(DOCUMENT_STATES)
