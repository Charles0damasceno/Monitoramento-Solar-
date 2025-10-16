"""
Script de instalação do Sistema de Monitoramento Solar
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Executar comando e mostrar progresso"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} concluído")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro em {description}: {e}")
        print(f"Saída de erro: {e.stderr}")
        return False

def create_directories():
    """Criar diretórios necessários"""
    directories = [
        "logs",
        "data", 
        "backups",
        "frontend/dist"
    ]
    
    print("📁 Criando diretórios...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}")
    print("✅ Diretórios criados")

def install_dependencies():
    """Instalar dependências Python"""
    if not run_command("pip install -r requirements.txt", "Instalando dependências Python"):
        print("❌ Falha ao instalar dependências Python")
        return False
    return True

def setup_environment():
    """Configurar arquivo de ambiente"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        print("⚙️ Configurando arquivo de ambiente...")
        shutil.copy(env_example, env_file)
        print("✅ Arquivo .env criado (configure as variáveis conforme necessário)")
    elif env_file.exists():
        print("✅ Arquivo .env já existe")
    else:
        print("⚠️ Arquivo env.example não encontrado")

def initialize_database():
    """Inicializar banco de dados"""
    print("🗄️ Inicializando banco de dados...")
    try:
        # Importar e executar inicialização do banco
        sys.path.append(os.getcwd())
        from backend.database import init_db
        import asyncio
        
        asyncio.run(init_db())
        print("✅ Banco de dados inicializado")
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        return False

def test_installation():
    """Testar instalação"""
    print("🧪 Testando instalação...")
    try:
        # Testar importação dos módulos principais
        sys.path.append(os.getcwd())
        from backend.main import app
        from backend.config import settings
        from backend.models import Base
        print("✅ Módulos importados com sucesso")
        
        # Testar configurações
        print(f"✅ Configurações carregadas: {settings.APP_NAME}")
        
        return True
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def show_next_steps():
    """Mostrar próximos passos"""
    print("\n" + "="*60)
    print("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print("\n📋 PRÓXIMOS PASSOS:")
    print("\n1. Configure o arquivo .env com suas configurações:")
    print("   - IP do inversor e logger")
    print("   - Configurações de alerta")
    print("   - Configurações de banco de dados")
    
    print("\n2. Inicie o sistema:")
    print("   python main.py")
    
    print("\n3. Acesse o dashboard:")
    print("   http://localhost:8000")
    
    print("\n4. Documentação da API:")
    print("   http://localhost:8000/docs")
    
    print("\n🔧 CONFIGURAÇÃO DOS EQUIPAMENTOS:")
    print("\nBaseado nas imagens fornecidas, configure:")
    print("- Inversor (SN: 2106027230): String Single Inverter 3kW")
    print("- Logger (SN: 1782433145): LSW3_15_FFFF")
    
    print("\n📡 CONECTIVIDADE:")
    print("Certifique-se de que os equipamentos estão na mesma rede")
    print("e configure os IPs no arquivo .env")
    
    print("\n📞 SUPORTE:")
    print("Para suporte técnico, consulte:")
    print("- Logs: logs/solar_monitoring.log")
    print("- Status: http://localhost:8000/health")
    print("- API Docs: http://localhost:8000/docs")

def main():
    """Função principal de instalação"""
    print("🚀 INSTALADOR DO SISTEMA DE MONITORAMENTO SOLAR")
    print("="*60)
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 ou superior é necessário")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detectado")
    
    # Verificar pip
    try:
        import pip
        print("✅ pip disponível")
    except ImportError:
        print("❌ pip não encontrado")
        sys.exit(1)
    
    # Executar instalação
    steps = [
        ("Criar diretórios", create_directories),
        ("Instalar dependências", install_dependencies),
        ("Configurar ambiente", setup_environment),
        ("Inicializar banco de dados", initialize_database),
        ("Testar instalação", test_installation)
    ]
    
    for step_name, step_function in steps:
        print(f"\n📋 {step_name}...")
        if not step_function():
            print(f"❌ Falha em: {step_name}")
            sys.exit(1)
    
    # Mostrar próximos passos
    show_next_steps()

if __name__ == "__main__":
    main()
