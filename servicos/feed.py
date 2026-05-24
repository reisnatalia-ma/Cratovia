from dados.database import conectar

POSTAGENS_POR_PAGINA = 10


def buscar_ocorrencias(pagina=1, bairro=None, natureza=None):
    conn = conectar()
    cursor = conn.cursor()

    condicoes = ["tipo = 'ocorrencia'", "status = 'ativa'"]
    parametros = []

    if bairro:
        condicoes.append("LOWER(bairro) LIKE LOWER(?)")
        parametros.append(f"%{bairro}%")

    if natureza:
        condicoes.append("natureza = ?")
        parametros.append(natureza)

    where = " AND ".join(condicoes)

    cursor.execute(f"SELECT COUNT(*) FROM postagens WHERE {where}", parametros)
    total = cursor.fetchone()[0]

    offset = (pagina - 1) * POSTAGENS_POR_PAGINA
    parametros_paginados = parametros + [POSTAGENS_POR_PAGINA, offset]

    cursor.execute(f"""
        SELECT * FROM postagens
        WHERE {where}
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """, parametros_paginados)

    postagens = [dict(row) for row in cursor.fetchall()]
    conn.close()

    total_paginas = max(1, (total + POSTAGENS_POR_PAGINA - 1) // POSTAGENS_POR_PAGINA)
    return postagens, total_paginas


def buscar_eventos(pagina=1):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM postagens WHERE tipo = 'evento' AND status = 'ativa'")
    total = cursor.fetchone()[0]

    offset = (pagina - 1) * POSTAGENS_POR_PAGINA
    cursor.execute("""
        SELECT * FROM postagens
        WHERE tipo = 'evento' AND status = 'ativa'
        ORDER BY destaque DESC, id DESC
        LIMIT ? OFFSET ?
    """, (POSTAGENS_POR_PAGINA, offset))

    eventos = [dict(row) for row in cursor.fetchall()]
    conn.close()

    total_paginas = max(1, (total + POSTAGENS_POR_PAGINA - 1) // POSTAGENS_POR_PAGINA)
    return eventos, total_paginas


def exibir_feed(usuario=None, bairro=None, natureza=None):
    from utils.formatacao import limpar_tela, linha_separadora
    from utils.componentes import titulo, card_postagem, mensagem_info
    from servicos.interacoes import menu_interacoes

    pagina = 1

    while True:
        limpar_tela()

        filtros = []
        if bairro:
            filtros.append(f"Bairro: {bairro}")
        if natureza:
            filtros.append(f"Natureza: {natureza}")
        cabecalho = "ÚLTIMAS OCORRÊNCIAS"
        if filtros:
            cabecalho += f" — {' | '.join(filtros)}"
        titulo(cabecalho)

        postagens, total_paginas = buscar_ocorrencias(pagina, bairro, natureza)

        if not postagens:
            mensagem_info("Nenhuma ocorrência encontrada.")
        else:
            for i, post in enumerate(postagens, 1):
                card_postagem(i, post)

        linha_separadora()
        print(f"Página {pagina} de {total_paginas}")
        linha_separadora()
        print("[A] Anterior  [P] Próxima  [V] Ver detalhes  [0] Voltar")
        linha_separadora()

        opcao = input("Escolha: ").strip().upper()

        if opcao == "P" and pagina < total_paginas:
            pagina += 1
        elif opcao == "A" and pagina > 1:
            pagina -= 1
        elif opcao == "V":
            num = input("Número da postagem: ").strip()
            if num.isdigit():
                indice = int(num) - 1
                if 0 <= indice < len(postagens):
                    menu_interacoes(postagens[indice], usuario)
        elif opcao == "0":
            break


def exibir_eventos(usuario=None):
    from utils.formatacao import limpar_tela, linha_separadora
    from utils.componentes import titulo, card_postagem, mensagem_info

    pagina = 1

    while True:
        limpar_tela()
        titulo("EVENTOS E COMUNICADOS")

        eventos, total_paginas = buscar_eventos(pagina)

        if not eventos:
            mensagem_info("Nenhum evento disponível no momento.")
        else:
            for i, evento in enumerate(eventos, 1):
                card_postagem(i, evento)

        from utils.formatacao import linha_separadora
        linha_separadora()
        print(f"Página {pagina} de {total_paginas}")
        linha_separadora()
        print("[A] Anterior  [P] Próxima  [0] Voltar")
        linha_separadora()

        opcao = input("Escolha: ").strip().upper()

        if opcao == "P" and pagina < total_paginas:
            pagina += 1
        elif opcao == "A" and pagina > 1:
            pagina -= 1
        elif opcao == "0":
            break


def menu_filtrar_bairro(usuario=None):
    from utils.formatacao import limpar_tela, linha_separadora
    from utils.componentes import titulo

    limpar_tela()
    titulo("FILTRAR POR BAIRRO")
    bairro = input("Digite o nome do bairro: ").strip()
    if bairro:
        exibir_feed(usuario=usuario, bairro=bairro)


def menu_filtrar_natureza(usuario=None):
    from utils.formatacao import limpar_tela, linha_separadora
    from utils.componentes import titulo
    from servicos.postagens import NATUREZAS

    limpar_tela()
    titulo("FILTRAR POR NATUREZA")

    for i, nat in enumerate(NATUREZAS, 1):
        print(f"  {i}. {nat}")
    linha_separadora()

    opcao = input("Escolha: ").strip()
    if opcao.isdigit() and 1 <= int(opcao) <= len(NATUREZAS):
        natureza = NATUREZAS[int(opcao) - 1]
        exibir_feed(usuario=usuario, natureza=natureza)