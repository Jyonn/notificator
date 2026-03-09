class NotificatorError(RuntimeError):
    pass


class NotificatorAPIError(NotificatorError):
    def __init__(self, identifier: str, message: str, details=None):
        self.identifier = identifier
        self.message = message
        self.details = details if details is not None else []
        super().__init__(f'{identifier}: {message} | details={self.details}')
