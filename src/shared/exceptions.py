class ModelError(Exception):
    """Exception raised when a machine learning model fails to load or process data."""
    pass


class APIConnectionError(Exception):
    """Exception raised when an external API adapter fails to connect or returns an error."""
    pass


class ValidationError(Exception):
    """Exception raised when input data does not meet the required domain constraints."""
    pass

class ModelNotFoundError(ModelError):
    """Exception raised when a requested model is not found or supported."""
    def __init__(self, model_name):
        self.model_name = model_name
        super().__init__(f"Model '{model_name}' not found or not supported.")