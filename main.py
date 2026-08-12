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
# ROTA DE IMPORTAÇÃO EM LOTE (EXCEL 2 PLANILHAS) - MODO SUBSTITUIÇÃO TOTAL
# ============================================================================
@app.post("/api/upload-cadastros")
async def upload_cadastros(file: UploadFile = File(...)):
    conteudo = await file.read()
    
    # 1. Lê as duas abas da planilha (0 = Planilha1, 1 = Planilha2)
    try:
        df_prof = pd.read_excel(io.BytesIO(conteudo), sheet_name=0)
        df_aulas = pd.read_excel(io.BytesIO(conteudo), sheet_name=1)
    except Exception as e:
        return {"erro": "Certifique-se de que o arquivo Excel possui as duas abas (Planilha1 e Planilha2)."}

    # Padroniza os nomes das colunas (remove espaços extras e deixa maiúsculo)
    df_prof.rename(columns=lambda x: str(x).strip().upper(), inplace=True)
    df_aulas.rename(columns=lambda x: str(x).strip().upper(), inplace=True)
    
    if 'TURMA' not in df_prof.columns:
        return {"erro": "A Planilha1 precisa ter uma coluna chamada 'TURMA'."}

    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    
    # 2. LIMPEZA TOTAL ANTES DA IMPORTAÇÃO
    cursor.execute("DELETE FROM turmas")
    cursor.execute("DELETE FROM disciplinas")
    cursor.execute("DELETE FROM professores")
    cursor.execute("DELETE FROM matrizes") 
    
    # Conjuntos para garantir que não teremos dados duplicados
    turmas_set = set()
    professores_set = set()
    disciplinas_set = set(col for col in df_prof.columns if col != 'TURMA')
    
    # 3. MAPEAMENTO DE DADOS BASE (Turmas e Professores)
    for index, row in df_prof.iterrows():
        turma = str(row['TURMA']).strip()
        if pd.isna(turma) or not turma or turma.lower() == 'nan': 
            continue
        turmas_set.add(turma)
        
        for disc in disciplinas_set:
            prof = str(row.get(disc, '')).strip()
            if prof and prof.lower() != 'nan':
                professores_set.add(prof)

    # 4. SALVANDO DADOS BASE E GUARDANDO OS IDs
    mapa_turmas = {}
    for t in turmas_set:
        cursor.execute("INSERT INTO turmas (nome) VALUES (?)", (t,))
        mapa_turmas[t] = cursor.lastrowid
        
    mapa_disc = {}
    for d in disciplinas_set:
        cursor.execute("INSERT INTO disciplinas (nome) VALUES (?)", (d,))
        mapa_disc[d] = cursor.lastrowid
        
    mapa_prof = {}
    for p in professores_set:
        cursor.execute("INSERT INTO professores (nome) VALUES (?)", (p,))
        mapa_prof[p] = cursor.lastrowid

    # 5. CRUZAMENTO DE DADOS (Criando os vínculos da Matriz)
    vinculos_criados = 0
    for index, row_prof in df_prof.iterrows():
        turma_nome = str(row_prof['TURMA']).strip()
        if turma_nome not in mapa_turmas: continue
        
        # Procura a mesma turma na Planilha 2 (Quantidade de aulas)
        row_aulas = df_aulas[df_aulas['TURMA'].astype(str).str.strip() == turma_nome]
        if row_aulas.empty: continue
        row_aulas = row_aulas.iloc[0] # Pega a linha correspondente
        
        # Para cada disciplina, verifica o professor e a quantidade de aulas
        for disc_nome in disciplinas_set:
            prof_nome = str(row_prof.get(disc_nome, '')).strip()
            aulas_val = row_aulas.get(disc_nome, 0)
            
            try:
                qtd_aulas = int(float(aulas_val))
            except:
                qtd_aulas = 0
                
            # Se existe um professor válido e a quantidade de aulas é maior que zero, cria o vínculo
            if prof_nome and prof_nome.lower() != 'nan' and qtd_aulas > 0:
                t_id = mapa_turmas[turma_nome]
                d_id = mapa_disc[disc_nome]
                p_id = mapa_prof[prof_nome]
                
                cursor.execute(
                    "INSERT INTO matrizes (turma_id, disciplina_id, professor_id, aulas) VALUES (?, ?, ?, ?)", 
                    (t_id, d_id, p_id, qtd_aulas)
                )
                vinculos_criados += 1

    conexao.commit()
    conexao.close()
    
    resumo = {
        "turmas": len(turmas_set),
        "disciplinas": len(disciplinas_set),
        "professores": len(professores_set),
        "vinculos": vinculos_criados
    }
    
    return {"mensagem": "Automação concluída!", "resumo": resumo}

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
    periodos = range(6)
    
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
    # PASSO C: REGRAS DE COLISÃO E RESTRIÇÕES
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

    # C3. Controle de Fadiga (Regra Personalizada)
    # O limite diário de 6 aulas já é garantido pelos 6 períodos.
    # Esta regra garante que o professor dê no máximo 2 aulas para a MESMA turma por dia.
    for d in dias:
        for prof in professores_unicos:
            for turma in turmas_unicas:
                # Coleta todas as aulas que este professor dará para esta turma neste dia
                aulas_prof_turma_dia = [
                    grade[(m[0], d, p)] 
                    for m in matriz if m[3] == prof and m[1] == turma 
                    for p in periodos
                ]
                # Se existe vínculo, aplica a trava de limite máximo = 2
                if aulas_prof_turma_dia:
                    modelo.Add(sum(aulas_prof_turma_dia) <= 2)

   # C3. Controle de Fadiga (Regra Personalizada)
    # Garante que o professor dê no máximo 2 aulas para a MESMA turma por dia.
    for d in dias:
        for prof in professores_unicos:
            for turma in turmas_unicas:
                aulas_prof_turma_dia = [
                    grade[(m[0], d, p)] 
                    for m in matriz if m[3] == prof and m[1] == turma 
                    for p in periodos
                ]
                if aulas_prof_turma_dia:
                    modelo.Add(sum(aulas_prof_turma_dia) <= 2)

    # C4. Dobradinhas e Dispersão Uniforme
    # Substituímos a trava genérica por Padrões Permitidos (Allowed Assignments).
    padroes_permitidos = []
    
    # Cenário A: 0 aulas no dia
    padroes_permitidos.append([0, 0, 0, 0, 0, 0])
    
    # Cenário B: 1 aula isolada (Pode cair em qualquer um dos 6 horários)
    for p in range(6):
        padrao = [0] * 6
        padrao[p] = 1
        padroes_permitidos.append(padrao)
        
    # Cenário C: 2 aulas seguidas (Dobradinha)
    for p in range(5):
        if p == 2:
            continue # Bloqueia a dobradinha que atravessa o recreio (Horários 2 e 3 na contagem do Python)
        padrao = [0] * 6
        padrao[p] = 1
        padrao[p+1] = 1
        padroes_permitidos.append(padrao)

    # Aplica a regra de padrões para cada vínculo da matriz em todos os dias
    for d in dias:
        for m in matriz:
            aulas_no_dia = [grade[(m[0], d, p)] for p in range(6)]
            modelo.AddAllowedAssignments(aulas_no_dia, padroes_permitidos)

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
