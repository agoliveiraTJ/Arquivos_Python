# Importando as bibliotecas necessárias
import pyautogui
import time

# Habilita o Failsafe: Mova o mouse para o canto superior esquerdo para parar o script
pyautogui.FAILSAFE = True

# Define uma pausa padrão de 1 segundo entre cada comando do pyautogui. Isso torna o script mais estável e fácil de acompanhar.
pyautogui.PAUSE = 1.0

# --- Início da Automação ---

try:
    print("Carregamento automático inicalizando...")
    time.sleep(1)

    # 1. Abrir o Google Chrome em uma página em branco (sem as páginas configuradas)
    pyautogui.hotkey('win', 'r')
    pyautogui.write('chrome --new-window about:blank')
    pyautogui.press('enter')
    time.sleep(3)

    # Digitar a primeira URL e navegar
    url_emerj = "https://www.emerj.com.br/sistemas"
    pyautogui.hotkey('ctrl', 'l')
    pyautogui.write(url_emerj, interval=0.05)
    pyautogui.press('enter')
    time.sleep(3)

    # Tente garantir o foco no campo usuário (ajuste se necessário)
    pyautogui.press('tab')
    time.sleep(0.5)
    pyautogui.write('agoliveira@tjrj.jus.br', interval=0.05)
    pyautogui.press('tab')
    pyautogui.write('13246', interval=0.05)  # senha corrigida
    pyautogui.press('enter')
    time.sleep(2)

    # Abrir nova aba e acessar o GitHub
    pyautogui.hotkey('ctrl', 't')  # Nova aba
    time.sleep(1)
    url_github = "https://github.com/"
    pyautogui.write(url_github, interval=0.05)
    pyautogui.press('enter')
    time.sleep(2)

    # Abrir nova aba e acessar o Webmail
    pyautogui.hotkey('ctrl', 't')  # Nova aba
    time.sleep(1)
    url_webmail = "https://outlook.office.com/mail/"
    pyautogui.write(url_webmail, interval=0.05)
    pyautogui.press('enter')
    time.sleep(2)

    # Abrir nova aba e acessar o ChatGPT
    pyautogui.hotkey('ctrl', 't')  # Nova aba
    time.sleep(1)
    url_chatGPT = "https://chatgpt.com/"
    pyautogui.write(url_chatGPT, interval=0.05)
    pyautogui.press('enter')
    time.sleep(2)

    # 2. Abrir o Teams
    pyautogui.hotkey('win', 's')
    pyautogui.write('Teams')
    pyautogui.press('enter')

    print("\nAutomação concluída com sucesso!")

except pyautogui.FailSafeException:
    print("\nAVISO: Automação interrompida pelo usuário (Failsafe ativado).")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
