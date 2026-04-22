from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = ""
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "gemini-1.5-flash"
    qdrant_path: str = "./qdrant_data"
    collection_name: str = "chatdoctor"
    chunk_size: int = 512
    chunk_overlap: int = 64

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
