import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Adiciona o diretório raiz do projeto ao path para encontrar os módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ..core.correction_pipeline import correct_essay_pipeline

# Configura o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Inicializa a aplicação FastAPI
app = FastAPI(
    title="Elysia-Sabia API",
    description="API para correção de redações utilizando RAG e LLMs.",
    version="1.0.0"
)

# Adiciona o middleware CORS logo após a criação do app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ou especifique ["http://localhost:8080"] para restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve arquivos estáticos do frontend
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'frontend'))
app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Define o modelo de dados para a requisição (o que a API espera receber)
class EssayRequest(BaseModel):
    text: str

@app.get("/", summary="Frontend principal")
async def read_index():
    """Serve a página principal do frontend."""
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/script.js")
async def read_script():
    """Serve o arquivo JavaScript."""
    return FileResponse(os.path.join(frontend_path, "script.js"))

@app.get("/style.css")
async def read_style():
    """Serve o arquivo CSS."""
    return FileResponse(os.path.join(frontend_path, "style.css"))

@app.post("/correct/", summary="Corrige uma redação")
async def correct_essay(request: EssayRequest):
    """
    Recebe o texto de uma redação, executa o pipeline de correção completo
    e retorna a análise gerada pela IA.
    """
    logging.info("Recebida nova requisição de correção.")
    
    if not request.text or not request.text.strip():
        logging.warning("Requisição recebida com texto vazio.")
        raise HTTPException(status_code=400, detail="O texto da redação não pode estar vazio.")
    
    try:
        # Chama a função principal do seu backend
        correction_result = correct_essay_pipeline(request.text)
        
        # Verifica se houve erro no pipeline
        if "Erro" in correction_result:
            logging.error(f"Erro retornado pelo pipeline: {correction_result}")
            raise HTTPException(status_code=500, detail=correction_result)
            
        logging.info("Correção gerada com sucesso.")
        return {"correction": correction_result}

    except Exception as e:
        logging.error(f"Erro inesperado no endpoint /correct/: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {str(e)}")

@app.get("/health", summary="Endpoint de verificação")
def read_root():
    """Endpoint raiz para verificar se a API está funcionando."""
    return {"status": "Elysia-Sabia API está online!"}