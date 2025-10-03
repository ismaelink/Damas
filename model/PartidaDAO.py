# model/PartidaDAO.py
import os
import sqlite3

def _caminho_banco():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'banco', 'banco.db')

def _norm_dif(x):
    s = (x or "").strip().lower()
    if s in ("Fácil", "facil", "fácil"):
        return "Fácil"
    if s in ("Médio", "medio", "médio"):
        return "Médio"
    if s in ("Difícil", "dificil", "difícil"):
        return "Difícil"
    # fallback: guarda como veio, mas ideal é sempre cair nos 3 acima
    return s or "Fácil"

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
        # NORMALIZA a dificuldade antes de salvar
        dificuldade = _norm_dif(dificuldade)

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

    def listar_filtrado(self, usuario_id, dificuldade=None, resultado=None,
                        limite=200):
        sql = """
            SELECT id, usuario_id, adversario, dificuldade, comeca, tema,
                   resultado, movimentos, duracao_segundos, criado_em
            FROM partidas
            WHERE usuario_id = ?
        """
        params = [usuario_id]
        if dificuldade:
            sql += " AND dificuldade = ?"
            params.append(_norm_dif(dificuldade))  # normaliza no filtro também
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

    # ---------- Agregações p/ EstatísticasFrame ----------
    def agregados(self, usuario_id):
        """
        Retorna dict com totais:
        { 'total': X, 'vitorias': Y, 'derrotas': Z, 'empates': W, 'encerradas': K }
        """
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                COUNT(*) AS total_todos,
                SUM(CASE WHEN resultado='vitoria'   THEN 1 ELSE 0 END) AS vitorias,
                SUM(CASE WHEN resultado='derrota'   THEN 1 ELSE 0 END) AS derrotas,
                SUM(CASE WHEN resultado='empate'    THEN 1 ELSE 0 END) AS empates,
                SUM(CASE WHEN resultado='encerrada' THEN 1 ELSE 0 END) AS encerradas
                FROM partidas
                WHERE usuario_id = ?;
            """, (usuario_id,))
            row = cur.fetchone()
            if not row:
                return {'total': 0, 'vitorias': 0, 'derrotas': 0, 'empates': 0, 'encerradas': 0}
            # Se preferir que "total" seja apenas v+d+e (exclui encerradas), troque a linha abaixo:
            total = (row[1] or 0) + (row[2] or 0) + (row[3] or 0) + (row[4] or 0)  # inclui encerradas
            return {
                'total': total,
                'vitorias': row[1] or 0,
                'derrotas': row[2] or 0,
                'empates': row[3] or 0,
                'encerradas': row[4] or 0
            }
        finally:
            conn.close()

    def agregados_por_nivel(self, usuario_id):
        """
        Retorna sempre nas chaves 'Fácil'|'Médio'|'Difícil', mesmo que o banco
        tenha guardado 'facil/medio/dificil' em registros antigos.
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
                'Fácil':   {'vitorias': 0, 'derrotas': 0, 'empates': 0},
                'Médio': {'vitorias': 0, 'derrotas': 0, 'empates': 0},
                'Difícil':   {'vitorias': 0, 'derrotas': 0, 'empates': 0},
            }

            for r in cur.fetchall():
                dif_norm = _norm_dif(r[0])
                if dif_norm not in base:
                    base[dif_norm] = {'vitorias': 0, 'derrotas': 0, 'empates': 0}
                base[dif_norm]['vitorias'] = (r[1] or 0)
                base[dif_norm]['derrotas'] = (r[2] or 0)
                base[dif_norm]['empates']  = (r[3] or 0)

            return base
        finally:
            conn.close()
