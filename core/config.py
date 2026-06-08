from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str = "mock"  # opciones: mock, ollama, openai, anthropic
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.3"

    # Anthropic (Claude) — visión + interpretación cultural
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-opus-4-8"  # interpretación cultural (RAG)
    vision_model: str = "claude-sonnet-4-6"  # descripción de la imagen

    # MongoDB (vector store) — Railway self-hosted
    # MONGO_URL: dominio privado (corriendo dentro de Railway)
    # MONGO_PUBLIC_URL: proxy TCP (corriendo en local, p.ej. para indexar)
    mongo_url: str = ""
    mongo_public_url: str = ""
    mongo_db: str = "rupestre"
    mongo_collection: str = "corpus_rupestre"
    corpus_top_k: int = 4  # pasajes recuperados por consulta

    # Detección de motivos (YOLO) + clasificación por visión
    # Umbral bajo = más recall (detecta más figuras); las genéricas las
    # reclasifica Claude visión recortando cada caja.
    motif_confidence_threshold: float = 0.2
    motif_max_classify: int = 20  # máx. recortes enviados a Claude por imagen
    max_regional_parallels: int = 3  # máx. paralelos iconográficos en la ficha

    output_dir: str = "./data/fichas"
    samples_dir: str = "./data/samples"
    min_image_resolution: int = 1_000_000  # 1MP
    max_upscale_factor: float = 4.0  # evita inflar imágenes extremadamente pequeñas
    blur_threshold: float = 30.0
    # Realce DStretch: desviación objetivo del eje rojo-verde (canal a* LAB).
    # Mayor = pigmento rojo más vívido. El ~95% de los pictogramas son rojos.
    dstretch_red_std: float = 32.0
    hitl_confidence_threshold: float = 0.6
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    # LaMa inpainting
    lama_enabled: bool = True
    lama_device: str = "cpu"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def mongo_uri(self) -> str:
        """URI efectiva: privada (Railway) con fallback a la pública (local)."""
        return self.mongo_url or self.mongo_public_url


settings = Settings()
