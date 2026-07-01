from datetime import datetime
from dados.database import conectar
from utils.formatacao import linha_separadora, limpar_tela
from utils.componentes import titulo, mensagem_sucesso, mensagem_erro


def _agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _listar_bairros():
    with conectar() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT id, nome FROM bairros ORDER BY nome"
        ).fetchall()]


def _listar_naturezas():
    with conectar() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT id, nome FROM naturezas ORDER BY nome"
        ).fetchall()]


def _selecionar_bairro():
    bairros = _listar_bairros()

    print("\n  Bairros disponíveis:\n")
    for i, b in enumerate(bairros, 1):
        print(f"  {i:2}. {b['nome']}")

    linha_separadora()

    while True:
        try:
            escolha = int(input("\n  Número do bairro: ").strip())
            if 1 <= escolha <= len(bairros):
                return bairros[escolha - 1]
            print("  Número fora do intervalo.")
        except ValueError:
            print("  Digite um número válido.")


def _selecionar_natureza():
    naturezas = _listar_naturezas()

    print("\n  Categorias disponíveis:\n")
    for i, n in enumerate(naturezas, 1):
        print(f"  {i}. {n['nome']}")

    linha_separadora()

    while True:
        try:
            escolha = int(input("\n  Número da categoria: ").strip())
            if 1 <= escolha <= len(naturezas):
                return naturezas[escolha - 1]
            print("  Número fora do intervalo.")
        except ValueError:
            print("  Digite um número válido.")


def _coletar_conteudo():
    print("\n  Texto completo (linha em branco para encerrar):\n")
    linhas = []
    while True:
        linha = input("  ")
        if linha == "":
            break
        linhas.append(linha)
    return "\n".join(linhas)


def _status_inicial(usuario):
    # - As postagens de servidor público são publicadas imediatamente já as demais aguarda moderação
    if usuario.get("tipo") == "servidor":
        return "aprovado"
    return "aguardando"


def criar_ocorrencia(usuario):
    limpar_tela()
    titulo("NOVA OCORRÊNCIA")

    titulo_post = input("  Título: ").strip()
    if not titulo_post:
        mensagem_erro("Título não pode estar vazio.")
        return

    descricao = input("  Descrição breve: ").strip()
    if not descricao:
        mensagem_erro("Descrição não pode estar vazia.")
        return

    print()
    bairro = _selecionar_bairro()
    local_bairro = input("\n  Endereço / ponto de referência (opcional): ").strip()

    print()
    natureza = _selecionar_natureza()

    conteudo = _coletar_conteudo()
    if not conteudo:
        mensagem_erro("Conteúdo não pode estar vazio.")
        return

    status = _status_inicial(usuario)

    with conectar() as conn:
        conn.execute("""
            INSERT INTO postagens
                (usuario_id, bairro_id, local_bairro, titulo, descricao,
                conteudo, natureza_id, status, criado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
            usuario["id"],
            bairro["id"],
            local_bairro or None,
            titulo_post,
            descricao,
            conteudo,
            natureza["id"],
            status,
            _agora()
        ))

    if status == "aprovado":
        mensagem_sucesso("Ocorrência publicada com sucesso!")
    else:
        mensagem_sucesso("Ocorrência enviada! Aguarda aprovação de um moderador.")

    input("  ENTER para continuar...")


def criar_evento(usuario):
    limpar_tela()
    titulo("NOVO EVENTO")

    titulo_post = input("  Título do evento: ").strip()
    if not titulo_post:
        mensagem_erro("Título não pode estar vazio.")
        return

    descricao = input("  Descrição breve: ").strip()
    if not descricao:
        mensagem_erro("Descrição não pode estar vazia.")
        return

    print()
    bairro = _selecionar_bairro()
    local_bairro = input("\n  Endereço / local do evento (opcional): ").strip()

    conteudo = _coletar_conteudo()
    if not conteudo:
        mensagem_erro("Conteúdo não pode estar vazio.")
        return

    status = _status_inicial(usuario)

    with conectar() as conn:
        conn.execute("""
            INSERT INTO anuncios_eventos
                (usuario_id, bairro_id, local_bairro, titulo, descricao,
                conteudo, status, criado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
            usuario["id"],
            bairro["id"],
            local_bairro or None,
            titulo_post,
            descricao,
            conteudo,
            status,
            _agora()
        ))

    if status == "aprovado":
        mensagem_sucesso("Evento publicado com sucesso!")
    else:
        mensagem_sucesso("Evento enviado! Aguarda aprovação de um moderador.")

    input("  ENTER para continuar...")


def menu_nova_postagem(usuario):
    limpar_tela()
    titulo("PUBLICAR")

    print("  O que deseja publicar?\n")
    print("  [1] Ocorrência")
    print("  [2] Evento")
    print("  [X] Voltar")

    linha_separadora()
    op = input("\n  Escolha: ").strip().upper()

    if op == "1":
        criar_ocorrencia(usuario)
    elif op == "2":
        criar_evento(usuario)