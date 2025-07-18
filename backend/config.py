import os
from dotenv import load_dotenv

load_dotenv()

# Chaves de API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MARITACA_API_KEY = os.getenv("MARITACA_API_KEY") # Chave da Maritaca AI
COHERE_API_KEY = os.getenv("COHERE_API_KEY")     # Chave da Cohere

# Caminhos do projeto (pode adicionar outros conforme necessário)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "db")
