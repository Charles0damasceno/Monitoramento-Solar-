"""
Sistema de Monitoramento Solar - Versão Corrigida
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
import os
import json
from datetime import datetime

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema de Monitoramento Solar",
    description="Monitoramento de placas solares",
    version="1.0.0"
)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página inicial"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Monitoramento Solar</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; color: #2c3e50; margin-bottom: 30px; }
            .status { background: #27ae60; color: white; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .info { background: #3498db; color: white; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .warning { background: #f39c12; color: white; padding: 20px; border-radius: 5px; margin: 20px 0; }
            a { color: white; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .btn { display: inline-block; background: #e74c3c; color: white; padding: 10px 20px; border-radius: 5px; margin: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔋 Sistema de Monitoramento Solar</h1>
                <p>Versão 1.0.0 - Sistema em Execução</p>
            </div>
            
            <div class="status">
                <h3>✅ Sistema Online</h3>
                <p>O sistema de monitoramento está funcionando corretamente!</p>
            </div>
            
            <div class="info">
                <h3>📊 Funcionalidades Disponíveis</h3>
                <ul>
                    <li><strong>API REST:</strong> <a href="/docs">/docs</a> - Documentação completa</li>
                    <li><strong>Status do Sistema:</strong> <a href="/health">/health</a> - Verificação de saúde</li>
                    <li><strong>Configuração:</strong> <a href="/config">/config</a> - Configurar equipamentos</li>
                    <li><strong>Dados do Inversor:</strong> <a href="/api/v1/inverters/1/status">/api/v1/inverters/1/status</a></li>
                    <li><strong>Alertas:</strong> <a href="/api/v1/alerts/active">/api/v1/alerts/active</a></li>
                </ul>
            </div>
            
            <div class="warning">
                <h3>⚠️ Configuração Necessária</h3>
                <p>Para conectar com seus equipamentos reais:</p>
                <ol>
                    <li>Acesse a página de <a href="/config">Configuração</a></li>
                    <li>Configure os IPs dos seus equipamentos</li>
                    <li>Teste as conexões</li>
                    <li>Salve as configurações</li>
                </ol>
            </div>
            
            <div class="info">
                <h3>🎯 Seus Equipamentos</h3>
                <p><strong>Inversor:</strong> String Single Inverter 3kW (SN: 2106027230)</p>
                <p><strong>Logger:</strong> LSW3_15_FFFF (SN: 1782433145)</p>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/config" class="btn">⚙️ Configurar Equipamentos</a>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/config", response_class=HTMLResponse)
async def config_page():
    """Página de configuração"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Configuração - Sistema de Monitoramento Solar</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        </style>
    </head>
    <body class="bg-gray-100">
        <header class="gradient-bg text-white shadow-lg">
            <div class="container mx-auto px-4 py-6">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                        <i class="fas fa-cogs text-4xl"></i>
                        <div>
                            <h1 class="text-3xl font-bold">Configuração do Sistema</h1>
                            <p class="text-blue-200">Configure os equipamentos de monitoramento solar</p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-4">
                        <a href="/" class="bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg transition-all">
                            <i class="fas fa-home mr-2"></i>Dashboard
                        </a>
                    </div>
                </div>
            </div>
        </header>
        
        <main class="container mx-auto px-4 py-8">
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h2 class="text-2xl font-bold text-gray-800 mb-6">
                    <i class="fas fa-network-wired text-green-500 mr-2"></i>
                    Configuração de Rede
                </h2>
                
                <form id="config-form" class="space-y-6">
                    <div class="border border-gray-200 rounded-lg p-6">
                        <h3 class="text-lg font-semibold text-gray-800 mb-4">
                            <i class="fas fa-microchip text-purple-500 mr-2"></i>
                            Inversor (SN: 2106027230)
                        </h3>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Endereço IP</label>
                                <input type="text" id="inverter-host" value="192.168.1.100" 
                                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Porta Modbus</label>
                                <input type="number" id="inverter-port" value="502" 
                                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Unit ID</label>
                                <input type="number" id="inverter-address" value="1" 
                                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500">
                            </div>
                        </div>
                    </div>
                    
                    <div class="border border-gray-200 rounded-lg p-6">
                        <h3 class="text-lg font-semibold text-gray-800 mb-4">
                            <i class="fas fa-wifi text-blue-500 mr-2"></i>
                            Logger (SN: 1782433145)
                        </h3>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Endereço IP</label>
                                <input type="text" id="logger-host" value="192.168.1.101" 
                                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Porta Modbus</label>
                                <input type="number" id="logger-port" value="502" 
                                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Unit ID</label>
                                <input type="number" id="logger-address" value="2" 
                                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                            </div>
                        </div>
                    </div>
                    
                    <div class="flex gap-4">
                        <button type="submit" class="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-md font-semibold transition-colors">
                            <i class="fas fa-save mr-2"></i>Salvar Configurações
                        </button>
                        <button type="button" onclick="testConnection('inverter')" class="bg-purple-500 hover:bg-purple-600 text-white px-6 py-3 rounded-md font-semibold transition-colors">
                            <i class="fas fa-plug mr-2"></i>Testar Inversor
                        </button>
                        <button type="button" onclick="testConnection('logger')" class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-md font-semibold transition-colors">
                            <i class="fas fa-plug mr-2"></i>Testar Logger
                        </button>
                    </div>
                </form>
                
                <div id="test-results" class="mt-6 hidden">
                    <div class="bg-white rounded-lg shadow-lg p-6">
                        <h3 class="text-lg font-semibold text-gray-800 mb-4">
                            <i class="fas fa-clipboard-check text-blue-500 mr-2"></i>
                            Resultados dos Testes
                        </h3>
                        <div id="test-results-content"></div>
                    </div>
                </div>
            </div>
        </main>
        
        <script>
            document.getElementById('config-form').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const config = {
                    inverter_host: document.getElementById('inverter-host').value,
                    inverter_port: parseInt(document.getElementById('inverter-port').value),
                    inverter_address: parseInt(document.getElementById('inverter-address').value),
                    logger_host: document.getElementById('logger-host').value,
                    logger_port: parseInt(document.getElementById('logger-port').value),
                    logger_address: parseInt(document.getElementById('logger-address').value)
                };
                
                try {
                    const response = await fetch('/api/v1/config', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(config)
                    });
                    
                    if (response.ok) {
                        showNotification('Configurações salvas com sucesso!', 'success');
                    } else {
                        throw new Error('Erro ao salvar configurações');
                    }
                } catch (error) {
                    showNotification('Erro ao salvar configurações', 'error');
                }
            });
            
            async function testConnection(equipment) {
                const host = document.getElementById(`${equipment}-host`).value;
                const port = parseInt(document.getElementById(`${equipment}-port`).value);
                
                showNotification(`Testando conexão com ${equipment}...`, 'info');
                
                try {
                    const response = await fetch('/api/v1/test-connection', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ equipment, host, port })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        showNotification(`${equipment} conectado com sucesso!`, 'success');
                    } else {
                        showNotification(`Erro ao conectar com ${equipment}: ${result.message}`, 'error');
                    }
                } catch (error) {
                    showNotification(`Erro ao testar ${equipment}`, 'error');
                }
            }
            
            function showNotification(message, type = 'info') {
                const notification = document.createElement('div');
                notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
                    type === 'success' ? 'bg-green-500 text-white' :
                    type === 'error' ? 'bg-red-500 text-white' :
                    type === 'warning' ? 'bg-yellow-500 text-white' :
                    'bg-blue-500 text-white'
                }`;
                
                notification.innerHTML = `<span>${message}</span>`;
                document.body.appendChild(notification);
                
                setTimeout(() => notification.remove(), 5000);
            }
        </script>
    </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """Verificação de saúde do sistema"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "api": True,
            "database": False,
            "modbus": False
        },
        "message": "Sistema funcionando - Configure os IPs dos equipamentos"
    }

@app.get("/api/v1/config")
async def get_config():
    """Obter configurações atuais"""
    try:
        config = {}
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value
        
        return {
            "modbus": {
                "inverter_host": config.get("INVERTER_HOST", "192.168.1.100"),
                "inverter_port": int(config.get("INVERTER_PORT", "502")),
                "inverter_address": int(config.get("INVERTER_ADDRESS", "1")),
                "logger_host": config.get("LOGGER_HOST", "192.168.1.101"),
                "logger_port": int(config.get("LOGGER_PORT", "502")),
                "logger_address": int(config.get("LOGGER_ADDRESS", "2"))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler configurações: {str(e)}")

@app.post("/api/v1/config")
async def save_config(config_data: dict):
    """Salvar configurações"""
    try:
        current_config = {}
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        current_config[key] = value
        
        current_config.update({
            "INVERTER_HOST": config_data.get("inverter_host", "192.168.1.100"),
            "INVERTER_PORT": str(config_data.get("inverter_port", 502)),
            "INVERTER_ADDRESS": str(config_data.get("inverter_address", 1)),
            "LOGGER_HOST": config_data.get("logger_host", "192.168.1.101"),
            "LOGGER_PORT": str(config_data.get("logger_port", 502)),
            "LOGGER_ADDRESS": str(config_data.get("logger_address", 2))
        })
        
        with open('.env', 'w') as f:
            f.write("# Configurações do Sistema de Monitoramento Solar\n")
            f.write("# Gerado automaticamente pela interface web\n\n")
            for key, value in current_config.items():
                f.write(f"{key}={value}\n")
        
        return {"message": "Configurações salvas com sucesso!", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar configurações: {str(e)}")

@app.post("/api/v1/test-connection")
async def test_connection(connection_data: dict):
    """Testar conexão com equipamento"""
    try:
        import socket
        
        host = connection_data.get("host")
        port = connection_data.get("port")
        equipment = connection_data.get("equipment")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return {
                "success": True,
                "message": f"Conexão com {equipment} estabelecida com sucesso!",
                "host": host,
                "port": port
            }
        else:
            return {
                "success": False,
                "message": f"Não foi possível conectar com {equipment} em {host}:{port}",
                "host": host,
                "port": port
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao testar conexão: {str(e)}"
        }

if __name__ == "__main__":
    print("Iniciando Sistema de Monitoramento Solar - Versão Corrigida")
    print("=" * 60)
    print("Dashboard: http://localhost:8000")
    print("Configuração: http://localhost:8000/config")
    print("API Docs: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
