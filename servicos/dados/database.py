import sqlite3


def conectar():

    conn = sqlite3.connect("cratovia.db")

    # transforma resultado em dicionário
    conn.row_factory = sqlite3.Row

    return conn