from dados.database import iniciar_tabelas, conectar, popular_postagens_exemplo
from utils.formatacao import linha_separadora, linha_dupla, limpar_tela
from utils.componentes import titulo
from servicos.autenticacao import menu_autenticacao
from servicos.feed import menu_feed
from servicos.postagens import menu_nova_postagem
from servicos.moderacao import menu_moderacao
from servicos.usuarios import ver_perfil


# Usuário sem login - apenas visualização do feed
def _menu_anonimo():
    while True:
        limpar_tela()
        titulo("CRATOVIA")

        print("  Bem-vindo(a) ao Cratovia!\n")
        print("  [1] Ver ocorrências e eventos")
        print("  [2] Entrar / Criar conta")
        print("  [0] Sair")

        linha_separadora()
        op = input("\n  Escolha: ").strip()

        if op == "1":
            menu_feed(None)
        elif op == "2":
            return menu_autenticacao()
        elif op == "0":
            _sair()


def _menu_comum(usuario):
    while True:
        limpar_tela()
        titulo("CRATOVIA")

        print(f"  Olá, {usuario['nome']}!\n")
        print("  [1] Ver ocorrências e eventos")
        print("  [2] Publicar ocorrência ou evento")
        print("  [3] Meu perfil")
        print("  [0] Sair")

        linha_separadora()
        op = input("\n  Escolha: ").strip()

        if op == "1":
            menu_feed(usuario)
        elif op == "2":
            menu_nova_postagem(usuario)
        elif op == "3":
            ver_perfil(usuario)
        elif op == "0":
            _sair()


def _menu_servidor(usuario):
    while True:
        limpar_tela()
        titulo("CRATOVIA")

        orgao = usuario.get("orgao") or "Servidor público"
        print(f"  Olá, {usuario['nome']} [{orgao}]!\n")
        print("  [1] Ver ocorrências e eventos")
        print("  [2] Publicar ocorrência ou evento")
        print("  [3] Meu perfil")
        print("  [0] Sair")

        linha_separadora()
        op = input("\n  Escolha: ").strip()

        if op == "1":
            menu_feed(usuario)
        elif op == "2":
            menu_nova_postagem(usuario)
        elif op == "3":
            ver_perfil(usuario)
        elif op == "0":
            _sair()


def _menu_moderador(usuario):
    while True:
        limpar_tela()
        titulo("CRATOVIA")

        pendentes = _contar_pendentes()
        aviso = f"  [{pendentes} pendente(s)]" if pendentes > 0 else ""

        print(f"  Olá, {usuario['nome']} [MOD]!\n")
        print("  [1] Ver ocorrências e eventos")
        print("  [2] Publicar ocorrência ou evento")
        print(f"  [3] Moderação{aviso}")
        print("  [4] Meu perfil")
        print("  [0] Sair")

        linha_separadora()
        op = input("\n  Escolha: ").strip()

        if op == "1":
            menu_feed(usuario)
        elif op == "2":
            menu_nova_postagem(usuario)
        elif op == "3":
            menu_moderacao(usuario)
        elif op == "4":
            ver_perfil(usuario)
        elif op == "0":
            _sair()


def _contar_pendentes():
    with conectar() as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM postagens WHERE status IN ('aguardando', 'oculto')"
        ).fetchone()[0]


def _sair():
    limpar_tela()
    print("\n  Até logo!\n")
    exit()


def main():
    iniciar_tabelas()
    popular_postagens_exemplo()

    usuario = _menu_anonimo()

    if usuario is None:
        _menu_anonimo()
    elif usuario.get("tipo") == "moderador":
        _menu_moderador(usuario)
    elif usuario.get("tipo") == "servidor":
        _menu_servidor(usuario)
    else:
        _menu_comum(usuario)


if __name__ == "__main__":
    main()