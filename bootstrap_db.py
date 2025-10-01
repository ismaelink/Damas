import os
import sqlite3

def __caminho_banco():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, 'banco/banco.db')

SQL_CRIAR_TABELAS = [
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
]

def criar_banco():
    caminho = __caminho_banco()
    conn = sqlite3.connect(caminho)

    try:
        cur = conn.cursor()

        for tbl in SQL_CRIAR_TABELAS: cur.execute(tbl)

        conn.commit()
    finally:
        conn.close()

    return caminho

