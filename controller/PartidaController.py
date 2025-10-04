# controller/PartidaController.py
from model.Partida import Partida


class PartidaController:
    def __init__(self, autenticar_controller):
        self.__aut = autenticar_controller

    def get_auth_controller(self):
        """Exposto para telas que precisam abrir login do Jogador 2."""
        return self.__aut

    def criar_partida(self, adversario='IA', dificuldade='Fácil', quem_comeca='brancas',
                      tema='padrao', jogador2=None):
        """
        Cria a configuração da partida em memória.
        - Se adversário = 'Humano', exige que um Jogador 2 esteja autenticado
          (via jogador2 recebido ou via self.__aut.obter_jogador2_atual()).
        - Não exige Jogador 2 se adversário = 'IA'.
        """
        # Garante jogador 1 logado
        ok, msg = self.__aut.exigir_login()
        if not ok:
            return False, msg, None

        jogador1 = self.__aut.obter_usuario_atual()

        # Se for humano vs humano, exige jogador 2
        j2 = None
        if adversario == 'Humano':
            j2 = jogador2 or self.__aut.obter_jogador2_atual()
            if not j2:
                return False, "O segundo jogador precisa fazer login ou criar conta.", None

        # Monta o objeto da partida (em memória)
        partida = Partida(
            jogador_logado_id=jogador1['id'],
            adversario=adversario,           # 'IA' ou 'Humano'
            dificuldade_ia=dificuldade,      # 'Fácil' | 'Médio' | 'Difícil' (para IA)
            quem_comeca=quem_comeca,         # 'brancas' | 'pretas'
            tema_tabuleiro=tema
        )

        # Se houver Jogador 2, guarda como atributos (mesmo que Partida __init__ não tenha esses campos)
        if j2:
            try:
                partida.jogador2_id = j2.get('id')
                partida.jogador2_nome = j2.get('nome')
            except Exception:
                # não falha a criação da partida por isso
                pass

        return True, "Partida configurada.", partida
