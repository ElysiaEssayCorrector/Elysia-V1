import logging
import config

# Importações dos outros módulos do projeto
from .llm_integration import SabiáLLM
from .rag_advanced import generate_hypothetical_document, rerank_with_cross_encoder

# Importações do LangChain ATUALIZADAS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence

# Configura o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_components():
    """Inicializa e retorna todos os componentes necessários para o pipeline."""
    logging.info("Inicializando componentes...")
    
    try:
        # LLM da OpenAI para gerar o documento hipotético (HyDE)
        llm_openai = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=config.OPENAI_API_KEY)
        
        # LLM Sabiá para a correção final
        llm_sabia = SabiáLLM()
        
        # Modelo de embeddings para a busca inicial
        embeddings = OpenAIEmbeddings(api_key=config.OPENAI_API_KEY)
        
        # Conexão com o banco de dados vetorial
        vector_store = Chroma(persist_directory=config.DB_PATH, embedding_function=embeddings)
        
        # Retriever base para a busca inicial
        base_retriever = vector_store.as_retriever(search_kwargs={"k": 20})
        
        logging.info("Componentes inicializados com sucesso.")
        return llm_openai, llm_sabia, base_retriever
        
    except Exception as e:
        logging.error(f"Erro ao inicializar componentes: {e}")
        raise

def correct_essay_pipeline(essay_text: str):
    """
    Executa o pipeline completo de correção de redação com RAG, HyDE e Re-ranking.
    """
    try:
        # Verifica se as chaves de API estão configuradas
        if not all([config.OPENAI_API_KEY, config.MARITACA_API_KEY]):
            error_msg = "Chaves de API (OpenAI, Maritaca) não foram encontradas. Verifique seus arquivos .env e config.py."
            logging.error(error_msg)
            return error_msg

        # 1. Inicializa os componentes
        llm_openai, llm_sabia, base_retriever = initialize_components()

        # 2. Passo HyDE: Gera um documento hipotético para usar como query de busca
        hypothetical_doc = generate_hypothetical_document(essay_text, llm_openai)
        
        # 3. Passo Retrieve: Faz a busca vetorial inicial
        logging.info("Buscando documentos iniciais no banco vetorial...")
        initial_docs = base_retriever.invoke(hypothetical_doc)
        
        # Verifica se foram encontrados documentos
        if not initial_docs:
            logging.warning("Nenhum documento foi encontrado na busca inicial. Verifique se o banco de dados está populado.")
            return "Erro: Nenhum documento de referência foi encontrado. Verifique se o banco de dados está configurado corretamente."
        
        # 4. Passo Re-rank: Usa o Cross-Encoder para reordenar os resultados
        relevant_docs = rerank_with_cross_encoder(query=hypothetical_doc, documents=initial_docs)
        
        # Verifica se há documentos após o re-ranking
        if not relevant_docs:
            logging.warning("Nenhum documento relevante após re-ranking.")
            return "Erro: Não foi possível encontrar documentos relevantes para análise."
          # Concatena o conteúdo dos documentos relevantes para o contexto
        context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])

        # 5. Passo Generate: Usa o Sabiá para gerar a correção final com o contexto
        correction_template = """
        Você é um corretor de redações do ENEM extremamente competente. Sua tarefa é fornecer uma análise detalhada e construtiva da redação a seguir, baseando-se nos materiais de referência fornecidos.

        **Instruções:**
        1.  Analise a redação do aluno em relação às cinco competências do ENEM.
        2.  Use os "Materiais de Referência" para embasar sua correção, citando exemplos de boas práticas ou erros comuns.
        3.  Não forneça notas, seu objetivo é apenas indicar os erros e sugerir melhorias.
        4.  Finalize com um parágrafo de feedback geral e sugestões de melhoria.

        **Materiais de Referência:**
        ---
        {contexto}
        ---

        **Redação do Aluno:**
        ---
        {redacao}
        ---

        **Análise Detalhada e Correção:**
        """
        
        correction_prompt = PromptTemplate(
            input_variables=["contexto", "redacao"], 
            template=correction_template
        )
        
        # Usando RunnableSequence em vez de LLMChain deprecado
        final_chain = correction_prompt | llm_sabia
        
        logging.info("Gerando a correção final com o LLM Sabiá...")
        final_correction = final_chain.invoke({"contexto": context, "redacao": essay_text})        
        return final_correction
        
    except Exception as e:
        logging.error(f"Erro no pipeline de correção: {e}")
        return f"Erro interno: {str(e)}. Verifique os logs para mais detalhes."


if __name__ == '__main__':
    try:
        # Lê a redação de exemplo do arquivo teste.txt que você já possui
        with open('teste.txt', 'r', encoding='utf-8') as f:
            sample_essay = f.read()
            
        if not sample_essay.strip():
            print("O arquivo teste.txt está vazio. Adicione uma redação de exemplo para testar.")
            exit(1)
            
        print("--- Redação para Análise ---")
        print(sample_essay[:500] + "...")
        print("\n" + "="*50 + "\n")
        
        # Executa o pipeline
        correction = correct_essay_pipeline(sample_essay)
        
        print("--- Correção Gerada ---")
        print(correction)
        
    except FileNotFoundError:
        print("Arquivo 'teste.txt' não encontrado. Crie este arquivo com uma redação de exemplo para testar o pipeline.")
    except Exception as e:
        print(f"Erro na execução: {e}")