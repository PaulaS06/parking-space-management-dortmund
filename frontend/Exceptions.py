class BackendError(Exception):
    """Basisklasse"""

class InvalidParameterError(BackendError):
    pass

class AuthFailedError(BackendError):
    pass

class NoResultsError(BackendError):
    pass

class BackendServerError(BackendError):
    pass