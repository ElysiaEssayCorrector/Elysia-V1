import os
import pickle
import logging
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Configura o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Verifica se a chave da API da OpenAI foi definida
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY não encontrada. Por favor, defina-a no seu arquivo .env")

# Define os caminhos
CHUNKS_PATH = "data/chunks/chunks.pkl"
DB_PATH = "db"  # Diretório para armazenar os arquivos do ChromaDB

def index_documents():
    """
    Carrega os chunks, gera os embeddings com a OpenAI e os armazena
    em um banco de dados vetorial Chroma.
    """
    # Carrega os chunks
    if not os.path.exists(CHUNKS_PATH):
        logging.error(f"Arquivo de chunks não encontrado em {CHUNKS_PATH}. Execute o script create_chunks.py primeiro.")
        return

    try:
        with open(CHUNKS_PATH, "rb") as f:
            chunks = pickle.load(f)
        logging.info(f"Carregados {len(chunks)} chunks de {CHUNKS_PATH}")
    except Exception as e:
        logging.error(f"Não foi possível carregar os chunks. Erro: {e}")
        return

    if not chunks:
        logging.warning("Nenhum chunk para indexar.")
        return

    # Inicializa o modelo de embeddings da OpenAI
    embedding_function = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

    # Verifica se já existe um banco de dados
    if os.path.exists(DB_PATH) and os.listdir(DB_PATH):
        logging.info("Banco de dados existente encontrado. Adicionando novos documentos...")
        vector_store = Chroma(
            persist_directory=DB_PATH,
            embedding_function=embedding_function
        )
        # Adiciona os novos documentos
        vector_store.add_documents(chunks)
    else:
        # Cria o ChromaDB a partir dos documentos
        logging.info("Criando o banco de dados vetorial e gerando os embeddings... Isso pode levar algum tempo.")
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_function,
            persist_directory=DB_PATH # Onde o banco de dados será salvo
        )

    logging.info(f"Banco de dados vetorial criado e salvo com sucesso em {DB_PATH}")
    logging.info(f"Total de documentos no banco: {vector_store._collection.count()}")

if __name__ == "__main__":
    try:
        index_documents()
    except Exception as e:
        logging.error(f"Erro durante a indexação: {e}")
        raise