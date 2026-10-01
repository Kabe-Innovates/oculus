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
    SINGLE_RULE_FACTOR: float = 0.65
    RULE_TIMEOUT_SECONDS: float = 0.5
    ALERT_COOLDOWN_SECONDS: int = 300
    NEW_DEVICE_MIN_AMOUNT: float = 1000.0
    BLOCKED_RECEIVERS: list[str] = ["merchant_666"]
    AMOUNT_MIN_HISTORY: int = 5
    AMOUNT_NO_HISTORY_LIMIT: float = 5000.0
    GEO_MIN_DISTANCE_KM: float = 50.0
    SIMULATOR_TARGET_URL: str = "http://127.0.0.1:8000/api/transactions"
    
    class Config:
        env_file = '.env'

settings = ConfigSettings()
