# Guia de Instalação - Sistema de Monitoramento Solar

## 🚀 Instalação Rápida

### Windows
1. Execute o arquivo `start.bat` como administrador
2. Aguarde a instalação automática das dependências
3. Configure o arquivo `.env` com os IPs dos seus equipamentos
4. Acesse http://localhost:8000

### Linux/macOS
1. Execute: `chmod +x start.sh && ./start.sh`
2. Aguarde a instalação automática das dependências
3. Configure o arquivo `.env` com os IPs dos seus equipamentos
4. Acesse http://localhost:8000

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Acesso à rede local onde estão os equipamentos
- Equipamentos configurados e funcionando

## 🔧 Configuração dos Equipamentos

### Baseado nas suas imagens:

**Inversor (SN: 2106027230)**
- Modelo: String Single Inverter
- Potência: 3kW
- MPPT: 1
- Protocolo: V0.2.0.1

**Logger (SN: 1782433145)**
- Modelo: LSW3_15_FFFF
- Firmware: 1.0.9E
- Sistema: V1.1.00.10
- Wi-Fi: NetPlus-Charles (90% sinal)

### Configuração do arquivo .env:

```env
# Modbus - Inversor
INVERTER_HOST=192.168.1.XXX  # IP do inversor na sua rede
INVERTER_PORT=502
INVERTER_ADDRESS=1

# Modbus - Logger  
LOGGER_HOST=192.168.1.YYY    # IP do logger na sua rede
LOGGER_PORT=502
LOGGER_ADDRESS=2
```

## 🔍 Como descobrir os IPs dos equipamentos

### Método 1: Aplicativo do fabricante
1. Abra o aplicativo que você já usa
2. Verifique as configurações de rede
3. Anote os endereços IP

### Método 2: Router/Gateway
1. Acesse o painel do seu roteador (geralmente 192.168.1.1)
2. Procure por "Dispositivos conectados" ou "DHCP"
3. Procure pelos dispositivos com nomes similares aos SNs

### Método 3: Scanner de rede
1. Use ferramentas como Advanced IP Scanner
2. Escaneie sua rede local
3. Procure por dispositivos nas portas 502 (Modbus)

## 🧪 Teste de Conectividade

Após configurar os IPs, execute o teste:

```bash
python test_connection.py
```

Este script irá:
- Testar conectividade de rede
- Verificar comunicação Modbus
- Ler dados dos equipamentos
- Mostrar status detalhado

## 📊 Funcionalidades do Sistema

### Dashboard Web
- **Produção em tempo real**: Potência atual, energia diária
- **Gráficos históricos**: Tendências de produção e eficiência
- **Status dos equipamentos**: Conectividade e funcionamento
- **Alertas**: Notificações de problemas
- **Análises**: Relatórios de performance e ROI

### API REST
- **Endpoints completos**: /api/v1/docs
- **Dados em tempo real**: Medições instantâneas
- **Histórico**: Dados históricos exportáveis
- **Analytics**: Análises avançadas de performance

### Coleta Automática
- **Intervalo configurável**: Padrão 60 segundos
- **Armazenamento histórico**: Banco de dados SQLite/PostgreSQL
- **Alertas automáticos**: Baixa produção, temperatura alta, falhas
- **Backup automático**: Proteção dos dados

## 🔧 Solução de Problemas

### Problema: "Falha ao conectar com equipamentos"
**Soluções:**
1. Verifique se os IPs estão corretos
2. Teste conectividade: `ping IP_DO_EQUIPAMENTO`
3. Verifique se a porta 502 está aberta
4. Confirme se os equipamentos estão ligados

### Problema: "Nenhum dado sendo coletado"
**Soluções:**
1. Execute `python test_connection.py`
2. Verifique os logs em `logs/solar_monitoring.log`
3. Confirme endereços Modbus no arquivo `.env`
4. Teste com aplicativo original do fabricante

### Problema: "Dashboard não carrega"
**Soluções:**
1. Verifique se a porta 8000 está livre
2. Acesse http://localhost:8000/health
3. Verifique logs de erro
4. Reinicie o sistema

## 📱 Acesso Remoto

Para acessar o sistema de outros dispositivos na rede:

1. Configure o IP do servidor no arquivo `.env`:
```env
ALLOWED_ORIGINS=["http://localhost:3000", "http://IP_DO_SERVIDOR:8000"]
```

2. Acesse: `http://IP_DO_SERVIDOR:8000`

## 🔒 Segurança

- Sistema roda localmente (não exposto à internet)
- Autenticação pode ser adicionada se necessário
- Logs de acesso e erros mantidos
- Backup automático dos dados

## 📞 Suporte

### Logs do Sistema
- Localização: `logs/solar_monitoring.log`
- Nível: INFO, WARNING, ERROR
- Rotação automática

### Endpoints de Diagnóstico
- **Health Check**: http://localhost:8000/health
- **Status do Sistema**: http://localhost:8000/api/v1/system/status
- **Documentação API**: http://localhost:8000/docs

### Comandos Úteis
```bash
# Ver logs em tempo real
tail -f logs/solar_monitoring.log

# Testar conectividade
python test_connection.py

# Reiniciar sistema
python main.py

# Backup manual
python -c "from backend.database import backup_database"
```

## 🚀 Próximos Passos

1. **Configure alertas por email** (opcional)
2. **Adicione mais equipamentos** se necessário
3. **Configure backup automático**
4. **Integre com Home Assistant** (se desejado)
5. **Configure monitoramento 24/7**

## 📈 Melhorias Futuras

- [ ] App mobile nativo
- [ ] Integração com APIs de previsão do tempo
- [ ] Análise de ROI avançada
- [ ] Relatórios em PDF
- [ ] Integração com inversores de outros fabricantes
- [ ] Dashboard com múltiplos sites
- [ ] Notificações push
- [ ] Análise de sombras e otimização

---

**Desenvolvido especificamente para seus equipamentos:**
- Inversor String Single 3kW (SN: 2106027230)
- Logger LSW3_15_FFFF (SN: 1782433145)

**Versão:** 1.0.0  
**Data:** 2024  
**Compatibilidade:** Python 3.8+
