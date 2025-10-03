import os
import sqlite3

class UsuarioDAO:
    def __init__(self):
        self.__caminho = self.__caminho_banco()

    def __caminho_banco(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'banco/banco.db')

    def __conectar(self):
        conn = sqlite3.connect(self.__caminho)
        conn.execute('PRAGMA foreign_keys = ON;')
        return conn

    def existe_nome(self, nome):
        conn = self.__conectar()
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM usuarios WHERE nome = ? LIMIT 1;", (nome,))
            return cur.fetchone() is not None
        finally:
            conn.close()

    def existe_nome_para_outro(self, nome, id_atual):
        conn = self.__conectar()
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM usuarios WHERE nome = ? AND id <> ? LIMIT 1;", (nome, id_atual))
            return cur.fetchone() is not None
        finally:
            conn.close()

    def criar(self, nome, senha_hash):
        conn = self.__conectar()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO usuarios (nome, senha_hash)
                VALUES (?, ?);
            """, (nome, senha_hash))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def buscar_por_nome(self, nome):
        conn = self.__conectar()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, nome, senha_hash, tema_preferido
                FROM usuarios
                WHERE nome = ?;
            """, (nome,))
            row = cur.fetchone()
            if not row:
                return None
            return {
                'id': row[0],
                'nome': row[1],
                'senha_hash': row[2],
                'tema_preferido': row[3],
            }
        finally:
            conn.close()

    # model/UsuarioDAO.py (adicione o parâmetro e a coluna)
def atualizar(self, user_id, novo_nome=None, novo_senha_hash=None, novo_tema_preferido=None):
    partes = []
    params = []

    if novo_nome is not None:
        partes.append("nome = ?")
        params.append(novo_nome)

    if novo_senha_hash is not None:
        partes.append("senha_hash = ?")
        params.append(novo_senha_hash)

    if novo_tema_preferido is not None:
        partes.append("tema_preferido = ?")
        params.append(novo_tema_preferido)

    # sempre atualiza timestamp
    partes.append("atualizado_em = CURRENT_TIMESTAMP")

    if not partes:
        return 0

    sql = "UPDATE usuarios SET " + ", ".join(partes) + " WHERE id = ?;"
    params.append(user_id)

    conn = self.__conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, tuple(params))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()



