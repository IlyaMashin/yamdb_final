from time import localtime

from rest_framework.exceptions import ValidationError

from api_yamdb.settings import USERNAME_SYMBOLS

ERROR_NAME = 'Недопустимое имя пользователя {value}!'
SYMBOLS_ERROR = 'Недопустимые символы: {value}!'


def validate_username(value):
    if value == 'me':
        raise ValidationError(ERROR_NAME.format(value=ERROR_NAME))
    if not USERNAME_SYMBOLS.match(value):
        raise ValidationError(
            SYMBOLS_ERROR.format(
                value=''.join(
                    symbol for symbol in value
                    if not USERNAME_SYMBOLS.match(symbol)
                )
            )
        )
    return value


def validate_year(value):
    if value > localtime().tm_year:
        raise ValidationError(
            f'{value} не может быть больше текущей даты'
        )
