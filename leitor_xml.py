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
from verificacao.verificacao_itens_simples import verificar_itens_simples
from verificacao.verificacao_itens_pis_cofins import verificar_itens_pis_cofins_regras

# --- Importação de Estilos (Fase 5 - Light) ---
from core import estilos
from verificacao.verificacao_itens import verificar_itens
from cadastro_item import cadastrar_item
from relacionar_item import relacionar
from core.utils import resource_path, get_config_path
from core import updater
from core.version import VERSION

# Carregar grupos do JSON
def carregar_grupos():
    # Tenta carregar do arquivo do usuário (editável)
    caminho_user = get_config_path("json_files/grupos.json")
    if os.path.exists(caminho_user):
        caminho_json = caminho_user
    else:
        # Se não existir, pega o padrão embutido
        caminho_json = resource_path("json_files/grupos.json")

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
    # Tenta carregar do arquivo do usuário (editável)
    caminho_user = get_config_path("json_files/desembolsos.json")
    if os.path.exists(caminho_user):
        caminho_json = caminho_user
    else:
        # Se não existir, pega o padrão embutido
        caminho_json = resource_path("json_files/desembolsos.json")
        
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
    # Usa nome base para garantir que pegamos o caminho persistente
    arquivo_persistente = get_config_path(os.path.basename(arquivo))

    try:
        # Tenta ler o arquivo existente para preservar outros dados
        if os.path.exists(arquivo_persistente):
            with open(arquivo_persistente, "r", encoding="utf-8") as f:
                dados = json.load(f)
        else:
             # Se não existir persistente, tenta ler do bundle pra usar de base (opcional)
             # ou começa vazio. Vamos começar vazio ou com o que tem.
             dados = {}
        
        # Atualiza a lista e salva
        lista.sort(key=str.casefold)
        dados[chave_lista] = lista
        
        with open(arquivo_persistente, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
            
        return True
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar no '{arquivo_persistente}': {e}")
        return False

# Função para salvar grupos e grupos especiais
def salvar_grupos_json(lista_grupos, lista_especiais):
    arquivo = get_config_path("json_files/grupos.json")
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

# --- FUNÇÕES PARA CONVERSÃO DE UNIDADES (FASE 4) ---
def carregar_unidades_conversao():
    # 1. Tentar ler do arquivo do usuário (configuração persistente)
    caminho_user = get_config_path("json_files/conversao_unidades.json")
    if os.path.exists(caminho_user):
        try:
            with open(caminho_user, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao ler config do usuário: {e}")

    # 2. Tentar ler do bundle (padrão embutido no EXE)
    caminho_bundle = resource_path("json_files/conversao_unidades.json")
    if os.path.exists(caminho_bundle):
        try:
            with open(caminho_bundle, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # 3. Fallback: Retorna dicionário padrão hardcoded
    dados_padrao = {
        "UN": ["Unid", "BD1", "PO1", "DIS", "un", "UN1", "UND", "UNID", "PC1", "TP1", 
                "EM1", "BR1", "LT1", "PE1", "PCT", "RESMA", "CADA", "ROLO", "BI1", 
                "UNIDAD", "Un***", "Un**", "PA"],
        "CX": ["CX1", "CX12", "DP1"],
        "PC": ["PCA", "Pt**", "PACOTE", "PT1", "PECA", "Pte", "PT", "PAC"],
        "KG": ["KG1", "Kg***"],
        "MT": ["METRO"],
        "FD": ["FD10"]
    }
    # Opcional: Criar o arquivo do usuário com o padrão para facilitar edição?
    # Vamos criar para garantir que o usuário veja o arquivo.
    try:
        with open(caminho_user, "w", encoding="utf-8") as f:
            json.dump(dados_padrao, f, indent=4, ensure_ascii=False)
    except Exception:
        pass
        
    return dados_padrao

def salvar_unidades_conversao(dados):
    # Sempre salvar no caminho do usuário (persistente)
    caminho_json = get_config_path("json_files/conversao_unidades.json")
    try:
        with open(caminho_json, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar '{caminho_json}': {e}")
        return False

def abrir_gerenciador_unidades():
    janela = tk.Toplevel()
    janela.title("Gerenciar Conversão de Unidades")
    janela.geometry("600x500")
    
    dados = carregar_unidades_conversao()
    
    # --- Layout Principal: Dois Paineis (Esquerda: Grupos/Destino, Direita: XML/Origem) ---
    frame_esq = tk.LabelFrame(janela, text="Unidade Destino (Sistema)", padx=5, pady=5)
    frame_esq.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    
    frame_dir = tk.LabelFrame(janela, text="Códigos XML (Origem)", padx=5, pady=5)
    frame_dir.pack(side="right", fill="both", expand=True, padx=5, pady=5)
    
    # --- Lista Esquerda (Chaves) ---
    frame_lista_esq = tk.Frame(frame_esq)
    frame_lista_esq.pack(fill="both", expand=True)

    scrollbar_esq = tk.Scrollbar(frame_lista_esq, orient="vertical")
    listbox_unidades = tk.Listbox(frame_lista_esq, yscrollcommand=scrollbar_esq.set, exportselection=False)
    scrollbar_esq.config(command=listbox_unidades.yview)
    
    scrollbar_esq.pack(side="right", fill="y")
    listbox_unidades.pack(side="left", fill="both", expand=True)
    
    entry_nova_unidade = tk.Entry(frame_esq)
    entry_nova_unidade.pack(fill="x", pady=5)
    
    def atualizar_lista_unidades():
        listbox_unidades.delete(0, tk.END)
        for un in sorted(dados.keys()):
            listbox_unidades.insert(tk.END, un)
            
    def adicionar_unidade():
        nova = entry_nova_unidade.get().strip().upper()
        if nova and nova not in dados:
            dados[nova] = []
            salvar_unidades_conversao(dados)
            atualizar_lista_unidades()
            entry_nova_unidade.delete(0, tk.END)
        elif nova in dados:
            messagebox.showwarning("Aviso", "Unidade já existe!", parent=janela)
            
    def remover_unidade():
        sel = listbox_unidades.curselection()
        if not sel: return
        un = listbox_unidades.get(sel[0])
        if messagebox.askyesno("Confirmar", f"Remover unidade '{un}' e todos os seus mapeamentos?", parent=janela):
            del dados[un]
            salvar_unidades_conversao(dados)
            atualizar_lista_unidades()
            listbox_xml.delete(0, tk.END)
            
    tk.Button(frame_esq, text="Adicionar Unidade", command=adicionar_unidade).pack(fill="x")
    tk.Button(frame_esq, text="Remover Selecionada", command=remover_unidade, bg="#ffcccc").pack(fill="x")
    
    # --- Lista Direita (Valores) ---
    frame_lista_dir = tk.Frame(frame_dir)
    frame_lista_dir.pack(fill="both", expand=True)

    scrollbar_dir = tk.Scrollbar(frame_lista_dir, orient="vertical")
    listbox_xml = tk.Listbox(frame_lista_dir, yscrollcommand=scrollbar_dir.set, exportselection=False)
    scrollbar_dir.config(command=listbox_xml.yview)
    
    scrollbar_dir.pack(side="right", fill="y")
    listbox_xml.pack(side="left", fill="both", expand=True)
    
    entry_novo_xml = tk.Entry(frame_dir)
    entry_novo_xml.pack(fill="x", pady=5)
    
    def on_unidade_select(event):
        sel = listbox_unidades.curselection()
        if not sel: return
        un = listbox_unidades.get(sel[0])
        
        listbox_xml.delete(0, tk.END)
        if un in dados:
            for xml_code in sorted(dados[un], key=str.casefold):
                listbox_xml.insert(tk.END, xml_code)
                
    listbox_unidades.bind("<<ListboxSelect>>", on_unidade_select)
    
    def adicionar_xml():
        sel = listbox_unidades.curselection()
        if not sel: 
            messagebox.showwarning("Aviso", "Selecione uma Unidade Destino primeiro.", parent=janela)
            return
        un = listbox_unidades.get(sel[0])
        novo_xml = entry_novo_xml.get().strip()
        
        if novo_xml:
            # Verifica duplicidade em TODO o dicionário (evitar ambiguidade) forçada?
            # Ou permite? Melhor permitir, mas avisar. O sistema pega a primeira que achar?
            # A lógica de conversão vai buscar chave por chave. Se tiver duplicado, a ordem do dict define (py3.7+ insertion order).
            # Mas idealmente deve ser único.
            for k, v in dados.items():
                if novo_xml in v and k != un:
                    if not messagebox.askyesno("Duplicidade", f"O código '{novo_xml}' já está mapeado em '{k}'. Deseja adicionar em '{un}' também? (Pode causar ambiguidade)", parent=janela):
                        return
            
            if novo_xml not in dados[un]:
                dados[un].append(novo_xml)
                salvar_unidades_conversao(dados)
                # Refresh listbox logic (re-trigger select or manual insert)
                listbox_xml.insert(tk.END, novo_xml)
                entry_novo_xml.delete(0, tk.END)
                
    def remover_xml():
        sel_u = listbox_unidades.curselection()
        sel_x = listbox_xml.curselection()
        if not sel_u or not sel_x: return
        
        un = listbox_unidades.get(sel_u[0])
        xml_code = listbox_xml.get(sel_x[0])
        
        if xml_code in dados[un]:
            if not messagebox.askyesno("Confirmar", f"Remover código '{xml_code}' da unidade '{un}'?", parent=janela):
                return
            dados[un].remove(xml_code)

            salvar_unidades_conversao(dados)
            listbox_xml.delete(sel_x[0])
            
    tk.Button(frame_dir, text="Adicionar Código XML", command=adicionar_xml).pack(fill="x")
    tk.Button(frame_dir, text="Remover Selecionado", command=remover_xml, bg="#ffcccc").pack(fill="x")
    
    atualizar_lista_unidades()



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

# --- Editor de Regras Fiscais ---
def abrir_editor_regras(perfil_alvo="verificacao_padrao"):
    caminho_json = "json_files/regras_fiscais.json"
    
    def carregar_dados():
        if not os.path.exists(caminho_json):
            return {}
        try:
            with open(caminho_json, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def salvar_dados(dados):
        try:
            with open(caminho_json, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar regras: {e}")
            return False

    def abrir_janela_regra(dados_completos, indice_editar=None):
        janela_regra = tk.Toplevel()
        janela_regra.title("Editar Regra" if indice_editar is not None else "Nova Regra")
        janela_regra.geometry("500x600")

        regras_perfil = dados_completos.get(perfil_alvo, [])
        regra_atual = regras_perfil[indice_editar] if indice_editar is not None else {"entrada": {"cfop": [], "cst": []}, "saida": {}}

        # --- Entradas ---
        frame_entrada = tk.LabelFrame(janela_regra, text="SE a Nota Fiscal tiver (Entrada):", padx=5, pady=5)
        frame_entrada.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_entrada, text="CFOPs (separar por vírgula):").pack(anchor="w")
        entry_cfop_in = tk.Entry(frame_entrada)
        entry_cfop_in.pack(fill="x")
        entry_cfop_in.insert(0, ", ".join(regra_atual.get("entrada", {}).get("cfop", [])))

        tk.Label(frame_entrada, text="CSTs (separar por vírgula):").pack(anchor="w")
        entry_cst_in = tk.Entry(frame_entrada)
        entry_cst_in.pack(fill="x")
        entry_cst_in.insert(0, ", ".join(regra_atual.get("entrada", {}).get("cst", [])))

        # --- Saídas ---
        # --- Saídas ---
        frame_saida = tk.LabelFrame(janela_regra, text="ENTÃO o Robô deve preencher (Saída):", padx=5, pady=5)
        frame_saida.pack(fill="x", padx=10, pady=5)

        # --- Frame Principal da Saída (para organizar Grid vs Templates) ---
        frame_campos_saida = tk.Frame(frame_saida)
        frame_campos_saida.pack(side="left", fill="both", expand=True)

        tk.Label(frame_campos_saida, text="CFOP Saída:").grid(row=0, column=0, sticky="w")
        entry_cfop_out = tk.Entry(frame_campos_saida)
        entry_cfop_out.grid(row=0, column=1, sticky="e")
        entry_cfop_out.insert(0, regra_atual.get("saida", {}).get("cfop", ""))

        tk.Label(frame_campos_saida, text="CST Saída:").grid(row=1, column=0, sticky="w")
        entry_cst_out = tk.Entry(frame_campos_saida)
        entry_cst_out.grid(row=1, column=1, sticky="e")
        entry_cst_out.insert(0, regra_atual.get("saida", {}).get("cst", ""))

        tk.Label(frame_campos_saida, text="PIS:").grid(row=2, column=0, sticky="w")
        entry_pis = tk.Entry(frame_campos_saida)
        entry_pis.grid(row=2, column=1, sticky="e")
        entry_pis.insert(0, regra_atual.get("saida", {}).get("pis", ""))

        tk.Label(frame_campos_saida, text="COFINS:").grid(row=3, column=0, sticky="w")
        entry_cofins = tk.Entry(frame_campos_saida)
        entry_cofins.grid(row=3, column=1, sticky="e")
        entry_cofins.insert(0, regra_atual.get("saida", {}).get("cofins", ""))

        tk.Label(frame_campos_saida, text="IPI:").grid(row=4, column=0, sticky="w")
        entry_ipi = tk.Entry(frame_campos_saida)
        entry_ipi.grid(row=4, column=1, sticky="e")
        entry_ipi.insert(0, regra_atual.get("saida", {}).get("ipi", ""))

        # Checkboxes para Isento/Integral
        var_isento = tk.BooleanVar(value=regra_atual.get("saida", {}).get("clicar_isento", False))
        tk.Checkbutton(frame_campos_saida, text="Clicar ISENTO", variable=var_isento).grid(row=5, column=0, columnspan=2, sticky="w")

        var_integral = tk.BooleanVar(value=regra_atual.get("saida", {}).get("clicar_integral", False))
        tk.Checkbutton(frame_campos_saida, text="Clicar INTEGRAL", variable=var_integral).grid(row=6, column=0, columnspan=2, sticky="w")
        
        # --- Templates (Botões Rápidos) ---
        frame_templates = tk.Frame(frame_saida, padx=10, borderwidth=1, relief="sunken")
        frame_templates.pack(side="right", fill="y", padx=5, pady=5)
        
        tk.Label(frame_templates, text="Modelos Rápidos:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(0,5))

        def aplicar_template(pis, cofins, ipi, isento, integral):
            entry_pis.delete(0, tk.END); entry_pis.insert(0, pis)
            entry_cofins.delete(0, tk.END); entry_cofins.insert(0, cofins)
            entry_ipi.delete(0, tk.END); entry_ipi.insert(0, ipi)
            var_isento.set(isento)
            var_integral.set(integral)

        tk.Button(frame_templates, text="ISENTO (73/73/49)", 
                  command=lambda: aplicar_template("73", "73", "49", True, False), 
                  bg="#e1f5fe", width=20, anchor="w").pack(fill="x", pady=2)
                  
        tk.Button(frame_templates, text="INTEGRAL (50/50/49)", 
                  command=lambda: aplicar_template("50", "50", "49", False, True), 
                  bg="#e8f5e9", width=20, anchor="w").pack(fill="x", pady=2)
                  
        tk.Button(frame_templates, text="USO/CONS (98/98/49)", 
                  command=lambda: aplicar_template("98", "98", "49", True, False), 
                  bg="#fff9c4", width=20, anchor="w").pack(fill="x", pady=2)

        tk.Label(frame_templates, text="(Preenche campos automaticamente)", font=("Arial", 7)).pack(pady=5)
        
        def salvar_regra():
            # Processar Entradas
            cfops_in = [x.strip() for x in entry_cfop_in.get().split(",") if x.strip()]
            csts_in = [x.strip() for x in entry_cst_in.get().split(",") if x.strip()]
            
            # Processar Saídas
            nova_saida = {
                "cfop": entry_cfop_out.get().strip(),
                "cst": entry_cst_out.get().strip(),
                "pis": entry_pis.get().strip(),
                "cofins": entry_cofins.get().strip(),
                "ipi": entry_ipi.get().strip(),
                "clicar_isento": var_isento.get(),
                "clicar_integral": var_integral.get()
            }
            
            # Processar Entradas
            nova_entrada = {
                "cfop": cfops_in, 
                "cst": csts_in
            }
                
            nova_regra = {
                "entrada": nova_entrada,
                "saida": nova_saida
            }

            if indice_editar is not None:
                regras_perfil[indice_editar] = nova_regra
            else:
                regras_perfil.append(nova_regra)
            
            # Atualiza no dicionário principal e salva
            dados_completos[perfil_alvo] = regras_perfil
            if salvar_dados(dados_completos):
                janela_regra.destroy()
                atualizar_lista() # Atualiza a janela anterior

        tk.Button(janela_regra, text="Salvar Regra", command=salvar_regra, bg="green", fg="white").pack(pady=20)


    janela = tk.Toplevel()
    janela.title(f"Editor de Regras - {perfil_alvo}")
    janela.geometry("900x500") # Janela maior para caber a tabela

    # Frame para a tabela
    frame_lista = tk.Frame(janela)
    frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

    # Configuração da Treeview
    # Configuração da Treeview
    colunas = ("entrada", "saida")
    tree = ttk.Treeview(frame_lista, columns=colunas, show="headings", selectmode="browse")
    
    tree.heading("entrada", text="Condições de Entrada (CFOP / CST)")
    tree.heading("saida", text="Ação de Saída")
    
    tree.column("entrada", minwidth=300, width=400)
    tree.column("saida", minwidth=250, width=300)

    scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    dados = carregar_dados()
    
    def atualizar_lista():
        # Limpa tabela
        for item in tree.get_children():
            tree.delete(item)
            
        regras = dados.get(perfil_alvo, [])
        regras = dados.get(perfil_alvo, [])
        for i, r in enumerate(regras):
            cfops = ", ".join(r.get("entrada", {}).get("cfop", []))
            csts = ", ".join(r.get("entrada", {}).get("cst", []))
            entrada_str = f"CFOP: [{cfops}]  |  CST: [{csts}]"
            
            s = r.get("saida", {})
            # Detalhes da saída
            detalhes = []
            if s.get("cfop"): detalhes.append(f"CFOP {s['cfop']}")
            if s.get("cst"): detalhes.append(f"CST {s['cst']}")
            if s.get("pis"): detalhes.append(f"PIS {s['pis']}")
            
            saida_str = " / ".join(detalhes)
            
            # Usa o índice 'i' como ID para facilitar edição/removação
            tree.insert("", "end", iid=str(i), values=(entrada_str, saida_str))

    atualizar_lista()

    frame_btns = tk.Frame(janela)
    frame_btns.pack(pady=5)

    def nova():
        abrir_janela_regra(dados)
    
    def editar():
        sel = tree.selection()
        if not sel: return
        idx = int(sel[0]) # Recupera o ID (que é o índice)
        abrir_janela_regra(dados, idx)

    def remover():
        sel = tree.selection()
        if not sel: return
        idx = int(sel[0])
        if messagebox.askyesno("Confirmar", "Remover regra selecionada?"):
            regras = dados.get(perfil_alvo, [])
            del regras[idx]
            dados[perfil_alvo] = regras
            salvar_dados(dados)
            atualizar_lista()

    tk.Button(frame_btns, text="Nova Regra", command=nova, bg="#90ee90").pack(side="left", padx=5)
    tk.Button(frame_btns, text="Editar Regra", command=editar, bg="#add8e6").pack(side="left", padx=5)
    tk.Button(frame_btns, text="Remover Regra", command=remover, bg="#ffcccb").pack(side="left", padx=5)

def clique_gerenciar_desembolso():
    abrir_gerenciador("Gerenciar Desembolsos", "json_files/desembolsos.json", "desembolsos", combo_desembolso)

def carregar_config():
    caminho_config = get_config_path("json_files/config.json")
    if not os.path.exists(caminho_config):
        return {"velocidade": 0.2} # Valor padrão
    try:
        with open(caminho_config, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"velocidade": 0.2}

def salvar_config(dados):
    caminho_config = get_config_path("json_files/config.json")
    try:
        with open(caminho_config, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar config: {e}")

def clique_gerenciar_grupo():
    abrir_gerenciador("Gerenciar Grupos de Produto", "json_files/grupos.json", "grupos", combo_grupo_produto)

def abrir_ajuste_velocidade():
    janela = tk.Toplevel()
    janela.title("Ajuste de Velocidade")
    janela.geometry("300x150")
    estilos.aplicar_tema_janela(janela)

    tk.Label(janela, text="Ajuste a velocidade da automação:", font=("Arial", 10)).pack(pady=10)
    
    # Slider vinculado à variábel global var_velocidade
    scale = tk.Scale(janela, from_=0.2, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, length=200, variable=var_velocidade)
    scale.pack(pady=10)
    
    def fechar_e_salvar():
        # Salva a configuração ao fechar
        dados = {"velocidade": var_velocidade.get()}
        salvar_config(dados)
        janela.destroy()

    tk.Button(janela, text="OK", command=fechar_e_salvar, width=10, bg="#90ee90").pack(pady=5)

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
        localizacao = py.locateOnScreen(resource_path('images/seta.png'), confidence=0.8)
        if localizacao:
            centro = py.center(localizacao)
            py.click(centro, clicks=2)
            time.sleep(1)
            if checar_interrupcao():
                return
        rateio = py.locateOnScreen(resource_path('images/rateio.png'), confidence=0.8)
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
        confirmar = py.locateOnScreen(resource_path('images/confirmar2.png'), confidence=0.8)
        if confirmar:
            confirmar_centro = py.center(confirmar)
            py.click(confirmar_centro) 
            time.sleep(1)
            if checar_interrupcao():
                return
        localizacao = py.locateOnScreen(resource_path('images/seta.png'), confidence=0.8)
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
    rateio = py.locateOnScreen(resource_path('images/rateio.png'), confidence=0.8)
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
        
        # --- Lógica Dinâmica de Unidades (Fase 4) ---
        mapa_unidades = carregar_unidades_conversao()
        
        unidades = []
        for prod in root.findall('.//ns:det/ns:prod', namespace):
            ucom_element = prod.find('ns:uCom', namespace)
            if ucom_element is not None:
                ucom = ucom_element.text.strip() if ucom_element.text else ""
                unidade_convertida = ucom # Valor padrão é o próprio ucom
                
                # Procura em todos os grupos mapeados
                for unidade_destino, lista_origem in mapa_unidades.items():
                    # Case insensitive check
                    if any(origem.lower() == ucom.lower() for origem in lista_origem):
                        unidade_convertida = unidade_destino
                        break
                
                unidades.append(unidade_convertida)
            else:
                unidades.append("N/A")

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
        global vars_uso_consumo
        vars_uso_consumo = [] # Lista para armazenar as variaveis dos checkboxes
        if produtos:
            for i, produto in enumerate(produtos):
                # Labels e entradas para cada item
                lb_item = tk.Label(frame_itens, text=f"ITEM {i + 1}:")
                estilos.estilizar_label(lb_item, destaque=True)
                lb_item.grid(row=i + 1, column=0, padx=10, pady=5, sticky="w")

                entry_produto = tk.Entry(frame_itens, width=45, font=('Arial', 10))
                entry_produto.insert(0, produto)
                entry_produto.grid(row=i + 1, column=1, padx=20, pady=5, sticky="w")

                lb_cst = tk.Label(frame_itens, text="CST:")
                estilos.estilizar_label(lb_cst)
                lb_cst.grid(row=i + 1, column=2, padx=10, pady=5, sticky="w")
    
                entry_cst = tk.Entry(frame_itens, width=4, font=('Arial', 10))
                entry_cst.insert(0, csts[i] if i < len(csts) else "")
                entry_cst.grid(row=i + 1, column=3, padx=10, pady=5, sticky="w")
                entry_cst_widgets.append(entry_cst)

                lb_cfop = tk.Label(frame_itens, text="CFOP:")
                estilos.estilizar_label(lb_cfop)
                lb_cfop.grid(row=i + 1, column=4, padx=10, pady=5, sticky="w")

                entry_cfop = tk.Entry(frame_itens, width=5, font=('Arial', 10))
                entry_cfop.insert(0, cfops[i].text if i < len(cfops) and cfops[i] is not None else "")
                entry_cfop.grid(row=i + 1, column=5, padx=10, pady=5, sticky="w")
                entry_cfop_widgets.append(entry_cfop)

                # Checkbox Uso/Consumo
                var_uso = tk.BooleanVar()
                chk_uso = tk.Checkbutton(frame_itens, text="Uso", variable=var_uso, bg='#c3ccdb') 
                chk_uso.grid(row=i + 1, column=6, padx=2, pady=5, sticky="w")
                vars_uso_consumo.append(var_uso)

                lb_ncm = tk.Label(frame_itens, text="NCM:")
                estilos.estilizar_label(lb_ncm)
                lb_ncm.grid(row=i + 1, column=7, padx=10, pady=5, sticky="w")

                entry_ncm = tk.Entry(frame_itens, width=9, font=('Arial', 10))
                entry_ncm.insert(0, ncm[i] if i < len(ncm) else "N/A")
                entry_ncm.grid(row=i + 1, column=8, padx=10, pady=5, sticky="w")
                entry_ncm_widgets.append(entry_ncm)

                # Unidade de medida
                lb_un = tk.Label(frame_itens, text="UN:")
                estilos.estilizar_label(lb_un)
                lb_un.grid(row=i + 1, column=9, padx=10, pady=5, sticky="w")

                entry_un = tk.Entry(frame_itens, width=5, font=('Arial', 10))
                entry_un.insert(0, unidades[i] if i < len(unidades) else "N/A")
                entry_un.grid(row=i + 1, column=10, padx=10, pady=5, sticky="w")
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
                    text="Código:"
                )
                estilos.estilizar_label(lb_codigo, destaque=True)
                lb_codigo.place(x=930, y=10)  # Ajuste a posição conforme necessário

                entry_codigo = tk.Entry(frame_itens, width=10, font=('Arial', 10))
                entry_codigo.grid(row=i + 1, column=11, padx=10, pady=5, sticky="w")  # Use grid aqui
                
                entry_codigo_widgets.append(entry_codigo)



                
                
                btn_cadastrar_item = tk.Button(
                    frame_itens,
                    text=f"Cadastrar Item  {i + 1}",
                    width=16, # Tamanho fixo para padronizar
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
                estilos.estilizar_botao(btn_cadastrar_item, "acao")
                btn_cadastrar_item.grid(row=i + 1, column=12, padx=10, pady=5, sticky="w")
                
                               

                
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
                    width=14, # Tamanho fixo para padronizar
                    command=lambda item_id=i + 1, 
                                  entry_codigo=entry_codigo_widgets[i], 
                                  entry_un=entry_un_widgets[i]: 
                                  relacionar(
                                      item_id,
                                      entry_codigo.get(),  # Obtenha o valor no momento do clique
                                      entry_un.get()       # Obtenha o valor no momento do clique
                                  )
                )
                estilos.estilizar_botao(btn_relacionar, "neutro")
                
                
                btn_relacionar.grid(row=i + 1, column=13, padx=10, pady=5, sticky="w")

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

# Carregar configuração inicial
config_inicial = carregar_config()
velocidade_inicial = config_inicial.get("velocidade", 0.2)
var_velocidade = tk.DoubleVar(value=velocidade_inicial)

root.title(f"Leitor de XML de NF v{VERSION}")
root.geometry("1300x700")

# Iniciar verificação de atualizações (silenciosa)
updater.verificar_atualizacao_silenciosa()

# --- Ícone da Janela ---
try:
    root.iconbitmap(resource_path("images/icone.ico"))
except Exception as e:
    print(f"Erro ao carregar ícone: {e}")

# Aplica fundo
estilos.aplicar_tema_janela(root)

# --- MENU BAR ---
menubar = tk.Menu(root)
root.config(menu=menubar)

# Menu Cadastros
menu_cadastros = tk.Menu(menubar, tearoff=0)
menu_cadastros.add_command(label="Gerenciar Desembolsos", command=clique_gerenciar_desembolso)
menu_cadastros.add_command(label="Gerenciar Grupos de Produto", command=clique_gerenciar_grupo)
menu_cadastros.add_command(label="Gerenciar Conversão de Unidades", command=abrir_gerenciador_unidades)
menu_cadastros.add_separator()
menu_cadastros.add_command(label="Ajuste de Velocidade", command=abrir_ajuste_velocidade)

# Submenu Regras Fiscais
menu_regras = tk.Menu(menu_cadastros, tearoff=0)
menu_regras.add_command(label="Regras Verificar Itens", command=lambda: abrir_editor_regras("verificacao_padrao"))
menu_regras.add_command(label="Regras Verificar Itens Simples", command=lambda: abrir_editor_regras("verificacao_simples"))
menu_regras.add_command(label="Regras Verificar PIS/COFINS", command=lambda: abrir_editor_regras("verificacao_pis_cofins"))
menu_cadastros.add_cascade(label="Regras Fiscais", menu=menu_regras)

menubar.add_cascade(label="Cadastros", menu=menu_cadastros)

# Menu Ajuda
menu_ajuda = tk.Menu(menubar, tearoff=0)
menu_ajuda.add_command(label="Verificar Atualizações", command=updater.verificar_atualizacao_manual)
menubar.add_cascade(label="Ajuda", menu=menu_ajuda)
# ----------------



# Frame para entrada do caminho do arquivo
frame_caminho = tk.Frame(root)
estilos.estilizar_frame(frame_caminho)
frame_caminho.pack(fill=tk.X, padx=10, pady=5)  # O próprio frame ainda pode usar `pack`

lb_caminho = tk.Label(frame_caminho, text="Caminho do arquivo:")
estilos.estilizar_label(lb_caminho, destaque=True)
lb_caminho.grid(row=0, column=0, padx=5, pady=5, sticky="w")  # Alinhado à esquerda

entry_caminho = tk.Entry(frame_caminho, width=50, font=('Arial', 10))
entry_caminho.grid(row=0, column=1, padx=5, pady=5)

btn_abrir = tk.Button(frame_caminho, text="Abrir", command=abrir_arquivo)
estilos.estilizar_botao(btn_abrir, "neutro")
btn_abrir.grid(row=0, column=2, padx=5, pady=5)

# btn_verificar = tk.Button(frame_caminho, text="Verificar Itens", command=verificar_itens)
btn_verificar = tk.Button(frame_caminho, text="Verificar Itens", command=lambda: verificar_itens(entry_ncm_widgets, combo_desembolso, entry_cfop_widgets, entry_cst_widgets, checar_interrupcao, clicar_rateio, vars_uso_consumo))
estilos.estilizar_botao(btn_verificar, "destaque")
btn_verificar.grid(row=0, column=3, padx=5, pady=5)



# Adicionando o botão "Limpar Tela" ao frame de controle
btn_limpar = tk.Button(frame_caminho, text="Limpar Tela", command=limpar_tela)
estilos.estilizar_botao(btn_limpar, "limpar")
btn_limpar.grid(row=0, column=4, padx=5, pady=5)

i = 0  # Defina o valor inicial de i
btn_alterar_desembolso = tk.Button(frame_caminho, text="Alterar desembolso", command=lambda i=i: alterar_desembolso(i))
estilos.estilizar_botao(btn_alterar_desembolso, "neutro")
btn_alterar_desembolso.grid(row=0, column=5, padx=5, pady=5)


# btn_verificar = tk.Button(frame_caminho, text="Verificar Itens", command=verificar_itens)
btn_verificar_simples = tk.Button(frame_caminho, text="Verificar Itens simples", command=lambda: verificar_itens_simples(entry_ncm_widgets, combo_desembolso, entry_cfop_widgets, entry_cst_widgets, checar_interrupcao, clicar_rateio, vars_uso_consumo))
estilos.estilizar_botao(btn_verificar_simples, "destaque")
btn_verificar_simples.grid(row=0, column=6, padx=5, pady=5)

# btn_verificar = tk.Button(frame_caminho, text="Verificar Itens", command=verificar_itens)
btn_verificar_pis_cofins = tk.Button(frame_caminho, text="Verificar KMR,KJP,HPB,KPL", command=lambda: verificar_itens_pis_cofins_regras(entry_ncm_widgets, combo_desembolso, entry_cfop_widgets, entry_cst_widgets, checar_interrupcao, clicar_rateio, vars_uso_consumo, var_velocidade.get()))
estilos.estilizar_botao(btn_verificar_pis_cofins, "amarelo")
btn_verificar_pis_cofins.grid(row=0, column=7, padx=5, pady=5)

# Atualizando comandos dos outros botões para incluir velocidade
btn_verificar.config(command=lambda: verificar_itens(entry_ncm_widgets, combo_desembolso, entry_cfop_widgets, entry_cst_widgets, checar_interrupcao, clicar_rateio, vars_uso_consumo, var_velocidade.get()))

btn_verificar_simples.config(command=lambda: verificar_itens_simples(entry_ncm_widgets, combo_desembolso, entry_cfop_widgets, entry_cst_widgets, checar_interrupcao, clicar_rateio, vars_uso_consumo, var_velocidade.get()))


# Novo Label "Desembolso" e Combobox para selecionar "Restaurante" ou "Café da manhã"
lb_desembolso = tk.Label(frame_caminho, text="Desembolso:")
estilos.estilizar_label(lb_desembolso, destaque=True)
lb_desembolso.grid(row=1, column=0, padx=5, pady=5, sticky="w")  # Coloca na linha abaixo do caminho do arquivo

lb_empresa = tk.Label(frame_caminho, text='Empresa:')
estilos.estilizar_label(lb_empresa, destaque=True)
lb_empresa.place(x=400, y=40)

lb_nf = tk.Label(frame_caminho, text='NF:')
estilos.estilizar_label(lb_nf, destaque=True)
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

#Associa a função de filtragem ao evento de digitação no combobox
combo_desembolso.set(sorted(desembolso_opcoes)[0])  # Define o primeiro item da lista ordenada como padrão 

# Associa a função de filtragem ao evento de digitação no combobox
combo_desembolso.bind("<KeyRelease>", filtrar_desembolso)

# Botão (+) removido - agora no Menu

lb_grupo_produto = tk.Label(frame_caminho, text='Grupo de Produto:')
estilos.estilizar_label(lb_grupo_produto, destaque=True)
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
estilos.estilizar_frame(frame_canvas)
frame_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

canvas = tk.Canvas(frame_canvas)
estilos.estilizar_frame(canvas)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame_canvas, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas.configure(yscrollcommand=scrollbar.set)

frame_itens = tk.Frame(canvas)
estilos.estilizar_frame(frame_itens)
canvas.create_window((0, 0), window=frame_itens, anchor="nw")

def _on_mousewheel(event):
    # Verifica se o scroll ocorreu dentro de uma janela Toplevel (popup)
    widget = event.widget
    if isinstance(widget, str):
        try:
            widget = root.nametowidget(widget)
        except KeyError:
            pass # Widget não encontrado, segue o fluxo normal
            
    if hasattr(widget, "winfo_toplevel"):
        top = widget.winfo_toplevel()
        if top != root:
            # Se a janela atual não for a root (principal), NAO ROLA A CANVAS
            return

    if canvas.yview() != (0.0, 1.0):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)


# Frame para o rodapé
frame_footer = tk.Frame(root)
estilos.estilizar_frame(frame_footer)
frame_footer.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

# Copyright e informações do app
lb_copyright = tk.Label(
    frame_footer, 
    text="© 2025 Gibasanapp - Telefone: 81 988877159"
)
estilos.estilizar_label(lb_copyright)
lb_copyright.pack()


root.mainloop()
