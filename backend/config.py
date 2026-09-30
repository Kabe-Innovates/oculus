from pydantic_settings import BaseSettings

class ConfigSettings(BaseSettings):
    DATABASE_URL: str = 'sqlite+aiosqlite:///./sentinelpay.db'
    SNS_TOPIC_ARN: str = ''
    AWS_REGION: str = 'ap-south-1'
    VELOCITY_WINDOW_SECONDS: int = 300
    VELOCITY_THRESHOLD: int = 5
    AMOUNT_DEVIATION_THRESHOLD: float = 2.0
    GEO_MAX_SPEED_KMH: float = 900.0
    RISK_BLOCK_THRESHOLD: float = 60.0
    RISK_REVIEW_THRESHOLD: float = 30.0
    SIMULATOR_RATE: float = 2.0
    
    class Config:
        env_file = '.env'

settings = ConfigSettings()
