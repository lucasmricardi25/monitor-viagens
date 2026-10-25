import os
import requests
from datetime import datetime, timedelta

# Credenciais obtidas via GitHub Secrets
API_KEY_SERPAPI = os.getenv("SERPAPI_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Os 4 destinos escolhidos (Cabo Verde, Canárias, Açores)
DESTINOS = [
    {"nome": "Boa Vista (Cabo Verde)", "codigo": "BVB"},
    {"nome": "Sal (Cabo Verde)", "codigo": "SID"},
    {"nome": "Tenerife (Canárias)", "codigo": "TFS"},
    {"nome": "Ponta Delgada (Açores)", "codigo": "PDL"}
]

ORIGEM = "OPO"  # Porto
PRECO_TETO = 1000  # Teto alto para teste

# Janela de datas flexíveis (Final de novembro / Início de dezembro)
DATA_INICIO_BUSCA = datetime(2026, 11, 25)
DATA_FIM_BUSCA = datetime(2026, 12, 3)
DURACAO_VIAGEM = 4  # Duração de estadia em dias

def enviar_telegram(texto):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Erro: Token ou Chat ID do Telegram em falta nas Secrets!")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, data=payload, timeout=10)
        print(f"Status Telegram: {res.status_code} | Resposta: {res.text}")
    except Exception as e:
        print(f"Erro ao comunicar com o Telegram: {e}")

def verificar_voos():
    if not API_KEY_SERPAPI:
        print("Erro: Chave da SerpApi em falta nas Secrets!")
        return

    for destino in DESTINOS:
        data_atual = DATA_INICIO_BUSCA
        
        while data_atual <= DATA_FIM_BUSCA:
            data_ida = data_atual.strftime("%Y-%m-%d")
            data_volta = (data_atual + timedelta(days=DURACAO_VIAGEM)).strftime("%Y-%m-%d")
            
            url = (f"https://serpapi.com/search.json?engine=google_flights"
                   f"&departure_id={ORIGEM}&arrival_id={destino['codigo']}"
                   f"&outbound_date={data_ida}&return_date={data_volta}"
                   f"&currency=EUR&api_key={API_KEY_SERPAPI}")
            
            try:
                response = requests.get(url, timeout=10).json()
                best_flights = response.get("best_flights", [])
                
                if best_flights:
                    preco = best_flights[0]["price"]
                    if preco <= PRECO_TETO:
                        msg = (f"🚨 **ALERTA DE VOO BARATO!** 🚨\n\n"
                               f"✈️ **Destino:** {destino['nome']}\n"
                               f"💶 **Preço:** €{preco} (Ida e Volta)\n"
                               f"📅 **Datas:** {data_ida} a {data_volta}")
                        enviar_telegram(msg)
            except Exception as e:
                print(f"Erro ao consultar {destino['nome']} para {data_ida}: {e}")
            
            data_atual += timedelta(days=1)

if __name__ == "__main__":
    print("🤖 A iniciar o script de monitorização de voos...")
    # Mensagem de teste forçada para garantir que o Telegram responde
    enviar_telegram("🚀 **Teste direto:** O bot de voos do Porto foi acionado com sucesso!")
    verificar_voos()
