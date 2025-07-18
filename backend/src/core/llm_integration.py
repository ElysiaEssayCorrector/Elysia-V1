import config
from typing import Any, List, Mapping, Optional
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from openai import OpenAI

class SabiáLLM(LLM):
    """
    Wrapper customizado do LangChain para o LLM Sabiá da Maritaca AI.
    Agora usa a nova API compatível com OpenAI.
    """
    model: str = "sabia-3"  
    temperature: float = 0.35
    max_tokens: int = 2048
    client: Any = None

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        # Inicializa o cliente OpenAI com endpoint da Maritaca
        self.client = OpenAI(
            api_key=config.MARITACA_API_KEY,
            base_url="https://chat.maritaca.ai/api"  # Nova URL da API
        )

    @property
    def _llm_type(self) -> str:
        return "sabia"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        try:
            # Prepara as mensagens no formato da API
            messages = [{"role": "user", "content": prompt}]
            
            # Faz a chamada para a API usando o cliente OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs
            )
            
            # Extrai e retorna o conteúdo da resposta
            return response.choices[0].message.content

        except Exception as e:
            return f"Erro na chamada da API da Maritaca: {e}"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Obtém os parâmetros de identificação do LLM."""
        return {
            "model": self.model, 
            "temperature": self.temperature, 
            "max_tokens": self.max_tokens
        }