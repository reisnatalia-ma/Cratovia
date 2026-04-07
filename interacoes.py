from utils import (
    Cor, cabecalho, linha, msg_erro, msg_info, entrada, pausar,
    badge_usuario, pode_moderar, LARGURA, limpar_tela
)

# ─────────────────────────────────────────
#  TELA DE BOAS-VINDAS / SPLASH
# ─────────────────────────────────────────
def tela_boas_vindas():
    limpar_tela()
    print()
    print(f"  {Cor.AZUL}{'═' * (LARGURA - 4)}{Cor.RESET}")
    print()
    print(f"  {Cor.BOLD}{Cor.BRANCO}  🏙️   S I S T E M A   C R A T O{Cor.RESET}")
    print()
    print(f"  {Cor.DIM}  Portal de Ocorrências e Notícias da Cidade do Crato{Cor.RESET}")
    print(f"  {Cor.DIM}  Ceará — Brasil{Cor.RESET}")
    print()
    print(f"  {Cor.AZUL}{'═' * (LARGURA - 4)}{Cor.RESET}")
    print()

# ─────────────────────────────────────────
#  MENU INICIAL — Cadastro / Login / Continuar
# ─────────────────────────────────────────
def menu_inicial() -> str:
    """
    Retorna: 'cadastro' | 'login' | 'continuar'
    """
    tela_boas_vindas()

    print(f"  {Cor.BOLD}Como deseja continuar?{Cor.RESET}\n")
    print(f"  {Cor.AMARELO}[1]{Cor.RESET} Criar conta")
    print(f"  {Cor.AMARELO}[2]{Cor.RESET} Entrar (login)")
    print(f"  {Cor.AMARELO}[3]{Cor.RESET} Continuar sem login")
    print(f"\n  {Cor.DIM}[0] Sair do sistema{Cor.RESET}")
    print()

    while True:
        cmd = entrada("  Escolha: ", obrigatorio=False).strip()
        if cmd == "1":
            return "cadastro"
        if cmd == "2":
            return "login"
        if cmd == "3":
            return "continuar"
        if cmd == "0":
            return "sair"
        msg_erro("Opção inválida. Digite 1, 2, 3 ou 0.")


# ─────────────────────────────────────────
#  MENU PRINCIPAL
# ─────────────────────────────────────────
def menu_principal(usuario: dict | None) -> str:
    """
    Retorna: '1' a '6' (ou '7' para moderadores), ou 'sair'
    """
    limpar_tela()
    print()
    print(f"  {Cor.AZUL}{'═' * (LARGURA - 4)}{Cor.RESET}")
    print(f"  {Cor.BOLD}{Cor.BRANCO}  🏙️  SISTEMA CRATO{Cor.RESET}")
    print(f"  {Cor.AZUL}{'═' * (LARGURA - 4)}{Cor.RESET}")
    print()

    # Badge do usuário
    print(f"  Usuário: {badge_usuario(usuario)}")
    print()
    linha("─", Cor.DIM)
    print()

    print(f"  {Cor.AMARELO}[1]{Cor.RESET} Últimas notícias e ocorrências em Crato")
    print(f"  {Cor.AMARELO}[2]{Cor.RESET} Consultar notícias por bairro")
    print(f"  {Cor.AMARELO}[3]{Cor.RESET} Consultar por tipo de ocorrência")
    print(f"  {Cor.AMARELO}[4]{Cor.RESET} Divulgar uma ocorrência")
    print(f"  {Cor.AMARELO}[5]{Cor.RESET} {Cor.DIM}Anúncios e eventos (em breve){Cor.RESET}")

    if pode_moderar(usuario):
        print()
        linha("─", Cor.DIM)
        print(f"  {Cor.BG_AZUL}{Cor.BRANCO} MODERAÇÃO {Cor.RESET}")
        print(f"  {Cor.AMARELO}[6]{Cor.RESET} Painel de moderação")
        print()
        linha("─", Cor.DIM)
        print(f"\n  {Cor.DIM}[0] Sair{Cor.RESET}")
    else:
        print(f"\n  {Cor.DIM}[0] Sair{Cor.RESET}")

    print()

    opcoes_validas = {"1", "2", "3", "4", "5", "0"}
    if pode_moderar(usuario):
        opcoes_validas.add("6")

    while True:
        cmd = entrada("  Escolha uma opção: ", obrigatorio=False).strip()
        if cmd in opcoes_validas:
            return cmd
        msg_erro("Opção inválida.")


# ─────────────────────────────────────────
#  TELA "EM BREVE" — Anúncios e Eventos
# ─────────────────────────────────────────
def tela_em_breve():
    limpar_tela()
    print()
    print(f"  {Cor.AZUL}{'═' * (LARGURA - 4)}{Cor.RESET}")
    print(f"  {Cor.BOLD}{Cor.BRANCO}  📢  ANÚNCIOS E EVENTOS — CRATO{Cor.RESET}")
    print(f"  {Cor.AZUL}{'═' * (LARGURA - 4)}{Cor.RESET}")
    print()
    print(f"  {Cor.AMARELO}Esta funcionalidade está sendo desenvolvida{Cor.RESET}")
    print(f"  {Cor.AMARELO}e estará disponível em breve.{Cor.RESET}")
    print()
    print(f"  {Cor.DIM}Em breve você poderá visualizar e publicar{Cor.RESET}")
    print(f"  {Cor.DIM}anúncios de eventos, feiras, shows e demais{Cor.RESET}")
    print(f"  {Cor.DIM}acontecimentos na cidade do Crato — CE.{Cor.RESET}")
    print()
    print(f"  {Cor.AZUL}{'─' * (LARGURA - 4)}{Cor.RESET}")
    print()
    print(f"  {Cor.DIM}[ENTER] Voltar ao menu principal{Cor.RESET}")
    input()


# ─────────────────────────────────────────
#  TELA DE SAÍDA
# ─────────────────────────────────────────
def tela_saida():
    limpar_tela()
    print()
    print(f"  {Cor.AZUL}{'═' * (LARGURA - 4)}{Cor.RESET}")
    print(f"  {Cor.BOLD}{Cor.BRANCO}  🏙️  SISTEMA CRATO{Cor.RESET}")
    print(f"  {Cor.AZUL}{'═' * (LARGURA - 4)}{Cor.RESET}")
    print()
    print(f"  {Cor.VERDE}Obrigado por usar o Sistema Crato!{Cor.RESET}")
    print(f"  {Cor.DIM}Juntos construímos uma cidade melhor.{Cor.RESET}")
    print()
    print(f"  {Cor.DIM}Cidade do Crato — Ceará — Brasil 🇧🇷{Cor.RESET}")
    print()
    print(f"  {Cor.AZUL}{'═' * (LARGURA - 4)}{Cor.RESET}")
