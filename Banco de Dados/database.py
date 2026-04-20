import sqlite3

conexao = sqlite3.connect('cratovia.db')
cursor = conexao.cursor()

# - TABELA DE USUÁRIOS
cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    telefone TEXT UNIQUE NOT NULL,
                    senha TEXT NOT NULL);''')

# - TABELA DE CÓDIGOS DE ACESSO
cursor.execute('''CREATE TABLE IF NOT EXISTS codigos_acesso (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    tipo TEXT NOT NULL,
                    orgao TEXT,
                    usado INTEGER DEFAULT 0);''')

# - TABELA DE BAIRROS
cursor.execute('''CREATE TABLE IF NOT EXISTS bairros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL);''')

# TABELA DE NATUREZAS
cursor.execute('''CREATE TABLE IF NOT EXISTS naturezas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL);''')

# - TABELA DE POSTAGENS
cursor.execute('''CREATE TABLE IF NOT EXISTS postagens (
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
                    criado_em TEXT NOT NULL);''')

# - TABELA DE VOTOS ÚTEIS
cursor.execute('''
                CREATE TABLE IF NOT EXISTS votos_uteis (
                    usuario_id INTEGER REFERENCES usuarios(id),
                    postagem_id INTEGER REFERENCES postagens(id),
                    PRIMARY KEY (usuario_id, postagem_id));''')

# - TABELA DE DENÚNCIAS COMO FALSO
cursor.execute('''
                CREATE TABLE IF NOT EXISTS denuncias_fake (
                    usuario_id INTEGER REFERENCES usuarios(id),
                    postagem_id INTEGER REFERENCES postagens(id),
                    PRIMARY KEY (usuario_id, postagem_id));''')

# - TABELA DE ANÚNCIOS E EVENTOS
cursor.execute('''
                CREATE TABLE IF NOT EXISTS anuncio_evento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER REFERENCES usuarios(id),
                    bairro_id INTEGER REFERENCES bairros(id),
                    local_bairro TEXT,
                    titulo TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'aguardando',
                    aprovador_por INTEGER REFERENCES usuarios(id),
                    criado_em TEXT NOT NULL);''')

conexao.commit()
conexao.close()