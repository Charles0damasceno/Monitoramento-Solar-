"""
Serviço de alertas do sistema de monitoramento solar
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from ..config import settings, ALARM_CONFIG
from ..database import SessionLocal
from ..models import Alert, Inverter, InverterMeasurement, Logger, LoggerMeasurement

logger = logging.getLogger(__name__)

class AlertService:
    """Serviço para gerenciamento de alertas"""
    
    def __init__(self):
        self.last_alert_check = None
        
    async def check_alerts(self):
        """Verificar e criar alertas baseados nas condições atuais"""
        try:
            db = SessionLocal()
            
            # Verificar alertas de baixa produção
            await self._check_low_production_alerts(db)
            
            # Verificar alertas de temperatura alta
            await self._check_high_temperature_alerts(db)
            
            # Verificar alertas de comunicação
            await self._check_communication_alerts(db)
            
            # Verificar alertas de falha
            await self._check_fault_alerts(db)
            
            self.last_alert_check = datetime.utcnow()
            db.commit()
            
        except Exception as e:
            logger.error(f"Erro ao verificar alertas: {e}")
            db.rollback()
        finally:
            db.close()
            
    async def _check_low_production_alerts(self, db: Session):
        """Verificar alertas de baixa produção"""
        if not ALARM_CONFIG["low_production"]["enabled"]:
            return
            
        try:
            threshold = ALARM_CONFIG["low_production"]["threshold"]
            message = ALARM_CONFIG["low_production"]["message"]
            
            # Obter inversor
            inverter = db.query(Inverter).first()
            if not inverter:
                return
                
            # Obter última medição
            latest_measurement = db.query(InverterMeasurement)\
                .filter(InverterMeasurement.inverter_id == inverter.id)\
                .order_by(InverterMeasurement.timestamp.desc())\
                .first()
                
            if not latest_measurement or not latest_measurement.power_output:
                return
                
            # Verificar se a produção está abaixo do threshold
            if latest_measurement.power_output < threshold:
                # Verificar se já existe alerta ativo
                existing_alert = db.query(Alert)\
                    .filter(Alert.inverter_id == inverter.id)\
                    .filter(Alert.alert_type == "low_production")\
                    .filter(Alert.resolved == False)\
                    .first()
                    
                if not existing_alert:
                    await self.create_alert(
                        alert_type="low_production",
                        severity="medium",
                        message=message,
                        value=latest_measurement.power_output,
                        threshold=threshold,
                        inverter_id=inverter.id
                    )
                    
        except Exception as e:
            logger.error(f"Erro ao verificar alertas de baixa produção: {e}")
            
    async def _check_high_temperature_alerts(self, db: Session):
        """Verificar alertas de temperatura alta"""
        if not ALARM_CONFIG["high_temperature"]["enabled"]:
            return
            
        try:
            threshold = ALARM_CONFIG["high_temperature"]["threshold"]
            message = ALARM_CONFIG["high_temperature"]["message"]
            
            # Obter inversor
            inverter = db.query(Inverter).first()
            if not inverter:
                return
                
            # Obter última medição
            latest_measurement = db.query(InverterMeasurement)\
                .filter(InverterMeasurement.inverter_id == inverter.id)\
                .order_by(InverterMeasurement.timestamp.desc())\
                .first()
                
            if not latest_measurement or not latest_measurement.temperature:
                return
                
            # Verificar se a temperatura está acima do threshold
            if latest_measurement.temperature > threshold:
                # Verificar se já existe alerta ativo
                existing_alert = db.query(Alert)\
                    .filter(Alert.inverter_id == inverter.id)\
                    .filter(Alert.alert_type == "high_temperature")\
                    .filter(Alert.resolved == False)\
                    .first()
                    
                if not existing_alert:
                    await self.create_alert(
                        alert_type="high_temperature",
                        severity="high",
                        message=message,
                        value=latest_measurement.temperature,
                        threshold=threshold,
                        inverter_id=inverter.id
                    )
                    
        except Exception as e:
            logger.error(f"Erro ao verificar alertas de temperatura alta: {e}")
            
    async def _check_communication_alerts(self, db: Session):
        """Verificar alertas de comunicação"""
        if not ALARM_CONFIG["communication_error"]["enabled"]:
            return
            
        try:
            timeout_threshold = ALARM_CONFIG["communication_error"]["timeout"]
            message = ALARM_CONFIG["communication_error"]["message"]
            
            # Verificar última atualização do inversor
            latest_inverter_measurement = db.query(InverterMeasurement)\
                .order_by(InverterMeasurement.timestamp.desc())\
                .first()
                
            if latest_inverter_measurement:
                time_diff = datetime.utcnow() - latest_inverter_measurement.timestamp
                if time_diff.total_seconds() > timeout_threshold:
                    # Verificar se já existe alerta ativo
                    existing_alert = db.query(Alert)\
                        .filter(Alert.alert_type == "communication_error")\
                        .filter(Alert.resolved == False)\
                        .first()
                        
                    if not existing_alert:
                        await self.create_alert(
                            alert_type="communication_error",
                            severity="high",
                            message=f"{message} - Última atualização: {time_diff.total_seconds():.0f}s atrás"
                        )
                        
            # Verificar última atualização do logger
            latest_logger_measurement = db.query(LoggerMeasurement)\
                .order_by(LoggerMeasurement.timestamp.desc())\
                .first()
                
            if latest_logger_measurement:
                time_diff = datetime.utcnow() - latest_logger_measurement.timestamp
                if time_diff.total_seconds() > timeout_threshold:
                    # Verificar se já existe alerta ativo
                    existing_alert = db.query(Alert)\
                        .filter(Alert.alert_type == "logger_communication_error")\
                        .filter(Alert.resolved == False)\
                        .first()
                        
                    if not existing_alert:
                        await self.create_alert(
                            alert_type="logger_communication_error",
                            severity="medium",
                            message=f"Erro de comunicação com logger - Última atualização: {time_diff.total_seconds():.0f}s atrás"
                        )
                        
        except Exception as e:
            logger.error(f"Erro ao verificar alertas de comunicação: {e}")
            
    async def _check_fault_alerts(self, db: Session):
        """Verificar alertas de falha"""
        if not ALARM_CONFIG["fault_detected"]["enabled"]:
            return
            
        try:
            message = ALARM_CONFIG["fault_detected"]["message"]
            
            # Obter inversor
            inverter = db.query(Inverter).first()
            if not inverter:
                return
                
            # Obter última medição
            latest_measurement = db.query(InverterMeasurement)\
                .filter(InverterMeasurement.inverter_id == inverter.id)\
                .order_by(InverterMeasurement.timestamp.desc())\
                .first()
                
            if not latest_measurement:
                return
                
            # Verificar códigos de falha
            if latest_measurement.fault_code and latest_measurement.fault_code > 0:
                # Verificar se já existe alerta ativo para esta falha
                existing_alert = db.query(Alert)\
                    .filter(Alert.inverter_id == inverter.id)\
                    .filter(Alert.alert_type == "fault_detected")\
                    .filter(Alert.value == latest_measurement.fault_code)\
                    .filter(Alert.resolved == False)\
                    .first()
                    
                if not existing_alert:
                    await self.create_alert(
                        alert_type="fault_detected",
                        severity="critical",
                        message=f"{message} - Código: {latest_measurement.fault_code}",
                        value=latest_measurement.fault_code,
                        inverter_id=inverter.id
                    )
                    
            # Verificar status do inversor
            if latest_measurement.status_code and latest_measurement.status_code != 1:
                # Status diferente de 1 pode indicar problema
                existing_alert = db.query(Alert)\
                    .filter(Alert.inverter_id == inverter.id)\
                    .filter(Alert.alert_type == "status_warning")\
                    .filter(Alert.value == latest_measurement.status_code)\
                    .filter(Alert.resolved == False)\
                    .first()
                    
                if not existing_alert:
                    await self.create_alert(
                        alert_type="status_warning",
                        severity="medium",
                        message=f"Status anômalo do inversor - Código: {latest_measurement.status_code}",
                        value=latest_measurement.status_code,
                        inverter_id=inverter.id
                    )
                    
        except Exception as e:
            logger.error(f"Erro ao verificar alertas de falha: {e}")
            
    async def create_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        value: Optional[float] = None,
        threshold: Optional[float] = None,
        inverter_id: Optional[int] = None,
        logger_id: Optional[int] = None
    ) -> Alert:
        """Criar novo alerta"""
        db = SessionLocal()
        try:
            alert = Alert(
                inverter_id=inverter_id,
                logger_id=logger_id,
                alert_type=alert_type,
                severity=severity,
                message=message,
                value=value,
                threshold=threshold,
                timestamp=datetime.utcnow()
            )
            
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            logger.info(f"Alerta criado: {alert_type} - {message}")
            
            # Aqui você pode adicionar lógica para enviar notificações
            # (email, SMS, webhook, etc.)
            await self._send_notification(alert)
            
            return alert
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta: {e}")
            db.rollback()
            raise
        finally:
            db.close()
            
    async def _send_notification(self, alert: Alert):
        """Enviar notificação do alerta"""
        try:
            # Implementar envio de notificações aqui
            # Exemplos:
            # - Email
            # - SMS
            # - Webhook
            # - Push notification
            
            logger.info(f"Notificação enviada para alerta: {alert.alert_type}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação: {e}")
            
    async def acknowledge_alert(self, alert_id: int) -> bool:
        """Reconhecer alerta"""
        db = SessionLocal()
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                return False
                
            alert.acknowledged = True
            alert.acknowledged_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Alerta {alert_id} reconhecido")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao reconhecer alerta {alert_id}: {e}")
            db.rollback()
            return False
        finally:
            db.close()
            
    async def resolve_alert(self, alert_id: int) -> bool:
        """Resolver alerta"""
        db = SessionLocal()
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                return False
                
            alert.resolved = True
            alert.resolved_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Alerta {alert_id} resolvido")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao resolver alerta {alert_id}: {e}")
            db.rollback()
            return False
        finally:
            db.close()
            
    async def get_active_alerts(self) -> List[Alert]:
        """Obter alertas ativos"""
        db = SessionLocal()
        try:
            alerts = db.query(Alert)\
                .filter(Alert.resolved == False)\
                .order_by(Alert.timestamp.desc())\
                .all()
                
            return alerts
            
        except Exception as e:
            logger.error(f"Erro ao obter alertas ativos: {e}")
            return []
        finally:
            db.close()
            
    async def get_alert_statistics(self) -> Dict[str, Any]:
        """Obter estatísticas de alertas"""
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            last_24h = now - timedelta(hours=24)
            last_7d = now - timedelta(days=7)
            last_30d = now - timedelta(days=30)
            
            stats = {
                "total_alerts": db.query(Alert).count(),
                "active_alerts": db.query(Alert).filter(Alert.resolved == False).count(),
                "alerts_24h": db.query(Alert).filter(Alert.timestamp >= last_24h).count(),
                "alerts_7d": db.query(Alert).filter(Alert.timestamp >= last_7d).count(),
                "alerts_30d": db.query(Alert).filter(Alert.timestamp >= last_30d).count(),
                "by_severity": {
                    "critical": db.query(Alert).filter(Alert.severity == "critical", Alert.resolved == False).count(),
                    "high": db.query(Alert).filter(Alert.severity == "high", Alert.resolved == False).count(),
                    "medium": db.query(Alert).filter(Alert.severity == "medium", Alert.resolved == False).count(),
                    "low": db.query(Alert).filter(Alert.severity == "low", Alert.resolved == False).count(),
                },
                "by_type": {}
            }
            
            # Contar por tipo de alerta
            alert_types = db.query(Alert.alert_type).distinct().all()
            for alert_type in alert_types:
                count = db.query(Alert).filter(
                    Alert.alert_type == alert_type[0],
                    Alert.resolved == False
                ).count()
                stats["by_type"][alert_type[0]] = count
                
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de alertas: {e}")
            return {}
        finally:
            db.close()
