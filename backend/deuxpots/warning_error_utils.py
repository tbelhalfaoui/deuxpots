from warnings import catch_warnings, warn

from prometheus_client import Counter


DEFAULT_USER_ERROR_MESSAGE = "Une erreur imprévue s'est produite sur le serveur."

PROM_WARNING_COUNT = Counter('warning_count', 'Count the warnings returned to the user.', ['warning', 'arg'])


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
                warning = record.message
                warn(warning)
                if isinstance(warning, category):
                    warnings.append(str(warning))
                PROM_WARNING_COUNT.labels(type(warning).__name__, warning.args[0]).inc()
                print("****** ", type(warning).__name__, warning.args[0])
            return {**response, 'warnings': warnings}
        return func_decorated
    return _decorator
