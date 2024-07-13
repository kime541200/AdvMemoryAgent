import torch
from pydantic_settings import BaseSettings
from pydantic import BaseModel, field_validator, model_validator

# === System ===

class SystemSetting(BaseModel):
    device: str = "cuda"
    store_chat_to_db: bool = True
    chat_verbose: bool = False
    
    @field_validator('device')
    def check_device(cls, v):
        if v not in ['cuda', 'cpu']:
            raise ValueError(f"\n`device` must be one of ['cuda', 'cpu'], got {v}.\n")
        return v

    @model_validator(mode="after")
    def check_values(cls, values):
        values.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        return values

# === LLM ===

class LLMClientSetting(BaseModel):
    host: str = 'http://127.0.0.1:11434'
    model: str = "gemma2"
    keep_alive: int = 0
    
    @field_validator('keep_alive')
    def check_keep_alive(cls, v):
        if v < 0:
            raise ValueError(f"\n`keep_alive` must higher than 0, got {v}.\n")
        return v

# === Vector store database ===

class VectorStoreDatabaseSetting(BaseModel):
    name: str = 'conversation'

# === Indexing ===

class IndexingSetting(BaseModel):
    embed_model: str = ""

# === Reranker ===

class RerankerSetting(BaseModel):
    reranker_model_path: str
    rerank_threshold: float = 0.01

# === PostgreSQL database ===

class PostgreSQLDatabaseSetting(BaseModel):
    dbname: str
    user: str
    password: str
    host: str
    port: str

# === Setting ===

class Settings(BaseSettings):
    system: SystemSetting
    llm_client: LLMClientSetting
    vector_db: VectorStoreDatabaseSetting
    indexing: IndexingSetting
    sql_db: PostgreSQLDatabaseSetting
    reranker: RerankerSetting

    class Config:
        env_file = '.env'