from rest_framework.exceptions import ValidationError

from api_yamdb.settings import USERNAME_SYMBOLS

ERROR_NAME = 'Недопустимое имя пользователя {value}!'
SYMBOLS_ERROR = 'Недопустимые символы: {value}!'


class UserValidator:
    def validate_username(self, value):
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
