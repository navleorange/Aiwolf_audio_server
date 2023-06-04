from faster_whisper import WhisperModel
import configparser

class WhisperModelWrapper:
    def __init__(self, inifile:configparser.ConfigParser):
        self.inifile = inifile
        self.model_size_or_path = self.inifile.get("whisper","model_size_or_path")
        self.model = WhisperModel(
            self.model_size_or_path, device=self.inifile.get("whisper","device"), compute_type=self.inifile.get("whisper","compute_type")
        )

    def transcribe(self, audio):
        """
        --------transcribe--------
        audio_type:<class 'numpy.ndarray'>
        [ 61  62  68 ... -71 -23  41]
        """
        segments, _ = self.model.transcribe(
            audio=audio, beam_size=self.inifile.getint("whisper","beam_size"), language=self.inifile.get("whisper","language"), without_timestamps=self.inifile.getboolean("whisper","without_timestamps") 
        )
        return segments