from view import JanelaPrincipal
from bootstrap_db import criar_banco

if __name__ == '__main__':
    criar_banco()

    app = JanelaPrincipal()
    app.mainloop()

