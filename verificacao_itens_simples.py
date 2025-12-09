import pyautogui as py
import time


def verificar_itens_simples(ncm_entry, combo_desembolso, entry_cfop_widgets, entry_cst_widgets, checar_interrupcao_callback, clicar_rateio_callback):
    py.PAUSE = 1
    desembolso2 = combo_desembolso.get()  # Obtenha o valor selecionado no combobox
    
    # Localiza a imagem na tela
    if clicar_imagem('seta.png'):
        time.sleep(1)
        if checar_interrupcao_callback():
            return
    py.press('up', presses=50)  # Pressiona a seta para cima 4 vezes
    time.sleep(2)
    if checar_interrupcao_callback():
            return
    for i, (cfop_entry, cst_entry, ncm_widget) in enumerate(zip(entry_cfop_widgets, entry_cst_widgets, ncm_entry)):
        cfop_valor = cfop_entry.get()
        cst_valor = cst_entry.get()
        ncm_valor = ncm_widget.get()  # Extrair o valor do widget específico de NCM
        print(f"Índice atual: {i}, CFOP: {cfop_valor}, CST: {cst_valor}, NCM: {ncm_valor}")
        if checar_interrupcao_callback():
            return
        # Localiza a imagem na tela
        localizacao = py.locateOnScreen('seta.png', confidence=0.8)
        if checar_interrupcao_callback():
            return
        # Verifica se a imagem foi encontrada
        if localizacao:
            centro = py.center(localizacao)
            py.click(centro, clicks=2)
            if checar_interrupcao_callback(): return
            time.sleep(0.4)
            if checar_interrupcao_callback(): return
            py.press('tab', presses=9)
            if checar_interrupcao_callback(): return
            time.sleep(0.1)
            if checar_interrupcao_callback():
                return
            if cfop_valor in ['5101', '5102', '5106']:    
                time.sleep(0.1)
                py.write('1102')
                if checar_interrupcao_callback():
                    return
                time.sleep(0.1)
                if checar_interrupcao_callback(): return
                py.press('tab', presses=3)
                if checar_interrupcao_callback(): return
                py.write('0')
                if checar_interrupcao_callback(): return
                time.sleep(0.1)
                if checar_interrupcao_callback():
                    return
    
                    
                if cst_valor in ['000','020','040', '101','102','300','400']:
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    if checar_interrupcao_callback():
                        return
                    py.write('40')
                    if checar_interrupcao_callback(): return
                    time.sleep(0.2)
                    if checar_interrupcao_callback():
                        return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    py.write('73')
                    if checar_interrupcao_callback():
                        return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    py.write('73')
                    if checar_interrupcao_callback():
                        return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    py.write('49')
                    if checar_interrupcao_callback():
                        return
                    time.sleep(1)
                    if checar_interrupcao_callback(): return
                    clicar_rateio_callback(desembolso2)
                    if checar_interrupcao_callback():
                        return
            if cfop_valor in ['5556']:    
                time.sleep(0.1)
                if checar_interrupcao_callback():
                    return
                py.write('1556')
                if checar_interrupcao_callback(): return
                time.sleep(0.1)
                if checar_interrupcao_callback():
                    return
                py.press('tab', presses=3)
                if checar_interrupcao_callback(): return
                py.write('0')
                if checar_interrupcao_callback(): return
                if checar_interrupcao_callback():
                    return
                time.sleep(0.1)
            
                if cst_valor in ['000', '020','040','060', '101','102', '500']:
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    if checar_interrupcao_callback():
                        return
                    py.write('90')
                    if checar_interrupcao_callback(): return
                    time.sleep(0.2)
                    if checar_interrupcao_callback():
                        return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    py.write('98')
                    if checar_interrupcao_callback():
                        return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    py.write('98')
                    if checar_interrupcao_callback():
                        return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    py.write('49')
                    if checar_interrupcao_callback():
                        return
                    time.sleep(1)
                    if checar_interrupcao_callback(): return
                    clicar_rateio_callback(desembolso2)   
                    if checar_interrupcao_callback():
                        return
            if cfop_valor in ['6101','6102','6105','6107']:
                time.sleep(0.1)
                py.write('2102')
                if checar_interrupcao_callback(): return
                if checar_interrupcao_callback():
                    return
                time.sleep(0.1)
                py.press('tab', presses=3)
                py.write('0')
                time.sleep(0.1)
                if checar_interrupcao_callback():
                    return
                if cst_valor in ['000','020','040', '101','102','300']:
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    if checar_interrupcao_callback():
                        return
                    py.write('40')
                    if checar_interrupcao_callback(): return
                    time.sleep(0.2)
                    if checar_interrupcao_callback():
                        return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    py.write('73')
                    if checar_interrupcao_callback():
                        return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    py.write('73')
                    if checar_interrupcao_callback():
                        return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    py.write('49')
                    if checar_interrupcao_callback():
                        return
                    time.sleep(1)
                    if checar_interrupcao_callback(): return
                    clicar_rateio_callback(desembolso2)

                    
            if cfop_valor == '6401':
                time.sleep(0.1)
                py.write('2403')
                if checar_interrupcao_callback(): return
                if checar_interrupcao_callback():
                    return
                time.sleep(0.1)
                py.press('tab', presses=3)
                if checar_interrupcao_callback(): return
                py.write('0')
                if checar_interrupcao_callback(): return
                if checar_interrupcao_callback():
                    return
                time.sleep(0.1)

                if cst_valor in ['010', '060', '070', '500']:
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    if checar_interrupcao_callback():
                        return
                    py.write('60')
                    if checar_interrupcao_callback(): return
                    time.sleep(0.2)
                    if checar_interrupcao_callback():
                        return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    py.write('73')
                    if checar_interrupcao_callback():
                        return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    py.write('73')
                    if checar_interrupcao_callback():
                        return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    py.write('49')
                    if checar_interrupcao_callback():
                        return
                    time.sleep(1)
                    if checar_interrupcao_callback(): return
                    clicar_rateio_callback(desembolso2)   
                    
            if cfop_valor in ['5115','5401','5403','5405']:    
                time.sleep(0.1)
                if checar_interrupcao_callback():
                    return
                py.write('1403')
                if checar_interrupcao_callback(): return
                time.sleep(0.1)
                if checar_interrupcao_callback():
                    return
                py.press('tab', presses=3)
                if checar_interrupcao_callback(): return
                py.write('0')
                if checar_interrupcao_callback(): return
                if checar_interrupcao_callback():
                    return
                time.sleep(0.1)
                if cst_valor in ['010','030', '060', '070','201','500']:
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    if checar_interrupcao_callback():
                        return
                    py.write('60')
                    if checar_interrupcao_callback(): return
                    time.sleep(0.1)
                    if checar_interrupcao_callback():
                        return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    py.write('73')
                    if checar_interrupcao_callback():
                        return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    py.write('73')
                    if checar_interrupcao_callback():
                        return
                    py.press('tab')
                    if checar_interrupcao_callback(): return
                    py.write('49')
                    if checar_interrupcao_callback():
                        return
                    if checar_interrupcao_callback(): return
                    clicar_rateio_callback(desembolso2)  # Passa o valor de desembolso
                    if checar_interrupcao_callback(): return
            
        if clicar_imagem('confirmar2.png'):
            if checar_interrupcao_callback(): return
            time.sleep(1.5)
            if checar_interrupcao_callback(): return
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


# Função para clicar em uma imagem na tela
def clicar_imagem(imagem, timeout=5, offset_x=0, offset_y=0):
    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            posicao = py.locateCenterOnScreen(imagem, confidence=0.8)
            if posicao:
                py.click(posicao.x + offset_x, posicao.y + offset_y)
                return True
        except Exception:
            pass
        time.sleep(0.5)
    
    # Fallback se não encontrar a imagem
    print(f"Imagem {imagem} não encontrada.")
    return False
