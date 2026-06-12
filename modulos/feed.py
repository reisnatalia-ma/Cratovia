from dados.database import conectar
from modulos.utils import cabecalho, pausar, so_hora, paginar
from modulos.postagens import ler_postagem, buscar_bairros, buscar_naturezas

# ── Buscar postagens aprovadas com filtros opcionais ─────────────────────────
def buscar_posts(bairro_id=None, natureza_id=None):
    where  = "WHERE p.status = 'aprovado'"
    params = []

    if bairro_id:
        where += " AND p.bairro_id = ?"
        params.append(bairro_id)
    if natureza_id:
        where += " AND p.natureza_id = ?"
        params.append(natureza_id)

    with conectar() as conn:
        return [dict(r) for r in conn.execute(f"""
            SELECT p.*, b.nome AS bairro_nome, n.nome AS natureza_nome
            FROM postagens p
            LEFT JOIN bairros b   ON b.id = p.bairro_id
            LEFT JOIN naturezas n ON n.id = p.natureza_id
            {where}
            ORDER BY p.criado_em DESC
        """, params).fetchall()]

# ── Exibir postagens completas ────────────────────────────────────────────────
def exibir_lista(posts, titulo, usuario):
    cabecalho(titulo)

    if not posts:
        print("  Nenhuma ocorrência encontrada.")
        pausar()
        return

    for post in posts:
        bairro = (post.get("bairro_nome") or "?").upper()
        hora   = so_hora(post["criado_em"])
        print(f"\n  {bairro} [{hora}] — {post['titulo']}")
        if post.get("natureza_nome"):
            print(f"  [{post['natureza_nome']}]")
        print(f"  Local: {post['local_bairro'] or 'Não informado'}")
        print()
        for linha in post["conteudo"].split("\n"):
            print(f"  {linha}")
        votos = post["votos_uteis"]
        print(f"\n  {votos} {'pessoa achou' if votos == 1 else 'pessoas acharam'} isso útil.")
        print("  " + "-" * 46)

    if usuario:
        print("\n  Digite o número da postagem para interagir, ou [X] para voltar.")
        for i, post in enumerate(posts, 1):
            print(f"  [{i}] {post['titulo'][:45]}")
        op = input("\n  Escolha: ").strip().upper()
        if op != "X":
            try:
                num = int(op)
                if 1 <= num <= len(posts):
                    ler_postagem(posts[num - 1]["id"], usuario)
            except ValueError:
                pass
    else:
        print("\n  Faça login para interagir.")
        pausar()

# ── 1. Feed geral ─────────────────────────────────────────────────────────────
def feed_geral(usuario):
    posts = buscar_posts()
    exibir_lista(posts, "ÚLTIMAS NOTÍCIAS E OCORRÊNCIAS", usuario)

# ── 2. Feed por bairro ────────────────────────────────────────────────────────
def feed_por_bairro(usuario):
    bairros = buscar_bairros()
    pagina  = 1
    filtro_letra = None

    while True:
        lista = bairros
        if filtro_letra:
            lista = [b for b in bairros if b["nome"].upper().startswith(filtro_letra)]

        cabecalho("FILTRAR POR BAIRRO")
        itens, pagina, total = paginar(lista, 10, pagina)
        print(f"  Página {pagina}/{total}")
        if filtro_letra:
            print(f"  Filtrando por letra: {filtro_letra}")
        print()

        for i, b in enumerate(itens, start=(pagina-1)*10+1):
            print(f"  [{i:>2}] {b['nome']}")

        print("\n  Número = Selecionar   [letra] Filtrar   [*] Todos   [>] [<] Páginas   [X] Voltar")
        op = input("\n  Comando: ").strip().upper()

        if op == "X":
            return
        if op == "*":
            filtro_letra = None
            pagina = 1
            continue
        if op == ">" and pagina < total:
            pagina += 1
            continue
        if op == "<" and pagina > 1:
            pagina -= 1
            continue
        if len(op) == 1 and op.isalpha():
            filtro_letra = op
            pagina = 1
            continue
        try:
            num = int(op)
            if 1 <= num <= len(lista):
                bairro = lista[num - 1]
                posts  = buscar_posts(bairro_id=bairro["id"])
                exibir_lista(posts, f"BAIRRO: {bairro['nome'].upper()}", usuario)
                continue
        except ValueError:
            pass
        print("  Opção inválida.")

# ── 3. Feed por natureza ──────────────────────────────────────────────────────
def feed_por_natureza(usuario):
    naturezas = buscar_naturezas()

    while True:
        cabecalho("FILTRAR POR TIPO DE OCORRÊNCIA")
        for i, n in enumerate(naturezas, 1):
            print(f"  [{i}] {n['nome']}")
        print("  [X] Voltar")

        op = input("\n  Tipo: ").strip().upper()
        if op == "X":
            return
        try:
            num = int(op)
            if 1 <= num <= len(naturezas):
                nat   = naturezas[num - 1]
                posts = buscar_posts(natureza_id=nat["id"])
                exibir_lista(posts, f"TIPO: {nat['nome'].upper()}", usuario)
                continue
        except ValueError:
            pass
        print("  Opção inválida.")