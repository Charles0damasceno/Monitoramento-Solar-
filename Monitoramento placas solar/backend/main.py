"""
Sistema de Monitoramento de Placas Solares - Backend API
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import uvicorn
import asyncio
from datetime import datetime, timedelta
import logging

from .config import settings
from .database import init_db
from .models import Base
from .routers import (
    inverter_router,
    data_router,
    analytics_router,
    system_router,
    alerts_router
)
from .services.data_collector import DataCollectorService
from .services.alert_service import AlertService

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Serviços globais
data_collector = None
alert_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciamento do ciclo de vida da aplicação"""
    global data_collector, alert_service
    
    # Inicialização
    logger.info("Inicializando sistema de monitoramento solar...")
    
    # Inicializar banco de dados
    await init_db()
    logger.info("Banco de dados inicializado")
    
    # Inicializar serviços
    data_collector = DataCollectorService()
    alert_service = AlertService()
    
    # Iniciar coleta de dados em background
    asyncio.create_task(data_collector.start_collection())
    logger.info("Coleta de dados iniciada")
    
    yield
    
    # Limpeza
    logger.info("Parando sistema de monitoramento...")
    if data_collector:
        await data_collector.stop_collection()
    logger.info("Sistema parado")

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema de Monitoramento Solar",
    description="API para monitoramento completo de placas solares",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(inverter_router.router, prefix="/api/v1/inverters", tags=["inverters"])
app.include_router(data_router.router, prefix="/api/v1/data", tags=["data"])
app.include_router(analytics_router.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(system_router.router, prefix="/api/v1/system", tags=["system"])
app.include_router(alerts_router.router, prefix="/api/v1/alerts", tags=["alerts"])

# Servir arquivos estáticos (frontend)
app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página inicial - redireciona para o dashboard"""
    with open("frontend/dist/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health_check():
    """Verificação de saúde do sistema"""
    try:
        # Verificar conectividade com equipamentos
        inverter_status = await data_collector.check_inverter_connection() if data_collector else False
        logger_status = await data_collector.check_logger_connection() if data_collector else False
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "services": {
                "data_collector": data_collector is not None,
                "alert_service": alert_service is not None,
                "inverter_connected": inverter_status,
                "logger_connected": logger_status
            },
            "uptime": "calculado_em_background"
        }
    except Exception as e:
        logger.error(f"Erro na verificação de saúde: {e}")
        raise HTTPException(status_code=503, detail="Sistema indisponível")

@app.get("/api/v1/status")
async def system_status():
    """Status detalhado do sistema"""
    if not data_collector:
        raise HTTPException(status_code=503, detail="Coletor de dados não inicializado")
    
    return await data_collector.get_system_status()

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
