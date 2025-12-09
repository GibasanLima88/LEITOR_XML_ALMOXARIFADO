import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from xml.etree import ElementTree as ET
import pyautogui as py
import time
from tkinter import ttk  # Importe ttk para o Combobox
import pyperclip
from tkinter import messagebox
import keyboard
import json
import os
import threading
from verificacao_itens_simples import verificar_itens_simples
from verificacao_itens import verificar_itens
from cadastro_item import cadastrar_item
from relacionar_item import relacionar

# Carregar grupos do JSON
def carregar_grupos():
    caminho_json = "grupos.json"
    if not os.path.exists(caminho_json):
        messagebox.showerror("Erro", f"Arquivo '{caminho_json}' não encontrado!")
        return [], []
    
    try:
        with open(caminho_json, "r", encoding="utf-8") as f:
            dados = json.load(f)
            return dados.get("grupos", []), dados.get("grupos_especiais", [])
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao ler '{caminho_json}': {e}")
        return [], []

# Carregar desembolsos do JSON
def carregar_desembolsos():
    caminho_json = "desembolsos.json"
    if not os.path.exists(caminho_json):
        messagebox.showerror("Erro", f"Arquivo '{caminho_json}' não encontrado!")
        return []
    
    try:
        with open(caminho_json, "r", encoding="utf-8") as f:
            dados = json.load(f)
            return dados.get("desembolsos", [])
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao ler '{caminho_json}': {e}")
        return []

grupos_produtos, grupos_especiais = carregar_grupos()
desembolsos_lista = carregar_desembolsos()

# Função para salvar a lista completa no JSON
def salvar_lista_json(arquivo, chave_lista, lista):
    if not os.path.exists(arquivo):
        messagebox.showerror("Erro", f"Arquivo '{arquivo}' não encontrado!")
        return False

    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        
        # Atualiza a lista e salva
        lista.sort(key=str.casefold)
        dados[chave_lista] = lista
        
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
            
        return True
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar no '{arquivo}': {e}")
        return False

# Função para salvar grupos e grupos especiais
def salvar_grupos_json(lista_grupos, lista_especiais):
    arquivo = "grupos.json"
    try:
        dados = {
            "grupos": sorted(lista_grupos, key=str.casefold),
            "grupos_especiais": sorted(lista_especiais, key=str.casefold)
        }
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar grupos: {e}")
        return False

def abrir_gerenciador(titulo, arquivo, chave_json, combobox_alvo):
    # Janela Toplevel
    gerenciador = tk.Toplevel()
    gerenciador.title(titulo)
    gerenciador.geometry("450x500") # Aumentei um pouco
    
    # Variáveis locais para listas
    lista_atual = []
    lista_especiais = []
    e_grupo = (chave_json == "grupos")

    # Carrega dados
    if e_grupo:
        lista_atual, lista_especiais = carregar_grupos()
    else:
        lista_atual = carregar_desembolsos()

    # Frame da Lista
    frame_lista = tk.Frame(gerenciador)
    frame_lista.pack(fill="both", expand=True, padx=10, pady=10)
    
    scrollbar = tk.Scrollbar(frame_lista, orient="vertical")
    listbox = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set, font=('Arial', 10))
    scrollbar.config(command=listbox.yview)
    
    scrollbar.pack(side="right", fill="y")
    listbox.pack(side="left", fill="both", expand=True)
    
    def atualizar_listbox():
        listbox.delete(0, tk.END)
        for item in lista_atual:
            display_text = item
            if e_grupo and item in lista_especiais:
                display_text += " [Uso e Consumo]"
            listbox.insert(tk.END, display_text)
            
    atualizar_listbox()
    
    # Funções CRUD
    def salvar_alteracoes():
        if e_grupo:
            sucesso = salvar_grupos_json(lista_atual, lista_especiais)
        else:
            sucesso = salvar_lista_json(arquivo, chave_json, lista_atual)
        
        if sucesso:
            atualizar_listbox()
            combobox_alvo['values'] = lista_atual
            return True
        return False

    def adicionar():
        novo = simpledialog.askstring("Adicionar", "Digite o nome do novo item:", parent=gerenciador)
        if novo:
            if novo in lista_atual:
                messagebox.showwarning("Aviso", "Este item já existe!", parent=gerenciador)
                return
            
            lista_atual.append(novo)
            if salvar_alteracoes():
                messagebox.showinfo("Sucesso", "Item adicionado!", parent=gerenciador)

    def editar():
        selecionado = listbox.curselection()
        if not selecionado:
            return
        indice = selecionado[0]
        # Recupera nome real (sem o sufixo [Uso e Consumo])
        nome_completo = listbox.get(indice)
        nome_real = nome_completo.replace(" [Uso e Consumo]", "")
        
        novo_valor = simpledialog.askstring("Editar", f"Editar '{nome_real}':", initialvalue=nome_real, parent=gerenciador)
        if novo_valor and novo_valor != nome_real:
            if novo_valor in lista_atual:
                messagebox.showwarning("Aviso", "Já existe um item com esse nome!", parent=gerenciador)
                return

            lista_atual[indice] = novo_valor
            
            # Se era especial, atualiza na lista de especiais também
            if e_grupo and nome_real in lista_especiais:
                lista_especiais.remove(nome_real)
                lista_especiais.append(novo_valor)

            if salvar_alteracoes():
                # Se o item editado estiver selecionado no combobox principal, atualiza ele
                if combobox_alvo.get() == nome_real:
                    combobox_alvo.set(novo_valor)
                messagebox.showinfo("Sucesso", "Item editado!", parent=gerenciador)

    def excluir():
        selecionado = listbox.curselection()
        if not selecionado:
            return
        indice = selecionado[0]
        nome_completo = listbox.get(indice)
        nome_real = nome_completo.replace(" [Uso e Consumo]", "")
        
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir '{nome_real}'?", parent=gerenciador):
            lista_atual.pop(indice)
            if e_grupo and nome_real in lista_especiais:
                lista_especiais.remove(nome_real)

            if salvar_alteracoes():
                if combobox_alvo.get() == nome_real:
                    combobox_alvo.set('')
                messagebox.showinfo("Sucesso", "Item excluído!", parent=gerenciador)

    def alternar_especial():
        if not e_grupo:
            return
        
        selecionado = listbox.curselection()
        if not selecionado:
            return
        indice = selecionado[0]
        nome_completo = listbox.get(indice)
        nome_real = nome_completo.replace(" [Uso e Consumo]", "")
        
        if nome_real in lista_especiais:
            lista_especiais.remove(nome_real)
        else:
            lista_especiais.append(nome_real)
            
        salvar_alteracoes()

    # Frame Botões
    frame_botoes = tk.Frame(gerenciador)
    frame_botoes.pack(fill="x", padx=10, pady=5)
    
    btn_add = tk.Button(frame_botoes, text="Adicionar", command=adicionar, bg="#90ee90")
    btn_add.pack(side="left", expand=True, fill="x", padx=2)
    
    btn_edit = tk.Button(frame_botoes, text="Editar", command=editar, bg="#add8e6")
    btn_edit.pack(side="left", expand=True, fill="x", padx=2)
    
    btn_del = tk.Button(frame_botoes, text="Excluir", command=excluir, bg="#ffcccb")
    btn_del.pack(side="left", expand=True, fill="x", padx=2)

    # Botão Extra para Grupos
    if e_grupo:
        frame_extra = tk.Frame(gerenciador)
        frame_extra.pack(fill="x", padx=10, pady=5)
        btn_esp = tk.Button(frame_extra, text="Alternar Especial (Uso e Consumo)", command=alternar_especial, bg="#ffd700")
        btn_esp.pack(fill="x")

def clique_gerenciar_desembolso():
    abrir_gerenciador("Gerenciar Desembolsos", "desembolsos.json", "desembolsos", combo_desembolso)

def clique_gerenciar_grupo():
    abrir_gerenciador("Gerenciar Grupos de Produto", "grupos.json", "grupos", combo_grupo_produto)

entry_cst_widgets = []
entry_cfop_widgets = []
entry_ncm_widgets = []

# Variável global para controlar a interrupção
interromper = False

def checar_interrupcao():
    if keyboard.is_pressed('alt'):
        messagebox.showinfo(
            "Interrupção",
            "Programa interrompido pelo usuário."
        )
        return True   # sinaliza que foi interrompido
    return False

# Função para limpar os widgets da tela de itens
def limpar_tela():
    """Limpa todos os widgets relacionados aos itens na tela."""
    for widget in frame_itens.winfo_children():
        widget.destroy()
    # Resetar o campo nome da empresa
    lb_empresa.config(text="Empresa: ", fg='black') 
    lb_nf.config(text="NF: ", fg='black') 
    # Limpar o campo entry_caminho
    entry_caminho.delete(0, tk.END)  # Limpa o campo de entrada
    
#     messagebox.showinfo("Tela Limpa", "Os itens foram removidos da tela.")

def alterar_desembolso(i):
    py.PAUSE = 0.2
    for index, widget in enumerate(entry_cfop_widgets):  
        desembolso = combo_desembolso.get()  # Obter o valor
        pyperclip.copy(desembolso)  # Copiar para a área de transferência
        print(f"Desembolso ajustado: {desembolso}")  # Depuração
        if checar_interrupcao():
                return
        localizacao = py.locateOnScreen('seta.png', confidence=0.8)
        if localizacao:
            centro = py.center(localizacao)
            py.click(centro, clicks=2)
            time.sleep(1)
            if checar_interrupcao():
                return
        rateio = py.locateOnScreen('rateio.png', confidence=0.8)
        if rateio:
            rateio_centro = py.center(rateio)
            py.click(rateio_centro)
            py.press('tab', presses=2)
            time.sleep(0.1)
            if checar_interrupcao():
                return
            py.hotkey('ctrl', 'v')  # Colar o valor
            py.press('tab')
            if checar_interrupcao():
                return
            py.moveTo(x=1313, y=320)
            py.click(x=1313, y=320)  
            if checar_interrupcao():
                return
        confirmar = py.locateOnScreen('confirmar2.png', confidence=0.8)
        if confirmar:
            confirmar_centro = py.center(confirmar)
            py.click(confirmar_centro) 
            time.sleep(1)
            if checar_interrupcao():
                return
        localizacao = py.locateOnScreen('seta.png', confidence=0.8)
        if localizacao:
            centro = py.center(localizacao)
            py.click(centro)
            if checar_interrupcao():
                return
            time.sleep(0.1)
            py.press('down')
            if checar_interrupcao():
                return
            time.sleep(0.1)    
            py.moveTo(x=527, y=360)

            
def clicar_rateio(desembolso2):
    desembolso2 = combo_desembolso.get()
    # Localiza e clica no botão "rateio"
    rateio = py.locateOnScreen('rateio.png', confidence=0.8)
    if rateio:
        rateio_centro = py.center(rateio)
        py.click(rateio_centro)
        time.sleep(0.2)
        py.press('tab', presses=2)
        time.sleep(0.1)
#         py.write(desembolso2)  # Preenche o valor de desembolso
        pyperclip.copy(desembolso2)  # Preenche o valor de desembolso
        py.hotkey('ctrl','v')
        py.press('tab')
#         py.moveTo(x=1313, y=320)
#         py.click(x=1313, y=320)  
    else:
        messagebox.showwarning("Aviso", "Botão 'rateio' não encontrado na tela.")            
            
            
def localizar_e_clicar(imagem, clicks=1):
    try:
        local = py.locateOnScreen(imagem, confidence=0.8)
        if local:
            centro = py.center(local)
            py.click(centro, clicks=clicks)
            return True
        else:
            print(f"⚠ Imagem '{imagem}' não encontrada (retornou None).")
            return False
    except py.ImageNotFoundException:
        print(f"⚠ Exceção: imagem '{imagem}' não encontrada (lançou ImageNotFoundException).")
        return False
    except Exception as e:
        print(f"⚠ Erro inesperado ao localizar '{imagem}': {e}")
        return False


import pyautogui as py
import time

def verificar_itens_pis_cofins(ncm_entry):
    py.PAUSE = 0.2
    desembolso2 = combo_desembolso.get().lower()

    if localizar_e_clicar('seta.png'):
        if checar_interrupcao(): return
        time.sleep(1)
        if checar_interrupcao(): return

    py.press('up', presses=50)
    if checar_interrupcao(): return
    time.sleep(2)
    if checar_interrupcao(): return

    cst_isentos = ['040', '101', '102', '300', '400', '051']
    cfops_subst = ['5115', '5401', '5403', '5405']
    csts_subst = ['010','030','060', '070', '201', '500']
    cfops_subst2 = ['6115', '6401', '6403', '6405']
    csts_subst2 = ['010', '060', '070', '201', '500']
    
    
    cfops_consumo = ['5556']
    csts_consumo = ['000','010','020', '060', '070', '201', '500','040', '101', '102', '300', '400', '051']

    for i, (cfop_entry, cst_entry, ncm_widget) in enumerate(zip(entry_cfop_widgets, entry_cst_widgets, ncm_entry)):
        cfop_valor = cfop_entry.get()
        cst_valor = cst_entry.get()
        ncm_valor = ncm_widget.get()
        print(f"Índice atual: {i}, CFOP: {cfop_valor}, CST: {cst_valor}, NCM: {ncm_valor}")

        localizar_e_clicar('seta.png', clicks=2)
        if checar_interrupcao(): return

        time.sleep(0.4)
        if checar_interrupcao(): return
        py.press('tab', presses=9)
        if checar_interrupcao(): return
        time.sleep(0.1)
        if checar_interrupcao():
            return

        # ====== NOVA LÓGICA PARA OS CFOPs/CSTs SUBST ======
        if cfop_valor in cfops_subst and cst_valor in csts_subst:
            if checar_interrupcao():
                return
            py.write('1403')
            if checar_interrupcao(): return
            time.sleep(0.2)
            if checar_interrupcao():
                return
            if cst_valor in csts_subst:
                py.press('tab',presses=3) 
                if checar_interrupcao(): return
                py.write('0')
                if checar_interrupcao(): return
                py.press ('tab')
                if checar_interrupcao(): return
                py.write('60')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao(): return
                py.write('73')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao(): return
                py.write('73')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao(): return
                py.write('49')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao():
                    return
                time.sleep(0.2)
                localizar_e_clicar('isento.png')
                py.press('tab')
                clicar_rateio(desembolso2)
                if checar_interrupcao():
                    return

            # Confirmar
            confirmar = py.locateOnScreen('confirmar2.png', confidence=0.8)
            if confirmar:
                confirmar_centro = py.center(confirmar)
                py.click(confirmar_centro) 
                if checar_interrupcao(): return
                time.sleep(1.5)
                if checar_interrupcao(): return

            localizacao = py.locateOnScreen('seta.png', confidence=0.8)
            if localizacao:
                centro = py.center(localizacao)
                py.click(centro)
                if checar_interrupcao(): return
                time.sleep(0.4)
                if checar_interrupcao(): return
                py.press('down')
                if checar_interrupcao(): return
                time.sleep(0.4)    
                if checar_interrupcao(): return
                py.moveTo(x=527, y=360)
                if checar_interrupcao(): return
            continue  # Vai para o próximo item
            

            
         # ====== NOVA LÓGICA PARA OS CFOPs/CSTs SUBST FORA DO ESTADO ======
        if cfop_valor in cfops_subst2 and cst_valor in csts_subst2:
            if checar_interrupcao():
                return
            py.write('2403')
            if checar_interrupcao(): return
            time.sleep(0.2)
            if checar_interrupcao():
                return
            if cst_valor in csts_subst:
                py.press('tab',presses=3) 
                if checar_interrupcao(): return
                py.write('0')
                if checar_interrupcao(): return
                py.press ('tab')
                if checar_interrupcao(): return
                py.write('60')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao(): return
                py.write('73')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao(): return
                py.write('73')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao(): return
                py.write('49')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao():
                    return
                time.sleep(0.2)
                localizar_e_clicar('isento.png')
                py.press('tab')
                clicar_rateio(desembolso2)
                if checar_interrupcao():
                    return

            # Confirmar
            confirmar = py.locateOnScreen('confirmar2.png', confidence=0.8)
            if confirmar:
                confirmar_centro = py.center(confirmar)
                py.click(confirmar_centro) 
                if checar_interrupcao(): return
                time.sleep(1.5)
                if checar_interrupcao(): return

            localizacao = py.locateOnScreen('seta.png', confidence=0.8)
            if localizacao:
                centro = py.center(localizacao)
                py.click(centro)
                if checar_interrupcao(): return
                time.sleep(0.4)
                if checar_interrupcao(): return
                py.press('down')
                if checar_interrupcao(): return
                time.sleep(0.4)    
                if checar_interrupcao(): return
                py.moveTo(x=527, y=360)
                if checar_interrupcao(): return
            continue  # Vai para o próximo item
            
            
# ====== NOVA LÓGICA PARA USO E CONSUMO ======
        if cfop_valor in cfops_consumo and cst_valor in csts_consumo:
            if checar_interrupcao():
                return
            py.write('1556')
            if checar_interrupcao(): return
            time.sleep(0.2)
            if checar_interrupcao():
                return
            if cst_valor in csts_consumo:
                py.press('tab',presses=3) 
                if checar_interrupcao(): return
                py.write('0')
                if checar_interrupcao(): return
                py.press ('tab')
                if checar_interrupcao(): return
                py.write('90')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao(): return
                py.write('98')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao(): return
                py.write('98')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao(): return
                py.write('49')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao():
                    return
                time.sleep(0.2)
                if checar_interrupcao(): return
                localizar_e_clicar('isento.png')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao(): return
                clicar_rateio(desembolso2)
                if checar_interrupcao():
                    return

            # Confirmar
            confirmar = py.locateOnScreen('confirmar2.png', confidence=0.8)
            if confirmar:
                confirmar_centro = py.center(confirmar)
                py.click(confirmar_centro) 
                time.sleep(1.5)

            localizacao = py.locateOnScreen('seta.png', confidence=0.8)
            if localizacao:
                centro = py.center(localizacao)
                py.click(centro)
                if checar_interrupcao(): return
                time.sleep(0.4)
                if checar_interrupcao(): return
                py.press('down')
                if checar_interrupcao(): return
                time.sleep(0.4)    
                if checar_interrupcao(): return
                py.moveTo(x=527, y=360)
                if checar_interrupcao(): return
            continue  # Vai para o próximo item
            
            

        # ====== LÓGICA DOS CFOPs 5101, 5102, 5106 ======
        if cfop_valor in ['5101', '5102', '5106']:
            time.sleep(0.1)
            py.write('1102')
            if checar_interrupcao(): return
            time.sleep(0.1)
            py.press('tab', presses=3)
            if checar_interrupcao(): return
            py.write('0')
            if checar_interrupcao(): return
            time.sleep(0.1)
            if checar_interrupcao(): return

            # --- REGRAS DO "CLUBE 73" ---
            if cst_valor in cst_isentos:
                py.press('tab')
                if checar_interrupcao(): return
                py.write('40')
                if checar_interrupcao(): return
                time.sleep(0.2)
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao(): return

                py.write('73')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao(): return
                py.write('73')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao(): return
                py.write('49')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao(): return

                time.sleep(0.2)
                if checar_interrupcao(): return
                localizar_e_clicar('isento.png')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao(): return
                if checar_interrupcao(): return
                clicar_rateio(desembolso2)
                if checar_interrupcao(): return

            # --- REGRAS CST 000 E 020 ---
            elif cst_valor in ['000', '020']:
                py.press('tab')
                if checar_interrupcao():
                    return
                py.write('00' if cst_valor == '000' else '20')
                time.sleep(0.2)
                if checar_interrupcao():
                    return
                py.press('tab')

                # Café da manhã ou restaurante com CST 000 ou 020
                if 'cafe da manha' in desembolso2:
                    py.write('73')
                elif 'restaurante' in desembolso2:
                    py.write('50')
                else:
                    print(f"⚠ Desembolso '{desembolso2}' não tem regra definida para CFOP {cfop_valor}")
                    continue

                if checar_interrupcao():
                    return

                py.press('tab')
                if checar_interrupcao(): return
                py.write('73' if 'cafe da manha' in desembolso2 else '50')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao(): return
                py.write('49')
                if checar_interrupcao(): return
                py.press('tab')
                if checar_interrupcao(): return

                if 'cafe da manha' in desembolso2:
                    time.sleep(0.2)
                    if checar_interrupcao(): return
                    localizar_e_clicar('isento.png')
                    if checar_interrupcao(): return
                    py.press('tab')
                    if checar_interrupcao(): return
                    clicar_rateio(desembolso2)
                    if checar_interrupcao(): return
                elif 'restaurante' in desembolso2:
                    time.sleep(0.2)
                    if checar_interrupcao(): return
                    localizar_e_clicar('valor_integral.png')
                    if checar_interrupcao(): return
                    py.press('tab')
                    if checar_interrupcao(): return
                    clicar_rateio(desembolso2)
                    if checar_interrupcao(): return

            else:
                print(f"⚠ CST '{cst_valor}' não tem regra definida para CFOP {cfop_valor}")
                continue

            # Confirmar
            confirmar = py.locateOnScreen('confirmar2.png', confidence=0.8)
            if confirmar:
                confirmar_centro = py.center(confirmar)
                py.click(confirmar_centro) 
                time.sleep(1.5)

            localizacao = py.locateOnScreen('seta.png', confidence=0.8)
            if localizacao:
                centro = py.center(localizacao)
                py.click(centro)
                if checar_interrupcao(): return
                time.sleep(0.4)
                if checar_interrupcao(): return
                py.press('down')
                if checar_interrupcao(): return
                time.sleep(0.4)    
                if checar_interrupcao(): return
                py.moveTo(x=527, y=360)
                if checar_interrupcao(): return



        
        
        
        
        
        
        # ====== LÓGICA DOS CFOPs 6101, 6102, 6106 ======
        if cfop_valor in ['6101', '6102', '6106']:
            time.sleep(0.1)
            py.write('2102')
            if checar_interrupcao(): return
            time.sleep(0.1)
            if checar_interrupcao(): return
            py.press('tab', presses=3)
            if checar_interrupcao(): return
            py.write('0')
            if checar_interrupcao(): return
            time.sleep(0.1)
            if checar_interrupcao(): return

            # --- REGRAS DO "CLUBE 73" ---
            if cst_valor in cst_isentos:
                py.press('tab')
                if checar_interrupcao():
                    return
                py.write('40')
                time.sleep(0.2)
                if checar_interrupcao():
                    return
                py.press('tab')

                py.write('73')
                py.press('tab')
                py.write('73')
                py.press('tab')
                py.write('49')
                py.press('tab')
                if checar_interrupcao():
                    return

                time.sleep(0.2)
                localizar_e_clicar('isento.png')
                py.press('tab')
                clicar_rateio(desembolso2)
                if checar_interrupcao():
                    return

            # --- REGRAS CST 000 E 020 ---
            elif cst_valor in ['000', '020']:
                py.press('tab')
                if checar_interrupcao():
                    return
                py.write('00' if cst_valor == '000' else '20')
                time.sleep(0.2)
                if checar_interrupcao():
                    return
                py.press('tab')

                # Café da manhã ou restaurante com CST 000 ou 020
                if 'cafe da manha' in desembolso2:
                    py.write('73')
                elif 'restaurante' in desembolso2:
                    py.write('50')
                else:
                    print(f"⚠ Desembolso '{desembolso2}' não tem regra definida para CFOP {cfop_valor}")
                    continue

                if checar_interrupcao():
                    return

                py.press('tab')
                py.write('73' if 'cafe da manha' in desembolso2 else '50')
                py.press('tab')
                py.write('49')
                py.press('tab')
                if checar_interrupcao():
                    return

                if 'cafe da manha' in desembolso2:
                    time.sleep(0.2)
                    localizar_e_clicar('isento.png')
                    py.press('tab')
                    clicar_rateio(desembolso2)
                    if checar_interrupcao():
                        return
                elif 'restaurante' in desembolso2:
                    time.sleep(0.2)
                    localizar_e_clicar('valor_integral.png')
                    py.press('tab')
                    clicar_rateio(desembolso2)
                    if checar_interrupcao():
                        return

            else:
                print(f"⚠ CST '{cst_valor}' não tem regra definida para CFOP {cfop_valor}")
                continue

            # Confirmar
            confirmar = py.locateOnScreen('confirmar2.png', confidence=0.8)
            if confirmar:
                confirmar_centro = py.center(confirmar)
                py.click(confirmar_centro) 
                time.sleep(1.5)

            localizacao = py.locateOnScreen('seta.png', confidence=0.8)
            if localizacao:
                centro = py.center(localizacao)
                py.click(centro)
                time.sleep(0.4)
                py.press('down')
                time.sleep(0.4)    
                py.moveTo(x=527, y=360)

                    
#         confirmar = py.locateOnScreen('confirmar2.png', confidence=0.8)
#         if confirmar:
#             confirmar_centro = py.center(confirmar)
#             if checar_interrupcao():
#                 return
#             py.click(confirmar_centro) 
#             time.sleep(1.5)
#             if checar_interrupcao():
#                 return
#         localizacao = py.locateOnScreen('seta.png', confidence=0.8)
#         if localizacao:
#             if checar_interrupcao():
#                 return
#             centro = py.center(localizacao)
#             py.click(centro)
#             if checar_interrupcao():
#                 return
#             time.sleep(0.4)
#             py.press('down')
#             if checar_interrupcao():
#                 return
#             time.sleep(0.4)    
#             py.moveTo(x=527, y=360)  
#             if checar_interrupcao():
#                 return
            
###########################################################################


                



        
############################################################################






##########################################################################

def abrir_arquivo():
    file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
    if file_path:
        entry_caminho.delete(0, tk.END)
        entry_caminho.insert(0, file_path)

        # Limpar os widgets existentes no frame_itens
        for widget in frame_itens.winfo_children():
            widget.destroy()

        # Atualizar o título
        lb_titulo = tk.Label(frame_itens, text='Lançamento de NF no almoxarifado',
                             font=('Arial', 10, 'bold'), bg='#c3ccdb', anchor='center')
        lb_titulo.grid(row=0, column=0, columnspan=2, pady=10)

        # Ler os itens do XML
        global produtos, csts, cfops, entry_cst_widgets, entry_cfop_widgets
        produtos, csts, cfops, nome_empresa = extract_company_info(file_path)
        entry_cst_widgets = [] # Inicializa a lista
        entry_cfop_widgets = [] # Inicializa a lista
        entry_ncm_widgets = []
        if produtos:
            for i, produto in enumerate(produtos):
                # Labels e entradas para cada item
                lb_item = tk.Label(frame_itens, text=f"ITEM {i + 1}:", font=('Arial', 10), bg='#c3ccdb')
                lb_item.grid(row=i + 1, column=0, padx=10, pady=5, sticky="w")

                entry_produto = tk.Entry(frame_itens, width=45, font=('Arial', 10))
                entry_produto.insert(0, produto)
                entry_produto.grid(row=i + 1, column=1, padx=20, pady=5, sticky="w")

                lb_cst = tk.Label(frame_itens, text="CST:", font=('Arial', 10), bg='#c3ccdb')
                lb_cst.grid(row=i + 1, column=2, padx=10, pady=5, sticky="w")

                entry_cst = tk.Entry(frame_itens, width=4, font=('Arial', 10))
                entry_cst.insert(0, csts[i] if i < len(csts) else "")
                entry_cst.grid(row=i + 1, column=3, padx=10, pady=5, sticky="w")
                entry_cst_widgets.append(entry_cst)

                lb_cfop = tk.Label(frame_itens, text="CFOP:", font=('Arial', 10), bg='#c3ccdb')
                lb_cfop.grid(row=i + 1, column=4, padx=10, pady=5, sticky="w")

                entry_cfop = tk.Entry(frame_itens, width=4, font=('Arial', 10))
                entry_cfop.insert(0, cfops[i].text if i < len(cfops) and cfops[i] is not None else "")
                entry_cfop.grid(row=i + 1, column=5, padx=10, pady=5, sticky="w")
                entry_cfop_widgets.append(entry_cfop)
                
                # Criando o botão "Alterar Desembolso" para cada item
                button_alterar = tk.Button(frame_itens, text="Alterar Desembolso", 
                                           font=('Arial', 10), 
                                           command=lambda i=i: alterar_desembolso(i))
                button_alterar.grid(row=i + 1, column=6, padx=10, pady=5, sticky="w")
                
                
                btn_cadastrar_item = tk.Button(
                    frame_itens,
                    text=f"Cadastrar Item {i + 1}",  # Texto do botão
                    font=('Arial', 10),
                    command=lambda item_id=i + 1: cadastrar_item(item_id)  # Chama a função com o número do item
                )
                btn_cadastrar_item.grid(row=i + 1, column=10, padx=10, pady=5, sticky="w")
                
                

                
                

        else:
            messagebox.showerror("Erro", "Produtos não encontrados no XML.")

        # Atualizar o scrollregion para incluir todos os widgets
        frame_itens.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))


def extract_company_info(file_path):
    """Lê o arquivo XML e retorna os produtos, CSTs, CFOPs, unidades de medida, etc."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Substitua o namespace pelo utilizado no seu XML
        namespace = {'ns': 'http://www.portalfiscal.inf.br/nfe'}

        # Extrair o nome da empresa
        nome_empresa = root.find('.//ns:emit/ns:xNome', namespace).text

        # Extrair o numero da nota
        nf = root.find('.//ns:nNF', namespace).text

        produtos = [prod.find('ns:xProd', namespace).text for prod in root.findall('.//ns:det/ns:prod', namespace)]

        csts = [
            imposto.find('.//ns:CSOSN', namespace).text.zfill(3) if imposto.find('.//ns:CSOSN', namespace) is not None
            else imposto.find('.//ns:CST', namespace).text.zfill(3) if imposto.find('.//ns:CST', namespace) is not None
            else "N/A"
            for imposto in root.findall('.//ns:imposto', namespace)
        ]
        cfops = [prod.find('ns:CFOP', namespace) for prod in root.findall('.//ns:det/ns:prod', namespace)]

        ncm = [prod.find('ns:NCM', namespace).text if prod.find('ns:NCM', namespace) is not None else "N/A" 
               for prod in root.findall('.//ns:det/ns:prod', namespace)]

#         unidades = [prod.find('ns:uCom', namespace).text if prod.find('ns:uCom', namespace) is not None else "N/A" 
#                     for prod in root.findall('.//ns:det/ns:prod', namespace)]
        
        unidades = [
            "UN" if prod.find('ns:uCom', namespace) is not None and prod.find('ns:uCom', namespace).text in ["Unid","BD1","PO1",
                                "DIS","un","UN1","UND","UNID","PC1","TP1","EM1","BR1","LT1","PE1", 'PCT',"RESMA", "CADA", "ROLO","BI1",
                                "UNIDAD", "Un***", "Un**","PA"                                                                           
                                                                                                            ] 
                else "CX" if prod.find('ns:uCom', namespace) is not None and prod.find('ns:uCom', namespace).text in ["CX1","CX12",
                            "DP1","Un**",
                                                                                                                     ]
                else "PC" if prod.find('ns:uCom', namespace) is not None and prod.find('ns:uCom', namespace).text in ["PCA","Pt**","PACOTE","PT1",
                            "PECA","Pte","PT"]
                else "KG" if prod.find('ns:uCom', namespace) is not None and prod.find('ns:uCom', namespace).text in ["KG1", "Kg***"]
                else "MT" if prod.find('ns:uCom', namespace) is not None and prod.find('ns:uCom', namespace).text in ["METRO"]
                else "FD" if prod.find('ns:uCom', namespace) is not None and prod.find('ns:uCom', namespace).text in ["FD10"]
                else "PC" if prod.find('ns:uCom', namespace) is not None and prod.find('ns:uCom', namespace).text in ["PAC"]
                else prod.find('ns:uCom', namespace).text if prod.find('ns:uCom', namespace) is not None 
                else "N/A"
                for prod in root.findall('.//ns:det/ns:prod', namespace)
            ]

        return produtos, csts, cfops, nome_empresa, nf, ncm, unidades
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao processar o arquivo XML: {e}")
        return [], [], [], [], [], [], []

                
                
                
                
#         else:
#             messagebox.showerror("Erro", "Produtos não encontrados no XML.")
def abrir_arquivo():
    file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
    if file_path:
        # Atualizar o campo de entrada com o caminho do arquivo
        entry_caminho.delete(0, tk.END)
        entry_caminho.insert(0, file_path)

        # Limpar os widgets existentes no frame_itens
        for widget in frame_itens.winfo_children():
            widget.destroy()

        # Atualizar o título
        lb_titulo = tk.Label(frame_itens, text='Lançamento de NF no almoxarifado',
                             font=('Arial', 10, 'bold'), bg='#c3ccdb', anchor='center')
        lb_titulo.grid(row=0, column=0, columnspan=2, pady=10)

        # Ler os itens do XML e o nome da empresa
        global produtos, csts, cfops, entry_cst_widgets, entry_cfop_widgets, entry_ncm_widgets, entry_un_widgets
        produtos, csts, cfops, nome_empresa, nf, ncm, unidades = extract_company_info(file_path)
        entry_cst_widgets = []  # Inicializa a lista
        entry_cfop_widgets = []  # Inicializa a lista
        entry_ncm_widgets = []  # Inicializa a lista
        entry_un_widgets = []  # Inicializa a lista para armazenar widgets de unidades de medida

        # Atualizar o rótulo com o nome da empresa
#         if nome_empresa:
#             lb_empresa.config(text=f'Empresa: {nome_empresa}', fg='black', font=('bold'))
        if nome_empresa:
            nome_resumido = nome_empresa[:30]  # Pega os primeiros 15 caracteres
            lb_empresa.config(text=f'Empresa: {nome_resumido}', fg='black', font=('bold'))
        else:
            lb_empresa.config(text='Empresa: Não encontrada')
            
        if nf:
            lb_nf.config(text=f'NF: {nf}', fg='black', font=('bold'))
        else:
            lb_nf.config(text='NF: Não encontrada')    

        # Preencher os itens na interface
        entry_codigo_widgets = []  # Lista para armazenar os widgets de código
        if produtos:
            for i, produto in enumerate(produtos):
                # Labels e entradas para cada item
                lb_item = tk.Label(frame_itens, text=f"ITEM {i + 1}:", font=('Arial', 10), bg='#c3ccdb')
                lb_item.grid(row=i + 1, column=0, padx=10, pady=5, sticky="w")

                entry_produto = tk.Entry(frame_itens, width=45, font=('Arial', 10))
                entry_produto.insert(0, produto)
                entry_produto.grid(row=i + 1, column=1, padx=20, pady=5, sticky="w")

                lb_cst = tk.Label(frame_itens, text="CST:", font=('Arial', 10), bg='#c3ccdb')
                lb_cst.grid(row=i + 1, column=2, padx=10, pady=5, sticky="w")
    
                entry_cst = tk.Entry(frame_itens, width=4, font=('Arial', 10))
                entry_cst.insert(0, csts[i] if i < len(csts) else "")
                entry_cst.grid(row=i + 1, column=3, padx=10, pady=5, sticky="w")
                entry_cst_widgets.append(entry_cst)

                lb_cfop = tk.Label(frame_itens, text="CFOP:", font=('Arial', 10), bg='#c3ccdb')
                lb_cfop.grid(row=i + 1, column=4, padx=10, pady=5, sticky="w")

                entry_cfop = tk.Entry(frame_itens, width=5, font=('Arial', 10))
                entry_cfop.insert(0, cfops[i].text if i < len(cfops) and cfops[i] is not None else "")
                entry_cfop.grid(row=i + 1, column=5, padx=10, pady=5, sticky="w")
                entry_cfop_widgets.append(entry_cfop)

                lb_ncm = tk.Label(frame_itens, text="NCM:", font=('Arial', 10), bg='#c3ccdb')
                lb_ncm.grid(row=i + 1, column=6, padx=10, pady=5, sticky="w")

                entry_ncm = tk.Entry(frame_itens, width=9, font=('Arial', 10))
                entry_ncm.insert(0, ncm[i] if i < len(ncm) else "N/A")
                entry_ncm.grid(row=i + 1, column=7, padx=10, pady=5, sticky="w")
                entry_ncm_widgets.append(entry_ncm)

                # Unidade de medida
                lb_un = tk.Label(frame_itens, text="UN:", font=('Arial', 10), bg='#c3ccdb')
                lb_un.grid(row=i + 1, column=8, padx=10, pady=5, sticky="w")

                entry_un = tk.Entry(frame_itens, width=5, font=('Arial', 10))
                entry_un.insert(0, unidades[i] if i < len(unidades) else "N/A")
                entry_un.grid(row=i + 1, column=9, padx=10, pady=5, sticky="w")
                entry_un_widgets.append(entry_un)
                
#                 # Label para o Grupo de Produto
#                 lb_grupo_produto = tk.Label(
#                     frame_itens,
#                     text="Grupo de Produto:",
#                     font=('Arial', 10, 'bold'),
#                     bg='#c3ccdb'  # Mesmo fundo do frame
#                 )
#                 lb_grupo_produto.place(x=530, y=10)  # Ajuste a posição conforme necessário

                
#                 # Combobox para selecionar o grupo de produto
#                 combo_grupo_produto = ttk.Combobox(
#                     frame_itens, 
#                     values=["Cereais", "Aves e Ovos","CONFRATENIZAÇÃO", "Material de Manutencao","Bebidas Alcoolicas", "Governanca","Maquinas e equipamentos"], 
#                     width=15, 
#                     font=('Arial', 10 )
#                 )
# #                 combo_grupo_produto.grid(row=0, column=9, padx=10, pady=5, sticky="w")  # Ao lado do label
#                 combo_grupo_produto.place(x=650, y=10)
#                 combo_grupo_produto.set("Cereais")  # Valor padrão
                 
                # Adicionando Label e Entry para Código dentro do loop
                lb_codigo = tk.Label(
                    frame_itens,
                    text="Código:",
                    font=('Arial', 10, 'bold'),
                    bg='#c3ccdb'  # Mesmo fundo do frame
                )
                lb_codigo.place(x=930, y=10)  # Ajuste a posição conforme necessário

                entry_codigo = tk.Entry(frame_itens, width=10, font=('Arial', 10))
                entry_codigo.grid(row=i + 1, column=10, padx=10, pady=5, sticky="w")  # Use grid aqui
                
                entry_codigo_widgets.append(entry_codigo)



                
                
                btn_cadastrar_item = tk.Button(
                    frame_itens,
                    text=f"Cadastrar Item  {i + 1}",
                    font=('Arial', 10),
                    command=lambda item_id=i + 1, 
                                  ncm=entry_ncm_widgets[i], 
                                  entry_un=entry_un_widgets[i], 
                                  entry_codigo=entry_codigo_widgets[i], 
                                  entry_item=entry_produto: 
                                  cadastrar_item(
                                      item_id=item_id,
                                      ncm=ncm.get(),  # Pegue o valor no momento da execução
                                      combo_grupo_produto=combo_grupo_produto.get(),  # Pegue o valor dinâmico no momento da execução
                                      entry_un=entry_un,
                                      codigo=entry_codigo.get(),  # Pegue o valor do campo de código
                                      item=entry_item.get(),  # Pegue o valor do item
                                      grupos_especiais=grupos_especiais, # Passando grupos especiais
                                      checar_interrupcao_callback=checar_interrupcao # Passando callback de interrupção
                                  )
                )
                btn_cadastrar_item.grid(row=i + 1, column=11, padx=10, pady=5, sticky="w")
                
                               

                
#                 btn_relacionar = tk.Button(
#                     frame_itens,
#                     text=f"Relacionar {i + 1}",
#                     font=('Arial', 10, 'bold'),
#                     bg='green',  # Cor de fundo verde
#                     fg='white',  # Texto branco
#                     command=lambda item_id=i + 1: relacionar(
#                         item_id,
#                         entry_codigo_widgets[i].get(),  # Pega o valor dinâmico do campo no momento do clique
#                         entry_un_widgets[i].get()       # Pega o valor dinâmico do campo no momento do clique
#                     )
#                 )
                
                
                btn_relacionar = tk.Button(
                    frame_itens,
                    text=f"Relacionar {i + 1}",
                    font=('Arial', 10, 'bold'),
                    bg='green',  # Cor de fundo verde
                    fg='white',  # Texto branco
                    command=lambda item_id=i + 1, 
                                  entry_codigo=entry_codigo_widgets[i], 
                                  entry_un=entry_un_widgets[i]: 
                                  relacionar(
                                      item_id,
                                      entry_codigo.get(),  # Obtenha o valor no momento do clique
                                      entry_un.get()       # Obtenha o valor no momento do clique
                                  )
                )
                
                
                btn_relacionar.grid(row=i + 1, column=12, padx=10, pady=5, sticky="w")

        else:
            messagebox.showerror("Erro", "Produtos não encontrados no XML.")

        # Atualizar o scrollregion para incluir todos os widgets
        frame_itens.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
def filtrar_desembolso(event):
    """Filtra os itens do combobox com base no que foi digitado."""
    digitado = combo_desembolso.get().lower()  # Obtém o texto digitado e converte para minúsculas
    lista_filtrada = [item for item in desembolso_opcoes if digitado in item.lower()]  # Filtra a lista

    combo_desembolso['values'] = lista_filtrada  # Atualiza os valores exibidos no combobox    
    
    
def filtrar_grupo_produto(event):
    """Filtra os itens do combobox de grupo de produto com base no que foi digitado."""
    digitado = combo_grupo_produto.get().lower()  # Obtém o texto digitado e converte para minúsculas
    lista_filtrada = [item for item in grupo_produto_opcoes if digitado in item.lower()]  # Filtra a lista

    combo_grupo_produto['values'] = lista_filtrada  # Atualiza os valores exibidos no combobox
        
            
# Configuração da janela principal
root = tk.Tk()
root.title("Leitor de XML de NF v3.0 290525")
root.geometry("1300x700")

# --- MENU BAR ---
menubar = tk.Menu(root)
root.config(menu=menubar)

# Menu Cadastros
menu_cadastros = tk.Menu(menubar, tearoff=0)
menu_cadastros.add_command(label="Gerenciar Desembolsos", command=clique_gerenciar_desembolso)
menu_cadastros.add_command(label="Gerenciar Grupos de Produto", command=clique_gerenciar_grupo)
menubar.add_cascade(label="Cadastros", menu=menu_cadastros)
# ----------------



# Frame para entrada do caminho do arquivo
frame_caminho = tk.Frame(root, bg='#c3ccdb')
frame_caminho.pack(fill=tk.X, padx=10, pady=5)  # O próprio frame ainda pode usar `pack`

lb_caminho = tk.Label(frame_caminho, text="Caminho do arquivo:", font=('Arial', 10), bg='#c3ccdb')
lb_caminho.grid(row=0, column=0, padx=5, pady=5, sticky="w")  # Alinhado à esquerda

entry_caminho = tk.Entry(frame_caminho, width=50, font=('Arial', 10))
entry_caminho.grid(row=0, column=1, padx=5, pady=5)

btn_abrir = tk.Button(frame_caminho, text="Abrir", command=abrir_arquivo)
btn_abrir.grid(row=0, column=2, padx=5, pady=5)

# btn_verificar = tk.Button(frame_caminho, text="Verificar Itens", command=verificar_itens)
btn_verificar = tk.Button(frame_caminho, text="Verificar Itens", command=lambda: verificar_itens(entry_ncm_widgets, combo_desembolso, entry_cfop_widgets, entry_cst_widgets, checar_interrupcao, clicar_rateio))
btn_verificar.grid(row=0, column=3, padx=5, pady=5)



# Adicionando o botão "Limpar Tela" ao frame de controle
btn_limpar = tk.Button(frame_caminho, text="Limpar Tela", command=limpar_tela)
btn_limpar.grid(row=0, column=4, padx=5, pady=5)

i = 0  # Defina o valor inicial de i
btn_alterar_desembolso = tk.Button(frame_caminho, text="Alterar desembolso", command=lambda i=i: alterar_desembolso(i))
btn_alterar_desembolso.grid(row=0, column=5, padx=5, pady=5)


# btn_verificar = tk.Button(frame_caminho, text="Verificar Itens", command=verificar_itens)
btn_verificar_simples = tk.Button(frame_caminho, text="Verificar Itens simples", command=lambda: verificar_itens_simples(entry_ncm_widgets, combo_desembolso, entry_cfop_widgets, entry_cst_widgets, checar_interrupcao, clicar_rateio))
btn_verificar_simples.grid(row=0, column=6, padx=5, pady=5)

# btn_verificar = tk.Button(frame_caminho, text="Verificar Itens", command=verificar_itens)
btn_verificar_pis_cofins = tk.Button(frame_caminho, text="Verificar KMR,KJP,HPB,KPL",bg='yellow',activebackground='red', command=lambda: verificar_itens_pis_cofins(entry_ncm_widgets))
btn_verificar_pis_cofins.grid(row=0, column=7, padx=5, pady=5)


# Novo Label "Desembolso" e Combobox para selecionar "Restaurante" ou "Café da manhã"
lb_desembolso = tk.Label(frame_caminho, text="Desembolso:", font=('Arial', 10), bg='#c3ccdb')
lb_desembolso.grid(row=1, column=0, padx=5, pady=5, sticky="w")  # Coloca na linha abaixo do caminho do arquivo



lb_empresa = tk.Label(frame_caminho, text='Empresa:', font=('Arial', 10), bg='#c3ccdb')
lb_empresa.place(x=400, y=40)

lb_nf = tk.Label(frame_caminho, text='NF:', font=('Arial', 10), bg='#c3ccdb')
lb_nf.place(x=300, y=40)



# combo_desembolso = ttk.Combobox(frame_caminho, values=["Restaurante", "Cafe da Manha","Confraternizacao","Reposicao de Materiais","Material de Manutencao", "Limpeza/Higiene/Uso e Consumo", "Material de Escritorio"], width=20, font=('Arial', 10))
# combo_desembolso.place(x=100, y=40)#.grid(row=1, column=1, padx=5, pady=5)  # Ao lado do label "Desembolso"
# combo_desembolso.set("Cafe da Manha")  # Definir valor inicial como "Restaurante"

# Ordena automaticamente os itens do combobox
# Ordena automaticamente os itens do combobox
desembolso_opcoes = desembolsos_lista

combo_desembolso = ttk.Combobox(
    frame_caminho, 
    values=sorted(desembolso_opcoes),  # Ordena a lista automaticamente
    width=25, 
    font=('Arial', 10)
)

combo_desembolso.place(x=100, y=40)
combo_desembolso.set(sorted(desembolso_opcoes)[0])  # Define o primeiro item da lista ordenada como padrão

# Associa a função de filtragem ao evento de digitação no combobox
combo_desembolso.set(sorted(desembolso_opcoes)[0])  # Define o primeiro item da lista ordenada como padrão

# Associa a função de filtragem ao evento de digitação no combobox
combo_desembolso.bind("<KeyRelease>", filtrar_desembolso)

# Botão (+) removido - agora no Menu

lb_grupo_produto = tk.Label(frame_caminho, text='Grupo de Produto:', font=('Arial', 10,'bold'), bg='#c3ccdb')
lb_grupo_produto.place(x=800, y=40)

# # Combobox para selecionar o grupo de produto
# combo_grupo_produto = ttk.Combobox(
#                     frame_caminho, 
#                     values=["Beb. Ñ Alcool","Cereais", "Aves e Ovos","CONFRATENIZAÇÃO", "Material de Manutencao","Bebidas Alcoolicas", "Governanca","Maquinas e equipamentos", "Restaurante (Uso e consumo)"], 
#                     width=15, 
#                     font=('Arial', 10 ))
# combo_grupo_produto.place(x=930, y=40)
# combo_grupo_produto.set("Cereais")  # Valor padrão    

#########################################################################################################atual

# # Lista de opções do Grupo de Produto (não ordenada manualmente)
# grupo_produto_opcoes = [
#     "Beb. Ñ Alcool", "Cereais e Sacarias", "Aves e Ovos", "CONFRATENIZAÇÃO", 
#     "Material de Manutencao", "Bebidas Alcoolicas", "Governanca", 
#     "Maquinas e equipamentos", "Restaurante (Uso e consumo)","20(NAO USAR) Diversos (icms)",
#     "40(nao usar)","60*Diversos (NAO USAR)", "Carnes", "Cervejas", "Chocolate e doces", "comodato", "Moveis e utensilios",
#     "Mat. De Cozinha e Loucas", "Frios e Laticinios","Material de Escritorio","Massas", "Paes, Biscoitos"
# ]

# # Ordenando a lista alfabeticamente
# grupo_produto_opcoes.sort()

# # Criando o Combobox
# combo_grupo_produto = ttk.Combobox(
#     frame_caminho, 
#     values=sorted(grupo_produto_opcoes),  # Ordena automaticamente
#     width=30, 
#     font=('Arial', 10)
# )
# combo_grupo_produto.place(x=930, y=40)
# #combo_grupo_produto.set(sorted(grupo_produto_opcoes)[0])  # Define o primeiro item como padrão
# combo_grupo_produto.set('')  # Define o primeiro item como padrão

# # Associa a função de filtragem ao evento de digitação no combobox
# combo_grupo_produto.bind("<KeyRelease>", filtrar_grupo_produto)
# Lista de opções do Grupo de Produto (carregada do JSON)
grupo_produto_opcoes = grupos_produtos

# Ordenando a lista alfabeticamente ignorando maiúsculas e minúsculas
grupo_produto_opcoes.sort(key=str.casefold)

# Criando o Combobox
combo_grupo_produto = ttk.Combobox(
    frame_caminho, 
    values=grupo_produto_opcoes,  # Lista já ordenada
    width=30, 
    font=('Arial', 10)
)

combo_grupo_produto.place(x=930, y=40)

# Define o primeiro item como padrão ou deixa em branco
combo_grupo_produto.set('')  # Para iniciar sem seleção

# Associa a função de filtragem ao evento de digitação no combobox
combo_grupo_produto.bind("<KeyRelease>", filtrar_grupo_produto)

# Botão (+) removido - agora no Menu



# Canvas e scrollbar para os itens
frame_canvas = tk.Frame(root)
frame_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

canvas = tk.Canvas(frame_canvas, bg='#c3ccdb')
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame_canvas, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas.configure(yscrollcommand=scrollbar.set)

frame_itens = tk.Frame(canvas, bg='#c3ccdb')
canvas.create_window((0, 0), window=frame_itens, anchor="nw")

def _on_mousewheel(event):
    if canvas.yview() != (0.0, 1.0):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)


# Frame para o rodapé
frame_footer = tk.Frame(root, bg='#c3ccdb')
frame_footer.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

# Copyright e informações do app
lb_copyright = tk.Label(
    frame_footer, 
    text="© 2025 Gibasanapp - Telefone: 81 988877159", 
    font=('Arial', 10), 
    bg='#c3ccdb', 
    fg='black'
)
lb_copyright.pack()


root.mainloop()
