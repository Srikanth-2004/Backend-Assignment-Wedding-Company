import os
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    MASTER_DB_NAME: str = "master_db"
    JWT_SECRET: str = "your-secret-key"  # Change this in production
    JWT_ALGORITHM: str = "HS256"

settings = Settings()

class Database:
    client: AsyncIOMotorClient = None

    def connect(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URL)
        print("Connected to MongoDB")

    def close(self):
        self.client.close()

    def get_master_db(self):
        return self.client[settings.MASTER_DB_NAME]

    def get_tenant_collection(self, collection_name: str):
        # Dynamic access to tenant collections within the master DB 
        # (or a separate DB depending on preference, here we use collections)
        return self.client[settings.MASTER_DB_NAME][collection_name]

db = Database()