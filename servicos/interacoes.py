from datetime import datetime
from dados.database import conectar

LIMITE_DENUNCIAS = 5


def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Votar útil em uma postagem
def votar_util(postagem_id, usuario):
    uid = usuario["id"]

    with conectar() as conn:
        ja_votou = conn.execute(
            "SELECT 1 FROM votos_uteis WHERE usuario_id=? AND postagem_id=?",
            (uid, postagem_id)
        ).fetchone()

        if ja_votou:
            conn.execute(
                "DELETE FROM votos_uteis WHERE usuario_id=? AND postagem_id=?",
                (uid, postagem_id)
            )
            conn.execute(
                "UPDATE postagens SET votos_uteis = votos_uteis - 1 WHERE id=?",
                (postagem_id,)
            )
            conn.execute("""
                UPDATE usuarios SET relevancia = relevancia - 1
                WHERE id = (SELECT usuario_id FROM postagens WHERE id=?)
            """, (postagem_id,))

            votos = conn.execute(
                "SELECT votos_uteis FROM postagens WHERE id=?", (postagem_id,)
            ).fetchone()[0]
            print(f"  Voto removido. {votos} {'pessoa achou' if votos == 1 else 'pessoas acharam'} isso útil.")
            return

        conn.execute(
            "INSERT INTO votos_uteis (usuario_id, postagem_id) VALUES (?,?)",
            (uid, postagem_id)
        )
        conn.execute("""
            UPDATE usuarios SET relevancia = relevancia + 1
            WHERE id = (SELECT usuario_id FROM postagens WHERE id=?)
        """, (postagem_id,))

        votos = conn.execute(
            "SELECT votos_uteis FROM postagens WHERE id=?", (postagem_id,)
        ).fetchone()[0]

    print(f"  {votos} {'pessoa achou' if votos == 1 else 'pessoas acharam'} isso útil.")

# Denunciar postagem
def denunciar(postagem_id, usuario):
    uid = usuario["id"]

    with conectar() as conn:
        ja_denunciou = conn.execute(
            "SELECT 1 FROM denuncias_fake WHERE usuario_id=? AND postagem_id=?",
            (uid, postagem_id)
        ).fetchone()

        if ja_denunciou:
            print("  Você já denunciou esta postagem.")
            return

        resp = input("  Denunciar como fake news? (S/N): ").strip().upper()
        if resp != "S":
            return

        conn.execute(
            "INSERT INTO denuncias_fake (usuario_id, postagem_id) VALUES (?,?)",
            (uid, postagem_id)
        )
        conn.execute("""
                UPDATE usuarios SET relevancia = relevancia - 1
                WHERE id = (SELECT usuario_id FROM postagens WHERE id=?)
            """, (postagem_id,))
            
        conn.execute(
            "UPDATE postagens SET denuncias = denuncias + 1 WHERE id=?",
            (postagem_id,)
        )

        total = conn.execute(
            "SELECT denuncias FROM postagens WHERE id=?", (postagem_id,)
        ).fetchone()[0]
        

        if total >= LIMITE_DENUNCIAS:
            conn.execute(
                "UPDATE postagens SET status='oculto' WHERE id=?", (postagem_id,)
            )
            print("  Esta postagem foi ocultada por excesso de denúncias e será revisada.")
        else:
            print("  Denúncia registrada.")

# Comentários
def ver_comentarios(postagem_id, usuario):
    while True:
        with conectar() as conn:
            comentarios = [dict(r) for r in conn.execute("""
                SELECT c.*, u.nome AS autor_nome
                FROM comentarios c
                LEFT JOIN usuarios u ON u.id = c.usuario_id
                WHERE c.postagem_id = ? AND c.resposta_para IS NULL
                ORDER BY c.criado_em ASC
            """, (postagem_id,)).fetchall()]

        print("\n" + "=" * 50)
        print("  COMENTÁRIOS")
        print("=" * 50)

        if not comentarios:
            print("  Nenhum comentário ainda.")
        else:
            for i, c in enumerate(comentarios, 1):
                autor = c["autor_nome"] or "Anônimo"
                print(f"\n  [{i}] {autor} — {c['criado_em'][11:16]}")
                print(f"  {c['conteudo']}")

                with conectar() as conn:
                    respostas = [dict(r) for r in conn.execute("""
                        SELECT c.*, u.nome AS autor_nome
                        FROM comentarios c
                        LEFT JOIN usuarios u ON u.id = c.usuario_id
                        WHERE c.resposta_para = ?
                        ORDER BY c.criado_em ASC
                    """, (c["id"],)).fetchall()]

                for r in respostas:
                    autor_r = r["autor_nome"] or "Anônimo"
                    print(f"     ↳ {autor_r} — {r['criado_em'][11:16]}: {r['conteudo']}")

                print("  " + "-" * 44)

        if usuario:
            print("\n  [C] Comentar   [I] Interagir   [X] Voltar")
            op = input("\n  Ação: ").strip().upper()

            if op == "X":
                return

            elif op == "C":
                texto = input("  Comentário: ").strip()
                if texto:
                    with conectar() as conn:
                        conn.execute(
                            "INSERT INTO comentarios (postagem_id, usuario_id, conteudo, criado_em) VALUES (?,?,?,?)",
                            (postagem_id, usuario["id"], texto, agora())
                        )
                    print("  Comentário publicado!")

            elif op == "I":
                try:
                    num = int(input("  Número do comentário: ").strip())
                    if 1 <= num <= len(comentarios):
                        c = comentarios[num - 1]
                        print(f"\n  [{num}] {c['autor_nome']} — {c['conteudo']}")
                        print("  [U] Útil   [D] Denunciar   [R] Responder   [X] Cancelar")
                        acao = input("\n  Ação: ").strip().upper()

                        if acao == "U":
                            _votar_comentario(c["id"], usuario)
                        elif acao == "D":
                            _denunciar_comentario(c["id"], usuario)
                        elif acao == "R":
                            texto = input("  Resposta: ").strip()
                            if texto:
                                with conectar() as conn:
                                    conn.execute(
                                        "INSERT INTO comentarios (postagem_id, usuario_id, resposta_para, conteudo, criado_em) VALUES (?,?,?,?,?)",
                                        (postagem_id, usuario["id"], c["id"], texto, agora())
                                    )
                                print("  Resposta publicada!")
                except ValueError:
                    pass
        else:
            print("\n  Faça login para comentar.")
            input("  ENTER para voltar...")
            return

# Votar útil em comentári0
def _votar_comentario(comentario_id, usuario):
    uid = usuario["id"]
    with conectar() as conn:
        ja_votou = conn.execute(
            "SELECT 1 FROM votos_uteis WHERE usuario_id=? AND postagem_id=?",
            (uid, comentario_id)
        ).fetchone()
        if ja_votou:
            conn.execute(
                "DELETE FROM votos_uteis WHERE usuario_id=? AND postagem_id=?",
                (uid, comentario_id)
            )
            print("  Voto removido.")
        else:
            conn.execute(
                "INSERT INTO votos_uteis (usuario_id, postagem_id) VALUES (?,?)",
                (uid, comentario_id)
            )
            print("  Comentário marcado como útil.")

# Denunciar comentário
def _denunciar_comentario(comentario_id, usuario):
    uid = usuario["id"]
    with conectar() as conn:
        ja_denunciou = conn.execute(
            "SELECT 1 FROM denuncias_fake WHERE usuario_id=? AND postagem_id=?",
            (uid, comentario_id)
        ).fetchone()
        if ja_denunciou:
            print("  Você já denunciou este comentário.")
            return
        conn.execute(
            "INSERT INTO denuncias_fake (usuario_id, postagem_id) VALUES (?,?)",
            (uid, comentario_id)
        )
        print("  Comentário denunciado.")