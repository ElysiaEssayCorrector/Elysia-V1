import logging
from sentence_transformers import CrossEncoder
from langchain.prompts import PromptTemplate

# Configura o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_hypothetical_document(essay_text: str, llm):
    """
    Gera um documento hipotético (análise/correção) usando um LLM para melhorar a busca.
    Esta é a implementação da técnica HyDE.
    """
    template = """
    Você é um assistente especialista em redações do ENEM. 
    Com base na redação abaixo, gere um parágrafo de análise que capture os temas centrais, 
    os argumentos principais e a proposta de intervenção. Este parágrafo será usado para encontrar 
    exemplos e guias de correção relevantes.

    Redação:
    ---
    {redacao}
    ---
    
    Análise Hipotética:
    """
    prompt = PromptTemplate(input_variables=["redacao"], template=template)
    
    # Usando o novo método invoke em vez do run deprecado
    chain = prompt | llm
    
    logging.info("Gerando documento hipotético para a busca (HyDE)...")
    try:
        result = chain.invoke({"redacao": essay_text})
        return result if isinstance(result, str) else result.content
    except Exception as e:
        logging.error(f"Erro ao gerar documento hipotético: {e}")
        # Fallback: retorna parte da redação original
        return essay_text[:500]


def rerank_with_cross_encoder(query: str, documents: list, top_n: int = 5):
    """
    Reordena uma lista de documentos com base na relevância para a consulta usando um Cross-Encoder.
    """
    logging.info("Reordenando documentos com Cross-Encoder...")
    
    # Verifica se há documentos para reordenar
    if not documents:
        logging.warning("Nenhum documento fornecido para re-ranking.")
        return []
    
    # Limita o número de documentos se necessário
    if len(documents) < top_n:
        top_n = len(documents)
        logging.info(f"Ajustando top_n para {top_n} devido ao número limitado de documentos.")
    
    try:
        # Inicializa o modelo. Na primeira execução, ele será baixado.
        cross_encoder = CrossEncoder('amberoad/bert-multilingual-passage-reranking-msmarco')
        
        # Cria pares de [consulta, conteúdo do documento] para o modelo
        pairs = []
        valid_documents = []
        
        for doc in documents:
            if hasattr(doc, 'page_content') and doc.page_content.strip():
                pairs.append([query, doc.page_content])
                valid_documents.append(doc)
            else:
                logging.warning("Documento sem conteúdo válido encontrado, ignorando.")
        
        if not pairs:
            logging.warning("Nenhum documento válido para re-ranking.")
            return documents[:top_n]  # Retorna os primeiros documentos como fallback
        
        # Calcula as pontuações de relevância
        scores = cross_encoder.predict(pairs)
        
        # Combina os documentos com suas pontuações e ordena
        doc_scores = list(zip(valid_documents, scores))
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Retorna os 'top_n' documentos mais relevantes
        reranked_docs = [doc for doc, score in doc_scores[:top_n]]
        
        logging.info(f"Documentos reordenados. Retornando os {top_n} melhores de {len(valid_documents)} documentos válidos.")
        return reranked_docs
        
    except Exception as e:
        logging.error(f"Erro no re-ranking com Cross-Encoder: {e}")
        # Fallback: retorna os primeiros documentos sem re-ranking
        logging.info("Usando fallback: retornando documentos sem re-ranking.")
        return documents[:top_n]