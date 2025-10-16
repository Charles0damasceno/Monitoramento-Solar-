"""
Configuração e inicialização do banco de dados
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Configurar engine do banco de dados
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite para desenvolvimento
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DEBUG
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # PostgreSQL para produção
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_recycle=300
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Metadata para migrações
metadata = MetaData()

async def init_db():
    """Inicializar banco de dados e criar tabelas"""
    try:
        from .models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        raise

def get_db():
    """Dependency para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    """Dependency para obter sessão assíncrona do banco de dados"""
    # Para versão futura com async
    pass
