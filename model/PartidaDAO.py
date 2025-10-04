# model/PartidaDAO.py
import sqlite3
from model.bootstrap_db import _caminho_banco


class PartidaDAO:
    def __init__(self):
        self._caminho = _caminho_banco()

    def _conn(self):
        conn = sqlite3.connect(self._caminho)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON;')
        return conn

    # ---------- CRUD simples ----------
    def registrar(self, usuario_id, adversario, dificuldade, comeca, tema,
                  resultado, movimentos=0, duracao_segundos=0):
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO partidas (usuario_id, adversario, dificuldade, comeca, tema,
                                      resultado, movimentos, duracao_segundos)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (usuario_id, adversario, dificuldade, comeca, tema,
                  resultado, movimentos, duracao_segundos))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def listar_por_usuario(self, usuario_id, limite=200):
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, usuario_id, adversario, dificuldade, comeca, tema,
                       resultado, movimentos, duracao_segundos, criado_em
                FROM partidas
                WHERE usuario_id = ?
                ORDER BY criado_em DESC, id DESC
                LIMIT ?;
            """, (usuario_id, limite))
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def listar_filtrado(self, usuario_id, dificuldade=None, resultado=None, limite=200):
        sql = """
            SELECT id, usuario_id, adversario, dificuldade, comeca, tema,
                   resultado, movimentos, duracao_segundos, criado_em
            FROM partidas
            WHERE usuario_id = ?
        """
        params = [usuario_id]
        if dificuldade:
            sql += " AND dificuldade = ?"
            params.append(dificuldade)
        if resultado:
            sql += " AND resultado = ?"
            params.append(resultado)
        sql += " ORDER BY criado_em DESC, id DESC LIMIT ?"
        params.append(limite)

        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(sql, tuple(params))
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    # ---------- Agregações ----------
    def agregados(self, usuario_id):
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                  COUNT(*) AS total,
                  SUM(CASE WHEN resultado='vitoria'  THEN 1 ELSE 0 END) AS vitorias,
                  SUM(CASE WHEN resultado='derrota'  THEN 1 ELSE 0 END) AS derrotas,
                  SUM(CASE WHEN resultado='empate'   THEN 1 ELSE 0 END) AS empates
                FROM partidas
                WHERE usuario_id = ?;
            """, (usuario_id,))
            row = cur.fetchone()
            if not row:
                return {'total': 0, 'vitorias': 0, 'derrotas': 0, 'empates': 0}
            return {
                'total': row[0] or 0,
                'vitorias': row[1] or 0,
                'derrotas': row[2] or 0,
                'empates': row[3] or 0
            }
        finally:
            conn.close()

    def agregados_por_nivel(self, usuario_id):
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT dificuldade,
                  SUM(CASE WHEN resultado='vitoria' THEN 1 ELSE 0 END) AS vitorias,
                  SUM(CASE WHEN resultado='derrota' THEN 1 ELSE 0 END) AS derrotas,
                  SUM(CASE WHEN resultado='empate'  THEN 1 ELSE 0 END) AS empates
                FROM partidas
                WHERE usuario_id = ?
                GROUP BY dificuldade;
            """, (usuario_id,))
            base = {
                'Fácil':   {'vitorias': 0, 'derrotas': 0, 'empates': 0},
                'Médio':   {'vitorias': 0, 'derrotas': 0, 'empates': 0},
                'Difícil': {'vitorias': 0, 'derrotas': 0, 'empates': 0},
            }
            for r in cur.fetchall():
                dif = (r[0] or '')
                if dif not in base:
                    base[dif] = {'vitorias': 0, 'derrotas': 0, 'empates': 0}
                base[dif]['vitorias'] = r[1] or 0
                base[dif]['derrotas'] = r[2] or 0
                base[dif]['empates']  = r[3] or 0
            return base
        finally:
            conn.close()
