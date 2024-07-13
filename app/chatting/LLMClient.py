import ollama
from typing import Literal

class LLMClient():
    def __init__(self,
                 host: str,
                 model: str,
                 keep_alive: int = 0) -> None:
        self.host = host
        self.model = model
        self.keep_alive = keep_alive
        self.a_llm_client = ollama.AsyncClient(host=self.host)
        self.llm_client = ollama.Client(host=self.host)
        self.system_prompt = self._load_instruction_from_file()
    
    def _load_instruction_from_file(self, file_path: str = './app/chatting/prompts/system_prompt.txt'):
        with open(file_path, "r", encoding='utf-8') as f:
            load_text=f.read()
            return load_text

    async def a_ollama_stream(self, convo, format: Literal['', 'json']=''):
        response = await self.a_llm_client.chat(model=self.model, messages=convo, format=format, stream=True, keep_alive=self.keep_alive)
        async for part in response:
            yield part
    
    def ollama_invoke(self, convo, format: Literal['', 'json']=''):
        response = self.llm_client.chat(model=self.model, messages=convo, format=format, stream=False, keep_alive=self.keep_alive)
        return response