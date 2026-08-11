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

class DisciplinaBase(BaseModel):
    nome: str

class ProfessorBase(BaseModel):
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

# Rota para DELETAR uma turma
@app.delete("/api/turmas/{turma_id}")
def deletar_turma(turma_id: int):
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM turmas WHERE id = ?", (turma_id,))
    conexao.commit()
    conexao.close()
    
    return {"mensagem": "Turma removida com sucesso!"}

# ============================================================================
# 2. ROTAS VISUAIS (Frontend)
# ============================================================================
@app.get("/")
def pagina_principal():
    return FileResponse("index.html")


# ============================================================================
# ROTAS DA API - DISCIPLINAS
# ============================================================================
@app.get("/api/disciplinas")
def listar_disciplinas():
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome FROM disciplinas")
    linhas = cursor.fetchall()
    conexao.close()
    return [{"id": linha[0], "nome": linha[1]} for linha in linhas]

@app.post("/api/disciplinas")
def criar_disciplina(disciplina: DisciplinaBase):
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO disciplinas (nome) VALUES (?)", (disciplina.nome,))
    conexao.commit()
    conexao.close()
    return {"mensagem": "Disciplina salva com sucesso!"}

@app.delete("/api/disciplinas/{disciplina_id}")
def deletar_disciplina(disciplina_id: int):
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM disciplinas WHERE id = ?", (disciplina_id,))
    conexao.commit()
    conexao.close()
    return {"mensagem": "Disciplina removida!"}

# ============================================================================
# ROTAS DA API - PROFESSORES
# ============================================================================
@app.get("/api/professores")
def listar_professores():
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome FROM professores")
    linhas = cursor.fetchall()
    conexao.close()
    return [{"id": linha[0], "nome": linha[1]} for linha in linhas]

@app.post("/api/professores")
def criar_professor(professor: ProfessorBase):
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO professores (nome) VALUES (?)", (professor.nome,))
    conexao.commit()
    conexao.close()
    return {"mensagem": "Professor salvo com sucesso!"}

@app.delete("/api/professores/{professor_id}")
def deletar_professor(professor_id: int):
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM professores WHERE id = ?", (professor_id,))
    conexao.commit()
    conexao.close()
    return {"mensagem": "Professor removido!"}
