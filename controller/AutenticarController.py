import re
import hashlib
import secrets

class AutenticarController:
    def __init__(self, usuario_dao):
        self.__dao = usuario_dao
        self.__usuario_atual = None

    def __gerar_salt(self):
        return secrets.token_hex(16)

    def __hash_senha(self, senha, salt=''):
        if not salt:
            salt = self.__gerar_salt()
        h = hashlib.sha256((salt + senha).encode('utf-8')).hexdigest()
        return f"{salt}${h}"

    def __verificar_senha(self, senha, senha_hash):
        try:
            salt, hguardado = senha_hash.split('$', 1)
        except ValueError:
            return False
        h = hashlib.sha256((salt + senha).encode('utf-8')).hexdigest()
        return h == hguardado

    def __validar_nome(self, nome):
        if not nome or not nome.strip():
            return False, "O campo Nome está vazio."
        nome = nome.strip()
        if len(nome) < 3 or len(nome) > 32:
            return False, "O Nome deve ter entre 3 e 32 caracteres."
        if not re.fullmatch(r'[A-Za-z0-9_.-]+', nome):
            return False, "O Nome só pode conter letras, números, '.', '_' e '-'."
        return True, ""

    def __validar_senha(self, senha):
        if not senha or not senha.strip():
            return False, "O campo Senha está vazio."
        if len(senha) < 6:
            return False, "A Senha deve ter no mínimo 6 caracteres."
        return True, ""

    def registrar_usuario(self, nome, senha):
        ok, msg = self.__validar_nome(nome)
        if not ok:
            return False, msg
        ok, msg = self.__validar_senha(senha)
        if not ok:
            return False, msg

        nome = nome.strip()
        if self.__dao.existe_nome(nome):
            return False, "O nome de usuário já existe."

        senha_hash = self.__hash_senha(senha)
        self.__dao.criar(nome, senha_hash)
        return True, "Usuário cadastrado com sucesso."

    def autenticar_usuario(self, nome, senha):
        ok, msg = self.__validar_nome(nome)
        if not ok:
            return False, msg
        ok, msg = self.__validar_senha(senha)
        if not ok:
            return False, msg

        nome = nome.strip()
        registro = self.__dao.buscar_por_nome(nome)
        if not registro:
            return False, "O nome de usuário não existe."

        if not self.__verificar_senha(senha, registro['senha_hash']):
            return False, "Senha incorreta."

        self.__usuario_atual = {
            'id': registro['id'],
            'nome': registro['nome'],
            'tema_preferido': registro['tema_preferido'],
        }
        return True, "Bem-vindo, " + registro['nome'] + "!"

    def deslogar(self):
        self.__usuario_atual = None

    def exigir_login(self):
        if self.__usuario_atual is None:
            return False, "Faça login para continuar."
        return True, ""

    def obter_usuario_atual(self):
        return self.__usuario_atual

