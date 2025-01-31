

from pydantic_settings import BaseSettings, SettingsConfigDict

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_NAME: str
    DB_PASS: str
    DATABASE_URL: str
    PRIVATE_ACCESS_KEY: str
    PRIVATE_REFRESH_KEY: str
    ACCESS_TOKEN_EXPIRES_IN: int
    REFRESH_TOKEN_EXPIRES_IN: int
    JWT_ALGORITHM: str


    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()





engine = create_async_engine(url=settings.DATABASE_URL, echo=True, future=True)
async_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession)

async def get_async_session():
    async with async_session_maker() as session:
        yield session