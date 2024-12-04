from TTS.api import TTS
from torch import cuda


# TODO: Otimizar TTS
class TTSmodule(TTS):
    def __init__(self):
        super().__init__(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2",
            gpu=cuda.is_available(),
        )

    # TODO: Modificar função para retornar apenas retornar o texto, sem salva-lo.
    def text_to_speech(self, text):
        return self.tts_to_file(
            text=text,
            # file_path="output.wav",
            speaker_wav="sourc\carolina.mp3",
            language="pt",
        )