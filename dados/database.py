import sqlite3
import os

caminho_banco = os.path.join(os.path.dirname(__file__), "cratovia.db")
def conectar():
    conn = sqlite3.connect(caminho_banco)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

# - CRIAR TABELAS E POPULAR DADOS INICIAIS
def iniciar_tabelas():
    conexao = conectar()
    cursor = conexao.cursor()

    # - TABELA DE USUÁRIOS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            telefone TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'comum',
            relevancia INTEGER DEFAULT 0
        );
    """)

    # - TABELA DE CÓDIGOS DE ACESSO PARA MODERADOR E SERVIDOR PÚBLICO
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS codigos_acesso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            tipo TEXT NOT NULL,
            orgao TEXT,
            usado INTEGER DEFAULT 0
        );
    """)

    # - TABELA DE BAIRROS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bairros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL
        );
    """)

    # TABELA DE NATUREZAS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS naturezas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL
        );
    """)

    # - TABELA DE POSTAGENS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS postagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER REFERENCES usuarios(id),
            bairro_id INTEGER REFERENCES bairros(id),
            local_bairro TEXT,
            titulo TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            natureza_id INTEGER REFERENCES naturezas(id),
            status TEXT NOT NULL DEFAULT 'aguardando',
            votos_uteis INTEGER DEFAULT 0,
            denuncias INTEGER DEFAULT 0,
            aprovador_por INTEGER REFERENCES usuarios(id),
            criado_em TEXT NOT NULL
        );
    """)
    
    # - TABELAS DE COMENTARIOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comentarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        postagem_id INTEGER REFERENCES postagens(id),
        usuario_id INTEGER REFERENCES usuarios(id),
        resposta_para INTEGER REFERENCES comentarios(id),
        conteudo TEXT NOT NULL,
        oficial INTEGER DEFAULT 0,
        criado_em TEXT NOT NULL
    );
""")
    
    # - TABELA DE VOTOS ÚTEIS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS votos_uteis (
            usuario_id INTEGER REFERENCES usuarios(id),
            postagem_id INTEGER REFERENCES postagens(id),
            PRIMARY KEY (usuario_id, postagem_id)
        );
    """)

    # - TABELA DE DENÚNCIAS COMO FALSO
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS denuncias_fake (
            usuario_id INTEGER REFERENCES usuarios(id),
            postagem_id INTEGER REFERENCES postagens(id),
            PRIMARY KEY (usuario_id, postagem_id)
        );
    """)

    # - TABELA DE ANÚNCIOS E EVENTOS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anuncios_eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER REFERENCES usuarios(id),
            bairro_id INTEGER REFERENCES bairros(id),
            local_bairro TEXT,
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'aguardando',
            aprovador_por INTEGER REFERENCES usuarios(id),
            criado_em TEXT NOT NULL
        );
    """)

    # POPULAR ITENS DE BAIRRO
    bairros = [
        "Alto da Penha", "Barro Branco", "Cacimbas",
        "Centro", "Distrito de Baixio das Palmeiras",
        "Distrito de Bela Vista", "Distrito de Belmonte",
        "Distrito de Campo Alegre", "Distrito de Dom Quintino",
        "Distrito de Monte Alverne", "Distrito de Ponta da Serra",
        "Distrito de Santa Fé", "Distrito de Santa Rosa",
        "Gizélia Pinheiro (Batateiras)", "Grangeiro", "Independência",
        "Lameiro", "Mirandão","Muriti", "Mutirão", "Novo Crato",
        "Novo Horizonte", "Ossian Araripe (Caixa D'Água)", "Pantanal",
        "Parque Granjeiro", "Parque Recreio", "Pimenta", "Pinto Madeira",
        "Santa Luzia", "Seminário", "Sossego", "São Bento", "São Gonçalo",
        "São José", "São Miguel", "Vila Alta", "Vila Lobo","Zacarias Gonçalves"
    ]
    for b in bairros:
        cursor.execute("INSERT OR IGNORE INTO bairros (nome) VALUES (?)", (b,))

    # - POPULAR ITENS DE NATUREZAS
    naturezas = [
        "Acidente de trânsito", "Incêndio", "Alagamento",
        "Desastre ambiental", "Falta de infraestrutura",
        "Violência/Segurança pública", "Saúde pública", "Outros"
    ]
    for n in naturezas:
        cursor.execute("INSERT OR IGNORE INTO naturezas (nome) VALUES (?)", (n,))

    # - POPULAR ITENS DE CÓDIGOS DE ACESSO
    codigos_acesso = [
        ("MOD-CRATO-2024",   "moderador", None),
        ("MOD-CRATO-2025",   "moderador", None),
        ("SERV-DETRAN-001",  "servidor",  "DETRAN"),
        ("SERV-SAMU-001",    "servidor",  "SAMU"),
        ("SERV-BOMB-001",    "servidor",  "Corpo de Bombeiros"),
        ("SERV-SAUDE-001",   "servidor",  "Secretaria de Saúde")
    ]
    for cod, tipo, orgao in codigos_acesso:
        cursor.execute("INSERT OR IGNORE INTO codigos_acesso (codigo, tipo, orgao) VALUES (?,?,?)", (cod, tipo, orgao))
    conexao.commit()
    conexao.close()

# - CONSULTAR BANCO DE DADOS
def consultar_tabelas():
    conexao = conectar()
    cursor = conexao.cursor()
    tabela = input(
        "Qual tabela deseja consultar? "
        "\nusuarios | codigos_acesso | bairros | naturezas"
        "\npostagens | votos_uteis | denuncias_fake | anuncios_eventos\n"
    )
    tabelas_validas = [
        "usuarios", "codigos_acesso", "bairros", "naturezas",
        "postagens", "votos_uteis", "denuncias_fake", "anuncios_eventos"
    ]
    if tabela in tabelas_validas:
        cursor.execute(f"SELECT * FROM {tabela}")
        dados = cursor.fetchall()
        
        for linha in dados:
            print(linha)
    else:
        print("Tabela inválida!")
    conexao.close()