__all__  = (
    "OsakerError",
    "OsakerParseError"
)

class OsakerError(Exception):
    ...

class OsakerParseError(OsakerError):
    ...