import email
from typing import AsyncGenerator
import uuid
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, relationship
import datetime

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    """
    Crea la base de datos y todas las tablas definidas en los modelos.
    """
    async with engine.begin() as conn:
        await conn.run_sync(DeclarativeBase.metadata.create_all)


async def get_db()->AsyncGenerator[AsyncSession, None]:
    """
    Devuelve una sesión de la base de datos.
    """
    async with async_session() as session:
        yield session

class UserSqlModel(DeclarativeBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    disabled = Column(Boolean, default=False)
    password = Column(String, index=True)

    def __repr__(self):
        return f"UserSqlModel(id={self.id}, username={self.username}, full_name={self.full_name}, email={self.email}, disabled={self.disabled}, password={self.password})"
