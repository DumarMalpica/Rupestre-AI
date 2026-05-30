class ImageQualityError(Exception):
    def __init__(self, message: str, reason: str) -> None:
        super().__init__(message)
        self.reason = reason


class AgentExecutionError(Exception):
    def __init__(self, agent_name: str, message: str) -> None:
        super().__init__(message)
        self.agent_name = agent_name


class CorpusNotIndexedError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ModelNotAvailableError(Exception):
    def __init__(self, model_name: str) -> None:
        super().__init__(f"Model not available: {model_name}")
        self.model_name = model_name
