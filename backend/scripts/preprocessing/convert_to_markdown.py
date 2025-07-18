#!/usr/bin/env python3
"""
Script para converter documentos (PDF, DOC, TXT) para Markdown usando Docling
"""
import os
import logging
from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat

# Configura o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def convert_documents():
    """
    Converte todos os documentos da pasta data/raw para Markdown na pasta data/processed
    """
    
    # Define os caminhos
    raw_path = Path("data/raw")
    processed_path = Path("data/processed")
    
    # Cria a pasta processed se não existir
    processed_path.mkdir(parents=True, exist_ok=True)
    
    # Verifica se a pasta raw existe
    if not raw_path.exists():
        logging.error(f"Pasta {raw_path} não encontrada!")
        return
    
    # Encontra todos os documentos suportados
    supported_extensions = ['.pdf', '.doc', '.docx', '.txt']
    documents = []
    
    for ext in supported_extensions:
        documents.extend(raw_path.glob(f"*{ext}"))
    
    if not documents:
        logging.error(f"Nenhum documento encontrado em {raw_path}")
        logging.info(f"Extensões suportadas: {supported_extensions}")
        return
    
    logging.info(f"Encontrados {len(documents)} documentos para conversão")
    
    # Inicializa o conversor
    converter = DocumentConverter()
    
    # Processa cada documento
    for doc_path in documents:
        try:
            logging.info(f"Convertendo: {doc_path.name}")
            
            # Converte o documento
            result = converter.convert(doc_path)
            
            # Extrai o conteúdo em Markdown
            markdown_content = result.document.export_to_markdown()
            
            # Define o nome do arquivo de saída
            output_name = doc_path.stem + ".md"
            output_path = processed_path / output_name
            
            # Salva o arquivo Markdown
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logging.info(f"✅ Salvo: {output_path}")
            
        except Exception as e:
            logging.error(f"❌ Erro ao converter {doc_path.name}: {e}")
            continue
    
    # Resumo final
    converted_files = list(processed_path.glob("*.md"))
    logging.info(f"🎉 Conversão concluída! {len(converted_files)} arquivos Markdown criados em {processed_path}")
    
    return len(converted_files)

if __name__ == "__main__":
    try:
        convert_documents()
    except Exception as e:
        logging.error(f"Erro durante a conversão: {e}")
        
        # Fallback: conversão simples para TXT se Docling falhar
        logging.info("Tentando conversão alternativa...")
        
        raw_path = Path("data/raw")
        processed_path = Path("data/processed")
        processed_path.mkdir(parents=True, exist_ok=True)
        
        # Para arquivos TXT, apenas copiar
        txt_files = list(raw_path.glob("*.txt"))
        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                output_path = processed_path / (txt_file.stem + ".md")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {txt_file.stem}\n\n{content}")
                
                logging.info(f"✅ TXT convertido: {output_path}")
            except Exception as e:
                logging.error(f"❌ Erro na conversão alternativa: {e}")
        
        logging.info("⚠️  Para conversão completa de PDFs, instale: pip install docling")