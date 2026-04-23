from Data.database import conectar
from modulos.utils import cabecalho, pausar, so_hora, formatar_data, paginar

POR_PAGINA = 5

# Quais naturezas cada órgão pode aprovar
PERMISSOES = {
    "DETRAN":                       ["Acidente de trânsito", "Outros"],
    "SAMU":                         ["Acidente de trânsito", "Saúde pública", "Outros"],
    "Corpo de Bombeiros":           ["Incêndio", "Alagamento", "Desastre ambiental", "Outros"],
    "Secretaria de Infraestrutura": ["Falta de infraestrutura", "Alagamento", "Outros"],
    "Secretaria de Saúde":          ["Saúde pública", "Outros"],
}

# ── Verificar se o usuário pode aprovar uma postagem ─────────────────────────
def pode_aprovar(usuario, natureza_nome):
    if usuario["tipo"] == "moderador":
        return True
    orgao     = usuario.get("orgao") or ""
    permitidas = PERMISSOES.get(orgao, [])
    return not natureza_nome or natureza_nome in permitidas

# ── Buscar postagens por status ───────────────────────────────────────────────
def buscar_fila(status):
    with conectar() as conn:
        return [dict(r) for r in conn.execute("""
            SELECT p.*, b.nome AS bairro_nome, n.nome AS natureza_nome
            FROM postagens p
            LEFT JOIN bairros b   ON b.id = p.bairro_id
            LEFT JOIN naturezas n ON n.id = p.natureza_id
            WHERE p.status = ?
            ORDER BY p.criado_em ASC
        """, (status,)).fetchall()]

# ── Linha resumida para a fila ────────────────────────────────────────────────
def linha_fila(numero, post):
    bairro = (post.get("bairro_nome") or "?").upper()
    hora   = so_hora(post["criado_em"])
    titulo = post["titulo"][:38]
    status = post["status"]
    tag    = "[AGUARDANDO]" if status == "aguardando" else f"[DENUNCIADO x{post['denuncias']}]"
    return f"  {numero} {tag} {bairro} [{hora}] {titulo}"

# ── Analisar uma postagem da fila ─────────────────────────────────────────────
def analisar_postagem(post, usuario):
    while True:
        cabecalho("ANALISAR POSTAGEM")

        nat  = post.get("natureza_nome") or "Não classificada"
        pode = pode_aprovar(usuario, nat)

        print(f"  Bairro:    {post.get('bairro_nome', '?')}")
        print(f"  Título:    {post['titulo']}")
        print(f"  Natureza:  {nat}")
        print(f"  Status:    {post['status']}")
        print(f"  Denúncias: {post['denuncias']}")
        print(f"  Data:      {formatar_data(post['criado_em'])}")
        print(f"  Autor:     {post.get('autor_nome') or 'Anônimo'}")
        print("\n" + "-" * 50)
        print()
        for linha in post["conteudo"].split("\n"):
            print(f"  {linha}")
        print()
        print("-" * 50)

        if not pode:
            print(f"\n  Seu órgão não pode aprovar ocorrências do tipo '{nat}'.")

        print()
        if pode:
            print("  [A] Aprovar")
        print("  [R] Rejeitar/Excluir")
        print("  [X] Voltar")

        op = input("\n  Ação: ").strip().upper()

        if op == "X":
            return
        elif op == "A" and pode:
            with conectar() as conn:
                conn.execute(
                    "UPDATE postagens SET status='aprovado', aprovado_por=? WHERE id=?",
                    (usuario["id"], post["id"])
                )
            print("\n  Postagem aprovada!")
            pausar()
            return
        elif op == "R":
            confirma = input("  Tem certeza que deseja excluir? (S/N): ").strip().upper()
            if confirma == "S":
                with conectar() as conn:
                    conn.execute("DELETE FROM postagens WHERE id=?", (post["id"],))
                print("\n  Postagem excluída.")
                pausar()
                return
        else:
            print("  Opção inválida ou sem permissão.")

# ── Exibir fila de postagens ──────────────────────────────────────────────────
def exibir_fila(status, titulo, usuario):
    pagina = 1
    while True:
        posts = buscar_fila(status)
        itens, pagina, total = paginar(posts, POR_PAGINA, pagina)

        cabecalho(titulo)
        print(f"  {len(posts)} postagem(ns) na fila — Página {pagina}/{total}\n")

        if not posts:
            print("  Nenhuma postagem nesta fila.")
            pausar()
            return

        for i, post in enumerate(itens, start=(pagina-1)*POR_PAGINA+1):
            print(linha_fila(i, post))

        print("\n  Número = Analisar   [>] [<] Páginas   [X] Voltar")
        op = input("\n  Comando: ").strip().upper()

        if op == "X":
            return
        if op == ">" and pagina < total:
            pagina += 1
            continue
        if op == "<" and pagina > 1:
            pagina -= 1
            continue
        try:
            num = int(op)
            if 1 <= num <= len(posts):
                analisar_postagem(posts[num - 1], usuario)
                pagina = 1
                continue
        except ValueError:
            pass
        print("  Opção inválida.")

# ── Menu de moderação ─────────────────────────────────────────────────────────
def menu_moderacao(usuario):
    while True:
        cabecalho("PAINEL DE MODERAÇÃO")

        tipo  = usuario["tipo"].upper()
        orgao = usuario.get("orgao") or ""
        print(f"  Usuário: {usuario['nome']} [{tipo}]")
        if orgao:
            print(f"  Órgão:   {orgao}")

        with conectar() as conn:
            n_aguardando = conn.execute(
                "SELECT COUNT(*) FROM postagens WHERE status='aguardando'"
            ).fetchone()[0]
            n_ocultas = conn.execute(
                "SELECT COUNT(*) FROM postagens WHERE status='oculto'"
            ).fetchone()[0]

        print(f"\n  [1] Aguardando aprovação  ({n_aguardando})")
        print(f"  [2] Denunciadas/ocultas   ({n_ocultas})")

        if usuario["tipo"] == "moderador":
            n_total = conn.execute("SELECT COUNT(*) FROM postagens").fetchone()[0]
            print(f"  [3] Todas as postagens    ({n_total})")
            print(f"  [4] Gerenciar códigos de acesso")

        print("  [X] Voltar")

        op = input("\n  Escolha: ").strip().upper()

        if op == "X":
            return
        elif op == "1":
            exibir_fila("aguardando", "AGUARDANDO APROVAÇÃO", usuario)
        elif op == "2":
            exibir_fila("oculto", "POSTAGENS DENUNCIADAS", usuario)
        elif op == "3" and usuario["tipo"] == "moderador":
            exibir_todas(usuario)
        elif op == "4" and usuario["tipo"] == "moderador":
            gerenciar_codigos()
        else:
            print("  Opção inválida.")

# ── Todas as postagens (só moderador) ────────────────────────────────────────
def exibir_todas(usuario):
    pagina = 1
    while True:
        with conectar() as conn:
            posts = [dict(r) for r in conn.execute("""
                SELECT p.*, b.nome AS bairro_nome, n.nome AS natureza_nome
                FROM postagens p
                LEFT JOIN bairros b   ON b.id = p.bairro_id
                LEFT JOIN naturezas n ON n.id = p.natureza_id
                ORDER BY p.criado_em DESC
            """).fetchall()]

        itens, pagina, total = paginar(posts, POR_PAGINA, pagina)
        cabecalho("TODAS AS POSTAGENS")
        print(f"  Total: {len(posts)} — Página {pagina}/{total}\n")

        for i, post in enumerate(itens, start=(pagina-1)*POR_PAGINA+1):
            print(linha_fila(i, post))

        print("\n  Número = Analisar   [>] [<] Páginas   [X] Voltar")
        op = input("\n  Comando: ").strip().upper()

        if op == "X":
            return
        if op == ">" and pagina < total:
            pagina += 1
            continue
        if op == "<" and pagina > 1:
            pagina -= 1
            continue
        try:
            num = int(op)
            if 1 <= num <= len(posts):
                analisar_postagem(posts[num - 1], usuario)
                pagina = 1
                continue
        except ValueError:
            pass
        print("  Opção inválida.")

# ── Gerenciar códigos de acesso ───────────────────────────────────────────────
def gerenciar_codigos():
    while True:
        cabecalho("CÓDIGOS DE ACESSO")

        with conectar() as conn:
            codigos = [dict(r) for r in conn.execute(
                "SELECT * FROM codigos_acesso ORDER BY tipo, orgao"
            ).fetchall()]

        for c in codigos:
            usado = "[USADO]" if c["usado"] else "[DISPONÍVEL]"
            orgao = f" — {c['orgao']}" if c.get("orgao") else ""
            print(f"  {c['codigo']}  {c['tipo'].upper()}{orgao}  {usado}")

        print("\n  [1] Adicionar código  [2] Reativar código  [X] Voltar")
        op = input("\n  Ação: ").strip().upper()

        if op == "X":
            return
        elif op == "1":
            codigo = input("  Novo código: ").strip().upper()
            print("  [1] Moderador  [2] Servidor público")
            tipo_op = input("  Tipo: ").strip()
            tipo    = "moderador" if tipo_op == "1" else "servidor"
            orgao   = input("  Órgão (deixe vazio se moderador): ").strip() or None
            with conectar() as conn:
                try:
                    conn.execute(
                        "INSERT INTO codigos_acesso (codigo,tipo,orgao) VALUES (?,?,?)",
                        (codigo, tipo, orgao)
                    )
                    print("  Código adicionado!")
                except Exception as e:
                    print(f"  Erro: {e}")
            pausar()
        elif op == "2":
            codigo = input("  Código a reativar: ").strip().upper()
            with conectar() as conn:
                r = conn.execute("UPDATE codigos_acesso SET usado=0 WHERE codigo=?", (codigo,))
                print("  Reativado!" if r.rowcount else "  Código não encontrado.")
            pausar()
