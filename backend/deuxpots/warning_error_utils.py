from warnings import catch_warnings, warn


DEFAULT_USER_ERROR_MESSAGE = "Une erreur imprévue s'est produite sur le serveur."


class UserFacingWarning(Warning):
    pass


class UserFacingError(Exception):
    pass


def handle_warnings(category=Warning):
    """
    Decorate a function that returns a dictionary (e.g. Flask API route).
    Add a "warnings" key to the output with the list of warnings raised.
    """
    def _decorator(func):
        def func_decorated(*args, **kwargs):
            with catch_warnings(category=category, record=True) as records:
                response = func(*args, **kwargs)
            warnings = []
            for record in records:
                warn(record.message)
                if isinstance(record.message, category):
                    if record.message.args:
                        warnings.append(record.message.args[0])
                    else:
                        warnings.append(record.category.__name__)
            return {**response, 'warnings': warnings}
        return func_decorated
    return _decorator
