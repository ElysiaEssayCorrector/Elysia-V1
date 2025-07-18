# Elysia - Teste Local

Guia rápido para rodar o projeto localmente (Linux/Mac ou Windows).

---

## 1. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd Elysia
```

---

## 2. Crie e ative o ambiente virtual

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

---

## 3. Instale as dependências

```bash
pip install -r requirements.txt
```

---

## 4. Inicie o backend (API FastAPI)

```bash
uvicorn backend.src.api.main:app --reload
```

---

## 5. Inicie o frontend (servidor local)

Abra outro terminal e execute:

**Linux/Mac:**
```bash
cd frontend
python3 -m http.server 8080
```

**Windows (PowerShell):**
```powershell
cd frontend
python -m http.server 8080
```

---

## 6. Acesse o sistema

- **Frontend:**  
  [http://localhost:8080](http://localhost:8080)

- **Backend (API):**  
  [http://127.0.0.1:8000](http://127.0.0.1:8000)  
  Para acessar a interface de teste da FastAPI, use `/docs` no final do endereço do backend.

---

## 7. Configuração da chave de API

- O arquivo `.env` deve estar presente na raiz do backend (exemplo: `backend/src/.env`).
- Cada integrante do grupo deve colocar **sua própria chave de API** no arquivo `.env`, por exemplo:
  ```
  OPENAI_API_KEY="sua-chave-aqui"
  MARITACA_API_KEY="sua-chave-aqui"
  ```
- **Nunca compartilhe chaves reais em repositórios públicos.**

---

## 8. Organização das pastas de dados

- **backend/data/raw/**  
  Onde ficam os arquivos enviados pelo frontend (uploads dos usuários).

- **backend/data/training/**  
  Onde devem ser colocados os arquivos de treinamento da IA, como bases de redações, datasets de referência, textos para embeddings, etc.  
  **Esses arquivos não são enviados pelo usuário, mas sim usados internamente para treinar ou ajustar o sistema.**

- **backend/data/processed/**  
  (Opcional) Para arquivos já processados pelos scripts.

- **backend/data/chunks/**  
  (Opcional) Para os chunks/textos divididos usados na indexação de embeddings.

---

## Observações

- O frontend se comunica com o backend via API REST.
- Se precisar alterar a URL da API, edite a constante `API_URL` em `frontend/script.js`.
- Para dúvidas ou problemas, consulte o console do navegador (F12) ou o terminal.
- Para acessar a interface de teste da FastAPI use `/docs` no final do