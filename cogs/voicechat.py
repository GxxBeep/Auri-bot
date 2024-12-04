# A função ainda esta em fase de desenvolvimento e necessita de melhorias.
# Esse código esta em fase de revisão, por isso esta bagunçado.

import os
import wave
import time
import asyncio
import discord
import threading
import speech_recognition as sr

from discord import app_commands
from discord.ext import commands, voice_recv
from discord.errors import ClientException
from sourc.voz_train import TTSmodule
from sourc.gemini import Gemini



class ProcessAudioToAudio:
    # TODO: Realizar toda a configuração e tratar todo os erros
    def __init__(self):
        self.recognizer = sr.Recognizer() # Iniciar o reconhecimento de fala
        self.gemini = Gemini() # Iniciar o gemini
        self.tts = TTSmodule() # Iniciar o TTS
        self.audio_buffer:bytes = None # Buffer de audio
        

    # TODO: Melhorar o processamento do audio
    # Esta sendo salvo com audio picotado
    async def audio_callback(self, user, voice_data: voice_recv.VoiceData, channel: voice_recv.VoiceRecvClient):
        """
        Callback para processar o áudio recebido.
        """
        if self.audio_buffer is None:
            # Cria o buffer de audio, caso ele for vazio
            self.audio_buffer = bytearray()
        self.audio_buffer.extend(voice_data.pcm) # Adiciona o audio ao buffer
        self.voiceChannel = channel # Armazena o canal de voz

    def save_to_wav(self) -> bytes | str:
        # TODO: Função temporária, criada para afins de teste
        # Salva o audio em WAV
        try:
            with wave.open("audio.wav", "wb") as wav_fale:
                wav_fale.setnchannels(2)  # Stereo
                wav_fale.setsampwidth(2)  # 16-bit
                wav_fale.setframerate(48000)  # 48kHz
                wav_fale.writeframes(self.audio_buffer)  # Escreve os frames de audio
            self.audio_buffer = None # Limpa o buffer
            return
        except Exception as e:
            return f"Erro ao salvar WAV: {e}"

    def audio_to_text(self) -> str:
        # TODO: Fazer melhoria na transcrição do audio, esta tendo muito erros bobos em algumas palavras.
        # Transcreve o audio para texto
        for f in os.listdir("."): # Itera sobre os arquivos na pasta "."
            if f.endswith(".wav"): # Verifica se o arquivo termina com ".wav"
                with sr.AudioFile(f) as fileAudio:
                    audio = self.recognizer.record(fileAudio)
                try:
                    # Transcreve o audio
                    texto = self.recognizer.recognize_google(audio, language="pt-BR")
                    # remove o audio
                    os.remove(f)
                    return texto
                except sr.UnknownValueError:
                    print("O reconhecimento de fala não conseguiu entender o áudio")
                    return False
                except sr.RequestError as e:
                    print(f"Não foi possível solicitar resultados do serviço de reconhecimento de fala: {e}")
                    return False

    def text_to_IA(self, message):
        # TODO: Realizar toda a configuração e tratar todo os erros,
        # Tratar texto de resposta da IA, removendo caracteres especiais, tais como: '.', '?', '!', '😊'
        return self.gemini.send(message=message)

    def play_audio(self, audio): # type: ignore
        # TODO: Assim que o audio for finalizado, excluir o arquivo de audio.
        # Converte o audio em PCM
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
            source=audio,
            executable="c:/ffmpeg/bin/ffmpeg.exe" # Caminho para o FFmpeg
            ))
        try:
            self.voiceChannel.play(source=source) # Reproduz o audio
        except ClientException as e:
            print("Erro ao reproduzir o áudio:", e)
        return

    def speech_to_response_in_voice(self):
        self.save_to_wav() # salvar o audio em wav
        if _message:=self.audio_to_text(): # traduzir o audio para texto
            #print(f"_message: {_message}")
            
            _chat_response = self.text_to_IA(_message) # Retorna a resposta da IA
            #print(f"_chat_response: {_chat_response}")

            _speech_audio_return = self.tts.text_to_speech(text=_chat_response) # Cria a resposta em voz
            self.play_audio(audio=_speech_audio_return)
            time.sleep(1)
            return
        else:
            print("Erro ao transcrever o audio para texto")
            return


class Timer:
    # TODO: Realizar toda a configuração e tratar todo os erros
    def __init__(self, process_audio: ProcessAudioToAudio):
        self._ProcessAudioToAudio = process_audio # Armazena a classe ProcessAudioToAudio
        self._running = False # Armazena o estado do timer
        self._counted_timer = 0 # Armazena o timer
        self._thread = None # Armazena a thread do timer
        self._waiting_for_process = False # Armazena o estado do timer

    # Timer Thread
    def _run_threading(self):
        try:
            while self._running: # Enquanto o '_running' for True
                _current_timer = time.time() - self._counted_timer # Subtrai o tempo atual pelo timer
                if _current_timer >= 1.0:
                    self._running = False
                    #print(f"Timer result: {_current_timer}")
                    self._waiting_for_process = True
                    self._ProcessAudioToAudio.speech_to_response_in_voice() # processar o audio
                    self._waiting_for_process = False
                    break
                time.sleep(0.1) # 100ms
        except Exception as e:
            print(e)

    # Inicia Timer
    def start(self):
        # caso '_running' for False
        if not self._running:
            self._running = True
            # Construindo a thread
            self._thread = threading.Thread(target=self._run_threading, daemon=True)
            # Armazena o timer atual
            self._counted_timer = time.time()
            # Inicia a thread
            self._thread.start()
            #print("Timer iniciado!")

    # Para Timer
    def stop(self):
        if self._running:
            self._running = False
            if self._thread:
                self._thread.join() # Finaliza a thread
            #print("Timer parado!")

    # Reinicia Timer
    def reset(self):
        if self._running:
            # Armazena o timer atual
            self._counted_timer = time.time()
            #print("Timer resetado!")


class VoiceChat(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self._process_audio = ProcessAudioToAudio()
        self.timer = Timer(self._process_audio)


    # TODO: Realizar toda a configuração e tratar todo os erros, resolver problema de conexão, 
    # no segundo ou terceiro audio, o bot desconecta da ligação, mas permanece conectado ao canal de voz.
    @app_commands.command(name="conectar", description="Conecta o bot no canal de voz onde o usuário estiver")
    async def conectar(self, interaction: discord.Interaction):
        """
        Conecta o bot ao canal de voz onde o usuário estiver
        """
        if not interaction.user.voice: # Verifica se o usuário estiver em um canal de voz
            await interaction.response.send_message("Você precisa estar em um canal de voz!")
            return
        channel = interaction.user.voice.channel

        try:
            # Conecta ao canal de voz com suporte a recepção
            vc = await channel.connect(cls=voice_recv.VoiceRecvClient)
            await interaction.response.send_message(f"Conectado ao canal de voz: {channel.name}")

            # Recebe o audio
            def callback(user, voice_data: voice_recv.VoiceData):
                # Caso algum audio esteja sendo processado
                if self.timer._waiting_for_process:
                    return
                # Caso o bot esteja reproduzindo audio
                if vc.is_playing():
                    return

                self.timer.start() # Inicia o timer
                
                # Caso o usuário falando
                if vc.get_speaking(user): 
                    # A cada pacote recebido, Armazena o audio e reset o timer
                    asyncio.run_coroutine_threadsafe(
                        self._process_audio.audio_callback(user=user, voice_data=voice_data, channel=vc),
                        self.bot.loop
                        )
                    self.timer.reset()

            # Inicia a captura de audio
            vc.listen(voice_recv.BasicSink(callback)) # TODO: Ocorrendo bugs ao obter os packets de audio

        except Exception as e:
            await interaction.followup.send(f"Erro ao capturar áudio: {str(e)}")


    # TODO: Realizar toda a configuração e tratar todo os erros
    @app_commands.command(name="desconectar", description="Desconecta o bot do canal de voz")
    async def desconectar(self, interaction: discord.Interaction):
        # Obtém o canal de voz e verifica se em o bot conectado
        voice_channel = discord.utils.get(
            self.bot.voice_clients, guild=interaction.guild
        )
        if voice_channel is not None: # Caso o bot esteja conectado
            await voice_channel.disconnect() # Desconecta
            await interaction.response.send_message("Desconectando...")
        else:
            await interaction.response.send_message("Nenhum bot conectado")


async def setup(bot):
    cog = VoiceChat(bot)
    await bot.add_cog(cog)