# controller/AutenticarController.py
from hashlib import sha256
from model.UsuarioDAO import UsuarioDAO


class AutenticarController:
    """
    Gerencia autenticação do Jogador 1 (dono da sessão) e do Jogador 2 (convidado).
    Inclui migração automática de senhas legadas (texto puro) para SHA-256 no primeiro login.
    """

    def __init__(self, usuario_dao: UsuarioDAO):
        self.__dao = usuario_dao
        self.__usuario_atual = None   # Jogador 1
        self.__jogador2_atual = None  # Jogador 2 (convidado)

    # ---------- util ----------
    def _hash(self, s):
        return sha256((s or "").encode("utf-8")).hexdigest()

    def _migrar_senha_se_necessario(self, registro, senha_plana):
        """
        Se a senha salva for texto puro e igual à senha digitada, atualiza para SHA-256.
        Retorna True se migrou; False caso contrário.
        """
        if not registro:
            return False
        armazenada = (registro.get("senha_hash") or "").strip()
        if armazenada and senha_plana and armazenada == senha_plana:
            self.__dao.atualizar(usuario_id=registro["id"], senha_hash=self._hash(senha_plana))
            return True
        return False

    # ---------- sessão jogador 1 ----------
    def autenticar_usuario(self, nome, senha):
        nome = (nome or "").strip()
        senha = (senha or "").strip()
        if not nome or not senha:
            return False, "Informe nome e senha."

        registro = self.__dao.obter_por_nome(nome)
        if not registro:
            return False, "Usuário não encontrado."

        if registro.get("senha_hash") == self._hash(senha):
            self.__usuario_atual = dict(registro)
            return True, "Login realizado com sucesso."

        # Fallback para senha legada (em texto puro)
        if self._migrar_senha_se_necessario(registro, senha):
            self.__usuario_atual = self.__dao.obter_por_id(registro["id"])
            return True, "Login realizado com sucesso."

        return False, "Senha inválida."

    def obter_usuario_atual(self):
        return self.__usuario_atual

    def deslogar(self):
        self.__usuario_atual = None

    def exigir_login(self):
        if not self.__usuario_atual:
            return False, "Faça login para continuar."
        return True, "OK"

    # ---------- sessão jogador 2 (convidado) ----------
    def autenticar_jogador2(self, nome, senha):
        nome = (nome or "").strip()
        senha = (senha or "").strip()
        if not nome or not senha:
            return False, "Informe nome e senha do Jogador 2."

        registro = self.__dao.obter_por_nome(nome)
        if not registro:
            return False, "Usuário do Jogador 2 não encontrado."

        if registro.get("senha_hash") == self._hash(senha):
            self.__jogador2_atual = dict(registro)
            return True, "Jogador 2 autenticado."

        if self._migrar_senha_se_necessario(registro, senha):
            self.__jogador2_atual = self.__dao.obter_por_id(registro["id"])
            return True, "Jogador 2 autenticado."

        return False, "Senha do Jogador 2 inválida."

    def registrar_e_autenticar_jogador2(self, nome, senha):
        nome = (nome or "").strip()
        senha = (senha or "").strip()
        if not nome or not senha:
            return False, "Informe nome e senha para o Jogador 2."

        if self.__dao.obter_por_nome(nome):
            return False, "Já existe um usuário com esse nome."

        novo_id = self.__dao.inserir(nome, senha)  # DAO já grava com SHA-256
        registro = self.__dao.obter_por_id(novo_id)
        self.__jogador2_atual = dict(registro)
        return True, "Conta criada e Jogador 2 autenticado."

    def obter_jogador2_atual(self):
        return self.__jogador2_atual

    def deslogar_jogador2(self):
        self.__jogador2_atual = None

    # ---------- cadastro/alteração/tema (Jogador 1) ----------
    def registrar_usuario(self, nome, senha):
        nome = (nome or "").strip()
        senha = (senha or "").strip()
        if not nome or not senha:
            return False, "Informe nome e senha."

        if self.__dao.obter_por_nome(nome):
            return False, "Já existe um usuário com esse nome."

        try:
            self.__dao.inserir(nome, senha)  # DAO já aplica hash
            return True, "Conta criada com sucesso."
        except Exception as e:
            return False, f"Erro ao cadastrar: {e}"

    def alterar_dados_usuario(self, novo_nome, nova_senha=None):
        u = self.__usuario_atual
        if not u:
            return False, "Faça login."

        novo_nome = (novo_nome or "").strip()
        if not novo_nome:
            return False, "O nome não pode ficar vazio."

        existente = self.__dao.obter_por_nome(novo_nome)
        if existente and existente.get("id") != u["id"]:
            return False, "Já existe um usuário com esse nome."

        senha_hash = self._hash(nova_senha) if (nova_senha and nova_senha.strip()) else None
        ok, msg = self.__dao.atualizar(usuario_id=u["id"], nome=novo_nome, senha_hash=senha_hash)
        if ok:
            self.__usuario_atual = self.__dao.obter_por_id(u["id"])
        return ok, msg

    def salvar_tema_preferido(self, tema):
        u = self.__usuario_atual
        if not u:
            return False, "Faça login."
        ok = self.__dao.salvar_tema_preferido(u["id"], tema)
        if ok:
            self.__usuario_atual = self.__dao.obter_por_id(u["id"])
        return ok, "OK"
