import pyautogui as py
import time
from tkinter import messagebox

# Função para clicar em uma imagem na tela
def clicar_imagem(imagem, timeout=5, offset_x=0, offset_y=0, confidence=0.8):
    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            posicao = py.locateCenterOnScreen(imagem, confidence=confidence)
            if posicao:
                py.click(posicao.x + offset_x, posicao.y + offset_y)
                return True
        except Exception:
            pass
        time.sleep(0.5)
    
    # Fallback se não encontrar a imagem
    print(f"Imagem {imagem} não encontrada.")
    return False

def relacionar(item_id, codigo, unidade):
    try:
        if clicar_imagem("confirmar_cadastro_item.png", timeout=20):
            time.sleep(18)
        
        # Clica no 'Sair' usando a imagem combinada (offset para a direita)
        # Confidence alto (0.95) para evitar clicar quando estiver desabilitado (cinza)
        if clicar_imagem("sair_fiscal_flex.png", timeout=30, offset_x=80, confidence=0.95):
           time.sleep(0.7)

        if clicar_imagem("sair_enviar_itens_pos.png", timeout=30, offset_x=80):    
            time.sleep(1)
        
        if clicar_imagem("cancelar_tela_cadastro.png", timeout=30, offset_x=70):
            time.sleep(2)

        if clicar_imagem("clicar_artigo.png", timeout=30, offset_y=20):
            time.sleep(0.5)
            py.write(codigo)
            time.sleep(0.5)
            py.press("tab")
            py.press("tab")
            py.write(unidade)  # Unidade de medida
            time.sleep(2)
        
        if clicar_imagem("confirmar_item_artigo.png", timeout=30):
            time.sleep(0.5)
      
 
        
        messagebox.showinfo("Sucesso", f"Item {item_id} relacionado com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao relacionar o item {item_id}: {e}")
