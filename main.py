import sqlite3
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI(title="Sistema Base 2.0")

# ============================================================================
# 0. CONFIGURAÇÃO DO BANCO DE DADOS
# ============================================================================
def inicializar_banco():
    # Cria (ou conecta) a um arquivo de banco de dados local
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    
    # 1. Cria a gaveta de Turmas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS turmas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        )
    ''')
    
    # 2. Cria a gaveta de Disciplinas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS disciplinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        )
    ''')
    
    # 3. Cria a gaveta de Professores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS professores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        )
    ''')
    
    conexao.commit()
    conexao.close()
    print("Banco de dados inicializado com sucesso!")

# Executa a função assim que o servidor ligar
inicializar_banco()

# ============================================================================
# 1. ROTAS DE API (Backend)
# ============================================================================
@app.get("/api/status")
def status_sistema():
    return {"status": "Servidor e Banco de Dados rodando perfeitamente", "versao": "2.1"}



import sqlite3
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel # <-- 1. Nova ferramenta importada

app = FastAPI(title="Sistema Base 2.0")

# ... [Mantenha a sua função inicializar_banco() aqui] ...

# ============================================================================
# MODELOS DE DADOS (Filtro de Segurança)
# ============================================================================
class TurmaBase(BaseModel):
    nome: str

# ============================================================================
# ROTAS DA API - TURMAS
# ============================================================================

# Rota para LISTAR as turmas salvas
@app.get("/api/turmas")
def listar_turmas():
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome FROM turmas")
    linhas = cursor.fetchall()
    conexao.close()
    
    # Transforma o resultado do banco em uma lista que o JavaScript entende
    return [{"id": linha[0], "nome": linha[1]} for linha in linhas]

# Rota para CRIAR uma nova turma
@app.post("/api/turmas")
def criar_turma(turma: TurmaBase):
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO turmas (nome) VALUES (?)", (turma.nome,))
    conexao.commit()
    conexao.close()
    
    return {"mensagem": "Turma salva com sucesso!"}


# ============================================================================
# 2. ROTAS VISUAIS (Frontend)
# ============================================================================
@app.get("/")
def pagina_principal():
    return FileResponse("index.html")
