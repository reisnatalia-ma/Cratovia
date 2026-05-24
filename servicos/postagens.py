from datetime import datetime
from dados.database import conectar

NATUREZAS = [
    "Acidente",
    "Problema urbano",
    "Denúncia",
    "Alagamento",
    "Falta de energia",
    "Trânsito",
    "Aviso importante",
    "Outro"
]


def criar_postagem(titulo, descricao, bairro, conteudo, natureza, usuario_id):
    agora = datetime.now()
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO postagens (titulo, descricao, bairro, data, hora, conteudo, natureza, tipo, status, usuario_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'ocorrencia', 'ativa', ?)
    """, (titulo, descricao, bairro, data, hora, conteudo, natureza, usuario_id))
    conn.commit()
    postagem_id = cursor.lastrowid
    conn.close()
    return postagem_id


def criar_evento(titulo, descricao, bairro, conteudo, usuario_id):
    agora = datetime.now()
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO postagens (titulo, descricao, bairro, data, hora, conteudo, tipo, status, usuario_id)
        VALUES (?, ?, ?, ?, ?, ?, 'evento', 'ativa', ?)
    """, (titulo, descricao, bairro, data, hora, conteudo, usuario_id))
    conn.commit()
    postagem_id = cursor.lastrowid
    conn.close()
    return postagem_id


def buscar_postagem_por_id(postagem_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM postagens WHERE id = ?", (postagem_id,))
    postagem = cursor.fetchone()
    conn.close()
    if postagem:
        return dict(postagem)
    return None


def editar_postagem(postagem_id, titulo, descricao, bairro, conteudo, natureza, usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE postagens
        SET titulo = ?, descricao = ?, bairro = ?, conteudo = ?, natureza = ?
        WHERE id = ? AND usuario_id = ?
    """, (titulo, descricao, bairro, conteudo, natureza, postagem_id, usuario_id))
    conn.commit()
    alteradas = cursor.rowcount
    conn.close()
    return alteradas > 0


def remover_postagem(postagem_id, usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM postagens WHERE id = ? AND usuario_id = ?",
        (postagem_id, usuario_id)
    )
    conn.commit()
    alteradas = cursor.rowcount
    conn.close()
    return alteradas > 0


def formulario_nova_postagem(usuario):
    from utils.componentes import titulo, mensagem_erro, mensagem_sucesso
    from utils.formatacao import limpar_tela, linha_separadora

    limpar_tela()
    titulo("NOVA OCORRÊNCIA")

    postagem_titulo = input("Título: ").strip()
    if not postagem_titulo:
        mensagem_erro("Título não pode estar vazio.")
        input("Pressione Enter para voltar...")
        return

    descricao = input("Breve descrição: ").strip()
    bairro = input("Bairro: ").strip()

    print("\nNatureza da ocorrência (opcional):")
    for i, nat in enumerate(NATUREZAS, 1):
        print(f"  {i}. {nat}")
    print("  0. Não informar")
    linha_separadora()

    escolha = input("Escolha: ").strip()
    natureza = None
    if escolha.isdigit() and 1 <= int(escolha) <= len(NATUREZAS):
        natureza = NATUREZAS[int(escolha) - 1]

    print("\nDescrição completa (pressione Enter duas vezes para finalizar):")
    linhas = []
    while True:
        linha = input()
        if linha == "" and linhas and linhas[-1] == "":
            break
        linhas.append(linha)
    conteudo = "\n".join(linhas).strip()

    if not conteudo:
        mensagem_erro("Conteúdo não pode estar vazio.")
        input("Pressione Enter para voltar...")
        return

    postagem_id = criar_postagem(postagem_titulo, descricao, bairro, conteudo, natureza, usuario["id"])
    mensagem_sucesso(f"Ocorrência publicada com sucesso! ID: {postagem_id}")
    input("Pressione Enter para continuar...")