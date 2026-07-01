from dados.database import conectar
from utils.formatacao import linha_separadora, linha_dupla, limpar_tela, formatar_data
from utils.componentes import titulo, mensagem_sucesso, mensagem_erro


ORGAOS_NATUREZAS = {
    "DETRAN":               ["Acidente de trânsito"],
    "SAMU":                 ["Saúde pública"],
    "Corpo de Bombeiros":   ["Incêndio", "Alagamento", "Desastre ambiental"],
    "Secretaria de Saúde":  ["Saúde pública"],
}


def _pausar():
    input("\n  ENTER para continuar...")


def _pode_aprovar(usuario, natureza_nome):
    # Moderador aprova tudo
    if usuario.get("tipo") == "moderador":
        return True
    # Servidor só aprova naturezas do seu órgão
    if usuario.get("tipo") == "servidor":
        orgao = usuario.get("orgao") or ""
        permitidas = ORGAOS_NATUREZAS.get(orgao, [])
        return natureza_nome in permitidas
    return False


def _buscar_fila():
    with conectar() as conn:
        return [dict(r) for r in conn.execute("""
            SELECT p.*, b.nome AS bairro_nome, n.nome AS natureza_nome
            FROM postagens p
            LEFT JOIN bairros b ON b.id = p.bairro_id
            LEFT JOIN naturezas n ON n.id = p.natureza_id
            WHERE p.status IN ('aguardando', 'oculto')
            ORDER BY p.criado_em ASC
        """).fetchall()]


def analisar_postagem(post, usuario):
    while True:
        limpar_tela()
        titulo("ANALISAR POSTAGEM")

        nat  = post.get("natureza_nome") or "Não classificada"
        pode = _pode_aprovar(usuario, nat)

        print(f"  Bairro:    {post.get('bairro_nome', '?')}")
        print(f"  Título:    {post['titulo']}")
        print(f"  Natureza:  {nat}")
        print(f"  Status:    {post['status']}")
        print(f"  Denúncias: {post['denuncias']}")
        print(f"  Data:      {formatar_data(post['criado_em'])}")

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

        print("\n" + "-" * 60)
        print()
        for linha in post["conteudo"].split("\n"):
            print(f"  {linha}")
        print()
        linha_separadora()

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
                conn.execute(
                    "DELETE FROM denuncias_fake WHERE postagem_id=?",
                    (post["id"],)
                )
            mensagem_sucesso("Postagem aprovada e restaurada!")
            _pausar()
            return

        elif op == "R":
            confirma = input("  Tem certeza que deseja excluir? (S/N): ").strip().upper()
            if confirma == "S":
                with conectar() as conn:
                    conn.execute("DELETE FROM denuncias_fake WHERE postagem_id=?", (post["id"],))
                    conn.execute("DELETE FROM votos_uteis WHERE postagem_id=?", (post["id"],))
                    conn.execute("DELETE FROM comentarios WHERE postagem_id=?", (post["id"],))
                    conn.execute("DELETE FROM postagens WHERE id=?", (post["id"],))
                mensagem_sucesso("Postagem excluída.")
                _pausar()
                return

        else:
            mensagem_erro("Opção inválida ou sem permissão.")
            _pausar()


def menu_moderacao(usuario):
    while True:
        limpar_tela()
        titulo("MODERAÇÃO")

        fila = _buscar_fila()

        if not fila:
            print("  Nenhuma postagem aguardando revisão.")
            linha_separadora()
            input("\n  ENTER para voltar...")
            return

        print(f"  {len(fila)} postagem(ns) aguardando revisão:\n")

        for i, post in enumerate(fila, 1):
            status_label = "⏳ Pendente" if post["status"] == "aguardando" else "🚩 Denunciada"
            print(f"  [{i}] {post['titulo']}")
            print(f"       {post.get('bairro_nome') or '—'} · {post.get('natureza_nome') or '—'}")
            print(f"       {status_label} · Denúncias: {post['denuncias']}")
            linha_separadora()

        print("\n  Número → analisar postagem   [X] Voltar")
        op = input("\n  Ação: ").strip().upper()

        if op == "X":
            return

        try:
            num = int(op)
            if 1 <= num <= len(fila):
                analisar_postagem(fila[num - 1], usuario)
        except ValueError:
            pass