import pyautogui as py
import time
import json
import os
from tkinter import messagebox

def carregar_regras(perfil="verificacao_padrao"):
    caminho_json = "regras_fiscais.json"
    if not os.path.exists(caminho_json):
        messagebox.showerror("Erro", f"Arquivo de regras '{caminho_json}' não encontrado!")
        return []
    
    try:
        with open(caminho_json, "r", encoding="utf-8") as f:
            dados = json.load(f)
            return dados.get(perfil, [])
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao ler regras fiscais: {e}")
        return []

def clicar_imagem(imagem, timeout=5, offset_x=0, offset_y=0, clicks=1):
    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            posicao = py.locateCenterOnScreen(imagem, confidence=0.8)
            if posicao:
                py.click(posicao.x + offset_x, posicao.y + offset_y, clicks=clicks)
                return True
        except Exception:
            pass
        time.sleep(0.5)
    
    # Fallback se não encontrar a imagem
    print(f"Imagem {imagem} não encontrada.")
    return False

def verificar_itens(ncm_entry, combo_desembolso, entry_cfop_widgets, entry_cst_widgets, checar_interrupcao_callback, clicar_rateio_callback):
    py.PAUSE = 0.2
    desembolso2 = combo_desembolso.get()  # Obtenha o valor selecionado no combobox
    
    # Carregar regras do perfil padrão
    regras = carregar_regras("verificacao_padrao")
    if not regras:
        return # Aborta se não houver regras

    # Localiza a imagem na tela
    if clicar_imagem('seta.png'):
        if checar_interrupcao_callback(): return
        time.sleep(1)
        if checar_interrupcao_callback(): return
    
    py.press('up', presses=60)  # Pressiona a seta para cima 4 vezes
    if checar_interrupcao_callback(): return
    time.sleep(2)
    if checar_interrupcao_callback(): return
    
    for i, (cfop_entry, cst_entry, ncm_widget) in enumerate(zip(entry_cfop_widgets, entry_cst_widgets, ncm_entry)):
        cfop_valor = cfop_entry.get()
        cst_valor = cst_entry.get()
        ncm_valor = ncm_widget.get()  # Extrair o valor do widget específico de NCM
        print(f"Índice atual: {i}, CFOP: {cfop_valor}, CST: {cst_valor}, NCM: {ncm_valor}")

        # Localiza a imagem na tela
        if clicar_imagem('seta.png', clicks=2):
            if checar_interrupcao_callback():
                return
            time.sleep(0.3)
            py.press('tab', presses=9)
            time.sleep(0.1)
            if checar_interrupcao_callback():
                return
            
            # --- INICIO DO MOTOR DE REGRAS ---
            regra_encontrada = False
            for regra in regras:
                condicoes = regra.get("entrada", {})
                
                # Verifica se CFOP e CST correspondem
                cfop_match = cfop_valor in condicoes.get("cfop", [])
                cst_match = cst_valor in condicoes.get("cst", [])
                
                if cfop_match and cst_match:
                    print(f"Regra aplicada: CFOP {cfop_valor} / CST {cst_valor}")
                    saida = regra.get("saida", {})
                    
                    time.sleep(0.1)
                    if checar_interrupcao_callback(): return
                    
                    # Digita CFOP de Saída
                    if "cfop" in saida:
                        py.write(saida["cfop"])
                        if checar_interrupcao_callback(): return
                    
                    time.sleep(0.1)
                    py.press('tab', presses=3)
                    if checar_interrupcao_callback(): return
                    
                    # Digita '0' (Padrão)
                    py.write('0')
                    time.sleep(0.1)
                    if checar_interrupcao_callback(): return
                    
                    # Lógica de Tabs e CST de Saída
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    
                    # Se tiver CST de saída, digita
                    if "cst" in saida:
                         py.write(saida["cst"])
                         if checar_interrupcao_callback(): return
                    
                    time.sleep(0.2)
                    if checar_interrupcao_callback(): return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    
                    # PIS
                    if "pis" in saida:
                        py.write(saida["pis"])
                        if checar_interrupcao_callback(): return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    
                    # COFINS
                    if "cofins" in saida:
                        py.write(saida["cofins"])
                        if checar_interrupcao_callback(): return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    
                    # IPI
                    if "ipi" in saida:
                        py.write(saida["ipi"])
                        if checar_interrupcao_callback(): return
                    
                    time.sleep(1)
                    if checar_interrupcao_callback(): return
                    
                    # Clicar Rateio
                    clicar_rateio_callback(desembolso2)
                    if checar_interrupcao_callback(): return
                    
                    regra_encontrada = True
                    break # Sai do loop de regras e vai para confirmar/próximo item

            if not regra_encontrada:
                print(f"Nenhuma regra encontrada para CFOP {cfop_valor} e CST {cst_valor}")
            
            # --- FIM DO MOTOR DE REGRAS ---

        if clicar_imagem('confirmar2.png'):
            time.sleep(1.5)
            if checar_interrupcao_callback():
                return
        if clicar_imagem('seta.png'):
            if checar_interrupcao_callback():
                return
            time.sleep(0.4)
            py.press('down')
            if checar_interrupcao_callback():
                return
            time.sleep(0.4)    
            py.moveTo(x=527, y=360)  
            if checar_interrupcao_callback():
                return
