import pyautogui as py
import time
import json
import os
from tkinter import messagebox
from core.utils import resource_path

def carregar_regras(perfil="verificacao_padrao"):
    caminho_json = resource_path("json_files/regras_fiscais.json")
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

def clicar_imagem(imagem, timeout=5, offset_x=0, offset_y=0, clicks=1, confidence=0.8):
    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            caminho_img = f"images/{imagem}" if not imagem.startswith("images") else imagem
            posicao = py.locateCenterOnScreen(resource_path(caminho_img), confidence=confidence)
            if posicao:
                py.click(posicao.x + offset_x, posicao.y + offset_y, clicks=clicks)
                return True
        except Exception:
            pass
        time.sleep(0.5)
    
    # Fallback se não encontrar a imagem
    print(f"Imagem {imagem} não encontrada.")
    return False

def verificar_itens(ncm_entry, combo_desembolso, entry_cfop_widgets, entry_cst_widgets, checar_interrupcao_callback, clicar_rateio_callback, vars_uso_consumo=None, velocidade=0.2):
    py.PAUSE = velocidade
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
            if not clicar_imagem('cfop.png', offset_y=10, timeout=10, confidence=0.9): return
            #py.press('tab', presses=9)
            time.sleep(0.2)
            if checar_interrupcao_callback():
                return
            
            
            # --- LÓGICA INTELIGENTE DE USO E CONSUMO ---
            uso_consumo = False
            regra_encontrada = False # Inicializa variável de controle
            if vars_uso_consumo and i < len(vars_uso_consumo):
                uso_consumo = vars_uso_consumo[i].get()

            if uso_consumo:
                 print(f"Item {i+1} marcado como USO E CONSUMO. Aplicando lógica inteligente.")
                 # Lógica inteligente
                 cfop_saida = "1556"
                 if str(cfop_valor).strip().startswith('6'):
                     cfop_saida = "2556"
                 
                 # Executa preenchimento direto
                 time.sleep(0.1)
                 if checar_interrupcao_callback(): return
                 
                 # Digita CFOP de Saída
                 py.write(cfop_saida)
                 time.sleep(0.2)
                 py.press('enter')
                 if checar_interrupcao_callback(): return
                
                 
                 time.sleep(0.1)
                 # Situacao tributaria A
                 # if not clicar_imagem('situacao_tributaria_a.png',offset_y=20, timeout=10, confidence=0.8): return
                 py.press('tab', presses=3)
                 if checar_interrupcao_callback(): return
                 
                 py.write('0') # Padrão
                 time.sleep(0.1)
                 if checar_interrupcao_callback(): return
                 py.press('tab')

                 # Situacao B (Tab logic está comentada no código original, confiamos no TAB anterior)
                 if checar_interrupcao_callback(): return
                 
                 # CST 90
                 py.write("90")
                 time.sleep(0.2)
                 if checar_interrupcao_callback(): return
                 py.press('tab')
                 if checar_interrupcao_callback(): return
                 
                 # PIS 98
                 py.write("98")
                 if checar_interrupcao_callback(): return
                 py.press('tab')
                 if checar_interrupcao_callback(): return
                 
                 # COFINS 98
                 py.write("98")
                 if checar_interrupcao_callback(): return
                 py.press('tab')
                 if checar_interrupcao_callback(): return
                 
                 # IPI 49
                 py.write("49")
                 if checar_interrupcao_callback(): return
                 
                 time.sleep(1)
                 if checar_interrupcao_callback(): return
                 
                 # Rateio
                 clicar_rateio_callback(desembolso2)
                 if checar_interrupcao_callback(): return
                 
                 # PULA O MOTOR DE REGRAS PADRÃO (mas segue para confirmação)
                 regra_encontrada = True # Marca que foi processado com sucesso
                 pass 

            # --- INICIO DO MOTOR DE REGRAS ---
            # Só executa regras se NÃO for uso/consumo
            if not uso_consumo:
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
                            time.sleep(0.2)
                            py.press('enter')
                            if checar_interrupcao_callback(): return
                            
                        time.sleep(0.1)
                        # if not clicar_imagem('situacao_tributaria_a.png',offset_y=20, timeout=10, confidence=0.8): return
                        py.press('tab', presses=3)
                        if checar_interrupcao_callback(): return
                        
                        # Digita '0' (Padrão)
                        py.write('0')
                        time.sleep(0.2)
                        if checar_interrupcao_callback(): return
                        py.press('tab')
                        # Lógica de Tabs e CST de Saída
                        # if not clicar_imagem('situacao_tributaria_b.png', offset_y=20,timeout=10, confidence=0.9): return
                        # py.press('tab')
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
                            time.sleep(0.1)
                            if checar_interrupcao_callback(): return
                        py.press('tab')
                        if checar_interrupcao_callback(): return
                        
                        # COFINS
                        if "cofins" in saida:
                            py.write(saida["cofins"])
                            time.sleep(0.1)
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
