from core.config.errors import AppError

class MessageBusError(AppError):
    """Message bus specific errors."""
    pass

class MessageValidationError(MessageBusError):
    """Message validation errors."""
    pass

class MessageDeliveryError(MessageBusError):
    """Message delivery errors."""
    pass

class MessageHandlerError(MessageBusError):
    """Message handler errors."""
    pass 