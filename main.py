from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI(title="Sistema Base")

# ============================================================================
# 1. ROTAS DE API (Backend)
# ============================================================================
@app.get("/api/status")
def status_sistema():
    return {"status": "Servidor rodando perfeitamente", "versao": "2.0"}

# ============================================================================
# 2. ROTAS VISUAIS (Frontend)
# ============================================================================
@app.get("/")
def pagina_principal():
    return FileResponse("index.html")
