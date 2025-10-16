"""
Sistema de Monitoramento de Placas Solares - Arquivo Principal
"""

import uvicorn
import logging
import os
from backend.main import app
from backend.config import settings

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_directories():
    """Criar diretórios necessários"""
    directories = [
        "logs",
        "data",
        "backups",
        "frontend/dist"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

if __name__ == "__main__":
    logger.info("Iniciando Sistema de Monitoramento de Placas Solares")
    
    # Criar diretórios necessários
    create_directories()
    
    # Configurar servidor
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
