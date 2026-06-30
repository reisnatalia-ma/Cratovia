from dados.database import conectar
from utils.formatacao import linha_separadora, linha_dupla, limpar_tela, formatar_data
from utils.componentes import titulo, mensagem_erro
from servicos.interacoes import votar_util, denunciar, ver_comentarios


POSTAGENS_POR_PAGINA = 10


def _cabecalho_feed(titulo_secao, pagina, total_paginas):
    linha_dupla()
    print(f"  {titulo_secao}".center(60))
    print(f"  Página {pagina} de {total_paginas}".center(60))
    linha_dupla()
    print()


def _exibir_card(i, post):
    print(f"  [{i:2}] {post['titulo']}")
    print(f"        {post['descricao']}")
    print(f"        {formatar_data(post['criado_em'])}")
    linha_separadora()


def _paginar(lista, pagina):
    inicio = (pagina - 1) * POSTAGENS_POR_PAGINA
    fim = inicio + POSTAGENS_POR_PAGINA
    return lista[inicio:fim]


def _total_paginas(lista):
    total = len(lista)
    if total == 0:
        return 1
    return (total + POSTAGENS_POR_PAGINA - 1) // POSTAGENS_POR_PAGINA


def _ver_postagem(post, usuario):
    while True:
        limpar_tela()
        linha_dupla()
        print(f"  {post['titulo']}".center(60))
        linha_dupla()

        print(f"\n  Bairro:   {post.get('bairro_nome') or '—'}")
        if post.get("local_bairro"):
            print(f"  Local:    {post['local_bairro']}")
        print(f"  Natureza: {post.get('natureza_nome') or '—'}")
        print(f"  Data:     {formatar_data(post['criado_em'])}")
        print(f"  Votos úteis: {post['votos_uteis']}")

        # Autor
        with conectar() as conn:
            autor_row = conn.execute(
                "SELECT nome, tipo, orgao FROM usuarios WHERE id=?",
                (post["usuario_id"],)
            ).fetchone() if post.get("usuario_id") else None

        if autor_row:
            autor_row = dict(autor_row)
            autor = autor_row["nome"]
            if autor_row["tipo"] == "moderador":
                autor += " [MOD]"
            elif autor_row["tipo"] == "servidor":
                autor += f" [SERVIDOR — {autor_row.get('orgao') or ''}]"
        else:
            autor = "Anônimo"

        print(f"  Autor:    {autor}")

        print("\n" + "-" * 60)
        print()
        for linha in post["conteudo"].split("\n"):
            print(f"  {linha}")
        print()
        linha_separadora()

        if usuario:
            print("  [U] Útil   [D] Denunciar   [C] Comentários   [X] Voltar")
            op = input("\n  Ação: ").strip().upper()

            if op == "X":
                return
            elif op == "U":
                votar_util(post["id"], usuario)
                input("  ENTER para continuar...")
            elif op == "D":
                denunciar(post["id"], usuario)
                input("  ENTER para continuar...")
            elif op == "C":
                ver_comentarios(post["id"], usuario)
        else:
            print("  [C] Ver comentários   [X] Voltar")
            op = input("\n  Ação: ").strip().upper()
            if op == "X":
                return
            elif op == "C":
                ver_comentarios(post["id"], usuario)


def _buscar_ocorrencias(bairro_id=None, natureza_id=None):
    query = """
        SELECT p.*, b.nome AS bairro_nome, n.nome AS natureza_nome
        FROM postagens p
        LEFT JOIN bairros b ON b.id = p.bairro_id
        LEFT JOIN naturezas n ON n.id = p.natureza_id
        WHERE p.status = 'aprovado'
    """
    params = []

    if bairro_id:
        query += " AND p.bairro_id = ?"
        params.append(bairro_id)

    if natureza_id:
        query += " AND p.natureza_id = ?"
        params.append(natureza_id)

    query += " ORDER BY p.criado_em DESC"

    with conectar() as conn:
        return [dict(r) for r in conn.execute(query, params).fetchall()]

def listar_ocorrencias(usuario, bairro_id=None, natureza_id=None):
    pagina = 1

    while True:
        ocorrencias = _buscar_ocorrencias(bairro_id, natureza_id)
        total = _total_paginas(ocorrencias)
        pagina_atual = _paginar(ocorrencias, pagina)

        limpar_tela()
        _cabecalho_feed("OCORRÊNCIAS", pagina, total)

        if not ocorrencias:
            print("  Nenhuma ocorrência encontrada.")
            linha_separadora()
            input("\n  ENTER para voltar...")
            return

        for i, post in enumerate(pagina_atual, 1):
            _exibir_card(i, post)

        print()
        print("  Número → abrir postagem", end="")
        if pagina > 1:
            print("   [A] Anterior", end="")
        if pagina < total:
            print("   [P] Próxima", end="")
        print("   [X] Voltar")

        op = input("\n  Ação: ").strip().upper()

        if op == "X":
            return
        elif op == "P" and pagina < total:
            pagina += 1
        elif op == "A" and pagina > 1:
            pagina -= 1
        else:
            try:
                num = int(op)
                if 1 <= num <= len(pagina_atual):
                    _ver_postagem(pagina_atual[num - 1], usuario)
            except ValueError:
                pass


def filtrar_por_bairro(usuario):
    with conectar() as conn:
        bairros = [dict(r) for r in conn.execute(
            "SELECT id, nome FROM bairros ORDER BY nome"
        ).fetchall()]

    limpar_tela()
    titulo("FILTRAR POR BAIRRO")

    for i, b in enumerate(bairros, 1):
        print(f"  {i:2}. {b['nome']}")

    linha_separadora()

    try:
        escolha = int(input("\n  Número do bairro: ").strip())
        if 1 <= escolha <= len(bairros):
            bairro = bairros[escolha - 1]
            listar_ocorrencias(usuario, bairro_id=bairro["id"])
        else:
            mensagem_erro("Número fora do intervalo.")
            input("  ENTER para continuar...")
    except ValueError:
        mensagem_erro("Digite um número válido.")
        input("  ENTER para continuar...")


def filtrar_por_natureza(usuario):
    with conectar() as conn:
        naturezas = [dict(r) for r in conn.execute(
            "SELECT id, nome FROM naturezas ORDER BY nome"
        ).fetchall()]

    limpar_tela()
    titulo("FILTRAR POR CATEGORIA")

    for i, n in enumerate(naturezas, 1):
        print(f"  {i}. {n['nome']}")

    linha_separadora()

    try:
        escolha = int(input("\n  Número da categoria: ").strip())
        if 1 <= escolha <= len(naturezas):
            natureza = naturezas[escolha - 1]
            listar_ocorrencias(usuario, natureza_id=natureza["id"])
        else:
            mensagem_erro("Número fora do intervalo.")
            input("  ENTER para continuar...")
    except ValueError:
        mensagem_erro("Digite um número válido.")
        input("  ENTER para continuar...")


def listar_eventos(usuario):
    pagina = 1

    while True:
        with conectar() as conn:
            eventos = [dict(r) for r in conn.execute("""
                SELECT e.*, b.nome AS bairro_nome
                FROM anuncios_eventos e
                LEFT JOIN bairros b ON b.id = e.bairro_id
                WHERE e.status = 'aprovado'
                ORDER BY e.criado_em DESC
            """).fetchall()]

        total = _total_paginas(eventos)
        pagina_atual = _paginar(eventos, pagina)

        limpar_tela()
        _cabecalho_feed("EVENTOS", pagina, total)

        if not eventos:
            print("  Nenhum evento encontrado.")
            linha_separadora()
            input("\n  ENTER para voltar...")
            return

        for i, ev in enumerate(pagina_atual, 1):
            _exibir_card(i, ev)

        print()
        print("  Número → abrir evento", end="")
        if pagina > 1:
            print("   [A] Anterior", end="")
        if pagina < total:
            print("   [P] Próxima", end="")
        print("   [X] Voltar")

        op = input("\n  Ação: ").strip().upper()

        if op == "X":
            return
        elif op == "P" and pagina < total:
            pagina += 1
        elif op == "A" and pagina > 1:
            pagina -= 1
        else:
            try:
                num = int(op)
                if 1 <= num <= len(pagina_atual):
                    _ver_evento(pagina_atual[num - 1], usuario)
            except ValueError:
                pass


def _ver_evento(ev, usuario):
    limpar_tela()
    linha_dupla()
    print(f"  {ev['titulo']}".center(60))
    linha_dupla()

    print(f"\n  Bairro: {ev.get('bairro_nome') or '—'}")
    if ev.get("local_bairro"):
        print(f"  Local:  {ev['local_bairro']}")
    print(f"  Data:   {formatar_data(ev['criado_em'])}")

    print("\n" + "-" * 60)
    print()
    print(f"  {ev['descricao']}")
    if ev.get("conteudo"):
        print()
        for linha in ev["conteudo"].split("\n"):
            print(f"  {linha}")
    print()
    linha_separadora()

    input("  ENTER para voltar...")


def menu_feed(usuario):
    while True:
        limpar_tela()
        titulo("FEED — CRATOVIA")

        print("  [1] Ver ocorrências")
        print("  [2] Filtrar por bairro")
        print("  [3] Filtrar por categoria")
        print("  [4] Ver eventos")
        print("  [X] Voltar ao menu principal")

        linha_separadora()
        op = input("\n  Escolha: ").strip().upper()

        if op == "1":
            listar_ocorrencias(usuario)
        elif op == "2":
            filtrar_por_bairro(usuario)
        elif op == "3":
            filtrar_por_natureza(usuario)
        elif op == "4":
            listar_eventos(usuario)
        elif op == "X":
            return
