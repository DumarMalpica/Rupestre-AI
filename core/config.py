from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str = "mock"  # opciones: mock, ollama, openai
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.3"
    chromadb_path: str = "./data/chroma"
    chromadb_collection: str = "corpus_rupestre"
    output_dir: str = "./data/fichas"
    samples_dir: str = "./data/samples"
    min_image_resolution: int = 1_000_000  # 1MP
    max_upscale_factor: float = 4.0  # evita inflar imágenes extremadamente pequeñas
    blur_threshold: float = 100.0
    hitl_confidence_threshold: float = 0.6
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
