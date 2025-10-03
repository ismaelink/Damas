# model/PartidaDAO.py
import os
import sqlite3
from datetime import datetime

class PartidaDAO:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.__caminho = os.path.join(base_dir, 'banco/banco.db')

    def __con(self):
        c = sqlite3.connect(self.__caminho)
        c.execute('PRAGMA foreign_keys = ON;')
        return c

    # ---------- gravação ----------
    def registrar(self, usuario_id:int, adversario:str, dificuldade:str,
                  comeca:str, tema:str, resultado:str,
                  movimentos:int=0, duracao_segundos:int=0):
        con = self.__con()
        try:
            cur = con.cursor()
            cur.execute("""
                INSERT INTO partidas
                (usuario_id, adversario, dificuldade, comeca, tema, resultado, movimentos, duracao_segundos)
                VALUES (?,?,?,?,?,?,?,?);
            """, (usuario_id, adversario, dificuldade, comeca, tema, resultado, movimentos, duracao_segundos))
            con.commit()
            return cur.lastrowid
        finally:
            con.close()

    # ---------- consultas simples ----------
    def listar_por_usuario(self, usuario_id:int, limite:int=100):
        con = self.__con()
        try:
            cur = con.cursor()
            cur.execute("""
                SELECT id, criado_em, adversario, dificuldade, comeca, tema, resultado,
                       movimentos, duracao_segundos
                  FROM partidas
                 WHERE usuario_id = ?
                 ORDER BY datetime(criado_em) DESC
                 LIMIT ?;
            """, (usuario_id, limite))
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        finally:
            con.close()

    def agregados(self, usuario_id:int):
        con = self.__con()
        try:
            cur = con.cursor()
            cur.execute("""
                SELECT
                  SUM(CASE WHEN resultado='vitoria'  THEN 1 ELSE 0 END),
                  SUM(CASE WHEN resultado='derrota'  THEN 1 ELSE 0 END),
                  SUM(CASE WHEN resultado='empate'   THEN 1 ELSE 0 END),
                  COUNT(*)
                FROM partidas
                WHERE usuario_id = ?;
            """, (usuario_id,))
            v, d, e, total = cur.fetchone()
            v = v or 0; d = d or 0; e = e or 0; total = total or 0
            return {"vitorias": v, "derrotas": d, "empates": e, "total": total}
        finally:
            con.close()

    # ---------- filtros ----------
    def listar_filtrado(self, usuario_id:int, dificuldade:str|None, resultado:str|None,
                        data_ini:str|None, data_fim:str|None, limite:int=500):
        """
        data_ini/data_fim em 'YYYY-MM-DD' (inclusive). Campos None/'' são ignorados.
        """
        con = self.__con()
        try:
            sql = ["""
                SELECT id, criado_em, adversario, dificuldade, comeca, tema, resultado,
                       movimentos, duracao_segundos
                  FROM partidas
                 WHERE usuario_id = ?
            """]
            params = [usuario_id]

            if dificuldade and dificuldade.lower() != 'todos':
                sql.append("AND dificuldade = ?")
                params.append(dificuldade)

            if resultado and resultado.lower() != 'todos':
                sql.append("AND resultado = ?")
                params.append(resultado)

            if data_ini:
                # inclui 00:00:00
                sql.append("AND date(criado_em) >= date(?)")
                params.append(data_ini)

            if data_fim:
                # inclui até o fim do dia
                sql.append("AND date(criado_em) <= date(?)")
                params.append(data_fim)

            sql.append("ORDER BY datetime(criado_em) DESC")
            sql.append("LIMIT ?")
            params.append(limite)

            q = " ".join(sql)
            cur = con.cursor()
            cur.execute(q, tuple(params))
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        finally:
            con.close()

    def agregados_por_nivel(self, usuario_id:int):
        """Retorna dict por dificuldade: {nivel: {'vitorias': X, 'derrotas': Y, 'empates': Z, 'total': T}}"""
        con = self.__con()
        try:
            cur = con.cursor()
            cur.execute("""
                SELECT dificuldade,
                       SUM(CASE WHEN resultado='vitoria' THEN 1 ELSE 0 END) AS v,
                       SUM(CASE WHEN resultado='derrota' THEN 1 ELSE 0 END) AS d,
                       SUM(CASE WHEN resultado='empate'  THEN 1 ELSE 0 END) AS e,
                       COUNT(*) AS t
                  FROM partidas
                 WHERE usuario_id = ?
                 GROUP BY dificuldade
            """, (usuario_id,))
            out = {}
            for dif, v, d, e, t in cur.fetchall():
                out[dif] = {
                    "vitorias": v or 0,
                    "derrotas": d or 0,
                    "empates":  e or 0,
                    "total":    t or 0
                }
            return out
        finally:
            con.close()
