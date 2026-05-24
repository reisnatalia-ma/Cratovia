from utils.formatacao import linha_dupla, linha_separadora, centralizar, LARGURA


def titulo(texto):
    linha_dupla()
    centralizar(f"  {texto}  ")
    linha_dupla()
    print()


def mensagem_sucesso(texto):
    print(f"\n[OK] {texto}\n")


def mensagem_erro(texto):
    print(f"\n[ERRO] {texto}\n")


def mensagem_info(texto):
    print(f"\n[INFO] {texto}\n")


def card_postagem(numero, postagem):
    destaque = " ★ DESTAQUE" if postagem.get("destaque") else ""
    tipo_label = " [EVENTO]" if postagem.get("tipo") == "evento" else ""
    print(f"\n  {numero}.{destaque}{tipo_label} {postagem['titulo']}")
    print(f"     {postagem['descricao'][:80]}")
    print(f"     Bairro: {postagem['bairro']} | {postagem['data']} {postagem['hora']}")
    if postagem.get("natureza"):
        print(f"     Natureza: {postagem['natureza']}")
    linha_separadora()


def exibir_usuario_logado(usuario):
    if usuario:
        tipo = usuario["tipo"].capitalize()
        print(f"  Usuário: {usuario['nome']} ({tipo})")
    else:
        print("  Acesso sem login")
    linha_separadora()