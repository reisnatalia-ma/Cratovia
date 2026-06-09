from datetime import datetime
from dados.database import conectar


def curtir_postagem(postagem_id, usuario_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM curtidas WHERE postagem_id = ? AND usuario_id = ?",
        (postagem_id, usuario_id)
    )
    ja_curtiu = cursor.fetchone()

    if ja_curtiu:
        cursor.execute(
            "DELETE FROM curtidas WHERE postagem_id = ? AND usuario_id = ?",
            (postagem_id, usuario_id)
        )
        conn.commit()
        conn.close()
        return "descurtido"
    else:
        cursor.execute(
            "INSERT INTO curtidas (postagem_id, usuario_id) VALUES (?, ?)",
            (postagem_id, usuario_id)
        )
        conn.commit()
        conn.close()
        return "curtido"


def contar_curtidas(postagem_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM curtidas WHERE postagem_id = ?", (postagem_id,))
    total = cursor.fetchone()[0]
    conn.close()
    return total


def adicionar_comentario(postagem_id, usuario_id, texto):
    agora = datetime.now()
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO comentarios (postagem_id, usuario_id, texto, data, hora)
        VALUES (?, ?, ?, ?, ?)
    """, (postagem_id, usuario_id, texto, data, hora))
    conn.commit()
    conn.close()


def buscar_comentarios(postagem_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.texto, c.data, c.hora, u.nome
        FROM comentarios c
        JOIN usuarios u ON c.usuario_id = u.id
        WHERE c.postagem_id = ?
        ORDER BY c.id ASC
    """, (postagem_id,))
    comentarios = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return comentarios


def denunciar_postagem(postagem_id, usuario_id, motivo):
    agora = datetime.now()
    data = agora.strftime("%d/%m/%Y")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM denuncias WHERE postagem_id = ? AND usuario_id = ?",
        (postagem_id, usuario_id)
    )
    if cursor.fetchone():
        conn.close()
        return False, "Você já denunciou esta postagem."

    cursor.execute("""
        INSERT INTO denuncias (postagem_id, usuario_id, motivo, data)
        VALUES (?, ?, ?, ?)
    """, (postagem_id, usuario_id, motivo, data))
    conn.commit()
    conn.close()
    return True, "Denúncia registrada."


def menu_interacoes(postagem, usuario):
    from utils.formatacao import limpar_tela, linha_separadora
    from utils.componentes import titulo, mensagem_sucesso, mensagem_erro

    while True:
        limpar_tela()
        titulo(postagem["titulo"])

        print(f"Bairro: {postagem['bairro']}")
        print(f"Data: {postagem['data']} às {postagem['hora']}")
        if postagem.get("natureza"):
            print(f"Natureza: {postagem['natureza']}")
        linha_separadora()
        print(postagem["conteudo"])
        linha_separadora()

        curtidas = contar_curtidas(postagem["id"])
        print(f"Curtidas: {curtidas}")

        comentarios = buscar_comentarios(postagem["id"])
        if comentarios:
            print(f"\nComentários ({len(comentarios)}):")
            for com in comentarios:
                print(f"  [{com['data']} {com['hora']}] {com['nome']}: {com['texto']}")

        linha_separadora()

        if usuario:
            print("[C] Curtir/Descurtir  [M] Comentar  [D] Denunciar  [0] Voltar")
        else:
            print("[0] Voltar")

        linha_separadora()
        opcao = input("Escolha: ").strip().upper()

        if opcao == "C" and usuario:
            resultado = curtir_postagem(postagem["id"], usuario["id"])
            mensagem_sucesso(f"Postagem {resultado}!")
            input("Pressione Enter para continuar...")

        elif opcao == "M" and usuario:
            texto = input("Seu comentário: ").strip()
            if texto:
                adicionar_comentario(postagem["id"], usuario["id"], texto)
                mensagem_sucesso("Comentário adicionado!")
                input("Pressione Enter para continuar...")

        elif opcao == "D" and usuario:
            motivo = input("Motivo da denúncia: ").strip()
            if motivo:
                ok, msg = denunciar_postagem(postagem["id"], usuario["id"], motivo)
                if ok:
                    mensagem_sucesso(msg)
                else:
                    mensagem_erro(msg)
                input("Pressione Enter para continuar...")

        elif opcao == "0":
            break
