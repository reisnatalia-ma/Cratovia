from Data.database import conectar
from modulos.utils import cabecalho, pausar, so_hora, paginar
from modulos.postagens import ler_postagem, buscar_bairros, buscar_naturezas

POR_PAGINA = 5

# ── Linha resumida de postagem ────────────────────────────────────────────────
def linha_post(numero, post):
    bairro = (post.get("bairro_nome") or "?").upper()
    hora   = so_hora(post["criado_em"])
    titulo = post["titulo"][:45]
    return f"  {numero} - {bairro} [{hora}] : {titulo}"

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

# ── Exibir lista com paginação ────────────────────────────────────────────────
def exibir_lista(posts, titulo, usuario):
    pagina = 1
    while True:
        itens, pagina, total = paginar(posts, POR_PAGINA, pagina)

        cabecalho(titulo)
        print(f"  Página {pagina}/{total}\n")

        if not posts:
            print("  Nenhuma ocorrência encontrada.")
            pausar()
            return

        for i, post in enumerate(itens, start=(pagina-1)*POR_PAGINA+1):
            print(linha_post(i, post))

        print("\n  Número = Ler   [R] Recarregar   [>] Próxima   [<] Anterior   [X] Voltar")
        op = input("\n  Comando: ").strip().upper()

        if op == "X":
            return
        if op == "R":
            pagina = 1
            continue
        if op == ">" and pagina < total:
            pagina += 1
            continue
        if op == "<" and pagina > 1:
            pagina -= 1
            continue
        try:
            num = int(op)
            if 1 <= num <= len(posts):
                ler_postagem(posts[num - 1]["id"], usuario)
                posts = buscar_posts()  # recarrega após leitura
                continue
            if 1 <= num <= total:
                pagina = num
                continue
        except ValueError:
            pass
        print("  Opção inválida.")

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

# ── 5. Anúncios e eventos ─────────────────────────────────────────────────────
def ver_anuncios(usuario):
    cabecalho("ANÚNCIOS E EVENTOS EM CRATO")

    with conectar() as conn:
        anuncios = [dict(r) for r in conn.execute(
            "SELECT * FROM anuncios ORDER BY criado_em DESC"
        ).fetchall()]

    if not anuncios:
        print("  Nenhum anúncio cadastrado.")
        pausar()
        return

    for a in anuncios:
        tipo = "EVENTO" if a["tipo"] == "evento" else "AVISO"
        print(f"\n  [{tipo}] {a['titulo']}")
        if a.get("data"):
            print(f"  Data:  {a['data']}")
        if a.get("local"):
            print(f"  Local: {a['local']}")
        print(f"  {a['descricao']}")
        print("  " + "·" * 46)

    pausar()
