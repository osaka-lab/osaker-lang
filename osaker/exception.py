__all__  = (
    "OsakerError",
    "OsakerParseError",
    "OsakerSyntaxError"
)

class OsakerError(Exception):
    ...

class OsakerParseError(OsakerError):
    def __init__(self, error: Exception) -> None:
        super().__init__(f"uhhh idk parse error! Error: {error}")

class OsakerSyntaxError(OsakerError):
    ...