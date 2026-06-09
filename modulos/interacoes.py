from Data.database import conectar

LIMITE_DENUNCIAS = 5

# ── Votar útil em uma postagem ────────────────────────────────────────────────
def votar_util(postagem_id, usuario):
    uid = usuario["id"]

    with conectar() as conn:
        ja_votou = conn.execute(
            "SELECT 1 FROM votos_uteis WHERE usuario_id=? AND postagem_id=?",
            (uid, postagem_id)
        ).fetchone()

    if ja_votou:
        print("  Você já marcou esta postagem como útil.")
        return

    resp = input("  Achou útil? (S/N): ").strip().upper()
    if resp != "S":
        return

    with conectar() as conn:
        conn.execute(
            "INSERT INTO votos_uteis (usuario_id, postagem_id) VALUES (?,?)",
            (uid, postagem_id)
        )
        conn.execute(
            "UPDATE postagens SET votos_uteis = votos_uteis + 1 WHERE id=?",
            (postagem_id,)
        )
        votos = conn.execute(
            "SELECT votos_uteis FROM postagens WHERE id=?", (postagem_id,)
        ).fetchone()[0]

    print(f"  {votos} {'pessoa achou' if votos == 1 else 'pessoas acharam'} isso útil.")

# ── Denunciar postagem como fake news ─────────────────────────────────────────
def denunciar(postagem_id, usuario):
    uid = usuario["id"]

    with conectar() as conn:
        ja_denunciou = conn.execute(
            "SELECT 1 FROM denuncias WHERE usuario_id=? AND postagem_id=?",
            (uid, postagem_id)
        ).fetchone()

    if ja_denunciou:
        print("  Você já denunciou esta postagem.")
        return

    resp = input("  Denunciar como fake news? (S/N): ").strip().upper()
    if resp != "S":
        return

    with conectar() as conn:
        conn.execute(
            "INSERT INTO denuncias (usuario_id, postagem_id) VALUES (?,?)",
            (uid, postagem_id)
        )
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
