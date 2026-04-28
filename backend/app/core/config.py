from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Scenic Admin API"
    api_prefix: str = "/api"
    database_url: str = "mysql+pymysql://root:password@127.0.0.1:3306/scenic_admin"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120

    # AI / LLM
    dashscope_api_key: str = ""
    llm_model: str = "qwen-plus"
    llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    llm_max_tokens: int = 1024
    llm_temperature: float = 0.7

    # Embedding
    embedding_model: str = "text-embedding-v3"
    embedding_dimension: int = 1024

    # RAG
    rag_top_k: int = 5
    rag_score_threshold: float = 0.5
    rag_context_max_tokens: int = 2000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
