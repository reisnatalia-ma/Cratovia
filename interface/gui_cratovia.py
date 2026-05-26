"""
gui_cratovia.py  —  Interface gráfica Tkinter para o Cratovia
Coloque na raiz do projeto e execute:  python gui_cratovia.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys, os

sys.path.insert(0, os.path.dirname(__file__))

from dados.database import criar_tabelas
from servicos.autenticacao import cadastrar_usuario, fazer_login
from servicos.interacoes import (
    curtir_postagem, contar_curtidas,
    adicionar_comentario, buscar_comentarios,
    denunciar_postagem,
)
from servicos.feed import buscar_ocorrencias, buscar_eventos
from servicos.postagens import criar_postagem, criar_evento, NATUREZAS
from servicos.moderacao import (
    pode_moderar, pode_destacar,
    ocultar_postagem, aprovar_postagem,
    remover_postagem_moderacao, destacar_postagem,
    buscar_denuncias_pendentes, buscar_postagens_ocultas,
)

# ── Paleta ────────────────────────────────────────────────────────────────────
BG          = "#1E2128"   # fundo principal (cinza escuro)
BG_CARD     = "#262B35"   # cards
BG_PANEL    = "#1A1E26"   # painéis/sidebar
BG_INPUT    = "#2E3340"   # inputs
BG_HOVER    = "#2F3543"
FG          = "#E8EAF0"   # texto principal
FG_MUTED    = "#8B91A0"   # texto secundário
FG_DIM      = "#565E70"   # texto muito apagado
ACCENT      = "#3B82F6"   # azul principal
ACCENT_HV   = "#2563EB"
ACCENT_DIM  = "#1E3A5F"   # azul escuro para badges
SUCCESS     = "#22C55E"
DANGER      = "#EF4444"
DANGER_HV   = "#DC2626"
WARNING     = "#F59E0B"
BORDER      = "#2E3340"
BORDER_LT   = "#383F50"

FONT_TITLE  = ("Georgia", 22, "bold")
FONT_H2     = ("Georgia", 14, "bold")
FONT_H3     = ("Georgia", 11, "bold")
FONT_BODY   = ("Helvetica Neue", 10)
FONT_BOLD   = ("Helvetica Neue", 10, "bold")
FONT_SM     = ("Helvetica Neue", 9)
FONT_SM_B   = ("Helvetica Neue", 9, "bold")
FONT_XS     = ("Helvetica Neue", 8)

BAIRROS = [
    "Alto da Penha", "Barro Branco", "Cacimbas", "Centro",
    "Distrito de Baixio das Palmeiras", "Distrito de Bela Vista",
    "Distrito de Belmonte", "Distrito de Campo Alegre",
    "Distrito de Dom Quintino", "Distrito de Monte Alverne",
    "Distrito de Ponta da Serra", "Distrito de Santa Fé",
    "Distrito de Santa Rosa", "Gizélia Pinheiro (Batateiras)",
    "Grangeiro", "Independência", "Lameiro", "Mirandão", "Muriti",
    "Mutirão", "Novo Crato", "Novo Horizonte",
    "Ossian Araripe (Caixa D'Água)", "Pantanal", "Parque Granjeiro",
    "Parque Recreio", "Pimenta", "Pinto Madeira", "Santa Luzia",
    "Seminário", "Sossego", "São Bento", "São Gonçalo", "São José",
    "São Miguel", "Vila Alta", "Vila Lobo", "Zacarias Gonçalves",
]

NATUREZA_ICONE = {
    "Acidente":                  "🚗",
    "Problema urbano":           "🏗",
    "Denúncia":                  "📢",
    "Alagamento":                "🌊",
    "Falta de energia":          "⚡",
    "Trânsito":                  "🚦",
    "Aviso importante":          "⚠️",
    "Outro":                     "📌",
    "Acidente de trânsito":      "🚗",
    "Incêndio":                  "🔥",
    "Desastre ambiental":        "🌿",
    "Falta de infraestrutura":   "🏗",
    "Violência/Segurança pública":"🚨",
    "Saúde pública":             "🏥",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _icone_natureza(natureza):
    return NATUREZA_ICONE.get(natureza, "📌")


def _btn(parent, text, cmd, danger=False, secondary=False, small=False, **kw):
    if danger:
        bg, hv, fg = DANGER, DANGER_HV, "white"
    elif secondary:
        bg, hv, fg = BG_INPUT, BG_HOVER, FG
    else:
        bg, hv, fg = ACCENT, ACCENT_HV, "white"
    fs = 9 if small else 10
    b = tk.Button(
        parent, text=text, command=cmd,
        bg=bg, fg=fg, relief="flat", cursor="hand2",
        font=("Helvetica Neue", fs), padx=12, pady=5,
        activebackground=hv, activeforeground=fg, **kw
    )
    b.bind("<Enter>", lambda e: b.config(bg=hv))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b


def _entry(parent, show=None, width=30, placeholder=""):
    e = tk.Entry(
        parent, show=show, width=width,
        bg=BG_INPUT, fg=FG, relief="flat",
        font=FONT_BODY, insertbackground=FG,
        highlightthickness=1, highlightbackground=BORDER_LT,
        highlightcolor=ACCENT, disabledbackground=BG_INPUT,
    )
    if placeholder:
        e.insert(0, placeholder)
        e.config(fg=FG_MUTED)
        def _focus_in(ev):
            if e.get() == placeholder:
                e.delete(0, "end")
                e.config(fg=FG)
        def _focus_out(ev):
            if not e.get():
                e.insert(0, placeholder)
                e.config(fg=FG_MUTED)
        e.bind("<FocusIn>",  _focus_in)
        e.bind("<FocusOut>", _focus_out)
    return e


def _lbl(parent, text, bold=False, muted=False, size=10, color=None):
    fg = color or (FG_MUTED if muted else FG)
    style = "bold" if bold else "normal"
    return tk.Label(parent, text=text, bg=parent.cget("bg"),
                    fg=fg, font=("Helvetica Neue", size, style))


def _sep(parent, color=BORDER_LT):
    return tk.Frame(parent, bg=color, height=1)


def _badge(parent, text, color=ACCENT_DIM, fg=ACCENT):
    f = tk.Frame(parent, bg=color, padx=6, pady=2)
    tk.Label(f, text=text, bg=color, fg=fg, font=FONT_XS).pack()
    return f


def _scrollable(parent):
    """Retorna (outer_frame, inner_frame, canvas) com scroll vertical."""
    canvas = tk.Canvas(parent, bg=parent.cget("bg"), highlightthickness=0)
    sb     = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    inner = tk.Frame(canvas, bg=parent.cget("bg"))
    win   = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _resize(e): canvas.itemconfig(win, width=e.width)
    canvas.bind("<Configure>", _resize)
    inner.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def _scroll(e): canvas.yview_scroll(int(-1*(e.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _scroll)

    return inner, canvas


# ═════════════════════════════════════════════════════════════════════════════
# TELA DE LOGIN
# ═════════════════════════════════════════════════════════════════════════════

class TelaAuth(tk.Frame):
    def __init__(self, master, on_login):
        super().__init__(master, bg=BG)
        self.on_login = on_login
        self._modo_login = True
        self._build()

    def _build(self):
        # Container centralizado
        wrap = tk.Frame(self, bg=BG)
        wrap.place(relx=.5, rely=.5, anchor="center")

        # Título
        tk.Label(wrap, text="Cratovia", font=("Georgia", 36, "bold"),
                 bg=BG, fg=FG).pack(pady=(0, 4))
        tk.Label(wrap, text="Ocorrências · Crato — CE",
                 font=("Helvetica Neue", 11), bg=BG, fg=FG_MUTED).pack(pady=(0, 32))

        # Campos
        self._frm = tk.Frame(wrap, bg=BG)
        self._frm.pack()

        # Nome (só cadastro)
        self._nome_row = tk.Frame(self._frm, bg=BG)
        self._e_nome = _entry(self._nome_row, width=34, placeholder="Nome completo")
        self._e_nome.pack(ipady=6, fill="x")

        # Email
        self._e_email = _entry(self._frm, width=34, placeholder="E-mail")
        self._e_email.pack(ipady=6, fill="x", pady=(0, 8))

        # Senha
        self._e_senha = _entry(self._frm, show="•", width=34, placeholder="Senha")
        self._e_senha.pack(ipady=6, fill="x")
        self._e_senha.bind("<Return>", lambda e: self._submit())

        # Mensagem
        self._msg_var = tk.StringVar()
        self._msg_lbl = tk.Label(self._frm, textvariable=self._msg_var,
                                  bg=BG, fg=DANGER, font=FONT_SM,
                                  wraplength=280)
        self._msg_lbl.pack(pady=(8, 0))

        # Botão principal
        self._btn_sub = _btn(self._frm, "Entrar", self._submit)
        self._btn_sub.pack(fill="x", ipady=6, pady=(12, 0))

        # Separador
        sep_frm = tk.Frame(self._frm, bg=BG)
        sep_frm.pack(fill="x", pady=16)
        tk.Frame(sep_frm, bg=BORDER_LT, height=1).pack(
            side="left", fill="x", expand=True)
        tk.Label(sep_frm, text="  ou  ", bg=BG,
                 fg=FG_DIM, font=FONT_XS).pack(side="left")
        tk.Frame(sep_frm, bg=BORDER_LT, height=1).pack(
            side="left", fill="x", expand=True)

        # Toggle login/cadastro
        self._toggle_var = tk.StringVar(value="Criar conta")
        tog = tk.Button(
            self._frm, textvariable=self._toggle_var,
            bg=BG, fg=ACCENT, relief="flat", font=FONT_SM_B,
            cursor="hand2", activebackground=BG, activeforeground=ACCENT_HV,
            command=self._toggle,
        )
        tog.pack(fill="x", ipady=5)

        # Sem login
        tk.Button(
            self._frm, text="Continuar sem login",
            bg=BG, fg=FG_DIM, relief="flat", font=FONT_SM,
            cursor="hand2", activebackground=BG, activeforeground=FG_MUTED,
            command=lambda: self.on_login(None),
        ).pack(fill="x", ipady=4, pady=(4, 0))

        self._aplicar_modo()

    def _toggle(self):
        self._modo_login = not self._modo_login
        self._msg_var.set("")
        self._aplicar_modo()

    def _aplicar_modo(self):
        if self._modo_login:
            self._btn_sub.config(text="Entrar")
            self._toggle_var.set("Criar conta")
            self._nome_row.pack_forget()
        else:
            self._btn_sub.config(text="Cadastrar")
            self._toggle_var.set("Já tenho conta")
            self._nome_row.pack(fill="x", pady=(0, 8),
                                before=self._e_email)

    def _submit(self):
        email = self._e_email.get().strip()
        senha = self._e_senha.get().strip()
        if email == "E-mail": email = ""
        if senha == "Senha":  senha = ""

        if self._modo_login:
            usuario, msg = fazer_login(email, senha)
            if usuario:
                self.on_login(usuario)
            else:
                self._msg_var.set(msg)
        else:
            nome = self._e_nome.get().strip()
            if nome == "Nome completo": nome = ""
            if not nome:
                self._msg_var.set("Informe seu nome.")
                return
            uid, msg = cadastrar_usuario(nome, email, senha)
            if uid:
                self._msg_var.set(msg)
                self._msg_lbl.config(fg=SUCCESS)
                usuario, _ = fazer_login(email, senha)
                self.after(700, lambda: self.on_login(usuario))
            else:
                self._msg_var.set(msg)
                self._msg_lbl.config(fg=DANGER)


# ═════════════════════════════════════════════════════════════════════════════
# CARD DE POSTAGEM
# ═════════════════════════════════════════════════════════════════════════════

class CardPostagem(tk.Frame):
    def __init__(self, parent, postagem, on_abrir, **kw):
        super().__init__(parent, bg=BG_CARD,
                         highlightthickness=1, highlightbackground=BORDER,
                         padx=20, pady=16, **kw)
        self._post    = postagem
        self._on_abrir = on_abrir
        self._build()
        for w in self.winfo_children():
            w.bind("<Button-1>", lambda e: on_abrir(postagem))
        self.bind("<Button-1>", lambda e: on_abrir(postagem))
        self.bind("<Enter>", lambda e: self._hover(True))
        self.bind("<Leave>", lambda e: self._hover(False))

    def _hover(self, on):
        c = BG_HOVER if on else BG_CARD
        b = ACCENT if on else BORDER
        self.config(bg=c, highlightbackground=b)
        for w in self.winfo_children():
            try: w.config(bg=c)
            except: pass

    def _build(self):
        p = self._post

        # Linha 1: ícone + título + badge destaque
        top = tk.Frame(self, bg=BG_CARD)
        top.pack(fill="x")

        icone = _icone_natureza(p.get("natureza", ""))
        tk.Label(top, text=icone, bg=BG_CARD, fg=FG,
                 font=("Helvetica Neue", 14)).pack(side="left", padx=(0, 10))

        titulo_txt = p["titulo"]
        lbl_titulo = tk.Label(top, text=titulo_txt, bg=BG_CARD, fg=FG,
                               font=FONT_H3, cursor="hand2",
                               wraplength=420, justify="left", anchor="w")
        lbl_titulo.pack(side="left", fill="x", expand=True)
        lbl_titulo.bind("<Button-1>", lambda e: self._on_abrir(p))

        if p.get("destaque"):
            _badge(top, "★ DESTAQUE", ACCENT_DIM, ACCENT).pack(
                side="right", padx=(8, 0))
        if p.get("tipo") == "evento":
            _badge(top, "EVENTO", "#1F3A1F", SUCCESS).pack(
                side="right", padx=(8, 0))

        # Linha 2: descrição
        desc = (p.get("descricao") or "")[:120]
        if desc:
            tk.Label(self, text=desc, bg=BG_CARD, fg=FG_MUTED,
                     font=FONT_SM, wraplength=480,
                     justify="left", anchor="w").pack(
                fill="x", pady=(6, 0))

        # Linha 3: meta
        meta_frm = tk.Frame(self, bg=BG_CARD)
        meta_frm.pack(fill="x", pady=(10, 0))

        curtidas = contar_curtidas(p["id"])
        for txt in [
            f"📍 {p['bairro']}",
            f"🗓 {p['data']} {p['hora']}",
            f"♥ {curtidas}",
        ]:
            tk.Label(meta_frm, text=txt, bg=BG_CARD, fg=FG_DIM,
                     font=FONT_XS).pack(side="left", padx=(0, 14))

        if p.get("natureza"):
            tk.Label(meta_frm, text=f"🏷 {p['natureza']}",
                     bg=BG_CARD, fg=FG_DIM, font=FONT_XS).pack(
                side="left", padx=(0, 14))


# ═════════════════════════════════════════════════════════════════════════════
# PAINEL DE DETALHE (substitui o feed na tela principal)
# ═════════════════════════════════════════════════════════════════════════════

class PainelDetalhe(tk.Frame):
    def __init__(self, parent, postagem, usuario, on_voltar):
        super().__init__(parent, bg=BG)
        self._post     = postagem
        self._usuario  = usuario
        self._on_voltar = on_voltar
        self._build()

    def _build(self):
        p = self._post

        # Topbar do detalhe
        top = tk.Frame(self, bg=BG_PANEL, padx=20, pady=12)
        top.pack(fill="x")
        _btn(top, "← Voltar", self._on_voltar, secondary=True, small=True).pack(side="left")

        # Conteúdo rolável
        inner, canvas = _scrollable(self)
        self.pack(fill="both", expand=True)

        wrap = tk.Frame(inner, bg=BG, padx=32, pady=24)
        wrap.pack(fill="both", expand=True)

        # Ícone + tipo
        icone = _icone_natureza(p.get("natureza", ""))
        meta_top = tk.Frame(wrap, bg=BG)
        meta_top.pack(fill="x", pady=(0, 8))
        tk.Label(meta_top, text=icone, bg=BG, fg=FG,
                 font=("Helvetica Neue", 20)).pack(side="left", padx=(0, 10))
        if p.get("natureza"):
            _badge(meta_top, p["natureza"], ACCENT_DIM, ACCENT).pack(
                side="left", padx=(0, 6))
        if p.get("tipo") == "evento":
            _badge(meta_top, "EVENTO", "#1F3A1F", SUCCESS).pack(side="left")
        if p.get("destaque"):
            _badge(meta_top, "★ DESTAQUE", ACCENT_DIM, WARNING).pack(
                side="left", padx=(6, 0))

        # Título
        tk.Label(wrap, text=p["titulo"], font=("Georgia", 18, "bold"),
                 bg=BG, fg=FG, wraplength=600, justify="left").pack(
            anchor="w", pady=(0, 6))

        # Meta
        meta = tk.Frame(wrap, bg=BG)
        meta.pack(fill="x", pady=(0, 16))
        for txt in [f"📍 {p['bairro']}", f"🗓 {p['data']} às {p['hora']}"]:
            tk.Label(meta, text=txt, bg=BG, fg=FG_MUTED,
                     font=FONT_SM).pack(side="left", padx=(0, 16))

        _sep(wrap).pack(fill="x", pady=(0, 16))

        # Conteúdo
        tk.Label(wrap, text=p["conteudo"], font=FONT_BODY,
                 bg=BG, fg=FG, wraplength=600, justify="left").pack(
            anchor="w", pady=(0, 20))

        _sep(wrap).pack(fill="x", pady=(0, 16))

        # Ações
        self._curtidas_var = tk.StringVar()
        self._refresh_curtidas()

        acoes = tk.Frame(wrap, bg=BG)
        acoes.pack(fill="x", pady=(0, 20))

        tk.Label(acoes, textvariable=self._curtidas_var,
                 bg=BG, fg=FG_MUTED, font=FONT_SM).pack(side="left", padx=(0, 16))

        if self._usuario:
            _btn(acoes, "♥  Curtir",    self._curtir,   small=True).pack(side="left", padx=(0, 8))
            _btn(acoes, "✎  Comentar",  lambda: self._e_com.focus(), secondary=True, small=True).pack(side="left", padx=(0, 8))
            _btn(acoes, "⚑  Denunciar", self._denunciar, danger=True, small=True).pack(side="left")

        _sep(wrap).pack(fill="x", pady=(0, 16))

        # Comentários
        tk.Label(wrap, text="Comentários", font=FONT_H3,
                 bg=BG, fg=FG).pack(anchor="w", pady=(0, 10))

        self._com_frame = tk.Frame(wrap, bg=BG)
        self._com_frame.pack(fill="x")
        self._carregar_comentarios()

        # Input comentário
        if self._usuario:
            inp = tk.Frame(wrap, bg=BG, pady=12)
            inp.pack(fill="x")
            self._e_com = _entry(inp, width=52, placeholder="Escreva um comentário...")
            self._e_com.pack(side="left", fill="x", expand=True,
                             ipady=6, padx=(0, 10))
            self._e_com.bind("<Return>", lambda e: self._comentar())
            _btn(inp, "Enviar", self._comentar, small=True).pack(side="left")

    def _refresh_curtidas(self):
        c = contar_curtidas(self._post["id"])
        self._curtidas_var.set(
            f"♥  {c} {'curtida' if c == 1 else 'curtidas'}")

    def _curtir(self):
        resultado = curtir_postagem(self._post["id"], self._usuario["id"])
        self._refresh_curtidas()

    def _denunciar(self):
        win = tk.Toplevel(self)
        win.title("Denunciar postagem")
        win.geometry("360x160")
        win.configure(bg=BG)
        win.resizable(False, False)
        tk.Label(win, text="Motivo da denúncia:",
                 font=FONT_BOLD, bg=BG, fg=FG).pack(
            padx=24, pady=(20, 6), anchor="w")
        e = _entry(win, width=38)
        e.pack(padx=24, ipady=6, fill="x")
        e.focus()

        def _enviar():
            motivo = e.get().strip()
            if not motivo: return
            ok, msg = denunciar_postagem(
                self._post["id"], self._usuario["id"], motivo)
            messagebox.showinfo("Denúncia", msg, parent=win)
            win.destroy()

        _btn(win, "Enviar denúncia", _enviar, danger=True).pack(
            pady=14, padx=24, anchor="w")

    def _carregar_comentarios(self):
        for w in self._com_frame.winfo_children():
            w.destroy()
        comentarios = buscar_comentarios(self._post["id"])
        if not comentarios:
            tk.Label(self._com_frame, text="Seja o primeiro a comentar.",
                     font=FONT_SM, bg=BG, fg=FG_DIM).pack(
                anchor="w", pady=4)
            return
        for com in comentarios:
            row = tk.Frame(self._com_frame, bg=BG_CARD,
                           padx=14, pady=10,
                           highlightthickness=1, highlightbackground=BORDER)
            row.pack(fill="x", pady=(0, 6))
            header = tk.Frame(row, bg=BG_CARD)
            header.pack(fill="x")
            tk.Label(header, text=com["nome"], font=FONT_SM_B,
                     bg=BG_CARD, fg=ACCENT).pack(side="left")
            tk.Label(header, text=f"  {com['data']} {com['hora']}",
                     font=FONT_XS, bg=BG_CARD, fg=FG_DIM).pack(side="left")
            tk.Label(row, text=com["texto"], font=FONT_BODY,
                     bg=BG_CARD, fg=FG, wraplength=560,
                     justify="left", anchor="w").pack(
                fill="x", pady=(6, 0))

    def _comentar(self):
        texto = self._e_com.get().strip()
        if not texto or texto == "Escreva um comentário...": return
        adicionar_comentario(self._post["id"], self._usuario["id"], texto)
        self._e_com.delete(0, "end")
        self._carregar_comentarios()


# ═════════════════════════════════════════════════════════════════════════════
# PAINEL DE NOVA POSTAGEM
# ═════════════════════════════════════════════════════════════════════════════

class PainelNova(tk.Frame):
    def __init__(self, parent, usuario, on_voltar, on_publicar):
        super().__init__(parent, bg=BG)
        self._usuario    = usuario
        self._on_voltar  = on_voltar
        self._on_publicar = on_publicar
        self._build()

    def _build(self):
        # Topbar
        top = tk.Frame(self, bg=BG_PANEL, padx=20, pady=12)
        top.pack(fill="x")
        _btn(top, "← Voltar", self._on_voltar, secondary=True, small=True).pack(side="left")
        tk.Label(top, text="Nova Postagem", font=FONT_H2,
                 bg=BG_PANEL, fg=FG).pack(side="left", padx=16)

        inner, _ = _scrollable(self)
        self.pack(fill="both", expand=True)

        frm = tk.Frame(inner, bg=BG, padx=40, pady=28)
        frm.pack(fill="both", expand=True)

        def campo(label, widget):
            tk.Label(frm, text=label, font=FONT_SM_B,
                     bg=BG, fg=FG_MUTED).pack(anchor="w", pady=(12, 3))
            widget.pack(fill="x", ipady=6)
            return widget

        self._e_titulo = campo("TÍTULO *", _entry(frm, width=52))
        self._e_desc   = campo("DESCRIÇÃO CURTA *", _entry(frm, width=52))

        # Bairro
        tk.Label(frm, text="BAIRRO *", font=FONT_SM_B,
                 bg=BG, fg=FG_MUTED).pack(anchor="w", pady=(12, 3))
        self._cb_bairro = ttk.Combobox(frm, values=BAIRROS,
                                        state="readonly", width=50)
        self._cb_bairro.pack(fill="x", ipady=4)

        # Natureza
        tk.Label(frm, text="NATUREZA", font=FONT_SM_B,
                 bg=BG, fg=FG_MUTED).pack(anchor="w", pady=(12, 3))
        self._cb_nat = ttk.Combobox(frm, values=NATUREZAS,
                                     state="readonly", width=50)
        self._cb_nat.pack(fill="x", ipady=4)

        # Tipo
        tk.Label(frm, text="TIPO *", font=FONT_SM_B,
                 bg=BG, fg=FG_MUTED).pack(anchor="w", pady=(12, 3))
        self._tipo_var = tk.StringVar(value="ocorrencia")
        tipo_frm = tk.Frame(frm, bg=BG)
        tipo_frm.pack(anchor="w")
        for val, txt in [("ocorrencia", "Ocorrência"), ("evento", "Evento")]:
            tk.Radiobutton(
                tipo_frm, text=txt, variable=self._tipo_var, value=val,
                bg=BG, fg=FG, activebackground=BG, selectcolor=ACCENT,
                font=FONT_BODY,
            ).pack(side="left", padx=(0, 20))

        # Conteúdo
        tk.Label(frm, text="CONTEÚDO *", font=FONT_SM_B,
                 bg=BG, fg=FG_MUTED).pack(anchor="w", pady=(12, 3))
        self._txt = scrolledtext.ScrolledText(
            frm, height=7, font=FONT_BODY,
            bg=BG_INPUT, fg=FG, insertbackground=FG,
            relief="flat", highlightthickness=1,
            highlightbackground=BORDER_LT, highlightcolor=ACCENT,
        )
        self._txt.pack(fill="x")

        self._msg_var = tk.StringVar()
        tk.Label(frm, textvariable=self._msg_var, bg=BG,
                 fg=DANGER, font=FONT_SM).pack(anchor="w", pady=(8, 0))

        _btn(frm, "Publicar postagem", self._publicar).pack(
            anchor="w", ipady=6, pady=(12, 0))

    def _publicar(self):
        titulo   = self._e_titulo.get().strip()
        desc     = self._e_desc.get().strip()
        bairro   = self._cb_bairro.get().strip()
        natureza = self._cb_nat.get().strip() or None
        tipo     = self._tipo_var.get()
        conteudo = self._txt.get("1.0", "end").strip()

        if not all([titulo, desc, bairro, conteudo]):
            self._msg_var.set("Preencha todos os campos obrigatórios (*).")
            return

        if tipo == "ocorrencia":
            criar_postagem(titulo, desc, bairro, conteudo,
                           natureza, self._usuario["id"])
        else:
            criar_evento(titulo, desc, bairro, conteudo, self._usuario["id"])

        self._on_publicar()


# ═════════════════════════════════════════════════════════════════════════════
# PAINEL DE MODERAÇÃO
# ═════════════════════════════════════════════════════════════════════════════

class PainelModeracao(tk.Frame):
    def __init__(self, parent, usuario, on_voltar):
        super().__init__(parent, bg=BG)
        self._usuario  = usuario
        self._on_voltar = on_voltar
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG_PANEL, padx=20, pady=12)
        top.pack(fill="x")
        _btn(top, "← Voltar", self._on_voltar, secondary=True, small=True).pack(side="left")
        tk.Label(top, text="Moderação", font=FONT_H2,
                 bg=BG_PANEL, fg=FG).pack(side="left", padx=16)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=16, pady=16)

        t1 = tk.Frame(nb, bg=BG)
        t2 = tk.Frame(nb, bg=BG)
        nb.add(t1, text="  Denúncias  ")
        nb.add(t2, text="  Postagens Ocultas  ")

        if pode_destacar(self._usuario):
            t3 = tk.Frame(nb, bg=BG)
            nb.add(t3, text="  Destacar  ")
            self._build_destacar(t3)

        self._build_denuncias(t1)
        self._build_ocultas(t2)

    def _mk_tree(self, parent, cols, headings, widths):
        frm = tk.Frame(parent, bg=BG)
        frm.pack(fill="both", expand=True, padx=16, pady=8)
        sb  = ttk.Scrollbar(frm, orient="vertical")
        tree = ttk.Treeview(frm, columns=cols, show="headings",
                             yscrollcommand=sb.set)
        sb.config(command=tree.yview)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        for col, head, w in zip(cols, headings, widths):
            tree.heading(col, text=head)
            tree.column(col, width=w, anchor="center" if w < 80 else "w")
        return tree

    def _build_denuncias(self, parent):
        tk.Label(parent, text="Denúncias registradas",
                 font=FONT_H3, bg=BG, fg=FG, pady=12).pack(anchor="w", padx=16)

        tree = self._mk_tree(parent,
            cols=("pid", "titulo", "denunciante", "motivo", "data"),
            headings=("ID", "Título", "Denunciante", "Motivo", "Data"),
            widths=(40, 200, 120, 200, 90),
        )
        for d in buscar_denuncias_pendentes():
            tree.insert("", "end", values=(
                d["postagem_id"], d["titulo"],
                d["denunciante"], d["motivo"], d["data"],
            ))

        def _ocultar():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Atenção", "Selecione uma denúncia.")
                return
            pid = int(tree.item(sel[0])["values"][0])
            ocultar_postagem(pid)
            tree.delete(sel[0])
            messagebox.showinfo("Moderação", "Postagem ocultada.")

        _btn(parent, "⊘  Ocultar postagem selecionada",
             _ocultar, danger=True, small=True).pack(
            pady=(0, 12), padx=16, anchor="w")

    def _build_ocultas(self, parent):
        tk.Label(parent, text="Postagens ocultas",
                 font=FONT_H3, bg=BG, fg=FG, pady=12).pack(anchor="w", padx=16)

        tree = self._mk_tree(parent,
            cols=("id", "titulo", "bairro", "data"),
            headings=("ID", "Título", "Bairro", "Data"),
            widths=(40, 260, 160, 90),
        )

        def _recarregar():
            for row in tree.get_children(): tree.delete(row)
            for p in buscar_postagens_ocultas():
                tree.insert("", "end", values=(
                    p["id"], p["titulo"], p["bairro"], p["data"]))

        _recarregar()

        btns = tk.Frame(parent, bg=BG)
        btns.pack(anchor="w", padx=16, pady=(0, 12))

        def _aprovar():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Atenção", "Selecione uma postagem.")
                return
            pid = int(tree.item(sel[0])["values"][0])
            aprovar_postagem(pid)
            _recarregar()
            messagebox.showinfo("Moderação", "Postagem reativada.")

        def _remover():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Atenção", "Selecione uma postagem.")
                return
            pid = int(tree.item(sel[0])["values"][0])
            if messagebox.askyesno("Confirmar", "Remover permanentemente?"):
                remover_postagem_moderacao(pid)
                _recarregar()

        _btn(btns, "✔  Aprovar", _aprovar, small=True).pack(side="left", padx=(0, 8))
        _btn(btns, "✖  Remover", _remover, danger=True, small=True).pack(side="left")

    def _build_destacar(self, parent):
        frm = tk.Frame(parent, bg=BG, padx=24, pady=24)
        frm.pack(fill="both", expand=True)
        tk.Label(frm, text="Destacar postagem", font=FONT_H3,
                 bg=BG, fg=FG).pack(anchor="w", pady=(0, 12))
        tk.Label(frm, text="ID da postagem:", font=FONT_SM_B,
                 bg=BG, fg=FG_MUTED).pack(anchor="w")
        e = _entry(frm, width=20)
        e.pack(anchor="w", ipady=6, pady=(4, 12))
        msg = tk.StringVar()
        tk.Label(frm, textvariable=msg, bg=BG, fg=SUCCESS, font=FONT_SM).pack(anchor="w")

        def _destacar():
            val = e.get().strip()
            if not val.isdigit():
                msg.set("Digite um ID válido.")
                return
            destacar_postagem(int(val))
            msg.set(f"Postagem #{val} destacada!")
            e.delete(0, "end")

        _btn(frm, "★  Destacar", _destacar, small=True).pack(anchor="w")


# ═════════════════════════════════════════════════════════════════════════════
# TELA PRINCIPAL
# ═════════════════════════════════════════════════════════════════════════════

class TelaApp(tk.Frame):
    def __init__(self, master, usuario):
        super().__init__(master, bg=BG)
        self._usuario   = usuario
        self._pagina    = 1
        self._total_pags = 1
        self._modo      = "ocorrencias"
        self._filtro_bairro   = None
        self._filtro_natureza = None
        self._painel_atual = None
        self._build()
        self._mostrar_feed()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        # Topbar
        top = tk.Frame(self, bg=BG_PANEL, padx=20, pady=0,
                       highlightthickness=1, highlightbackground=BORDER)
        top.pack(fill="x")

        tk.Label(top, text="Cratovia", font=("Georgia", 15, "bold"),
                 bg=BG_PANEL, fg=FG, pady=12).pack(side="left")

        # Botões de navegação no topo
        nav = tk.Frame(top, bg=BG_PANEL)
        nav.pack(side="left", padx=24)

        self._nav_btns = {}
        for key, label in [("ocorrencias", "Ocorrências"), ("eventos", "Eventos")]:
            b = tk.Button(nav, text=label, bg=BG_PANEL, fg=FG_MUTED,
                          relief="flat", font=FONT_SM, padx=12, pady=12,
                          cursor="hand2", activebackground=BG_PANEL,
                          activeforeground=FG,
                          command=lambda k=key: self._set_modo(k))
            b.pack(side="left")
            self._nav_btns[key] = b

        # Área direita do top
        right = tk.Frame(top, bg=BG_PANEL)
        right.pack(side="right")

        if self._usuario:
            _btn(right, "+ Nova postagem",
                 self._ir_nova, small=True).pack(side="right", padx=(8, 0))
            if pode_moderar(self._usuario):
                _btn(right, "🛡 Moderação",
                     self._ir_moderacao, secondary=True, small=True).pack(side="right", padx=(8, 0))

        user_txt = self._usuario["nome"] if self._usuario else "Visitante"
        tk.Label(right, text=user_txt, font=FONT_SM,
                 bg=BG_PANEL, fg=FG_MUTED, padx=12).pack(side="right")

        # Corpo: filtros + conteúdo
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)

        # Barra de filtros (fina, horizontal)
        self._filtros_bar = tk.Frame(body, bg=BG_PANEL, padx=20, pady=8,
                                      highlightthickness=1,
                                      highlightbackground=BORDER)
        self._filtros_bar.pack(fill="x")
        self._build_filtros(self._filtros_bar)

        # Área de conteúdo
        self._conteudo = tk.Frame(body, bg=BG)
        self._conteudo.pack(fill="both", expand=True)

        self._atualizar_nav()

    def _build_filtros(self, parent):
        tk.Label(parent, text="Filtros:", font=FONT_XS,
                 bg=BG_PANEL, fg=FG_DIM).pack(side="left", padx=(0, 10))

        _btn(parent, "📍 Bairro",    self._filtrar_bairro,   secondary=True, small=True).pack(side="left", padx=(0, 6))
        _btn(parent, "🏷 Natureza",  self._filtrar_natureza, secondary=True, small=True).pack(side="left", padx=(0, 6))
        _btn(parent, "✖ Limpar",     self._limpar_filtros,   secondary=True, small=True).pack(side="left")

        self._filtro_info = tk.StringVar()
        tk.Label(parent, textvariable=self._filtro_info,
                 font=FONT_XS, bg=BG_PANEL, fg=ACCENT).pack(side="left", padx=12)

    # ── Painéis ───────────────────────────────────────────────────────────────

    def _limpar_conteudo(self):
        for w in self._conteudo.winfo_children():
            w.destroy()

    def _mostrar_feed(self):
        self._limpar_conteudo()
        self._filtros_bar.pack(fill="x")  # garante visível

        # Feed rolável
        feed_outer = tk.Frame(self._conteudo, bg=BG)
        feed_outer.pack(fill="both", expand=True)

        # Cabeçalho do feed
        cab = tk.Frame(feed_outer, bg=BG, padx=24, pady=14)
        cab.pack(fill="x")
        self._cab_var = tk.StringVar()
        tk.Label(cab, textvariable=self._cab_var, font=FONT_H2,
                 bg=BG, fg=FG).pack(side="left")
        self._pag_var = tk.StringVar()
        tk.Label(cab, textvariable=self._pag_var, font=FONT_SM,
                 bg=BG, fg=FG_DIM).pack(side="right")

        # Paginação
        pag = tk.Frame(feed_outer, bg=BG, padx=24, pady=6)
        pag.pack(fill="x")
        _btn(pag, "← Anterior", self._pag_anterior, secondary=True, small=True).pack(side="left")
        _btn(pag, "Próxima →",  self._pag_proxima,  secondary=True, small=True).pack(side="right")

        _sep(feed_outer).pack(fill="x", padx=24)

        # Área dos cards
        scroll_area = tk.Frame(feed_outer, bg=BG)
        scroll_area.pack(fill="both", expand=True)
        self._feed_inner, self._feed_canvas = _scrollable(scroll_area)

        self._carregar_cards()

    def _carregar_cards(self):
        for w in self._feed_inner.winfo_children():
            w.destroy()

        if self._modo == "ocorrencias":
            postagens, total = buscar_ocorrencias(
                self._pagina,
                bairro=self._filtro_bairro,
                natureza=self._filtro_natureza,
            )
            cab = "Últimas Ocorrências"
            filtros = []
            if self._filtro_bairro:   filtros.append(self._filtro_bairro)
            if self._filtro_natureza: filtros.append(self._filtro_natureza)
            if filtros: cab += f" — {' · '.join(filtros)}"
        else:
            postagens, total = buscar_eventos(self._pagina)
            cab = "Eventos e Comunicados"

        self._total_pags = total
        self._cab_var.set(cab)
        self._pag_var.set(f"Pág. {self._pagina} / {total}")

        info = []
        if self._filtro_bairro:   info.append(f"Bairro: {self._filtro_bairro}")
        if self._filtro_natureza: info.append(f"Natureza: {self._filtro_natureza}")
        self._filtro_info.set("  ·  ".join(info))

        if not postagens:
            tk.Label(self._feed_inner, text="Nenhuma postagem encontrada.",
                     font=FONT_BODY, bg=BG, fg=FG_MUTED,
                     pady=40).pack()
            return

        for post in postagens:
            card = CardPostagem(self._feed_inner, post,
                                on_abrir=self._abrir_detalhe)
            card.pack(fill="x", padx=24, pady=(0, 10))

        self._feed_canvas.yview_moveto(0)

    def _abrir_detalhe(self, postagem):
        self._limpar_conteudo()
        self._filtros_bar.pack_forget()
        PainelDetalhe(
            self._conteudo, postagem, self._usuario,
            on_voltar=self._voltar_feed,
        ).pack(fill="both", expand=True)

    def _voltar_feed(self):
        self._filtros_bar.pack(fill="x", before=self._conteudo)
        self._mostrar_feed()

    def _ir_nova(self):
        self._limpar_conteudo()
        self._filtros_bar.pack_forget()
        PainelNova(
            self._conteudo, self._usuario,
            on_voltar=self._voltar_feed,
            on_publicar=self._apos_publicar,
        ).pack(fill="both", expand=True)

    def _apos_publicar(self):
        messagebox.showinfo("Publicado", "Postagem publicada com sucesso!")
        self._voltar_feed()

    def _ir_moderacao(self):
        self._limpar_conteudo()
        self._filtros_bar.pack_forget()
        PainelModeracao(
            self._conteudo, self._usuario,
            on_voltar=self._voltar_feed,
        ).pack(fill="both", expand=True)

    # ── Navegação ─────────────────────────────────────────────────────────────

    def _set_modo(self, modo):
        self._modo    = modo
        self._pagina  = 1
        self._filtro_bairro   = None
        self._filtro_natureza = None
        self._atualizar_nav()
        self._mostrar_feed()

    def _atualizar_nav(self):
        for key, btn in self._nav_btns.items():
            if key == self._modo:
                btn.config(fg=ACCENT,
                           font=("Helvetica Neue", 9, "bold"))
            else:
                btn.config(fg=FG_MUTED,
                           font=FONT_SM)

    def _pag_proxima(self):
        if self._pagina < self._total_pags:
            self._pagina += 1
            self._carregar_cards()

    def _pag_anterior(self):
        if self._pagina > 1:
            self._pagina -= 1
            self._carregar_cards()

    # ── Filtros ───────────────────────────────────────────────────────────────

    def _filtrar_bairro(self):
        win = tk.Toplevel(self)
        win.title("Filtrar por bairro")
        win.geometry("280x380")
        win.configure(bg=BG)
        win.resizable(False, False)

        tk.Label(win, text="Selecione o bairro",
                 font=FONT_H3, bg=BG, fg=FG).pack(padx=20, pady=(16, 8), anchor="w")

        frm = tk.Frame(win, bg=BG)
        frm.pack(fill="both", expand=True, padx=20)
        sb = tk.Scrollbar(frm)
        sb.pack(side="right", fill="y")
        lb = tk.Listbox(frm, yscrollcommand=sb.set, font=FONT_BODY,
                        bg=BG_INPUT, fg=FG, selectbackground=ACCENT,
                        relief="flat", highlightthickness=0,
                        activestyle="none")
        lb.pack(fill="both", expand=True)
        sb.config(command=lb.yview)
        for b in BAIRROS: lb.insert("end", b)

        def _ok():
            sel = lb.curselection()
            if sel:
                self._filtro_bairro = BAIRROS[sel[0]]
                self._pagina = 1
                self._carregar_cards()
            win.destroy()

        _btn(win, "Aplicar", _ok).pack(pady=12, padx=20, fill="x")

    def _filtrar_natureza(self):
        win = tk.Toplevel(self)
        win.title("Filtrar por natureza")
        win.geometry("280x320")
        win.configure(bg=BG)
        win.resizable(False, False)

        tk.Label(win, text="Selecione a natureza",
                 font=FONT_H3, bg=BG, fg=FG).pack(padx=20, pady=(16, 8), anchor="w")

        frm = tk.Frame(win, bg=BG)
        frm.pack(fill="both", expand=True, padx=20)
        lb = tk.Listbox(frm, font=FONT_BODY, bg=BG_INPUT, fg=FG,
                        selectbackground=ACCENT, relief="flat",
                        highlightthickness=0, activestyle="none")
        lb.pack(fill="both", expand=True)
        for n in NATUREZAS: lb.insert("end", n)

        def _ok():
            sel = lb.curselection()
            if sel:
                self._filtro_natureza = NATUREZAS[sel[0]]
                self._pagina = 1
                self._carregar_cards()
            win.destroy()

        _btn(win, "Aplicar", _ok).pack(pady=12, padx=20, fill="x")

    def _limpar_filtros(self):
        self._filtro_bairro   = None
        self._filtro_natureza = None
        self._pagina = 1
        self._carregar_cards()


# ═════════════════════════════════════════════════════════════════════════════
# APP
# ═════════════════════════════════════════════════════════════════════════════

class CratoviaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cratovia")
        self.geometry("960x660")
        self.minsize(720, 500)
        self.configure(bg=BG)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TScrollbar",
                        background=BORDER_LT, troughcolor=BG,
                        borderwidth=0, arrowsize=12,
                        darkcolor=BG, lightcolor=BG)
        style.configure("TCombobox",
                        fieldbackground=BG_INPUT, background=BG_INPUT,
                        foreground=FG, selectbackground=ACCENT,
                        bordercolor=BORDER_LT, arrowcolor=FG_MUTED)
        style.map("TCombobox", fieldbackground=[("readonly", BG_INPUT)])
        style.configure("TNotebook",
                        background=BG, borderwidth=0, tabmargins=0)
        style.configure("TNotebook.Tab",
                        background=BG_CARD, foreground=FG_MUTED,
                        padding=[12, 6], font=FONT_SM)
        style.map("TNotebook.Tab",
                  background=[("selected", BG)],
                  foreground=[("selected", ACCENT)])
        style.configure("Treeview",
                        background=BG_CARD, foreground=FG,
                        fieldbackground=BG_CARD, rowheight=28,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background=BG_PANEL, foreground=FG_MUTED,
                        relief="flat", font=FONT_SM_B)
        style.map("Treeview", background=[("selected", ACCENT_DIM)],
                  foreground=[("selected", FG)])

        criar_tabelas()
        self._mostrar_auth()

    def _mostrar_auth(self):
        self._limpar()
        TelaAuth(self, on_login=self._entrar).pack(fill="both", expand=True)

    def _entrar(self, usuario):
        self._limpar()
        TelaApp(self, usuario).pack(fill="both", expand=True)

    def _limpar(self):
        for w in self.winfo_children(): w.destroy()


if __name__ == "__main__":
    app = CratoviaApp()
    app.mainloop()