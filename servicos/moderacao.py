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

        # Busca o nome do autor
        with conectar() as conn:
            autor_row = conn.execute(
                "SELECT nome, tipo, orgao FROM usuarios WHERE id=?",
                (post.get("usuario_id"),)
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

        print(f"  Autor:     {autor}")

        # Se denunciada, lista quem denunciou
        if post["status"] == "oculto":
            with conectar() as conn:
                denunciantes = conn.execute("""
                    SELECT u.nome FROM denuncias_fake df
                    JOIN usuarios u ON u.id = df.usuario_id
                    WHERE df.postagem_id = ?
                """, (post["id"],)).fetchall()
            if denunciantes:
                nomes = ", ".join(row[0] for row in denunciantes)
                print(f"  Denunciado por: {nomes}")

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
            print("  [A] Aprovar / Restaurar postagem")
        print("  [R] Rejeitar / Excluir postagem")
        print("  [X] Voltar")

        op = input("\n  Ação: ").strip().upper()

        if op == "X":
            return

        elif op == "A" and pode:
            with conectar() as conn:
                conn.execute(
                    "UPDATE postagens SET status='aprovado', aprovado_por=?, denuncias=0 WHERE id=?",
                    (usuario["id"], post["id"])
                )
                # Limpa as denúncias registradas
                conn.execute(
                    "DELETE FROM denuncias_fake WHERE postagem_id=?",
                    (post["id"],)
                )
            print("\n  Postagem aprovada e restaurada!")
            pausar()
            return

        elif op == "R":
            confirma = input("  Tem certeza que deseja excluir? (S/N): ").strip().upper()
            if confirma == "S":
                with conectar() as conn:
                    conn.execute("DELETE FROM denuncias_fake WHERE postagem_id=?", (post["id"],))
                    conn.execute("DELETE FROM votos_uteis WHERE postagem_id=?", (post["id"],))
                    conn.execute("DELETE FROM postagens WHERE id=?", (post["id"],))
                print("\n  Postagem excluída.")
                pausar()
                return

        else:
            print("  Opção inválida ou sem permissão.")
