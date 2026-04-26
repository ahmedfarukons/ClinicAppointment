from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- LLM / Embeddings ---
    gemini_api_key: str = ""
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "gemini-flash-latest"
    qdrant_path: str = "./qdrant_data"
    collection_name: str = "chatdoctor"
    chunk_size: int = 512
    chunk_overlap: int = 64

    # --- Database ---
    database_path: str = "./data/chatdoctor.db"

    # --- Authentication ---
    jwt_secret: str = "change-me-in-production-use-a-random-string"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480  # 8 hours

    # --- Rate Limiting ---
    rate_limit: str = "30/minute"

    # --- Logging ---
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
