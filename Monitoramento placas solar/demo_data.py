"""
Script para gerar dados de demonstração do sistema de monitoramento solar
"""

import asyncio
import random
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Adicionar o diretório atual ao path
sys.path.append(os.getcwd())

from backend.database import SessionLocal, init_db
from backend.models import Inverter, InverterMeasurement, Logger, LoggerMeasurement, DailySummary, Alert

async def create_demo_data():
    """Criar dados de demonstração para o sistema"""
    print("🎭 Criando dados de demonstração...")
    
    # Inicializar banco de dados
    await init_db()
    
    db = SessionLocal()
    try:
        # Verificar se já existem dados
        existing_inverter = db.query(Inverter).first()
        if existing_inverter:
            print("⚠️ Dados já existem no banco. Pulando criação...")
            return
        
        print("📋 Criando equipamentos...")
        
        # Criar inversor
        inverter = Inverter(
            serial_number="2106027230",
            model="String Single Inverter",
            rated_power=3000.0,
            mppt_count=1,
            protocol_version="V0.2.0.1",
            firmware_version="V6.1.4.3"
        )
        db.add(inverter)
        db.flush()
        
        # Criar logger
        logger = Logger(
            serial_number="1782433145",
            model="LSW3_15_FFFF",
            firmware_version="1.0.9E",
            system_version="V1.1.00.10",
            mac_address="34EAE7B8618E",
            router_ssid="NetPlus-Charles",
            signal_strength=90,
            data_send_interval=5,
            data_log_interval=60,
            max_devices=1
        )
        db.add(logger)
        db.flush()
        
        print("📊 Gerando medições históricas...")
        
        # Gerar dados dos últimos 30 dias
        start_date = datetime.utcnow() - timedelta(days=30)
        current_date = start_date
        
        total_energy = 0.0
        
        while current_date < datetime.utcnow():
            # Simular produção solar baseada na hora do dia e estação
            hour = current_date.hour
            day_of_year = current_date.timetuple().tm_yday
            
            # Curva solar típica (pico ao meio-dia)
            solar_factor = max(0, 1 - ((hour - 12) / 6) ** 2)
            
            # Fator sazonal (verão no Brasil)
            seasonal_factor = 1.0
            if day_of_year in range(340, 365) or day_of_year in range(1, 80):  # Verão
                seasonal_factor = 1.2
            elif day_of_year in range(170, 260):  # Inverno
                seasonal_factor = 0.8
            
            # Potência base
            base_power = 3000 * solar_factor * seasonal_factor
            
            # Adicionar variação aleatória
            power_variation = random.uniform(0.8, 1.2)
            current_power = base_power * power_variation
            
            # Limitar a potência máxima
            current_power = min(current_power, 3000)
            
            # Calcular energia (assumindo medições a cada 5 minutos)
            energy_increment = (current_power * 5 / 60) / 1000  # kWh
            total_energy += energy_increment
            
            # Calcular eficiência (85-95% típico)
            efficiency = random.uniform(85, 95)
            
            # Calcular temperatura (baseada na potência e temperatura ambiente)
            ambient_temp = 25 + random.uniform(-5, 10)
            inverter_temp = ambient_temp + (current_power / 3000) * 15 + random.uniform(-2, 2)
            
            # Criar medição do inversor
            measurement = InverterMeasurement(
                inverter_id=inverter.id,
                timestamp=current_date,
                power_output=round(current_power, 2),
                energy_daily=round(total_energy, 3),
                energy_total=round(total_energy, 3),
                voltage_dc=round(400 + random.uniform(-20, 20), 1),
                current_dc=round(current_power / 400, 2),
                voltage_ac=round(220 + random.uniform(-5, 5), 1),
                current_ac=round(current_power / 220, 2),
                frequency=round(60 + random.uniform(-0.1, 0.1), 2),
                temperature=round(inverter_temp, 1),
                efficiency=round(efficiency, 1),
                status_code=1 if current_power > 0 else 0,
                fault_code=0,
                uptime=random.randint(1000, 8760)
            )
            db.add(measurement)
            
            # Criar medição do logger a cada 5 minutos
            if current_date.minute % 5 == 0:
                logger_measurement = LoggerMeasurement(
                    logger_id=logger.id,
                    timestamp=current_date,
                    connection_status=True,
                    signal_quality=random.randint(85, 95),
                    last_data_sync=current_date,
                    error_count=random.randint(0, 2)
                )
                db.add(logger_measurement)
            
            current_date += timedelta(minutes=5)
        
        print("📅 Criando resumos diários...")
        
        # Criar resumos diários
        for day in range(30):
            date = start_date + timedelta(days=day)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            # Obter medições do dia
            day_measurements = db.query(InverterMeasurement)\
                .filter(InverterMeasurement.inverter_id == inverter.id)\
                .filter(InverterMeasurement.timestamp >= day_start)\
                .filter(InverterMeasurement.timestamp < day_end)\
                .all()
            
            if day_measurements:
                power_values = [m.power_output for m in day_measurements if m.power_output]
                temp_values = [m.temperature for m in day_measurements if m.temperature]
                efficiency_values = [m.efficiency for m in day_measurements if m.efficiency]
                
                summary = DailySummary(
                    date=day_start,
                    inverter_id=inverter.id,
                    total_energy=round(max([m.energy_daily for m in day_measurements], default=0), 2),
                    peak_power=round(max(power_values, default=0), 2),
                    average_power=round(sum(power_values) / len(power_values) if power_values else 0, 2),
                    peak_efficiency=round(max(efficiency_values, default=0), 1),
                    average_efficiency=round(sum(efficiency_values) / len(efficiency_values) if efficiency_values else 0, 1),
                    operating_hours=round(len([m for m in day_measurements if m.power_output and m.power_output > 0]) * 5 / 60, 1),
                    downtime_hours=round(24 - len([m for m in day_measurements if m.power_output and m.power_output > 0]) * 5 / 60, 1),
                    min_temperature=round(min(temp_values, default=0), 1),
                    max_temperature=round(max(temp_values, default=0), 1),
                    average_temperature=round(sum(temp_values) / len(temp_values) if temp_values else 0, 1),
                    alert_count=random.randint(0, 2)
                )
                db.add(summary)
        
        print("⚠️ Criando alertas de demonstração...")
        
        # Criar alguns alertas
        alert_types = [
            ("low_production", "medium", "Baixa produção detectada durante período de alta irradiação"),
            ("high_temperature", "high", "Temperatura do inversor acima do normal"),
            ("communication_error", "high", "Falha temporária de comunicação com o inversor"),
            ("fault_detected", "critical", "Código de falha F001 detectado no inversor")
        ]
        
        for alert_type, severity, message in alert_types:
            # Criar alerta há alguns dias
            alert_date = datetime.utcnow() - timedelta(days=random.randint(1, 15))
            
            alert = Alert(
                inverter_id=inverter.id,
                alert_type=alert_type,
                severity=severity,
                message=message,
                timestamp=alert_date,
                acknowledged=random.choice([True, False]),
                resolved=random.choice([True, False])
            )
            
            if alert.acknowledged:
                alert.acknowledged_at = alert_date + timedelta(minutes=random.randint(5, 60))
            
            if alert.resolved:
                alert.resolved_at = alert_date + timedelta(hours=random.randint(1, 24))
            
            db.add(alert)
        
        # Commit todas as mudanças
        db.commit()
        
        print("✅ Dados de demonstração criados com sucesso!")
        print(f"📊 Total de medições: {db.query(InverterMeasurement).count()}")
        print(f"📅 Resumos diários: {db.query(DailySummary).count()}")
        print(f"⚠️ Alertas: {db.query(Alert).count()}")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados de demonstração: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Função principal"""
    print("🎭 GERADOR DE DADOS DE DEMONSTRAÇÃO")
    print("="*50)
    print("Este script criará dados simulados para demonstração do sistema.")
    print("Os dados incluem:")
    print("- 30 dias de medições do inversor")
    print("- Dados do logger")
    print("- Resumos diários")
    print("- Alertas de exemplo")
    print()
    
    response = input("Continuar? (s/N): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("Operação cancelada.")
        return
    
    try:
        asyncio.run(create_demo_data())
        print("\n🎉 Demonstração pronta!")
        print("Execute 'python main.py' e acesse http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    main()
