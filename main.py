import sqlite3
import io
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import List
from ortools.sat.python import cp_model

app = FastAPI(title="Sistema Base 2.0")

# ============================================================================
# INICIALIZAÇÃO DO BANCO DE DADOS
# ============================================================================
def inicializar_banco():
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS turmas (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS disciplinas (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS professores (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT)")
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

inicializar_banco()

# ============================================================================
# ROTAS VISUAIS
# ============================================================================
@app.get("/")
def renderizar_painel():
    return FileResponse("index.html")

# ============================================================================
# MODELOS DE DADOS (Filtros de Segurança)
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

class ConfigGrade(BaseModel):
    prioridades: List[str] = []

class ItemGrade(BaseModel):
    turma: str
    disciplina: str
    professor: str
    dia: int
    periodo: int

# ============================================================================
# ROTAS DA API - TURMAS
# ============================================================================
@app.get("/api/turmas")
def listar_turmas():
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome FROM turmas")
    linhas = cursor.fetchall()
    conexao.close()
    return [{"id": linha[0], "nome": linha[1]} for linha in linhas]

@app.post("/api/turmas")
def criar_turma(turma: TurmaBase):
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO turmas (nome) VALUES (?)", (turma.nome,))
    conexao.commit()
    conexao.close()
    return {"mensagem": "Turma salva com sucesso!"}

@app.delete("/api/turmas/{turma_id}")
def deletar_turma(turma_id: int):
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM turmas WHERE id = ?", (turma_id,))
    conexao.commit()
    conexao.close()
    return {"mensagem": "Turma removida com sucesso!"}

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
# ROTA DE IMPORTAÇÃO EM LOTE (EXCEL 2 PLANILHAS)
# ============================================================================
@app.post("/api/upload-cadastros")
async def upload_cadastros(file: UploadFile = File(...)):
    conteudo = await file.read()
    
    try:
        df_prof = pd.read_excel(io.BytesIO(conteudo), sheet_name=0)
        df_aulas = pd.read_excel(io.BytesIO(conteudo), sheet_name=1)
    except Exception as e:
        return {"erro": "Certifique-se de que o arquivo Excel possui as duas abas (Planilha1 e Planilha2)."}

    df_prof.rename(columns=lambda x: str(x).strip().upper(), inplace=True)
    df_aulas.rename(columns=lambda x: str(x).strip().upper(), inplace=True)
    
    if 'TURMA' not in df_prof.columns:
        return {"erro": "A Planilha1 precisa ter uma coluna chamada 'TURMA'."}

    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    
    cursor.execute("DELETE FROM turmas")
    cursor.execute("DELETE FROM disciplinas")
    cursor.execute("DELETE FROM professores")
    cursor.execute("DELETE FROM matrizes") 
    
    turmas_set = set()
    professores_set = set()
    disciplinas_set = set(col for col in df_prof.columns if col != 'TURMA')
    
    for index, row in df_prof.iterrows():
        turma = str(row['TURMA']).strip()
        if pd.isna(turma) or not turma or turma.lower() == 'nan': 
            continue
        turmas_set.add(turma)
        
        for disc in disciplinas_set:
            prof = str(row.get(disc, '')).strip()
            if prof and prof.lower() != 'nan':
                professores_set.add(prof)

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

    vinculos_criados = 0
    for index, row_prof in df_prof.iterrows():
        turma_nome = str(row_prof['TURMA']).strip()
        if turma_nome not in mapa_turmas: continue
        
        row_aulas = df_aulas[df_aulas['TURMA'].astype(str).str.strip() == turma_nome]
        if row_aulas.empty: continue
        row_aulas = row_aulas.iloc[0] 
        
        for disc_nome in disciplinas_set:
            prof_nome = str(row_prof.get(disc_nome, '')).strip()
            aulas_val = row_aulas.get(disc_nome, 0)
            
            try:
                qtd_aulas = int(float(aulas_val))
            except:
                qtd_aulas = 0
                
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
# MOTOR DE GERAÇÃO DE GRADE (OR-TOOLS) - FORÇA BRUTA (DOBRADINHAS)
# ============================================================================
@app.post("/api/gerar-grade")
def gerar_grade_mestra(config: ConfigGrade):
    conexao = sqlite3.connect("banco_sistema.db")
    cursor = conexao.cursor()
    
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

    modelo = cp_model.CpModel()
    
    # 5 dias da semana (Seg-Sex), 6 períodos por dia
    dias = range(5)
    periodos = range(6)
    
    # PASSO A: CRIANDO AS VARIÁVEIS (A Grade em Branco)
    grade = {}
    for m in matriz:
        m_id = m[0]
        for d in dias:
            for p in periodos:
                grade[(m_id, d, p)] = modelo.NewBoolVar(f'aula_{m_id}_d{d}_p{p}')

    # PASSO B: REGRA DE CAPACIDADE (Cumprir a Matriz)
    for m in matriz:
        m_id = m[0]
        qtd_aulas = m[4]
        modelo.Add(sum(grade[(m_id, d, p)] for d in dias for p in periodos) == qtd_aulas)

    # PASSO C: REGRAS DE COLISÃO
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

    # C3. Controle de Fadiga (Máximo 2 aulas por turma por dia para o mesmo professor)
    for d in dias:
        for prof in professores_unicos:
            for turma in turmas_unicas:
                aulas_prof_turma_dia = [
                    grade[(m[0], d, p)] for m in matriz if m[3] == prof and m[1] == turma for p in periodos
                ]
                if aulas_prof_turma_dia:
                    modelo.Add(sum(aulas_prof_turma_dia) <= 2)

    # C4. Dobradinhas Obrigatórias (Força Bruta)
    lista_prioridades = [p.strip().upper() for p in config.prioridades]

    padrao_zero = [0, 0, 0, 0, 0, 0]
    
    padroes_um = [] 
    for p in range(6):
        padrao = [0] * 6
        padrao[p] = 1
        padroes_um.append(padrao)
        
    padroes_dois = [] 
    for p in range(5):
        # A trava do recreio (if p == 2: continue) foi removida!
        # Agora a IA tem permissão total para criar uma dobradinha unindo a 3ª e a 4ª aula.
        padrao = [0] * 6
        padrao[p] = 1
        padrao[p+1] = 1
        padroes_dois.append(padrao)

    for m in matriz:
        m_id = m[0]
        nome_disciplina = str(m[2]).strip().upper()
        qtd_aulas = m[4]
        eh_prioridade = nome_disciplina in lista_prioridades
        
        if eh_prioridade:
            qtd_dobras_exigidas = qtd_aulas // 2
            qtd_soltas_exigidas = qtd_aulas % 2
            
            dias_com_dobradinha = []
            dias_com_aula_solta = []
            
            for d in dias:
                aulas_no_dia = [grade[(m_id, d, p)] for p in periodos]
                
                tem_duas = modelo.NewBoolVar(f'duas_{m_id}_d{d}')
                tem_uma = modelo.NewBoolVar(f'uma_{m_id}_d{d}')
                tem_zero = modelo.NewBoolVar(f'zero_{m_id}_d{d}')
                
                modelo.AddExactlyOne([tem_zero, tem_uma, tem_duas])
                
                modelo.Add(sum(aulas_no_dia) == 2).OnlyEnforceIf(tem_duas)
                modelo.Add(sum(aulas_no_dia) == 1).OnlyEnforceIf(tem_uma)
                modelo.Add(sum(aulas_no_dia) == 0).OnlyEnforceIf(tem_zero)
                
                modelo.AddAllowedAssignments(aulas_no_dia, [padrao_zero] + padroes_um + padroes_dois)
                
                dias_com_dobradinha.append(tem_duas)
                dias_com_aula_solta.append(tem_uma)
            
            modelo.Add(sum(dias_com_dobradinha) == qtd_dobras_exigidas)
            modelo.Add(sum(dias_com_aula_solta) == qtd_soltas_exigidas)
            
        else:
            for d in dias:
                aulas_no_dia = [grade[(m_id, d, p)] for p in periodos]
                modelo.AddAllowedAssignments(aulas_no_dia, [padrao_zero] + padroes_um + padroes_dois)

    # PASSO D: RESOLVER O QUEBRA-CABEÇA
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60.0 
    solver.parameters.num_search_workers = 8 

    status = solver.Solve(modelo)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
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
        return {"erro": "A Inteligência não conseguiu resolver a grade. Tente reduzir as restrições ou verifique se as aulas cadastradas ultrapassam 30 semanais por turma."}


# ============================================================================
# ROTA DE EXPORTAÇÃO PARA EXCEL
# ============================================================================
# ============================================================================
# ROTA DE EXPORTAÇÃO PARA EXCEL (FORMATO ESCOLAR TRADICIONAL)
# ============================================================================
@app.post("/api/exportar-grade")
def exportar_grade_excel(grade: List[ItemGrade]):
    import io
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Border, Side, Alignment, Font

    # Inicializa a planilha virtual
    wb = Workbook()
    ws = wb.active
    ws.title = "Grade_Mestra"

    # Extrai as listas únicas e ordenadas
    turmas = sorted(list(set(item.turma for item in grade)))
    professores_unicos = sorted(list(set(item.professor for item in grade)))
    
    # Nomenclatura oficial
    dias_nomes = {0: "SEG", 1: "TER", 2: "QUA", 3: "QUI", 4: "SEX"}

    # Cria um mapa de busca rápida (Dia, Período, Turma) -> Aula
    mapa_aulas = {}
    for item in grade:
        mapa_aulas[(item.dia, item.periodo, item.turma)] = {
            "texto": f"{item.disciplina}\n{item.professor}",
            "professor": item.professor
        }

    # Paleta de 20 cores pastéis suaves (padrão escolar)
    paleta_hex = [
        "FFB3BA", "FFDFBA", "FFFFBA", "BAFFC9", "BAE1FF",
        "D0E6A5", "FFCCB6", "F3B0C3", "C6DBDA", "FEE1E8",
        "FED7C3", "F6EAC2", "ECD5E3", "CBAACB", "FF968A",
        "8FCACA", "CCE2CB", "B6CFB6", "97C1A9", "FCB9AA"
    ]
    
    # Associa uma cor única a cada professor
    mapa_cores = {}
    for i, prof in enumerate(professores_unicos):
        cor = paleta_hex[i % len(paleta_hex)]
        mapa_cores[prof] = PatternFill(start_color=cor, end_color=cor, fill_type="solid")

    # Configuração de Estilos (Bordas, Alinhamento e Fonte)
    borda_fina = Side(border_style="thin", color="000000")
    borda_caixa = Border(left=borda_fina, right=borda_fina, top=borda_fina, bottom=borda_fina)
    alinhamento_centro = Alignment(horizontal="center", vertical="center", wrap_text=True)
    fonte_negrito = Font(bold=True)

    # 1. DESENHANDO O CABEÇALHO (Turmas)
    ws.cell(row=1, column=1, value="DIA").alignment = alinhamento_centro
    ws.cell(row=1, column=2, value="AULA").alignment = alinhamento_centro
    ws.cell(row=1, column=1).font = fonte_negrito
    ws.cell(row=1, column=2).font = fonte_negrito
    ws.cell(row=1, column=1).border = borda_caixa
    ws.cell(row=1, column=2).border = borda_caixa

    for col_idx, turma in enumerate(turmas, start=3):
        celula = ws.cell(row=1, column=col_idx, value=turma)
        celula.alignment = alinhamento_centro
        celula.font = fonte_negrito
        celula.border = borda_caixa

    # 2. DESENHANDO A GRADE (Dias e Períodos)
    linha_atual = 2
    for dia in range(5):
        linha_inicio_dia = linha_atual
        
        for periodo in range(6):
            # Coluna B: Número do Período
            celula_periodo = ws.cell(row=linha_atual, column=2, value=periodo + 1)
            celula_periodo.alignment = alinhamento_centro
            celula_periodo.font = fonte_negrito
            celula_periodo.border = borda_caixa

            # Colunas C em diante: Matérias e Professores
            for col_idx, turma in enumerate(turmas, start=3):
                celula_aula = ws.cell(row=linha_atual, column=col_idx)
                celula_aula.alignment = alinhamento_centro
                celula_aula.border = borda_caixa

                # Busca se existe aula neste cruzamento exato
                aula = mapa_aulas.get((dia, periodo, turma))
                if aula:
                    celula_aula.value = aula["texto"]
                    celula_aula.fill = mapa_cores[aula["professor"]]
            
            linha_atual += 1

        # Mescla as 6 linhas da Coluna A para formar o bloco do Dia da Semana
        ws.merge_cells(start_row=linha_inicio_dia, start_column=1, end_row=linha_atual - 1, end_column=1)
        celula_dia = ws.cell(row=linha_inicio_dia, column=1, value=dias_nomes[dia])
        celula_dia.alignment = alinhamento_centro
        celula_dia.font = fonte_negrito
        
        # Aplica borda em todas as células mescladas do dia para não perder a formatação visual
        for r in range(linha_inicio_dia, linha_atual):
            ws.cell(row=r, column=1).border = borda_caixa

    # 3. AJUSTE DE LARGURA E ALTURA
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 8
    for col_idx in range(3, len(turmas) + 3):
        letra_col = ws.cell(row=1, column=col_idx).column_letter
        ws.column_dimensions[letra_col].width = 18  # Espaço ideal para nome duplo

    for row_idx in range(2, linha_atual):
        ws.row_dimensions[row_idx].height = 35 # Altura suficiente para duas linhas de texto

    # Salva o arquivo na memória RAM
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    headers = {
        'Content-Disposition': 'attachment; filename="Grade_Escolar_Matriz.xlsx"'
    }
    return StreamingResponse(
        output, 
        headers=headers, 
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
