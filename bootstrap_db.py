# bootstrap_db.py
import os
import sqlite3

def __caminho_banco():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, 'banco', 'banco.db')

SQL_CRIAR_TABELAS = [
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        nome            TEXT NOT NULL UNIQUE,
        senha_hash      TEXT NOT NULL,
        tema_preferido  TEXT NOT NULL DEFAULT 'flatly',
        criado_em       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        atualizado_em   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS partidas (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id          INTEGER NOT NULL,
        adversario          TEXT NOT NULL,
        dificuldade         TEXT NOT NULL,
        comeca              TEXT NOT NULL,
        tema                TEXT NOT NULL,
        resultado           TEXT NOT NULL,
        movimentos          INTEGER NOT NULL DEFAULT 0,
        duracao_segundos    INTEGER NOT NULL DEFAULT 0,
        criado_em           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
    );
    """
]

def criar_banco():
    caminho = __caminho_banco()
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    conn = sqlite3.connect(caminho)
    try:
        cur = conn.cursor()
        for tbl in SQL_CRIAR_TABELAS:
            cur.execute(tbl)
        conn.commit()
    finally:
        conn.close()
    return caminho
