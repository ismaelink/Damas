# model/UsuarioDAO.py
import sqlite3
from hashlib import sha256
from model.bootstrap_db import _caminho_banco


class UsuarioDAO:
    def __init__(self):
        self._caminho = _caminho_banco()

    def _conn(self):
        conn = sqlite3.connect(self._caminho)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON;')
        return conn

    # ------------ CRUD BÁSICO ------------
    def obter_por_nome(self, nome):
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM usuarios WHERE nome = ?;", (nome,))
            r = cur.fetchone()
            return dict(r) if r else None
        finally:
            conn.close()

    def obter_por_id(self, usuario_id):
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM usuarios WHERE id = ?;", (usuario_id,))
            r = cur.fetchone()
            return dict(r) if r else None
        finally:
            conn.close()

    def inserir(self, nome, senha_plana):
        """Cria usuário novo."""
        senha_hash = sha256(senha_plana.encode('utf-8')).hexdigest()
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO usuarios (nome, senha_hash, tema_preferido)
                VALUES (?, ?, 'padrao');
            """, (nome, senha_hash))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def atualizar(self, usuario_id, nome=None, senha_hash=None):
        """
        Atualiza dados do usuário (nome e/ou senha).
        Retorna (ok, msg).
        """
        campos = []
        params = []

        if nome:
            campos.append("nome = ?")
            params.append(nome.strip())

        if senha_hash:
            campos.append("senha_hash = ?")
            params.append(senha_hash.strip())

        if not campos:
            return True, "Nada para atualizar."

        params.append(usuario_id)

        sql = f"""
            UPDATE usuarios
               SET {", ".join(campos)},
                   atualizado_em = CURRENT_TIMESTAMP
             WHERE id = ?;
        """

        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(sql, tuple(params))
            conn.commit()
            if cur.rowcount == 0:
                return False, "Usuário não encontrado."
            return True, "Dados atualizados com sucesso."
        except sqlite3.IntegrityError as e:
            if "UNIQUE" in str(e).upper():
                return False, "Já existe um usuário com esse nome."
            return False, f"Erro de integridade: {e}"
        finally:
            conn.close()

    def salvar_tema_preferido(self, usuario_id, tema):
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE usuarios
                   SET tema_preferido = ?,
                       atualizado_em  = CURRENT_TIMESTAMP
                 WHERE id = ?;
            """, (tema, usuario_id))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()
