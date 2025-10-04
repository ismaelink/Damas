import sqlite3, hashlib
from model.bootstrap_db import _caminho_banco

def hash_senha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def redefinir_senha(usuario, nova_senha):
    conn = sqlite3.connect(_caminho_banco())
    cur = conn.cursor()
    cur.execute("UPDATE usuarios SET senha_hash=? WHERE nome=?", (hash_senha(nova_senha), usuario))
    conn.commit()
    conn.close()
    print(f"Senha do usuário '{usuario}' foi redefinida com sucesso.")

# --- CONFIGURE AQUI ---
redefinir_senha("erika", "123456")
