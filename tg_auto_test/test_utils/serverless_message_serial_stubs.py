"""Mixin class for ServerlessMessage TL serialization protocol stubs."""


class ServerlessMessageSerialStubs:
    """Mixin class containing TL serialization protocol stubs for ServerlessMessage."""

    # TL protocol constants - set as class attributes
    CONSTRUCTOR_ID = 0
    SUBCLASS_OF_ID = 0

    @classmethod
    def from_reader(cls, *args, **kwargs) -> object:
        """TL protocol deserialization - not supported in serverless testing mode."""
        raise NotImplementedError("from_reader is not supported in serverless testing mode")

    @staticmethod
    def serialize_bytes(*args, **kwargs) -> object:
        """TL protocol serialization - not supported in serverless testing mode."""
        raise NotImplementedError("serialize_bytes is not supported in serverless testing mode")

    @staticmethod
    def serialize_datetime(*args, **kwargs) -> object:
        """TL protocol serialization helper - not supported in serverless testing mode."""
        raise NotImplementedError("serialize_datetime is not supported in serverless testing mode")

    def to_dict(self, *args, **kwargs) -> object:
        """TL protocol serialization - not supported in serverless testing mode."""
        raise NotImplementedError("to_dict is not supported in serverless testing mode")

    def to_json(self, *args, **kwargs) -> object:
        """TL protocol serialization - not supported in serverless testing mode."""
        raise NotImplementedError("to_json is not supported in serverless testing mode")

    def stringify(self, *args, **kwargs) -> object:
        """TL protocol debugging - not supported in serverless testing mode."""
        raise NotImplementedError("stringify is not supported in serverless testing mode")

    def pretty_format(self, *args, **kwargs) -> object:
        """TL protocol debugging - not supported in serverless testing mode."""
        raise NotImplementedError("pretty_format is not supported in serverless testing mode")
