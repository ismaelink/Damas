# model/Partida.py
from dataclasses import dataclass, field
from typing import Optional, Literal

Cor = Literal['brancas', 'pretas']

@dataclass
class Partida:
    jogador_logado_id: int
    adversario: Literal['IA', 'Humano'] = 'IA'
    dificuldade_ia: Literal['easy', 'medium', 'hard'] = 'easy'
    quem_comeca: Cor = 'brancas'
    tema_tabuleiro: str = 'padrao'
    id: Optional[int] = field(default=None)
