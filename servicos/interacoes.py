from datetime import datetime
from dados.database import conectar

def curtir_postagem(postagem_id, usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM curtidas WHERE postagem_id = ? AND usuario_id = ?",
            (postagem_id, usuario_id)
        )
        if cursor.fetchone():
            cursor.execute(
                "DELETE FROM curtidas WHERE postagem_id = ? AND usuario_id = ?",
                (postagem_id, usuario_id)
            )
            conn.commit()
            return "descurtido"
        else:
            cursor.execute(
                "INSERT INTO curtidas (postagem_id, usuario_id) VALUES (?, ?)",
                (postagem_id, usuario_id)
            )
            conn.commit()
            return "curtido"
    finally:
        conn.close()


def contar_curtidas(postagem_id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM curtidas WHERE postagem_id = ?", (postagem_id,))
        return cursor.fetchone()[0]
    finally:
        conn.close()
        
def adicionar_comentario(postagem_id, usuario_id, texto, resposta_para_id=None):
    """Insere um comentário. Se resposta_para_id for informado, é uma resposta."""
    if not texto or not texto.strip():
        return None

    agora = datetime.now()
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M")

    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO comentarios (postagem_id, usuario_id, texto, data, hora, resposta_para_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (postagem_id, usuario_id, texto.strip(), data, hora, resposta_para_id))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def buscar_comentarios(postagem_id):
    """
    Retorna comentários raiz (sem pai) com suas respostas aninhadas.
    Estrutura: lista de dicts com chave 'respostas' contendo lista de respostas.
    """
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT c.id, c.texto, c.data, c.hora, c.resposta_para_id, u.nome
            FROM comentarios c
            JOIN usuarios u ON c.usuario_id = u.id
            WHERE c.postagem_id = ?
            ORDER BY c.id ASC
        """, (postagem_id,))
        todos = [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

    raiz = []
    por_id = {}

    for com in todos:
        com["respostas"] = []
        por_id[com["id"]] = com

    for com in todos:
        pai_id = com["resposta_para_id"]
        if pai_id and pai_id in por_id:
            por_id[pai_id]["respostas"].append(com)
        else:
            raiz.append(com)

    return raiz

def denunciar_postagem(postagem_id, usuario_id, motivo):
    agora = datetime.now()
    data = agora.strftime("%d/%m/%Y")

    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM denuncias WHERE postagem_id = ? AND usuario_id = ?",
            (postagem_id, usuario_id)
        )
        if cursor.fetchone():
            return False, "Você já denunciou esta postagem."

        cursor.execute("""
            INSERT INTO denuncias (postagem_id, usuario_id, motivo, data)
            VALUES (?, ?, ?, ?)
        """, (postagem_id, usuario_id, motivo, data))
        conn.commit()
        return True, "Denúncia registrada."
    finally:
        conn.close()
        
def _exibir_comentario(com, indice, prefixo=""):
    """Exibe um comentário com número de referência e suas respostas."""
    from utils.formatacao import LARGURA
    print(f"  {prefixo}[{indice}] {com['nome']}  {com['data']} {com['hora']}")
    print(f"  {prefixo}    {com['texto']}")
    if com["respostas"]:
        for sub in com["respostas"]:
            print(f"  {prefixo}    ↳ {sub['nome']}  {sub['data']} {sub['hora']}")
            print(f"  {prefixo}       {sub['texto']}")
            
def menu_interacoes(postagem, usuario):
    from utils.formatacao import limpar_tela, linha_separadora
    from utils.componentes import titulo, mensagem_sucesso, mensagem_erro, mensagem_info

    while True:
        limpar_tela()
        titulo(postagem["titulo"])

        print(f"  Bairro: {postagem['bairro']}")
        print(f"  Data: {postagem['data']} às {postagem['hora']}")
        if postagem.get("natureza"):
            print(f"  Natureza: {postagem['natureza']}")
        linha_separadora()
        print(postagem["conteudo"])
        linha_separadora()

        curtidas = contar_curtidas(postagem["id"])
        print(f"  ♥ {curtidas} curtida(s)")

        comentarios = buscar_comentarios(postagem["id"])
        total_comentarios = sum(1 + len(c["respostas"]) for c in comentarios)

        if comentarios:
            print(f"\n  Comentários ({total_comentarios}):")
            linha_separadora()
            for i, com in enumerate(comentarios, 1):
                _exibir_comentario(com, i)
        else:
            print()
            mensagem_info("Nenhum comentário ainda.")

        linha_separadora()

        if usuario:
            print("[C] Curtir/Descurtir  [M] Comentar  [R] Responder comentário")
            print("[D] Denunciar         [0] Voltar")
        else:
            mensagem_info("Faça login para interagir.")
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
                mensagem_sucesso("Comentário publicado!")
            else:
                mensagem_erro("Comentário não pode estar vazio.")
            input("Pressione Enter para continuar...")

        elif opcao == "R" and usuario:
            if not comentarios:
                mensagem_erro("Não há comentários para responder.")
                input("Pressione Enter para continuar...")
                continue

            num = input(f"Número do comentário (1-{len(comentarios)}): ").strip()
            if not num.isdigit() or not (1 <= int(num) <= len(comentarios)):
                mensagem_erro("Número inválido.")
                input("Pressione Enter para continuar...")
                continue

            comentario_alvo = comentarios[int(num) - 1]
            print(f"\n  Respondendo para {comentario_alvo['nome']}:")
            print(f"  \"{comentario_alvo['texto'][:60]}{'...' if len(comentario_alvo['texto']) > 60 else ''}\"")
            linha_separadora()
            texto = input("Sua resposta: ").strip()
            if texto:
                adicionar_comentario(
                    postagem["id"],
                    usuario["id"],
                    texto,
                    resposta_para_id=comentario_alvo["id"]
                )
                mensagem_sucesso(f"Resposta enviada para {comentario_alvo['nome']}!")
            else:
                mensagem_erro("Resposta não pode estar vazia.")
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
