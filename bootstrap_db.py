import os
import sqlite3

def __caminho_banco():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, 'banco/banco.db')

SQL_CRIAR_TABELAS = [
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        nome            TEXT NOT NULL UNIQUE,
        senha_hash      TEXT NOT NULL,
        tema_preferido  TEXT NOT NULL DEFAULT 'padrao',
        criado_em       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        atualizado_em   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """
]

# bootstrap_db.py  -> dentro de SQL_CRIAR_TABELAS
SQL_CRIAR_TABELAS = [
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        nome            TEXT NOT NULL UNIQUE,
        senha_hash      TEXT NOT NULL,
        tema_preferido  TEXT NOT NULL DEFAULT 'padrao',
        criado_em       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        atualizado_em   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS partidas (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id          INTEGER NOT NULL,
        adversario          TEXT NOT NULL,                -- 'IA' (por enquanto)
        dificuldade         TEXT NOT NULL,                -- easy|medium|hard
        comeca              TEXT NOT NULL,                -- brancas|pretas
        tema                TEXT NOT NULL,                -- tema do tabuleiro
        resultado           TEXT NOT NULL,                -- vitoria|derrota|empate|encerrada
        movimentos          INTEGER NOT NULL DEFAULT 0,   -- opcional: qtd de lances da partida
        duracao_segundos    INTEGER NOT NULL DEFAULT 0,
        criado_em           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
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

