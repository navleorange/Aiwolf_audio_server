from .settings import Inform
from audio import whisper

class Player:
	def __init__(self,inifile ,socket, address, port, index:int) -> None:
		self.socket = socket
		self.address = address
		self.port = port
		self.index = index
		self.whisper = whisper.WhisperModelWrapper(inifile=inifile)

		# game setting
		self.alive = True

		# inform format
		self.inform_info = Inform()
		self.inform_format = self.inform_info.get_Inform_format()

	def set_name(self, name:str) -> None:
		self.name = name
	
	def set_human_flag(self, human_flag:bool) -> None:
		self.human_flag = human_flag

	def set_role(self, role:str) -> None:
		self.role = role
	
	def dead(self) -> None:
		self.alive = False