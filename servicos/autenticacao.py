import sqlite3
import os

CAMINHO_BANCO = os.path.join(os.path.dirname(__file__), "cratovia.db")


def conectar():
    conn = sqlite3.connect(CAMINHO_BANCO)
    conn.row_factory = sqlite3.Row
    return conn


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'comum'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS postagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            bairro TEXT NOT NULL,
            data TEXT NOT NULL,
            hora TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            natureza TEXT,
            tipo TEXT NOT NULL DEFAULT 'ocorrencia',
            status TEXT NOT NULL DEFAULT 'ativa',
            destaque INTEGER NOT NULL DEFAULT 0,
            usuario_id INTEGER,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS curtidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            postagem_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (postagem_id) REFERENCES postagens(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comentarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            postagem_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            texto TEXT NOT NULL,
            data TEXT NOT NULL,
            hora TEXT NOT NULL,
            FOREIGN KEY (postagem_id) REFERENCES postagens(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS denuncias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            postagem_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            motivo TEXT NOT NULL,
            data TEXT NOT NULL,
            FOREIGN KEY (postagem_id) REFERENCES postagens(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    conn.commit()
    conn.close()