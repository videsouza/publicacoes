import sqlite3
from fastapi import FastAPI
from fastapi.responses import FileResponse
from ortools.sat.python import cp_model
from fastapi import UploadFile, File
import pandas as pd
import io

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
# ROTA DE IMPORTAÇÃO EM LOTE (EXCEL) - MODO SUBSTITUIÇÃO TOTAL
# ============================================================================
@app.post("/api/upload-cadastros")
async def upload_cadastros(file: UploadFile = File(...)):
    conteudo = await file.read()
    
    # Lê a planilha usando o Pandas
    df = pd.read_excel(io.BytesIO(conteudo))
    df.columns = df.columns.str.strip().str.upper()
    
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    
    # 1. LIMPEZA TOTAL ANTES DA IMPORTAÇÃO
    # Apaga todos os registros antigos para iniciar um cadastro limpo
    cursor.execute("DELETE FROM turmas")
    cursor.execute("DELETE FROM disciplinas")
    cursor.execute("DELETE FROM professores")
    # Também apagamos a matriz para evitar que ela fique procurando IDs que não existem mais
    cursor.execute("DELETE FROM matrizes") 
    
    resumo = {"turmas": 0, "disciplinas": 0, "professores": 0}
    
    # 2. Processa a coluna TURMAS
    if 'TURMAS' in df.columns:
        turmas = df['TURMAS'].dropna().unique()
        for t in turmas:
            cursor.execute("INSERT INTO turmas (nome) VALUES (?)", (str(t).strip(),))
            resumo["turmas"] += 1
            
    # 3. Processa a coluna DISCIPLINAS
    if 'DISCIPLINAS' in df.columns:
        disciplinas = df['DISCIPLINAS'].dropna().unique()
        for d in disciplinas:
            cursor.execute("INSERT INTO disciplinas (nome) VALUES (?)", (str(d).strip(),))
            resumo["disciplinas"] += 1
            
    # 4. Processa a coluna PROFESSORES
    if 'PROFESSORES' in df.columns:
        professores = df['PROFESSORES'].dropna().unique()
        for p in professores:
            cursor.execute("INSERT INTO professores (nome) VALUES (?)", (str(p).strip(),))
            resumo["professores"] += 1
            
    conexao.commit()
    conexao.close()
    
    return {"mensagem": "Registros antigos apagados e importação concluída!", "resumo": resumo}

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
    
    # 1. Busca os vínculos cadastrados
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

    # Inicializa o Cérebro do OR-Tools
    modelo = cp_model.CpModel()
    
    # Dimensões padrão: 5 dias da semana (Seg-Sex), 5 períodos por dia
    dias = range(5)
    periodos = range(5)
    
    # ------------------------------------------------------------------------
    # PASSO A: CRIANDO AS VARIÁVEIS (A Grade em Branco)
    # ------------------------------------------------------------------------
    grade = {}
    for m in matriz:
        m_id = m[0]
        for d in dias:
            for p in periodos:
                # Cria um interruptor (0 ou 1) para cada possibilidade de horário
                grade[(m_id, d, p)] = modelo.NewBoolVar(f'aula_{m_id}_d{d}_p{p}')

    # ------------------------------------------------------------------------
    # PASSO B: REGRA DE CAPACIDADE (Cumprir a Matriz)
    # ------------------------------------------------------------------------
    for m in matriz:
        m_id = m[0]
        qtd_aulas = m[4]
        # A soma de todas as aulas daquele vínculo na semana deve ser exatamente a cadastrada
        modelo.Add(sum(grade[(m_id, d, p)] for d in dias for p in periodos) == qtd_aulas)

    # ------------------------------------------------------------------------
    # PASSO C: REGRAS DE COLISÃO (Ocupação de Espaço Físico)
    # ------------------------------------------------------------------------
    
    # C1. Uma TURMA só pode ter no máximo 1 aula por horário
    turmas_unicas = set(m[1] for m in matriz)
    for d in dias:
        for p in periodos:
            for turma in turmas_unicas:
                aulas_da_turma = [grade[(m[0], d, p)] for m in matriz if m[1] == turma]
                modelo.AddAtMostOne(aulas_da_turma)
                
    # C2. Um PROFESSOR só pode dar no máximo 1 aula por horário
    professores_unicos = set(m[3] for m in matriz)
    for d in dias:
        for p in periodos:
            for prof in professores_unicos:
                aulas_do_prof = [grade[(m[0], d, p)] for m in matriz if m[3] == prof]
                modelo.AddAtMostOne(aulas_do_prof)


    # C3. Controle de Fadiga (Professor não pode dar 4 aulas seguidas)
    # Pegamos janelas de 4 períodos. O professor pode ocupar no máximo 3 espaços nela.
    for d in dias:
        for prof in professores_unicos:
            # Janela 1: Horários 1, 2, 3 e 4 (índices 0, 1, 2, 3)
            aulas_janela_1 = [grade[(m[0], d, p)] for m in matriz if m[3] == prof for p in [0, 1, 2, 3]]
            modelo.Add(sum(aulas_janela_1) <= 3)
            
            # Janela 2: Horários 2, 3, 4 e 5 (índices 1, 2, 3, 4)
            aulas_janela_2 = [grade[(m[0], d, p)] for m in matriz if m[3] == prof for p in [1, 2, 3, 4]]
            modelo.Add(sum(aulas_janela_2) <= 3)

    # C4. Dispersão Uniforme (Evitar massificação de aulas)
    # Impede que a mesma turma tenha mais de 2 aulas da MESMA disciplina no mesmo dia.
    for d in dias:
        for m in matriz:
            # m[0] é a ID do vínculo (Turma + Disciplina + Professor)
            aulas_no_dia = [grade[(m[0], d, p)] for p in periodos]
            modelo.Add(sum(aulas_no_dia) <= 2)

    # ------------------------------------------------------------------------
    # PASSO D: RESOLVER O QUEBRA-CABEÇA
    # ------------------------------------------------------------------------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0 # Dá 10 segundos para a IA pensar
    
    status = solver.Solve(modelo)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Se encontrou solução, empacotamos o resultado para enviar à tela
        resultado_grade = []
        for m in matriz:
            for d in dias:
                for p in periodos:
                    if solver.Value(grade[(m[0], d, p)]) == 1:
                        resultado_grade.append({
                            "turma": m[1],
                            "disciplina": m[2],
                            "professor": m[3],
                            "dia": d,
                            "periodo": p
                        })
        
        return {
            "mensagem": "Grade gerada com sucesso!",
            "status": "sucesso",
            "grade": resultado_grade
        }
    else:
        return {"erro": "Impossível gerar a grade. Verifique se há aulas demais cadastradas para o limite de horários."}
