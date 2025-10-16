"""
Sistema de Monitoramento Solar - Versão com Dashboard Bonito
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
    description="Monitoramento de placas solares - Dashboard Profissional",
    version="1.0.0"
)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Dashboard principal - Interface bonita"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sistema de Monitoramento Solar</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            .gradient-bg {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .solar-panel {
                background: linear-gradient(45deg, #1e3c72 0%, #2a5298 100%);
            }
            .status-online {
                background-color: #10b981;
                box-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
            }
            .status-offline {
                background-color: #ef4444;
                box-shadow: 0 0 20px rgba(239, 68, 68, 0.5);
            }
            .card-hover {
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .card-hover:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            }
        </style>
    </head>
    <body class="bg-gray-100">
        <!-- Header -->
        <header class="gradient-bg text-white shadow-lg">
            <div class="container mx-auto px-4 py-6">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                        <i class="fas fa-solar-panel text-4xl"></i>
                        <div>
                            <h1 class="text-3xl font-bold">Monitoramento Solar</h1>
                            <p class="text-blue-200">Sistema Completo de Monitoramento</p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-6">
                        <a href="/config" class="bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg transition-all">
                            <i class="fas fa-cogs mr-2"></i>Configuração
                        </a>
                        <div class="text-right">
                            <div id="current-time" class="text-lg font-semibold">11:30</div>
                            <div class="text-blue-200 text-sm">Última atualização: <span id="last-update">--</span></div>
                        </div>
                        <div class="flex items-center space-x-2">
                            <div id="connection-status" class="w-3 h-3 rounded-full status-online"></div>
                            <span class="text-sm">Sistema</span>
                        </div>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="container mx-auto px-4 py-8">
            <!-- Status Cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <!-- Produção Atual -->
                <div class="bg-white rounded-lg shadow-lg p-6 card-hover">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-600 text-sm font-medium">Produção Atual</p>
                            <p class="text-3xl font-bold text-green-600" id="current-power">2.4 kW</p>
                            <p class="text-gray-500 text-sm" id="current-efficiency">89% eficiência</p>
                        </div>
                        <div class="solar-panel text-white p-3 rounded-lg">
                            <i class="fas fa-bolt text-2xl"></i>
                        </div>
                    </div>
                </div>

                <!-- Energia Diária -->
                <div class="bg-white rounded-lg shadow-lg p-6 card-hover">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-600 text-sm font-medium">Energia Diária</p>
                            <p class="text-3xl font-bold text-blue-600" id="daily-energy">18.7 kWh</p>
                            <p class="text-gray-500 text-sm" id="energy-trend">+12% vs ontem</p>
                        </div>
                        <div class="bg-blue-500 text-white p-3 rounded-lg">
                            <i class="fas fa-chart-line text-2xl"></i>
                        </div>
                    </div>
                </div>

                <!-- Temperatura -->
                <div class="bg-white rounded-lg shadow-lg p-6 card-hover">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-600 text-sm font-medium">Temperatura</p>
                            <p class="text-3xl font-bold text-orange-600" id="temperature">45°C</p>
                            <p class="text-gray-500 text-sm" id="temp-status">Normal</p>
                        </div>
                        <div class="bg-orange-500 text-white p-3 rounded-lg">
                            <i class="fas fa-thermometer-half text-2xl"></i>
                        </div>
                    </div>
                </div>

                <!-- Status Sistema -->
                <div class="bg-white rounded-lg shadow-lg p-6 card-hover">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-600 text-sm font-medium">Status Sistema</p>
                            <p class="text-lg font-bold text-green-600" id="system-status">Online</p>
                            <p class="text-gray-500 text-sm" id="uptime">24h operando</p>
                        </div>
                        <div class="bg-green-500 text-white p-3 rounded-lg">
                            <i class="fas fa-server text-2xl"></i>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts Section -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                <!-- Gráfico de Produção -->
                <div class="bg-white rounded-lg shadow-lg p-6">
                    <h3 class="text-xl font-semibold text-gray-800 mb-4">
                        <i class="fas fa-chart-area text-blue-500 mr-2"></i>
                        Produção de Energia (24h)
                    </h3>
                    <div class="relative" style="height: 300px;">
                        <canvas id="powerChart"></canvas>
                    </div>
                </div>

                <!-- Gráfico de Eficiência -->
                <div class="bg-white rounded-lg shadow-lg p-6">
                    <h3 class="text-xl font-semibold text-gray-800 mb-4">
                        <i class="fas fa-percentage text-green-500 mr-2"></i>
                        Eficiência do Sistema (7 dias)
                    </h3>
                    <div class="relative" style="height: 300px;">
                        <canvas id="efficiencyChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Detailed Information -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <!-- Informações do Inversor -->
                <div class="bg-white rounded-lg shadow-lg p-6">
                    <h3 class="text-xl font-semibold text-gray-800 mb-4">
                        <i class="fas fa-microchip text-purple-500 mr-2"></i>
                        Inversor
                    </h3>
                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span class="text-gray-600">Modelo:</span>
                            <span class="font-medium" id="inverter-model">String Single Inverter</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Potência Nominal:</span>
                            <span class="font-medium" id="rated-power">3 kW</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Status:</span>
                            <span class="font-medium text-green-600" id="inverter-status">Online</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Tempo de Funcionamento:</span>
                            <span class="font-medium" id="uptime-hours">24h</span>
                        </div>
                    </div>
                </div>

                <!-- Informações do Logger -->
                <div class="bg-white rounded-lg shadow-lg p-6">
                    <h3 class="text-xl font-semibold text-gray-800 mb-4">
                        <i class="fas fa-wifi text-blue-500 mr-2"></i>
                        Logger
                    </h3>
                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span class="text-gray-600">Modelo:</span>
                            <span class="font-medium" id="logger-model">LSW3_15_FFFF</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Firmware:</span>
                            <span class="font-medium" id="logger-firmware">1.0.9E</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Sinal Wi-Fi:</span>
                            <span class="font-medium" id="signal-strength">90%</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Status:</span>
                            <span class="font-medium text-green-600" id="logger-status">Conectado</span>
                        </div>
                    </div>
                </div>

                <!-- Alertas -->
                <div class="bg-white rounded-lg shadow-lg p-6">
                    <h3 class="text-xl font-semibold text-gray-800 mb-4">
                        <i class="fas fa-exclamation-triangle text-yellow-500 mr-2"></i>
                        Alertas
                    </h3>
                    <div id="alerts-container" class="space-y-2">
                        <div class="text-gray-500 text-center py-4">
                            <i class="fas fa-check-circle text-green-500 text-2xl mb-2"></i>
                            <p>Nenhum alerta ativo</p>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <!-- Footer -->
        <footer class="bg-gray-800 text-white py-8 mt-12">
            <div class="container mx-auto px-4 text-center">
                <p>&copy; 2024 Sistema de Monitoramento Solar. Todos os direitos reservados.</p>
                <p class="text-gray-400 text-sm mt-2">Versão 1.0.0 | Última atualização: <span id="system-version">Agora</span></p>
            </div>
        </footer>

        <script>
            // Variáveis globais
            let powerChart = null;
            let efficiencyChart = null;

            // Função para atualizar a hora atual
            function updateCurrentTime() {
                const now = new Date();
                const timeString = now.toLocaleTimeString('pt-BR');
                document.getElementById('current-time').textContent = timeString;
            }

            // Função para fazer requisições à API
            async function apiRequest(endpoint) {
                try {
                    const response = await fetch(`/api/v1${endpoint}`);
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return await response.json();
                } catch (error) {
                    console.error('Erro na requisição:', error);
                    return null;
                }
            }

            // Função para atualizar dados do sistema
            async function updateSystemData() {
                try {
                    // Atualizar dados do inversor
                    const inverterStatus = await apiRequest('/inverters/1/status');
                    if (inverterStatus) {
                        updateInverterData(inverterStatus);
                    }

                    // Atualizar medições atuais
                    const currentData = await apiRequest('/data/current');
                    if (currentData) {
                        updateCurrentMeasurement(currentData);
                    }

                    // Atualizar alertas
                    const alerts = await apiRequest('/alerts/active');
                    if (alerts) {
                        updateAlerts(alerts);
                    }

                    // Atualizar timestamp da última atualização
                    document.getElementById('last-update').textContent = new Date().toLocaleTimeString('pt-BR');

                } catch (error) {
                    console.error('Erro ao atualizar dados:', error);
                    updateConnectionStatus(false);
                }
            }

            // Função para atualizar status de conexão
            function updateConnectionStatus(isOnline) {
                const statusElement = document.getElementById('connection-status');
                const systemStatusElement = document.getElementById('system-status');
                
                if (isOnline) {
                    statusElement.className = 'w-3 h-3 rounded-full status-online';
                    systemStatusElement.textContent = 'Online';
                    systemStatusElement.className = 'text-lg font-bold text-green-600';
                } else {
                    statusElement.className = 'w-3 h-3 rounded-full status-offline';
                    systemStatusElement.textContent = 'Offline';
                    systemStatusElement.className = 'text-lg font-bold text-red-600';
                }
            }

            // Função para atualizar dados do inversor
            function updateInverterData(data) {
                document.getElementById('current-power').textContent = `${data.current_power || 2.4} kW`;
                document.getElementById('current-efficiency').textContent = `${data.efficiency || 89}% eficiência`;
                document.getElementById('temperature').textContent = `${data.temperature || 45}°C`;
                document.getElementById('inverter-status').textContent = data.is_online ? 'Online' : 'Offline';
                document.getElementById('uptime-hours').textContent = `${data.uptime || 24}h`;
                
                // Atualizar status da temperatura
                const tempStatus = document.getElementById('temp-status');
                if (data.temperature > 70) {
                    tempStatus.textContent = 'Alta';
                    tempStatus.className = 'text-red-600 text-sm font-medium';
                } else {
                    tempStatus.textContent = 'Normal';
                    tempStatus.className = 'text-gray-500 text-sm';
                }
            }

            // Função para atualizar medição atual
            function updateCurrentMeasurement(data) {
                document.getElementById('daily-energy').textContent = `${data.energy_daily || 18.7} kWh`;
            }

            // Função para atualizar alertas
            function updateAlerts(alerts) {
                const container = document.getElementById('alerts-container');
                
                if (alerts.length === 0) {
                    container.innerHTML = `
                        <div class="text-gray-500 text-center py-4">
                            <i class="fas fa-check-circle text-green-500 text-2xl mb-2"></i>
                            <p>Nenhum alerta ativo</p>
                        </div>
                    `;
                    return;
                }

                let alertsHTML = '';
                alerts.forEach(alert => {
                    const severityColors = {
                        'critical': 'bg-red-100 border-red-500 text-red-700',
                        'high': 'bg-orange-100 border-orange-500 text-orange-700',
                        'medium': 'bg-yellow-100 border-yellow-500 text-yellow-700',
                        'low': 'bg-blue-100 border-blue-500 text-blue-700'
                    };

                    const icon = {
                        'critical': 'fas fa-exclamation-circle',
                        'high': 'fas fa-exclamation-triangle',
                        'medium': 'fas fa-info-circle',
                        'low': 'fas fa-info'
                    };

                    alertsHTML += `
                        <div class="border-l-4 ${severityColors[alert.severity]} p-3 rounded">
                            <div class="flex items-center">
                                <i class="${icon[alert.severity]} mr-2"></i>
                                <div class="flex-1">
                                    <p class="font-medium">${alert.message}</p>
                                    <p class="text-xs opacity-75">${new Date(alert.timestamp).toLocaleString('pt-BR')}</p>
                                </div>
                            </div>
                        </div>
                    `;
                });

                container.innerHTML = alertsHTML;
            }

            // Inicializar gráficos
            function initializeCharts() {
                // Gráfico de Produção
                const powerCtx = document.getElementById('powerChart').getContext('2d');
                powerChart = new Chart(powerCtx, {
                    type: 'line',
                    data: {
                        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
                        datasets: [{
                            label: 'Potência (kW)',
                            data: [0, 0, 1.2, 2.8, 2.4, 1.8, 0],
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        aspectRatio: 2,
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Potência (kW)'
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: 'Horário'
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });

                // Gráfico de Eficiência
                const efficiencyCtx = document.getElementById('efficiencyChart').getContext('2d');
                efficiencyChart = new Chart(efficiencyCtx, {
                    type: 'bar',
                    data: {
                        labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
                        datasets: [{
                            label: 'Eficiência (%)',
                            data: [85, 87, 83, 89, 91, 88, 86],
                            backgroundColor: '#10b981',
                            borderColor: '#059669',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        aspectRatio: 2,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100,
                                title: {
                                    display: true,
                                    text: 'Eficiência (%)'
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: 'Dias da Semana'
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
            }

            // Inicializar aplicação
            function initializeApp() {
                updateCurrentTime();
                initializeCharts();
                updateSystemData();
                updateConnectionStatus(true);

                // Atualizar hora a cada segundo
                setInterval(updateCurrentTime, 1000);

                // Atualizar dados a cada 30 segundos
                setInterval(updateSystemData, 30000);

                console.log('Sistema de Monitoramento Solar inicializado');
            }

            // Inicializar quando a página carregar
            document.addEventListener('DOMContentLoaded', initializeApp);
        </script>
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
            .card-hover { transition: transform 0.3s ease, box-shadow 0.3s ease; }
            .card-hover:hover { transform: translateY(-2px); box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1); }
            .status-online { background-color: #10b981; }
            .status-offline { background-color: #ef4444; }
            .status-testing { background-color: #f59e0b; }
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

@app.get("/api/v1/inverters/1/status")
async def inverter_status():
    """Status do inversor (dados simulados)"""
    return {
        "inverter_id": 1,
        "serial_number": "2106027230",
        "is_online": True,
        "last_update": datetime.now().isoformat(),
        "current_power": 2.4,
        "daily_energy": 18.7,
        "temperature": 45.2,
        "efficiency": 89.5,
        "status_code": 1,
        "fault_code": 0,
        "uptime": 24
    }

@app.get("/api/v1/data/current")
async def current_data():
    """Dados atuais (simulados)"""
    return {
        "timestamp": datetime.now().isoformat(),
        "power_output": 2.4,
        "energy_daily": 18.7,
        "voltage_dc": 385.2,
        "current_dc": 6.36,
        "voltage_ac": 220.1,
        "current_ac": 11.13,
        "frequency": 60.0,
        "temperature": 45.2,
        "efficiency": 89.5,
        "status_code": 1,
        "fault_code": 0
    }

@app.get("/api/v1/alerts/active")
async def active_alerts():
    """Alertas ativos (simulados)"""
    return []

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
    print("Iniciando Sistema de Monitoramento Solar - Dashboard Bonito")
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
