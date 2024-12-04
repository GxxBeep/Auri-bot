import google.generativeai as gemini
#import asyncio
from dotenv import load_dotenv
from os import getenv

load_dotenv()

# TODO: Limitar tokens de saída
class Gemini:
    def __init__(self):
        gemini.configure(api_key=getenv("GEMINI_API_KEY"))
        
        # Criando o modelo
        self.generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 100,
            "response_mime_type": "text/plain",
        }

        # Configurando o modelo
        self.model = gemini.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=self.generation_config,
        )

    # TODO: Remover comentário abaixo
    """
    def save_text(self, response):
        with open('texto.txt', "w", encoding='utf-8') as file:
            file.write(response.text)
            file.close()
        return
    """

    def send(self, message):
        chat_session = self.model.start_chat(history=[]) # TODO: Definir history para definir o idioma da resposta em Português
        response = chat_session.send_message(message)
        #print(response.text)
        #self.save_text(response)
        response_encode = response.text.encode('utf-8')
        return response_encode.decode('utf-8')