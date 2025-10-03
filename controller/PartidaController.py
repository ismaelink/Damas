# controller/PartidaController.py
from model.Partida import Partida

class PartidaController:
    def __init__(self, autenticar_controller):
        self.__aut = autenticar_controller

    def criar_partida(self, adversario='IA', dificuldade='easy', quem_comeca='brancas', tema='padrao'):
        ok, msg = self.__aut.exigir_login()
        if not ok:
            return False, msg, None

        usuario = self.__aut.obter_usuario_atual()
        partida = Partida(
            jogador_logado_id=usuario['id'],
            adversario=adversario,
            dificuldade_ia=dificuldade,
            quem_comeca=quem_comeca,
            tema_tabuleiro=tema
        )

        # Aqui você pode persistir no BD (tabela partidas) quando existir.
        # Ex.: self.__dao_partida.salvar(partida) -> retorna id
        # Por enquanto, só devolve o objeto em memória.
        return True, "Partida configurada.", partida
