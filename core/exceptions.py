"""Excepciones personalizadas del sistema Rupestre AI."""


class RupestreBaseError(Exception):
    """Excepción base del sistema."""

    pass


class ImageQualityError(RupestreBaseError):
    """La imagen no cumple calidad mínima para procesarse."""

    pass


class AgentExecutionError(RupestreBaseError):
    """Error durante la ejecución de un agente."""

    def __init__(self, agent_name: str, message: str):
        self.agent_name = agent_name
        super().__init__(f"[{agent_name}] {message}")


class RAGRetrievalError(RupestreBaseError):
    """Error durante la recuperación de fragmentos del corpus."""

    pass


class GANInferenceError(RupestreBaseError):
    """Error durante la inferencia del modelo GAN."""

    pass


class DocumentationError(RupestreBaseError):
    """Error durante la generación de la ficha ICANH."""

    pass


class ModelNotFoundError(RupestreBaseError):
    """Pesos del modelo no encontrados en la ruta esperada."""

    pass
