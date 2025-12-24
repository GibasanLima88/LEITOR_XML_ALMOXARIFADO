import pyautogui as py
import time
import json
import os
from tkinter import messagebox
import unicodedata
from core.utils import resource_path

def normalizar_texto(texto):
    """Remove acentos e converte para minúsculas para comparação."""
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto))
                  if unicodedata.category(c) != 'Mn').lower()

def carregar_regras(perfil="verificacao_pis_cofins"):
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

# Função para clicar em uma imagem na tela
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

def verificar_itens_pis_cofins_regras(ncm_entry, combo_desembolso, entry_cfop_widgets, entry_cst_widgets, checar_interrupcao_callback, clicar_rateio_callback, vars_uso_consumo=None, velocidade=0.2):
    py.PAUSE = velocidade
    # Normaliza o desembolso (remove acentos e minúsculas)
    desembolso_raw = combo_desembolso.get()
    desembolso_norm = normalizar_texto(desembolso_raw)
    
    regras = carregar_regras("verificacao_pis_cofins")
    if not regras:
        return

    # Navegação inicial
    if clicar_imagem('seta.png'):
        if checar_interrupcao_callback(): return
        time.sleep(1)
        if checar_interrupcao_callback(): return

    py.press('up', presses=50)
    if checar_interrupcao_callback(): return
    time.sleep(2)
    if checar_interrupcao_callback(): return

    for i, (cfop_entry, cst_entry, ncm_widget) in enumerate(zip(entry_cfop_widgets, entry_cst_widgets, ncm_entry)):
        cfop_valor = str(cfop_entry.get()).strip()
        cst_valor = str(cst_entry.get()).strip()
        ncm_valor = str(ncm_widget.get()).strip()
        print(f"Índice atual: {i}, CFOP: {cfop_valor}, CST: {cst_valor}, NCM: {ncm_valor}")

        # Entrar no item
        clicar_imagem('seta.png', clicks=2)
        if checar_interrupcao_callback(): return

        time.sleep(0.4)
        if checar_interrupcao_callback(): return
        if not clicar_imagem('cfop.png', offset_y=10, timeout=10, confidence=0.9): return
        # py.press('tab', presses=9)
        if checar_interrupcao_callback(): return
        time.sleep(0.1)
        if checar_interrupcao_callback(): return

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
             py.press('enter')
             if checar_interrupcao_callback(): return

             time.sleep(0.2)
             if checar_interrupcao_callback(): return
             
             py.press('tab', presses=3) 
             if checar_interrupcao_callback(): return
             py.write('0') 
             time.sleep(0.2)
             if checar_interrupcao_callback(): return
             py.press ('tab')
             if checar_interrupcao_callback(): return
             
             # CST 90
             py.write("90")
             time.sleep(0.2)
             if checar_interrupcao_callback(): return

             py.press('tab')
             if checar_interrupcao_callback(): return
             
             # PIS 98
             py.write("98")
             time.sleep(0.2)
             if checar_interrupcao_callback(): return
             py.press('tab')
             if checar_interrupcao_callback(): return
             
             # COFINS 98
             py.write("98")
             time.sleep(0.2)
             if checar_interrupcao_callback(): return
             py.press('tab')
             if checar_interrupcao_callback(): return
             
             # IPI 49
             py.write("49")
             if checar_interrupcao_callback(): return
             py.press('tab')
             if checar_interrupcao_callback(): return
             
             time.sleep(1)
             if checar_interrupcao_callback(): return

             # Rateio
             clicar_rateio_callback(desembolso_raw)
             if checar_interrupcao_callback(): return
             
             # PULA REGRAS (mas segue para confirmação)
             regra_encontrada = True
             pass 

        # --- MOTOR DE REGRAS ---
        if not uso_consumo:
            # regra_encontrada já foi inicializada como False lá em cima
        
            for regra in regras:
                condicoes = regra.get("entrada", {})
                
                # Checa CFOP e CST
                lista_cfops = [str(c).strip() for c in condicoes.get("cfop", [])]
                lista_csts = [str(c).strip() for c in condicoes.get("cst", [])]

                cfop_match = cfop_valor in lista_cfops
                cst_match = cst_valor in lista_csts
                
                if cfop_match and cst_match:
                    print(f"Regra aplicada: CFOP {cfop_valor} / CST {cst_valor}")
                    saida = regra.get("saida", {})
                    
                    if checar_interrupcao_callback(): return
                    
                    # CFOP Saída
                    if "cfop" in saida:
                        py.write(saida["cfop"])
                        py.press('enter')
                        time.sleep(0.2)
                        if checar_interrupcao_callback(): return
                    
                    
                    
                    
                    # Navegação fixa (Tab x3 -> '0' -> Tab)
                    
                    py.press('tab', presses=3) 
                    if checar_interrupcao_callback(): return
                    py.write('0') 
                    time.sleep(0.1)
                    if checar_interrupcao_callback(): return
                    py.press ('tab')
                    if checar_interrupcao_callback(): return
                    
                    # CST Saída
                    if "cst" in saida:
                        py.write(saida["cst"])
                        time.sleep(0.1)
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
                        time.sleep(0.1)
                        if checar_interrupcao_callback(): return
                    py.press('tab')
                    if checar_interrupcao_callback(): return

                    time.sleep(0.1)
                    if checar_interrupcao_callback(): return
                    
                    # Clicar Isento ou Integral
                    if saida.get("clicar_isento"):
                        clicar_imagem('isento.png')
                    elif saida.get("clicar_integral"):
                        clicar_imagem('valor_integral.png')
                    
                    if checar_interrupcao_callback(): return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    
                    # Rateio
                    clicar_rateio_callback(desembolso_raw)
                    if checar_interrupcao_callback(): return
                    
                    regra_encontrada = True
                    break
        
            if not regra_encontrada:
                print(f"Nenhuma regra encontrada para CFOP {cfop_valor}, CST {cst_valor}, Desembolso {desembolso_raw}")
                # Se não encontrar regra, o código original continuava o loop (indo para o próximo item),
                # ou simplesmente não fazia nada e passava para a navegação de saída.
                # Vamos assumir que se não tem regra, não edita, apenas sai e vai pro próximo.
        
        # --- CONFIRMAÇÃO E NAVEGAÇÃO PRO PRÓXIMO ITEM ---
        
        # Confirmar
        if clicar_imagem('confirmar2.png'):
            if checar_interrupcao_callback(): return
            time.sleep(1.5)
            if checar_interrupcao_callback(): return

        # Voltar para lista (seta)
        if clicar_imagem('seta.png'):
            if checar_interrupcao_callback(): return
            time.sleep(0.4)
            if checar_interrupcao_callback(): return
            py.press('down')
            if checar_interrupcao_callback(): return
            time.sleep(0.4)    
            if checar_interrupcao_callback(): return
            py.moveTo(x=527, y=360)
            if checar_interrupcao_callback(): return
