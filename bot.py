import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from telegram import Bot

# === CONFIG ===
with open("config.json") as f:
    config = json.load(f)

TOKEN = config["7999272722:AAF_col3ZYUYvzZmQIwBAVbrRBbemu0ifs0"]
CHAT_ID = config["-1002874548550"]
TEMPO_ANALISE = config["10s"]
bot = Bot(token=TOKEN)

# === SETUP SELENIUM HEADLESS ===
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)

# === ABRE O SITE ===
driver.get(
    "https://www.elephantbet.co.ao/en/live-casino/home?openGames=217033-real&gameNames=Lightning%20Roulette"
)
time.sleep(15)  # espera carregar

ultimos_resultados = []


def extrair_resultados():
    global ultimos_resultados
    try:
        elementos = driver.find_elements(
            By.CLASS_NAME, "roulette-recent-numbers__item"
        )
        numeros = [int(e.text.strip()) for e in elementos if e.text.strip().isdigit()]
        if numeros and numeros != ultimos_resultados:
            ultimos_resultados = numeros
            return numeros[:3]
    except Exception as e:
        print("Erro ao extrair:", e)
    return None


def detectar_estrategias(numeros):
    n1, n2, n3 = numeros
    sinais = []
    u1, u2 = int(str(n1)[-1]), int(str(n2)[-1])

    # 1. Espelhados
    if (str(n1)[::-1] == str(n2)) or (str(n2)[::-1] == str(n3)):
        sinais.append("🔁 Estratégia dos NÚMEROS ESPELHADOS")

    # 2. Soma/Subtração
    soma = u1 + u2
    sub = abs(u1 - u2)
    if int(str(n3)[-1]) in [soma % 10, sub % 10]:
        sinais.append("➕ Estratégia de SOMA/SUBTRAÇÃO")

    # 3. Vizinhos do ZERO
    vz = [1, 5, 8, 11, 14, 23, 26, 32]
    if n1 in vz and n2 in vz and n3 not in vz:
        sinais.append("🟩 Estratégia dos VIZINHOS DO ZERO")

    # 4. Escada (ordenado)
    terminais = [int(str(x)[-1]) for x in numeros]
    if terminais == sorted(terminais):
        sinais.append("📈 Estratégia da ESCADA")

    # 5. Escada inversa
    if abs(n1 - n2) == 2:
        sinais.append(f"📉 ESCADA INVERSA entre {n1} e {n2}")

    # 6. Repetição
    if n1 == n2 or n1 == n3 or n2 == n3:
        sinais.append("♻️ Estratégia de NÚMEROS REPETIDOS")

    # 7. Multiplicados (3,6,9)
    if all(int(str(n)[-1]) in [3, 6, 9] for n in numeros):
        sinais.append("✖️ Estratégia de NÚMEROS MULTIPLICADOS")

    # 8. Duplo de repetição
    if n1 == n3 and n1 != n2:
        sinais.append("📛 Estratégia de DUPLOS DE REPETIÇÃO")

    # 9. Terminal zero
    if all(str(n)[-1] == "0" for n in numeros):
        sinais.append("🟩 Estratégia de TERMINAL ZERO")

    return sinais


def enviar_sinais(sinais, numeros):
    for s in sinais:
        bot.send_message(
            chat_id=CHAT_ID,
            text=f"📡 SINAL DETECTADO\n🔢 Números: {numeros}\n{s}"
        )


def verificar_win_loss(terminal_esperado):
    time.sleep(60)
    novos = extrair_resultados()
    if novos:
        status = (
            "✅ WIN"
            if int(str(novos[0])[-1]) == terminal_esperado
            else "❌ FODEU"
        )
        bot.send_message(
            chat_id=CHAT_ID,
            text=f"🎯 Resultado: {novos[0]}\nStatus do sinal: {status}"
        )


# === EXECUÇÃO ===
bot.send_message(chat_id=CHAT_ID, text="🤖 Bot de sinais iniciado!")
while True:
    numeros = extrair_resultados()
    if numeros:
        sinais = detectar_estrategias(numeros)
        if sinais:
            enviar_sinais(sinais, numeros)
            term_esp = int(str(numeros[2])[-1])
            verificar_win_loss(term_esp)
    time.sleep(TEMPO_ANALISE)
