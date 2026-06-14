class InfrastructureError(Exception):
    pass


class LostConnectionError(InfrastructureError):
    def __init__(self):
        super().__init__("Lost connection to database")
