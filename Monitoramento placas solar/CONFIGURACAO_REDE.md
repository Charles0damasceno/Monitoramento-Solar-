# Configuração de Rede - Sistema de Monitoramento Solar

## Situação Atual
- **IP do Logger**: `192.168.0.101`
- **Porta Modbus**: `502`
- **Problema**: Você não está na mesma rede que o equipamento

## Opções para Conectar ao Equipamento

### 1. **Conectar-se à Rede Local do Equipamento**
Para monitorar o equipamento, você precisa estar na mesma rede Wi-Fi que o logger.

**Passos:**
1. Conecte-se ao Wi-Fi "NetPlus-Charles" (conforme mostrado nas imagens)
2. Execute o teste de conectividade: `python test_simple.py`
3. Se conectar com sucesso, inicie o sistema: `python main.py`

### 2. **Configuração de Acesso Remoto (Avançado)**

Se você quiser monitorar remotamente, precisa configurar:

#### Opção A: Port Forwarding no Roteador
1. Acesse o roteador "NetPlus-Charles"
2. Configure port forwarding da porta 502 para o IP 192.168.0.101
3. Use o IP público do roteador para conectar

#### Opção B: VPN
1. Configure uma VPN no roteador
2. Conecte-se via VPN quando estiver fora da rede local

### 3. **Configuração do Sistema**

O sistema já está configurado com:
- **Logger IP**: `192.168.0.101`
- **Porta**: `502`
- **Protocolo**: Modbus TCP/IP

## Teste de Conectividade

Quando estiver na rede local, execute:

```bash
# Teste simples
python test_simple.py

# Teste completo (se disponível)
python test_connection.py
```

## Iniciando o Monitoramento

Após confirmar a conectividade:

```bash
# Iniciar o sistema
python main.py

# Ou usar o instalador automático
start.bat
```

## Dashboard Web

Após iniciar o sistema:
- **URL**: http://localhost:3000
- **API**: http://localhost:8000/docs

## Solução de Problemas

### Se não conseguir conectar:
1. **Verifique a rede**: Confirme que está conectado ao Wi-Fi "NetPlus-Charles"
2. **Teste o ping**: `ping 192.168.0.101`
3. **Verifique o firewall**: Porta 502 pode estar bloqueada
4. **Confirme o IP**: O logger pode ter mudado de IP

### Se o IP mudar:
1. Descubra o novo IP do logger
2. Atualize o arquivo `backend/config.py`
3. Reinicie o sistema

## Configuração Manual do IP

Se precisar alterar o IP, edite o arquivo `backend/config.py`:

```python
# Modbus - Logger
LOGGER_HOST: str = "192.168.0.101"  # Altere aqui
LOGGER_PORT: int = 502
LOGGER_ADDRESS: int = 2
```

## Próximos Passos

1. **Conecte-se à rede local** do equipamento
2. **Execute o teste** de conectividade
3. **Inicie o monitoramento** se a conexão for bem-sucedida
4. **Configure alertas** se necessário

## Suporte

Se tiver problemas:
- Verifique os logs em `logs/solar_monitoring.log`
- Execute o teste de diagnóstico
- Confirme as configurações de rede
