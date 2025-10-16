# Acesso Remoto - Sistema de Monitoramento Solar

## 🎯 Objetivo
Permitir monitoramento do sistema solar de qualquer lugar do mundo, acessando dados em tempo real.

## 🔧 Opções de Implementação

### **Opção 1: Port Forwarding (Mais Simples)**

#### Configuração no Roteador
1. **Acesse o roteador "NetPlus-Charles"**
   - IP: `192.168.0.1` (geralmente)
   - Login: admin/admin (ou conforme documentação)

2. **Configure Port Forwarding**
   ```
   Porta Externa: 8080 → 192.168.0.101:502 (Logger)
   Porta Externa: 8081 → 192.168.0.101:8000 (API)
   Porta Externa: 8082 → 192.168.0.101:3000 (Dashboard)
   ```

3. **Descubra seu IP público**
   - Acesse: https://whatismyipaddress.com
   - Anote o IP público do roteador

#### Configuração do Sistema
```python
# backend/config.py
REMOTE_ACCESS = True
PUBLIC_IP = "SEU_IP_PUBLICO_AQUI"
```

### **Opção 2: VPN (Mais Seguro)**

#### Configuração OpenVPN
1. **Instale OpenVPN no roteador**
2. **Configure certificados**
3. **Conecte-se via VPN quando estiver fora**

### **Opção 3: Solução em Nuvem (Profissional)**

#### A. Deploy em Servidor Cloud
- **AWS/Azure/Google Cloud**
- **Heroku/Railway/DigitalOcean**
- **Docker containers**

#### B. Serviços de Túnel
- **ngrok** (desenvolvimento)
- **Cloudflare Tunnel** (produção)
- **Tailscale** (rede privada)

## 🚀 Implementação Recomendada

### **Solução Híbrida: Local + Cloud**

#### 1. **Coletor Local** (no local do equipamento)
```python
# Sistema local coleta dados e envia para nuvem
LOCAL_COLLECTOR = {
    "collect_interval": 60,  # segundos
    "cloud_endpoint": "https://seu-servidor.com/api/data",
    "backup_local": True
}
```

#### 2. **API em Nuvem** (acessível globalmente)
```python
# Servidor na nuvem recebe e armazena dados
CLOUD_API = {
    "database": "PostgreSQL na nuvem",
    "storage": "Dados históricos",
    "dashboard": "Interface web global"
}
```

## 📋 Implementação Passo a Passo

### **Passo 1: Configurar Coletor Local**

Crie um script que roda no local do equipamento:

```python
# local_collector.py
import asyncio
import requests
from datetime import datetime

class LocalCollector:
    def __init__(self):
        self.logger_ip = "192.168.0.101"
        self.cloud_api = "https://seu-servidor.com/api"
        
    async def collect_and_send(self):
        # Coletar dados do logger
        data = await self.read_logger_data()
        
        # Enviar para nuvem
        await self.send_to_cloud(data)
        
    async def read_logger_data(self):
        # Implementar leitura Modbus
        pass
        
    async def send_to_cloud(self, data):
        # Enviar dados para API na nuvem
        pass
```

### **Passo 2: Deploy na Nuvem**

#### Opção A: Heroku (Gratuito)
```bash
# 1. Criar app no Heroku
heroku create seu-sistema-solar

# 2. Configurar variáveis
heroku config:set DATABASE_URL=postgresql://...
heroku config:set LOGGER_IP=192.168.0.101

# 3. Deploy
git push heroku main
```

#### Opção B: Railway (Mais Simples)
```bash
# 1. Conectar repositório GitHub
# 2. Railway detecta automaticamente
# 3. Configurar variáveis de ambiente
# 4. Deploy automático
```

### **Passo 3: Configurar Túnel Seguro**

#### Usando ngrok (Desenvolvimento)
```bash
# Instalar ngrok
npm install -g ngrok

# Expor porta local
ngrok http 8000

# Usar URL pública: https://abc123.ngrok.io
```

#### Usando Cloudflare Tunnel (Produção)
```bash
# Instalar cloudflared
# Configurar tunnel
cloudflared tunnel create solar-monitoring
cloudflared tunnel route dns solar-monitoring monitor.suadominio.com
```

## 🔒 Segurança para Acesso Remoto

### **1. Autenticação**
```python
# JWT tokens para API
API_SECRET_KEY = "sua_chave_secreta_super_forte"
TOKEN_EXPIRY = 3600  # 1 hora
```

### **2. HTTPS Obrigatório**
```python
# Certificado SSL
SSL_CERT = "certificado.pem"
SSL_KEY = "chave_privada.pem"
```

### **3. Rate Limiting**
```python
# Limitar requisições
RATE_LIMIT = "100/hour"
MAX_CONNECTIONS = 10
```

## 📱 Acesso Mobile

### **PWA (Progressive Web App)**
```javascript
// Manifest para instalação no celular
{
  "name": "Monitor Solar",
  "short_name": "Solar",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#000000"
}
```

### **Notificações Push**
```python
# Alertas via push notification
PUSH_NOTIFICATIONS = {
    "service": "Firebase",
    "topics": ["solar_alerts", "system_status"]
}
```

## 🌐 URLs de Acesso

Após configuração:
- **Dashboard**: `https://seu-dominio.com`
- **API**: `https://seu-dominio.com/api`
- **Mobile**: `https://seu-dominio.com` (PWA)

## 📊 Monitoramento Global

### **Métricas Disponíveis**
- Produção de energia em tempo real
- Histórico de produção
- Eficiência do sistema
- Alertas e notificações
- Relatórios personalizados

### **Alertas Automáticos**
- Email quando produção baixa
- SMS para falhas críticas
- Push notifications no mobile
- Webhook para integrações

## 🚀 Próximos Passos

1. **Escolher opção de deploy** (Heroku/Railway/AWS)
2. **Configurar coletor local** no local do equipamento
3. **Deploy da API na nuvem**
4. **Configurar domínio e SSL**
5. **Testar acesso remoto**
6. **Configurar alertas**

## 💡 Recomendação Final

**Para começar rapidamente:**
1. Use **Railway** para deploy (mais simples)
2. Configure **ngrok** para teste inicial
3. Implemente **coletor local** que envia dados para nuvem
4. Configure **domínio próprio** para acesso profissional

Quer que eu implemente alguma dessas soluções específicas?
