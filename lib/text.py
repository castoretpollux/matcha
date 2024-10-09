import string
from unidecode import unidecode

CLASS_ALLOWED_CHARS = string.ascii_letters + string.digits + ' '


def camel_case(s):
    return ''.join(x for x in s.title() if not x.isspace())


def create_class_name(s):
    no_diacritic = unidecode(s)
    allowed_string = ''.join(x for x in no_diacritic if x in CLASS_ALLOWED_CHARS)
    return camel_case(allowed_string)

