import pyautogui as py
import time
import pyperclip
from tkinter import messagebox
from core.utils import resource_path

# Função para clicar em uma imagem na tela
def clicar_imagem(imagem, timeout=5, offset_x=0, offset_y=0):
    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            caminho_img = f"images/{imagem}" if not imagem.startswith("images") else imagem
            posicao = py.locateCenterOnScreen(resource_path(caminho_img), confidence=0.8)
            if posicao:
                py.click(posicao.x + offset_x, posicao.y + offset_y)
                return True
        except Exception:
            pass
        time.sleep(0.5)
    
    # Fallback se não encontrar a imagem
    print(f"Imagem {imagem} não encontrada.")
    return False

def cadastrar_item(item_id, ncm, combo_grupo_produto, entry_un, codigo, item, grupos_especiais, checar_interrupcao_callback):
    py.PAUSE = 0.3
    """
    Realiza ações sequenciais do pyautogui e imprime o botão clicado.
    """
    # O valor do grupo de produto já é passado como uma string
    grupo_produto = combo_grupo_produto  
    
    try:
        # Verifica se o campo 'codigo' está preenchido
        if not codigo.strip():  # Verifica se o código está vazio ou só tem espaços
            messagebox.showerror("Erro", "O campo 'Código' está vazio. Preencha antes de continuar.")
            return  # Sai da função sem executar o restante

        # Verifica se o campo 'grupo_produto' está preenchido
        if not grupo_produto.strip():
            messagebox.showerror("Erro", "O campo 'Grupo de Produto' está vazio. Preencha antes de continuar.")
            return


        # Automação usando pyautogui
        
        # Clica no botão INCLUIR (usando imagem)
        
        if checar_interrupcao_callback(): return
        clicar_imagem("incluir.png")
        if checar_interrupcao_callback(): return
        time.sleep(0.5)
        if checar_interrupcao_callback(): return
        
        py.write(codigo)
        if checar_interrupcao_callback(): return
        py.press('tab')
        if checar_interrupcao_callback(): return

        pyperclip.copy(item.upper())
        py.hotkey('ctrl', 'v')
        if checar_interrupcao_callback(): return
        py.press('tab')
        if checar_interrupcao_callback(): return

        if grupo_produto in grupos_especiais:
            clicar_imagem("consumo.png")
            if checar_interrupcao_callback(): return
            
            # Clica no label 'Grupo de Produtos' com offset Y=30 para pegar o Entry
            if clicar_imagem("campo_grupo_label.png", offset_y=10):
                if checar_interrupcao_callback(): return
                time.sleep(0.5)
                if checar_interrupcao_callback(): return
                pyperclip.copy(grupo_produto)
                py.hotkey('ctrl', 'v')
                if checar_interrupcao_callback(): return
                time.sleep(1)
                if checar_interrupcao_callback(): return
                py.press('tab')
                if checar_interrupcao_callback(): return
            else:
                print("Campo Grupo de Produto (label) não encontrado.")
        else:
            clicar_imagem("campo_grupo_label.png", offset_y=10)
            if checar_interrupcao_callback(): return
            pyperclip.copy(grupo_produto)
            py.hotkey('ctrl', 'v')
            if checar_interrupcao_callback(): return
            time.sleep(1)
            if checar_interrupcao_callback(): return
            py.press('tab')
            if checar_interrupcao_callback(): return

        if checar_interrupcao_callback(): return
            
        time.sleep(9)
        if checar_interrupcao_callback(): return

        # py.moveTo(x=863, y=321) #unidade de medida
        # py.click() 
        clicar_imagem("un_medida.png",offset_y=10)  
        if checar_interrupcao_callback(): return
        
        py.write(entry_un.get())  # Captura a unidade do Entry
        if checar_interrupcao_callback(): return
        py.press('tab')
        if checar_interrupcao_callback(): return
        time.sleep(0.5)
        if checar_interrupcao_callback(): return

        # py.moveTo(x=509, y=229) #fiscal
        # py.click() 
        clicar_imagem("fiscal.png") 
        if checar_interrupcao_callback(): return
        time.sleep(0.3)
        if checar_interrupcao_callback(): return

        # py.moveTo(x=1112, y=216) #lupa do fiscal
        # py.click()
        clicar_imagem("lupa_fiscal.png") 
        if checar_interrupcao_callback(): return
        time.sleep(0.3)
        if checar_interrupcao_callback(): return

        py.write(ncm)
        if checar_interrupcao_callback(): return
        py.press('enter', presses=2)
        if checar_interrupcao_callback(): return
        
        

    except Exception as e:
        print(f"Erro ao realizar automação: {e}")
