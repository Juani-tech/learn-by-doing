"""Custom exceptions for the application."""


class LearnByDoingException(Exception):
    """Base exception for the application."""
    pass


class AgentException(LearnByDoingException):
    """Exception raised by agents."""
    pass


class LLMException(LearnByDoingException):
    """Exception raised by LLM client."""
    pass


class ValidationException(LearnByDoingException):
    """Exception raised during validation."""
    pass


class WorkflowException(LearnByDoingException):
    """Exception raised by workflow."""
    pass


class DatabaseException(LearnByDoingException):
    """Exception raised by database operations."""
    pass
