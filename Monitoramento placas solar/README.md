# Sistema de Monitoramento de Placas Solares

Sistema completo para monitoramento de energia solar com coleta automática de dados, dashboard web e análises avançadas.

## Equipamentos Suportados

- **Inversor String Single** (SN: 2106027230) - 3kW
- **Logger** (SN: 1782433145) - Dispositivo de comunicação

## Funcionalidades

### 🔌 Conexão com Equipamentos
- Comunicação via Modbus TCP/RTU
- Suporte a protocolos proprietários
- Conexão via Wi-Fi/Ethernet
- APIs REST para integração

### 📊 Dashboard em Tempo Real
- Visualização de produção de energia
- Gráficos de desempenho
- Alertas e notificações
- Comparação histórica

### 📈 Análises e Relatórios
- Eficiência do sistema
- Análise de ROI
- Previsão de produção
- Relatórios personalizados

### 🔄 Coleta Automática
- Coleta de dados a cada minuto
- Armazenamento histórico
- Backup automático
- Sincronização em nuvem

## Arquitetura do Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Inversor      │───▶│     Logger      │───▶│   Backend API   │
│   Solar         │    │   (Gateway)     │    │   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Dashboard     │◀───│   Frontend      │◀───│   Database      │
│   Web           │    │   (React)       │    │   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Instalação Rápida

### Windows
```bash
# Execute o instalador automático
start.bat
```

### Linux/macOS
```bash
# Execute o instalador automático
chmod +x start.sh && ./start.sh
```

### Manual
1. Instale as dependências: `pip install -r requirements.txt`
2. Configure as variáveis de ambiente (copie `env.example` para `.env`)
3. Execute o sistema: `python main.py`

## Configuração

### Variáveis de Ambiente
```env
DATABASE_URL=postgresql://user:password@localhost/solar_monitoring
MODBUS_HOST=192.168.1.100
MODBUS_PORT=502
INVERTER_ADDRESS=1
LOGGER_ADDRESS=2
API_KEY=sua_api_key_aqui
```

### Conexão com Equipamentos
1. Configure o IP do logger na rede local
2. Ajuste os endereços Modbus conforme documentação
3. Teste a conectividade com o comando de diagnóstico

## Uso

### Iniciando o Sistema
```bash
# Desenvolvimento
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Produção
python main.py
```

### Acessando o Dashboard
- URL: http://localhost:3000
- API: http://localhost:8000/docs

## Monitoramento

### Métricas Coletadas
- Potência instantânea (W)
- Energia diária (kWh)
- Tensão e corrente
- Temperatura do inversor
- Eficiência do sistema
- Status de funcionamento

### Alertas
- Falha na comunicação
- Baixa produção
- Temperatura elevada
- Problemas de conectividade

## Desenvolvimento

### Estrutura do Projeto
```
├── backend/          # API FastAPI
├── frontend/         # Dashboard React
├── database/         # Esquemas e migrações
├── modbus_client/    # Cliente Modbus
├── data_collector/   # Coletor de dados
├── analytics/        # Análises e relatórios
└── config/           # Configurações
```

### Contribuindo
1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Suporte

Para suporte técnico ou dúvidas sobre integração, consulte:
- Documentação da API: `/docs`
- Logs do sistema: `/logs`
- Status da conexão: `/health`

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
