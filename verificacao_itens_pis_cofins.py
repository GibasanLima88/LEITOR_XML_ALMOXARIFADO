import pyautogui as py
import time
import json
import os
from tkinter import messagebox
import unicodedata

def normalizar_texto(texto):
    """Remove acentos e converte para minúsculas para comparação."""
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto))
                  if unicodedata.category(c) != 'Mn').lower()

def carregar_regras(perfil="verificacao_pis_cofins"):
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

# Função para clicar em uma imagem na tela
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

def verificar_itens_pis_cofins_regras(ncm_entry, combo_desembolso, entry_cfop_widgets, entry_cst_widgets, checar_interrupcao_callback, clicar_rateio_callback):
    py.PAUSE = 0.2
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
        cfop_valor = cfop_entry.get()
        cst_valor = cst_entry.get()
        ncm_valor = ncm_widget.get()
        print(f"Índice atual: {i}, CFOP: {cfop_valor}, CST: {cst_valor}, NCM: {ncm_valor}")

        # Entrar no item
        clicar_imagem('seta.png', clicks=2)
        if checar_interrupcao_callback(): return

        time.sleep(0.4)
        if checar_interrupcao_callback(): return
        py.press('tab', presses=9)
        if checar_interrupcao_callback(): return
        time.sleep(0.1)
        if checar_interrupcao_callback(): return

        # --- MOTOR DE REGRAS ---
        regra_encontrada = False
        
        for regra in regras:
            condicoes = regra.get("entrada", {})
            
            # Checa CFOP e CST
            cfop_match = cfop_valor in condicoes.get("cfop", [])
            cst_match = cst_valor in condicoes.get("cst", [])
            
            # Checa Desembolso (se a regra exigir)
            desembolso_regra = condicoes.get("desembolso", "")
            if desembolso_regra:
                # Se a regra tem 'desembolso', precisa bater (contém)
                if normalizar_texto(desembolso_regra) not in desembolso_norm:
                    continue # Regra não se aplica a este desembolso
            
            if cfop_match and cst_match:
                print(f"Regra aplicada: CFOP {cfop_valor} / CST {cst_valor} / Filtro: {desembolso_regra}")
                saida = regra.get("saida", {})
                
                if checar_interrupcao_callback(): return
                
                # CFOP Saída
                if "cfop" in saida:
                    py.write(saida["cfop"])
                    if checar_interrupcao_callback(): return
                
                time.sleep(0.2)
                if checar_interrupcao_callback(): return
                
                # Navegação fixa (Tab x3 -> '0' -> Tab)
                # Algumas regras no original tinham variações minúsculas (tab x 3 ou não), 
                # mas em geral era isso. Vamos padronizar conforme a engine anterior,
                # mas observando o padrão "geral":
                # O código original das isenções fazia: Tabx3 -> '0' -> Tab.
                # O código do consumo fazia: Tabx3 -> '0' -> Tab.
                # O padrão 5101 fazia: Tabx3 -> '0' -> Tab.
                # Então é seguro manter.
                
                py.press('tab', presses=3) 
                if checar_interrupcao_callback(): return
                py.write('0') 
                if checar_interrupcao_callback(): return
                py.press ('tab')
                if checar_interrupcao_callback(): return
                
                # CST Saída
                if "cst" in saida:
                    py.write(saida["cst"])
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
                py.press('tab')
                if checar_interrupcao_callback(): return

                time.sleep(0.2)
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
