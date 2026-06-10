"""Exception hierarchy: one base class, one subclass per failure mode."""


class Url2md4aiError(Exception):
    """Base class for all url2md4ai errors."""


class FetchError(Url2md4aiError):
    """The URL could not be fetched (network failure or non-2xx response)."""


class UnsupportedContentError(Url2md4aiError):
    """The URL returned a content type that cannot be converted to Markdown."""


class ExtractionError(Url2md4aiError):
    """No meaningful content could be extracted from the page."""
