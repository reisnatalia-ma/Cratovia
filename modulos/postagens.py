from Data.database import conectar
from modulos.utils import cabecalho, pausar, agora, so_hora, formatar_data, paginar

# ── Buscar listas auxiliares ──────────────────────────────────────────────────
def buscar_bairros():
    with conectar() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM bairros ORDER BY nome").fetchall()]

def buscar_naturezas():
    with conectar() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM naturezas ORDER BY id").fetchall()]

# ── Criar postagem ────────────────────────────────────────────────────────────
def criar_postagem(usuario):
    bairros   = buscar_bairros()
    naturezas = buscar_naturezas()

    # Escolher bairro
    cabecalho("DIVULGAR OCORRÊNCIA — Bairro")
    pagina = 1
    while True:
        itens, pagina, total = paginar(bairros, 10, pagina)
        print(f"\n  Página {pagina}/{total}\n")
        for i, b in enumerate(itens, start=(pagina-1)*10+1):
            print(f"  [{i:>2}] {b['nome']}")
        print("\n  [>] Próxima  [<] Anterior  [X] Voltar")

        op = input("\n  Bairro: ").strip().upper()
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
            if 1 <= num <= len(bairros):
                bairro = bairros[num - 1]
                break
        except ValueError:
            pass
        print("  Opção inválida.")

    # Local dentro do bairro
    cabecalho("DIVULGAR OCORRÊNCIA — Local")
    local = input(f"  Local em {bairro['nome']}: ").strip()
    if not local:
        return

    # Título
    cabecalho("DIVULGAR OCORRÊNCIA — Título")
    print("  Escreva um título curto para a ocorrência.")
    titulo = input("  Título: ").strip()
    if not titulo:
        return

    # Conteúdo
    cabecalho("DIVULGAR OCORRÊNCIA — Descrição")
    print("  Descreva o que aconteceu. Pressione ENTER duas vezes para finalizar.\n")
    linhas = []
    while True:
        linha = input("  ")
        if linha == "" and linhas and linhas[-1] == "":
            break
        linhas.append(linha)
    conteudo = "\n".join(linhas).strip()
    if not conteudo:
        print("  Descrição vazia.")
        pausar()
        return

    # Natureza (opcional)
    cabecalho("DIVULGAR OCORRÊNCIA — Classificação")
    for i, n in enumerate(naturezas, 1):
        print(f"  [{i}] {n['nome']}")
    print("  [0] Não classificar")

    natureza_id = None
    op = input("\n  Classificação: ").strip()
    try:
        num = int(op)
        if 1 <= num <= len(naturezas):
            natureza_id = naturezas[num - 1]["id"]
    except ValueError:
        pass

    # Revisar e confirmar
    while True:
        cabecalho("DIVULGAR OCORRÊNCIA — Revisão")
        print(f"  Bairro:  {bairro['nome']}")
        print(f"  Local:   {local}")
        print(f"  Título:  {titulo}")
        print(f"\n  Descrição:\n  {conteudo[:200]}")
        print("\n  [S] Publicar  [E] Editar  [X] Cancelar")

        op = input("\n  Escolha: ").strip().upper()

        if op == "X":
            return

        elif op == "E":
            print("\n  [1] Título  [2] Descrição  [3] Local")
            campo = input("  Campo: ").strip()
            if campo == "1":
                titulo = input("  Novo título: ").strip() or titulo
            elif campo == "2":
                print("  Nova descrição (ENTER duas vezes para finalizar):\n")
                linhas = []
                while True:
                    linha = input("  ")
                    if linha == "" and linhas and linhas[-1] == "":
                        break
                    linhas.append(linha)
                novo = "\n".join(linhas).strip()
                if novo:
                    conteudo = novo
            elif campo == "3":
                local = input("  Novo local: ").strip() or local

        elif op == "S":
            status     = "aprovado" if usuario else "aguardando"
            usuario_id = usuario["id"] if usuario else None
            autor      = usuario["nome"] if usuario else "Anônimo"

            with conectar() as conn:
                conn.execute("""
                    INSERT INTO postagens
                    (bairro_id, local_bairro, titulo, conteudo, natureza_id,
                     usuario_id, autor_nome, status, criado_em)
                    VALUES (?,?,?,?,?,?,?,?,?)""",
                    (bairro["id"], local, titulo, conteudo, natureza_id,
                     usuario_id, autor, status, agora()))

            if status == "aprovado":
                print("\n  Ocorrência publicada com sucesso!")
            else:
                print("\n  Ocorrência enviada! Aguardando aprovação de um moderador.")
            pausar()
            return

# ── Exibir postagem completa ──────────────────────────────────────────────────
def ler_postagem(postagem_id, usuario):
    from modulos.interacoes import votar_util, denunciar

    with conectar() as conn:
        post = conn.execute("""
            SELECT p.*, b.nome AS bairro_nome, n.nome AS natureza_nome,
                   u.tipo AS autor_tipo, u.orgao AS autor_orgao
            FROM postagens p
            LEFT JOIN bairros b   ON b.id = p.bairro_id
            LEFT JOIN naturezas n ON n.id = p.natureza_id
            LEFT JOIN usuarios u  ON u.id = p.usuario_id
            WHERE p.id = ?
        """, (postagem_id,)).fetchone()

    if not post:
        print("  Postagem não encontrada.")
        pausar()
        return

    post = dict(post)
    cabecalho(post["bairro_nome"] or "?")

    print(f"  {so_hora(post['criado_em'])} — {post['titulo']}")
    if post["natureza_nome"]:
        print(f"  [{post['natureza_nome']}]")
    print(f"\n  Local: {post['local_bairro'] or 'Não informado'}")
    print("\n" + "-" * 50)
    print()
    for linha in post["conteudo"].split("\n"):
        print(f"  {linha}")
    print()
    print("-" * 50)

    # Autor
    autor = post["autor_nome"] or "Anônimo"
    tipo  = post.get("autor_tipo", "comum")
    if tipo == "moderador":
        autor += " [MOD]"
    elif tipo == "servidor":
        orgao = post.get("autor_orgao") or ""
        autor += f" [SERVIDOR — {orgao}]"
    print(f"  Publicado por: {autor}")
    print(f"  Data: {formatar_data(post['criado_em'])}")

    votos = post["votos_uteis"]
    print(f"\n  {votos} {'pessoa achou' if votos == 1 else 'pessoas acharam'} isso útil.")
    print("-" * 50)

    # Interações do usuário com a postagem
    if usuario:
        votar_util(postagem_id, usuario)
        denunciar(postagem_id, usuario)
    else:
        print("  Faça login para votar ou denunciar.")

    pausar()
