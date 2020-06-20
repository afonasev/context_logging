from pydantic import BaseSettings


class Config(BaseSettings):
    FILL_EXEPTIONS_DEFAULT: bool = True
    LOG_EXECUTION_TIME_DEFAULT: bool = True

    class Config:
        env_prefix = 'CONTEXT_LOGGING_'


config = Config()
