import re

from django.core.exceptions import ValidationError

from foodgram.constants import USER_ME


def username_validator(value):
    regex = r'^[\w.@+-]+\Z'
    if re.search(regex, value) is None:
        invalid_characters = set(re.findall(r'[^\w.@+-]', value))
        raise ValidationError(
            (
                f'Недопустимые символы {invalid_characters} в username. '
                f'username может содержать только буквы, цифры и '
                f'знаки @/./+/-/_.'
            ),
        )

    if value.lower() == USER_ME:
        raise ValidationError(
            f'Использовать имя <{USER_ME}> в качестве '
            f'username запрещено.'
        )


def color_validator(value):
    regex = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    if not re.match(regex, value):
        raise ValidationError(
            'Поле должно содержать корректный HEX-код цвета '
            'в формате #RRGGBB или #RGB'
        )
