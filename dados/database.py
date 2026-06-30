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
            orgao TEXT,
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
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id   INTEGER REFERENCES usuarios(id),
            bairro_id    INTEGER REFERENCES bairros(id),
            local_bairro TEXT,
            titulo       TEXT    NOT NULL,
            descricao    TEXT    NOT NULL,
            conteudo     TEXT    NOT NULL,
            natureza_id  INTEGER REFERENCES naturezas(id),
            status       TEXT    NOT NULL DEFAULT 'aguardando',
            votos_uteis  INTEGER DEFAULT 0,
            denuncias    INTEGER DEFAULT 0,
            aprovado_por INTEGER REFERENCES usuarios(id),
            criado_em    TEXT    NOT NULL
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
            conteudo TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'aguardando',
            aprovado_por INTEGER REFERENCES usuarios(id),
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
        ("MOD-CRATO-202",   "moderador", None),
        ("SERV-DETRAN-001",  "servidor",  "DETRAN"),
        ("SERV-SAMU-001",    "servidor",  "SAMU"),
        ("SERV-BOMB-001",    "servidor",  "Corpo de Bombeiros"),
        ("SERV-SAUDE-001",   "servidor",  "Secretaria de Saúde")
    ]
    for cod, tipo, orgao in codigos_acesso:
        cursor.execute("INSERT OR IGNORE INTO codigos_acesso (codigo, tipo, orgao) VALUES (?,?,?)", (cod, tipo, orgao))

    conexao.commit()
    conexao.close()


# - POPULAR POSTAGENS INICIAIS
def popular_postagens_exemplo():
    conexao = conectar()
    cursor = conexao.cursor()

    usuario_id = 37337

    cursor.execute("SELECT id FROM usuarios WHERE id = ?", (usuario_id,))
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO usuarios (id, nome, email, telefone, senha, tipo, orgao, relevancia)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            usuario_id,
            "Usuário Exemplo",
            "usuario.exemplo@cratovia.local",
            "88999990000",
            "senha123",
            "comum",
            None,
            0
        ))

    def pegar_id_bairro(nome):
        cursor.execute("SELECT id FROM bairros WHERE nome = ?", (nome,))
        linha = cursor.fetchone()
        return linha["id"] if linha else None

    def pegar_id_natureza(nome):
        cursor.execute("SELECT id FROM naturezas WHERE nome = ?", (nome,))
        linha = cursor.fetchone()
        return linha["id"] if linha else None

    cursor.execute("SELECT COUNT(*) AS total FROM postagens WHERE usuario_id = ?", (usuario_id,))
    if cursor.fetchone()["total"] == 0:
        postagens_exemplo = [
            {
                "bairro": "Centro",
                "local_bairro": "Rua Major Felizardo, próximo à praça",
                "titulo": "Alagamento após chuva forte",
                "descricao": "Via completamente alagada dificultando passagem de pedestres e veículos.",
                "conteudo": "Após a chuva da tarde, a rua ficou intransitável devido ao acúmulo de água, "
                            "que chegou a invadir algumas casas próximas. Moradores pedem providências da prefeitura.",
                "natureza": "Alagamento",
            },
            {
                "bairro": "São Miguel",
                "local_bairro": "Avenida principal, altura do nº 230",
                "titulo": "Buraco grande na via",
                "descricao": "Buraco profundo na pista representa risco para motociclistas.",
                "conteudo": "O buraco já causou a queda de pelo menos dois motociclistas nesta semana. "
                            "A comunidade solicita reparo urgente do asfalto.",
                "natureza": "Falta de infraestrutura",
            },
            {
                "bairro": "Pimenta",
                "local_bairro": "Rua das Flores",
                "titulo": "Princípio de incêndio em terreno baldio",
                "descricao": "Fogo em vegetação seca próximo a residências.",
                "conteudo": "Vizinhos perceberam fumaça e acionaram o Corpo de Bombeiros. "
                            "O fogo foi controlado, mas o mato alto no terreno continua sendo um risco.",
                "natureza": "Incêndio",
            },
        ]

        for p in postagens_exemplo:
            cursor.execute("""
                INSERT INTO postagens
                    (usuario_id, bairro_id, local_bairro, titulo, descricao, conteudo,
                    natureza_id, status, votos_uteis, denuncias, aprovado_por, criado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'aprovado', 0, 0, NULL, datetime('now'))
            """, (
                usuario_id,
                pegar_id_bairro(p["bairro"]),
                p["local_bairro"],
                p["titulo"],
                p["descricao"],
                p["conteudo"],
                pegar_id_natureza(p["natureza"]),
            ))

    cursor.execute("SELECT COUNT(*) AS total FROM anuncios_eventos WHERE usuario_id = ?", (usuario_id,))
    if cursor.fetchone()["total"] == 0:
        cursor.execute("""
            INSERT INTO anuncios_eventos
                (usuario_id, bairro_id, local_bairro, titulo, descricao, conteudo, status, aprovado_por, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, 'aprovado', NULL, datetime('now'))
        """, (
            usuario_id,
            pegar_id_bairro("Centro"),
            "Praça da Sé",
            "Feira cultural do Crato",
            "Evento com apresentações musicais, artesanato local e barracas de comida típica, "
            "aberto a toda a comunidade.",
            "Grande evento organizado pelo Crato para comemorar o lanamento do sistema CratoVia."
        ))

    conexao.commit()
    conexao.close()
