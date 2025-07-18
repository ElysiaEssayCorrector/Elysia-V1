"""
Script para criar chunks dos documentos Markdown de treinamento
"""
import os
import pickle
import logging
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Configura o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_training_chunks():
    """
    Cria chunks dos documentos Markdown de treinamento e salva em training_chunks.pkl
    """
    # Define os caminhos
    training_path = Path("data/training")
    chunks_path = Path("data/chunks")
    chunks_file = chunks_path / "training_chunks.pkl"
    
    # Cria a pasta chunks se não existir
    chunks_path.mkdir(parents=True, exist_ok=True)
    
    # Verifica se existem arquivos de treinamento
    if not training_path.exists():
        logging.error(f"Pasta {training_path} não encontrada!")
        return
    
    # Encontra todos os arquivos Markdown de treinamento
    md_files = list(training_path.glob("*.md"))
    
    if not md_files:
        logging.error(f"Nenhum arquivo Markdown encontrado em {training_path}")
        return
    
    logging.info(f"Encontrados {len(md_files)} arquivos Markdown de treinamento para chunking")
    
    # Configura o text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
    )
    
    # Lista para armazenar todos os chunks
    all_chunks = []
    
    # Processa cada arquivo Markdown
    for md_file in md_files:
        try:
            logging.info(f"Processando: {md_file.name}")
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            if not content.strip():
                logging.warning(f"Arquivo vazio: {md_file.name}")
                continue
            document = Document(
                page_content=content,
                metadata={
                    "source": str(md_file),
                    "filename": md_file.name,
                    "type": "treinamento"
                }
            )
            chunks = text_splitter.split_documents([document])
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "chunk_id": f"{md_file.stem}_{i}",
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
            all_chunks.extend(chunks)
            logging.info(f"✅ {md_file.name}: {len(chunks)} chunks criados")
        except Exception as e:
            logging.error(f"❌ Erro ao processar {md_file.name}: {e}")
            continue
    
    if not all_chunks:
        logging.error("Nenhum chunk foi criado!")
        return
    
    # Salva os chunks em arquivo pickle
    try:
        with open(chunks_file, 'wb') as f:
            pickle.dump(all_chunks, f)
        logging.info(f"🎉 Chunks de treinamento salvos com sucesso em {chunks_file}")
        logging.info(f"Total de chunks criados: {len(all_chunks)}")
        avg_length = sum(len(chunk.page_content) for chunk in all_chunks) / len(all_chunks)
        logging.info(f"Tamanho médio dos chunks: {avg_length:.1f} caracteres")
        return len(all_chunks)
    except Exception as e:
        logging.error(f"❌ Erro ao salvar chunks: {e}")
        return 0

if __name__ == "__main__":
    try:
        num_chunks = create_training_chunks()
        if num_chunks > 0:
            print(f"\n🎯 Próximo passo: python scripts/embedding_indexing/index_documents.py")
        else:
            print(f"\n❌ Falha na criação de chunks de treinamento. Verifique os logs acima.")
    except Exception as e:
        logging.error(f"Erro durante a criação de chunks de treinamento: {e}")