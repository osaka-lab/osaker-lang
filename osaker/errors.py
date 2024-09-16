__all__  = (
    "OsakerError",
    "OsakerParseError",
    "OsakerSyntaxError",
    "OsakerIncorrectTypeError",
    "OsakerNameError",
    "OsakerTypeError",
)

class OsakerError(Exception):
    ...

class OsakerParseError(OsakerError):
    def __init__(self, error: Exception) -> None:
        super().__init__(f"uhhh idk parse error! Error: {error}")

class OsakerSyntaxError(OsakerError):
    ...

class OsakerNameError(OsakerError):
    ...

class OsakerTypeError(OsakerError):
    ...

class OsakerIncorrectTypeError(OsakerTypeError):
    ...

class OsakerModuleDoesntExist(OsakerTypeError):
    ...