# model/bootstrap_db.py
import os
import sqlite3

# Função para obter o caminho do banco
def _caminho_banco():
    """
    Retorna o caminho absoluto para o arquivo banco.db
    Ele fica dentro da pasta 'banco/' na raiz do projeto.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho_banco = os.path.join(base_dir, "banco", "banco.db")

    # garante que a pasta banco existe
    pasta_banco = os.path.dirname(caminho_banco)
    if not os.path.exists(pasta_banco):
        os.makedirs(pasta_banco, exist_ok=True)

    return caminho_banco


# Tabelas
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
    """Cria o banco e as tabelas, se ainda não existirem."""
    caminho = _caminho_banco()
    conn = sqlite3.connect(caminho)

    try:
        cur = conn.cursor()
        for sql in SQL_CRIAR_TABELAS:
            cur.execute(sql)
        conn.commit()
    finally:
        conn.close()

    return caminho
