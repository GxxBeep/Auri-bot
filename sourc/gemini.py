import google.generativeai as gemini
from dotenv import load_dotenv
from os import getenv

load_dotenv()

# TODO: Limitar tokens de saída
class Gemini:
    def __init__(self):
        # Configurando o gemini
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
            model_name="gemini-1.5-flash", # Definindo o modelo a ser utilizado
            generation_config=self.generation_config, # Definindo a configuração do modelo
        )

    # Envia uma mensagem para o gemini
    def send(self, message):
        # Inicia a conversa passando o history
        chat_session = self.model.start_chat(history=[]) # TODO: Definir history para definir o idioma da resposta em Português
        # Envia a mensagem e recebe a resposta
        response = chat_session.send_message(message) 
        # Encode da resposta
        response_encode = response.text.encode('utf-8')
        # Retorna a resposta decodificada
        return response_encode.decode('utf-8') 