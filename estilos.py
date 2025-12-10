import tkinter as tk

# --- Paleta de Cores (Estilo ERP/TOTVS) ---
CORES = {
    "fundo_janela": "#f5f5f5",      # Cinza Neutro/Gelo (Totvs Style)
    "fundo_frames": "#f5f5f5",      # Mesmo do fundo
    "fundo_input": "#ffffff",       # Branco
    
    # Botões
    "btn_acao": "#4caf50",          # Verde (Verificar Itens, Cadastrar)
    "btn_limpar": "#f44336",        # VERMELHO (Solicitado: Limpar Tela)
    "btn_neutro": "#2196f3",        # Azul (Abrir, Relacionar)
    "btn_amarelo": "#FFD700",       # Amarelo (Verificar PIS/COFINS)
    "btn_destaque": "#2196f3",      # Azul (Verificar Simples)
    
    # Texto
    "texto_padrao": "#333333",      # Cinza Escuro
    "texto_branco": "#ffffff",      # Branco (Botoes escuros)
    "texto_preto": "#000000"        # Preto (Botoes claros ex: amarelo)
}

def aplicar_tema_janela(root):
    """Configura o fundo da janela principal."""
    root.configure(bg=CORES["fundo_janela"])

def estilizar_botao(btn, tipo="neutro"):
    """
    Aplica cores e efeito hover a um botão Tkinter padrão.
    Tipos: 'neutro', 'acao', 'limpar', 'amarelo', 'destaque'
    """
    cor_fundo = CORES.get(f"btn_{tipo}", CORES["btn_neutro"])
    
    # Texto em preto se o fundo for amarelo
    if tipo == "amarelo":
        cor_texto = CORES["texto_preto"]
    else:
        cor_texto = CORES["texto_branco"]
    
    # Configuração Inicial
    try:
        btn.config(
            bg=cor_fundo,
            fg=cor_texto,
            font=('Segoe UI', 9, 'bold'),
            relief="raised",
            cursor="hand2", # Mãozinha ao passar o mouse
            bd=1 # Borda fina para ficar mais clean
        )
    except Exception:
        pass 

    # Efeitos Hover (Passar o mouse)
    def on_enter(e):
        btn.config(relief="sunken") 
        
    def on_leave(e):
        btn.config(relief="raised", bg=cor_fundo)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

def estilizar_frame(frame):
    """Aplica o background padrão aos frames."""
    try:
        frame.config(bg=CORES["fundo_frames"])
    except:
        pass

def estilizar_label(label, destaque=False):
    """Aplica estilo aos labels."""
    try:
        bg = CORES["fundo_frames"]
        fg = CORES["texto_padrao"]
        
        # Labels padrão Totvs são bem clean, sem bold exagerado, exceto titulos
        font = ('Segoe UI', 9)
        
        if destaque:
            # Destaque sutil
            font = ('Segoe UI', 9, 'bold')
            
        label.config(bg=bg, fg=fg, font=font)
    except:
        pass
