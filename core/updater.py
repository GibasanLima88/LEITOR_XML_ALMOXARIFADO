import requests
import os
import sys
import subprocess
import time
from tkinter import messagebox
import threading
from core.version import VERSION

# Configuração do GitHub
REPO_OWNER = "GibasanLima88"
REPO_NAME = "LEITOR_XML_ALMOXARIFADO"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"

# MODO DE TESTE LOCAL
# Se True, simula uma atualização usando arquivos locais.
TEST_MODE = False
TEST_VERSION = "9.9.9" # Versão simulada maior que a atual
TEST_FILE_PATH = "leitor_xml_versao_teste.exe" # Arquivo simulado para download

def verificar_atualizacao_silenciosa():
    """Roda em thread para não travar a GUI (Modo Silencioso)"""
    threading.Thread(target=_processo_verificacao, args=(True,), daemon=True).start()

def verificar_atualizacao_manual():
    """Roda em thread para não travar a GUI (Modo Manual - com feedback)"""
    # Para manual, rodamos na thread principal ou thread separada? 
    # Melhor thread separada para não congelar se a rede estiver lenta, 
    # mas o feedback visual deve ser na thread principal (messagebox é thread-safe no tkinter na maioria dos casos, mas cuidado).
    # Como messagebox bloqueia, melhor rodar a lógica de rede em thread e o messagebox no final.
    threading.Thread(target=_processo_verificacao, args=(False,), daemon=True).start()

def _processo_verificacao(silencioso=True):
    try:
        dados_release = obter_dados_ultima_versao()
        
        ultima_versao = dados_release["tag_name"].replace("v", "")
        
        if _comparar_versoes(ultima_versao, VERSION):
            # Nova versão encontrada
            resposta = messagebox.askyesno(
                "Nova Versão Disponível",
                f"A versão {ultima_versao} está disponível (Atual: {VERSION}).\n\nDeseja atualizar agora?"
            )
            if resposta:
                realizar_atualizacao(dados_release)
        else:
            # Se não tem atualização e NÃO é silencioso, avisa o usuário
            if not silencioso:
                messagebox.showinfo("Atualização", f"O sistema já está na versão mais recente ({VERSION}).")

    except Exception as e:
        if not silencioso:
             messagebox.showerror("Erro", f"Erro ao verificar atualizações: {e}")
        else:
            print(f"Erro ao verificar atualizações: {e}")

def obter_dados_ultima_versao():
    if TEST_MODE:
        # Simula resposta da API do GitHub
        return {
            "tag_name": TEST_VERSION,
            "assets": [
                {
                    "name": "LeitorXML_v3.exe",
                    "browser_download_url": "local_test" 
                }
            ]
        }
    else:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        return response.json()

def _comparar_versoes(v_nova, v_atual):
    """Retorna True se v_nova > v_atual (simples)"""
    # Comparação simples de strings ou tuplas
    # Ex: 1.0.1 > 1.0.0
    return v_nova > v_atual

def realizar_atualizacao(dados_release):
    try:
        nome_arquivo = "LeitorXML_novo.exe"
        url_download = dados_release["assets"][0]["browser_download_url"]
        
        if TEST_MODE:
            # Simula download copiando arquivo local
            caminho_origem_teste = TEST_FILE_PATH 
            if not os.path.exists(caminho_origem_teste):
                messagebox.showerror("Erro de Teste", f"Crie um arquivo '{caminho_origem_teste}' para testar.")
                return
            
            with open(caminho_origem_teste, "rb") as f_in:
                conteudo = f_in.read()
        else:
            # Realiza download real
            print("Baixando atualização...")
            r = requests.get(url_download, stream=True)
            r.raise_for_status()
            conteudo = r.content

        # Salva o novo executável
        with open(nome_arquivo, "wb") as f_out:
            f_out.write(conteudo)
            
        # Cria script BAT para substituir
        criar_bat_substituicao(nome_arquivo)
        
    except Exception as e:
        messagebox.showerror("Erro na Atualização", f"Falha ao baixar/instalar: {e}")

def criar_bat_substituicao(novo_exe):
    """
    Cria um .bat que:
    1. Espera o processo atual morrer.
    2. Deleta o executável atual.
    3. Renomeia o novo para o nome do atual.
    4. Inicia o novo executável.
    """
    exe_atual = sys.argv[0] # Caminho do executável atual
    if not exe_atual.lower().endswith(".exe"):
        messagebox.showinfo("Modo DEV", "Simulação de update concluída!\n\n(O script não será substituído em ambiente de desenvolvimento)")
        return

    nome_exe_atual = os.path.basename(exe_atual)
    dir_atual = os.path.dirname(exe_atual)
    
    bat_content = f"""
@echo off
timeout /t 2 /nobreak > NUL
del "{nome_exe_atual}"
move "{novo_exe}" "{nome_exe_atual}"
start "" "{nome_exe_atual}"
del "%~f0"
"""
    bat_path = os.path.join(dir_atual, "update.bat")
    with open(bat_path, "w") as f:
        f.write(bat_content)
        
    subprocess.Popen(bat_path, shell=True)
    sys.exit() # Fecha o app atual
