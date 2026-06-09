from datetime import datetime
from dados.database import conectar


def buscar_bairros():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM bairros ORDER BY nome")
    bairros = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return bairros


def buscar_naturezas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM naturezas ORDER BY nome")
    naturezas = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return naturezas


def criar_postagem(titulo, conteudo, bairro_id, local_bairro, natureza_id, usuario_id):
    agora = datetime.now()
    criado_em = agora.strftime("%d/%m/%Y %H:%M")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO postagens (usuario_id, bairro_id, local_bairro, titulo, conteudo, natureza_id, status, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, 'aguardando', ?)
    """, (usuario_id, bairro_id, local_bairro, titulo, conteudo, natureza_id, criado_em))
    conn.commit()
    postagem_id = cursor.lastrowid
    conn.close()
    return postagem_id


def buscar_postagem_por_id(postagem_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, b.nome as bairro_nome, n.nome as natureza_nome, u.nome as autor_nome
        FROM postagens p
        LEFT JOIN bairros b ON p.bairro_id = b.id
        LEFT JOIN naturezas n ON p.natureza_id = n.id
        LEFT JOIN usuarios u ON p.usuario_id = u.id
        WHERE p.id = ?
    """, (postagem_id,))
    postagem = cursor.fetchone()
    conn.close()
    if postagem:
        return dict(postagem)
    return None


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


def selecionar_bairro():
    from utils.formatacao import limpar_tela, linha_separadora
    from utils.componentes import titulo

    bairros = buscar_bairros()

    limpar_tela()
    titulo("SELECIONAR BAIRRO")

    for i, b in enumerate(bairros, 1):
        print(f"  {i:2}. {b['nome']}")

    linha_separadora()
    escolha = input("Número do bairro: ").strip()

    if escolha.isdigit() and 1 <= int(escolha) <= len(bairros):
        return bairros[int(escolha) - 1]
    return None


def selecionar_natureza():
    from utils.formatacao import linha_separadora

    naturezas = buscar_naturezas()

    print("\nNatureza da ocorrência:")
    for i, n in enumerate(naturezas, 1):
        print(f"  {i}. {n['nome']}")
    print(f"  {len(naturezas) + 1}. Não informar")
    linha_separadora()

    escolha = input("Escolha: ").strip()
    if escolha.isdigit() and 1 <= int(escolha) <= len(naturezas):
        return naturezas[int(escolha) - 1]
    return None


def nova_postagem(usuario):
    from utils.componentes import titulo, mensagem_erro, mensagem_sucesso
    from utils.formatacao import limpar_tela, linha_separadora

    bairro = selecionar_bairro()
    if not bairro:
        mensagem_erro("Bairro inválido.")
        input("Pressione Enter para voltar...")
        return

    limpar_tela()
    titulo("NOVA OCORRÊNCIA")
    print(f"Bairro: {bairro['nome']}")
    linha_separadora()

    postagem_titulo = input("Título: ").strip()
    if not postagem_titulo:
        mensagem_erro("Título não pode estar vazio.")
        input("Pressione Enter para voltar...")
        return

    local_bairro = input("Local no bairro (rua, referência): ").strip()

    natureza = selecionar_natureza()
    natureza_id = natureza["id"] if natureza else None

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

    postagem_id = criar_postagem(postagem_titulo, conteudo, bairro["id"], local_bairro, natureza_id, usuario["id"])
    mensagem_sucesso(f"Ocorrência enviada para aprovação! ID: {postagem_id}")
    input("Pressione Enter para continuar...")