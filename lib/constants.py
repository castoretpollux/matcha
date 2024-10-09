from django.utils.translation import gettext as _

# Document "big" categories
KIND_TEXT = 'text'
KIND_IMAGE = 'image'
KIND_SOUND = 'sound'
KIND_AUDIO = 'audio'
KIND_MUSIC = 'music'
KIND_FILE = 'file'
KIND_SUMMARY = 'summary'
KIND_FILE_LIST = 'file list'
KIND_TEXT_AND_IMAGE = KIND_TEXT + '/' + KIND_IMAGE
KIND_TEXT_AND_FILE = KIND_TEXT + '/' + KIND_FILE

KIND_CHOICES = (
    (KIND_TEXT, _('text')),
    (KIND_IMAGE, _('image')),
    (KIND_SOUND, _('sound')),
    (KIND_AUDIO, _('audio')),
    (KIND_MUSIC, _('music')),
    (KIND_SUMMARY, _('summary')),
    (KIND_FILE, _('file')),
    (KIND_FILE_LIST, _('file list')),
    (KIND_TEXT_AND_IMAGE, _('text/image')),
    (KIND_TEXT_AND_FILE, _('text/file')),
)

KIND_TO_LABEL = dict(KIND_CHOICES)

# Message kinds

MESSAGE_KIND_REQUEST = 'request'
MESSAGE_KIND_RESPONSE = 'response'
MESSAGE_KIND_ERROR = 'error'

MESSAGE_KIND_CHOICES = (
    (MESSAGE_KIND_REQUEST, _('request')),
    (MESSAGE_KIND_RESPONSE, _('response')),
    (MESSAGE_KIND_ERROR, _('error'))
)
MESSAGE_KIND_TO_LABEL = dict(MESSAGE_KIND_CHOICES)

# Renderers

RENDERER_MARKDOWN = 'markdown'
RENDERER_HTML = 'html'

RENDERER_CHOICES = (
    (RENDERER_MARKDOWN, _('markdown')),
    (RENDERER_HTML, _('html'))
)

RENDERER_TO_LABEL = dict(RENDERER_CHOICES)


# Languages :

LANGUAGE_FRENCH = 'french'
LANGUAGE_ENGLISH = 'english'
LANGUAGE_GERMAN = 'german'
LANGUAGE_SPANISH = 'spanish'
LANGUAGE_ITALIAN = 'italian'

LANGUAGE_CHOICES = (
    (LANGUAGE_FRENCH, _('french')),
    (LANGUAGE_ENGLISH, _('english')),
    (LANGUAGE_GERMAN, _('german')),
    (LANGUAGE_SPANISH, _('spanish')),
    (LANGUAGE_ITALIAN, _('italian')),
)

LANGUAGE_TO_LABEL = dict(LANGUAGE_CHOICES)
