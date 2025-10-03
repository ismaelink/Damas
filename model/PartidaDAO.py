# model/PartidaDAO.py
import os
import sqlite3

def _caminho_banco():
    # Sobe um nível (..), saindo de /model para a raiz do projeto,
    # e aponta para banco/banco.db
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'banco', 'banco.db')

class PartidaDAO:
    def __init__(self):
        self._caminho = _caminho_banco()
        # garante que a pasta exista (caso alguém apague a pasta /banco)
        pasta = os.path.dirname(self._caminho)
        if not os.path.exists(pasta):
            os.makedirs(pasta, exist_ok=True)

    def _conn(self):
        conn = sqlite3.connect(self._caminho)
        conn.row_factory = sqlite3.Row
        # respeita chaves estrangeiras (FK usuario_id -> usuarios.id)
        conn.execute('PRAGMA foreign_keys = ON;')
        return conn

    # ========== CRUD ==========
    def registrar(self, usuario_id, adversario, dificuldade, comeca, tema,
                  resultado, movimentos=0, duracao_segundos=0):
        """
        Insere uma linha de histórico de partida.
        resultado: 'vitoria' | 'derrota' | 'empate' | 'encerrada'
        dificuldade: 'easy' | 'medium' | 'hard'
        comeca: 'brancas' | 'pretas'
        """
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO partidas (
                    usuario_id, adversario, dificuldade, comeca, tema,
                    resultado, movimentos, duracao_segundos
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                usuario_id, adversario, dificuldade, comeca, tema,
                resultado, movimentos, duracao_segundos
            ))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def listar_por_usuario(self, usuario_id, limite=200):
        """
        Lista as últimas 'limite' partidas de um usuário (mais recentes primeiro).
        """
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
        """
        Lista partidas com filtros opcionais por dificuldade e resultado.
        """
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

    # ========== Agregações (para EstatísticasFrame) ==========
    def agregados(self, usuario_id):
        """
        Totais gerais do usuário:
        {
          'total': N, 'vitorias': X, 'derrotas': Y, 'empates': Z
        }
        """
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                  COUNT(*) AS total,
                  SUM(CASE WHEN resultado='vitoria' THEN 1 ELSE 0 END) AS vitorias,
                  SUM(CASE WHEN resultado='derrota' THEN 1 ELSE 0 END) AS derrotas,
                  SUM(CASE WHEN resultado='empate'  THEN 1 ELSE 0 END) AS empates
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
        """
        Totais por dificuldade:
        {
          'easy':   {'vitorias': X, 'derrotas': Y, 'empates': Z},
          'medium': {...},
          'hard':   {...}
        }
        """
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
                'easy':   {'vitorias': 0, 'derrotas': 0, 'empates': 0},
                'medium': {'vitorias': 0, 'derrotas': 0, 'empates': 0},
                'hard':   {'vitorias': 0, 'derrotas': 0, 'empates': 0},
            }
            for r in cur.fetchall():
                dif = (r[0] or '').lower()
                if dif not in base:
                    base[dif] = {'vitorias': 0, 'derrotas': 0, 'empates': 0}
                base[dif]['vitorias'] = r[1] or 0
                base[dif]['derrotas'] = r[2] or 0
                base[dif]['empates']  = r[3] or 0
            return base
        finally:
            conn.close()
