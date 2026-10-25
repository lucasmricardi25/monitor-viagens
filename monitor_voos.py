import os
import requests
from datetime import datetime, timedelta

# Credenciais obtidas via variáveis de ambiente do GitHub Secrets
API_KEY_SERPAPI = os.getenv("SERPAPI_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 1. Os 4 destinos escolhidos (Cabo Verde, Canárias, Açores)
DESTINOS = [
    {"nome": "Boa Vista (Cabo Verde)", "codigo": "BVB"},
    {"nome": "Sal (Cabo Verde)", "codigo": "SID"},
    {"nome": "Tenerife (Canárias)", "codigo": "TFS"},
    {"nome": "Ponta Delgada (Açores)", "codigo": "PDL"}
]

ORIGEM = "OPO"  # Porto
PRECO_TETO = 1000  # Alerta dispara se o valor de ida e volta for <= a 160 EUR

# Janela de datas flexíveis (Final de novembro / Início de dezembro)
DATA_INICIO_BUSCA = datetime(2026, 11, 30)
DATA_FIM_BUSCA = datetime(2026, 12, 10)
DURACAO_VIAGEM = 6  # Duração de estadia em dias

def verificar_voos():
    if not API_KEY_SERPAPI or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Erro: As chaves de acesso (Secrets) não estão configuradas corretamente.")
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
                response = requests.get(url).json()
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
                print(f"Erro ao consultar {destino['nome']}: {e}")
            
            data_atual += timedelta(days=1)

def enviar_telegram(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

if __name__ == "__main__":
    verificar_voos()
