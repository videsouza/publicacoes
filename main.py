import sqlite3
from fastapi import FastAPI
from fastapi.responses import FileResponse
from ortools.sat.python import cp_model

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

    # 4. Cria a gaveta da Matriz Curricular (Os Vínculos)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matrizes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            turma_id INTEGER,
            disciplina_id INTEGER,
            professor_id INTEGER,
            aulas INTEGER
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

class MatrizBase(BaseModel):
    turma_id: int
    disciplina_id: int
    professor_id: int
    aulas: int

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

# ============================================================================
# ROTAS DA API - MATRIZ CURRICULAR (VÍNCULOS)
# ============================================================================
@app.get("/api/matrizes")
def listar_matrizes():
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    # Puxa os dados cruzando as tabelas para pegar os nomes em vez dos IDs
    cursor.execute('''
        SELECT m.id, t.nome, d.nome, p.nome, m.aulas 
        FROM matrizes m
        JOIN turmas t ON m.turma_id = t.id
        JOIN disciplinas d ON m.disciplina_id = d.id
        JOIN professores p ON m.professor_id = p.id
    ''')
    linhas = cursor.fetchall()
    conexao.close()
    return [{"id": l[0], "turma": l[1], "disciplina": l[2], "professor": l[3], "aulas": l[4]} for l in linhas]

@app.post("/api/matrizes")
def criar_matriz(matriz: MatrizBase):
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO matrizes (turma_id, disciplina_id, professor_id, aulas) VALUES (?, ?, ?, ?)", 
                   (matriz.turma_id, matriz.disciplina_id, matriz.professor_id, matriz.aulas))
    conexao.commit()
    conexao.close()
    return {"mensagem": "Vínculo salvo com sucesso!"}

@app.delete("/api/matrizes/{matriz_id}")
def deletar_matriz(matriz_id: int):
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM matrizes WHERE id = ?", (matriz_id,))
    conexao.commit()
    conexao.close()
    return {"mensagem": "Vínculo removido!"}

# ============================================================================
# ROTAS DA API - MOTOR DE GERAÇÃO DE GRADE (OR-TOOLS)
# ============================================================================
@app.post("/api/gerar-grade")
def gerar_grade_mestra():
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    
    # 1. Busca as regras do jogo (Matriz Curricular)
    cursor.execute('''
        SELECT m.id, t.nome, d.nome, p.nome, m.aulas 
        FROM matrizes m
        JOIN turmas t ON m.turma_id = t.id
        JOIN disciplinas d ON m.disciplina_id = d.id
        JOIN professores p ON m.professor_id = p.id
    ''')
    matriz = cursor.fetchall()
    conexao.close()

    if not matriz:
        return {"erro": "A matriz curricular está vazia. Adicione vínculos no Passo 2."}

    # 2. Inicializa o Cérebro do OR-Tools
    modelo = cp_model.CpModel()
    
    # ------------------------------------------------------------------------
    # O espaço onde a mágica matemática vai acontecer nas próximas etapas:
    # - Criação das Variáveis (Dias, Horários, Professores)
    # - Restrições Rígidas (Ex: Professor não pode dar duas aulas ao mesmo tempo)
    # - Restrições Flexíveis (Ex: Evitar janelas e fadiga)
    # ------------------------------------------------------------------------

    # 3. Retorno temporário para testarmos a conexão da tela com o Python
    return {
        "mensagem": "Motor OR-Tools acionado com sucesso!",
        "dados_lidos": len(matriz)
    }
