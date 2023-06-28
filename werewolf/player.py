from .settings import Inform
import configparser
import logging
from lib import util
from audio import whisper

class Player:
	def __init__(self,inifile:configparser.ConfigParser,socket, address, port, index:int) -> None:
		self.socket = socket
		self.address = address
		self.port = port
		self.index = index
		self.whisper = whisper.WhisperModelWrapper(inifile=inifile)
		self.log_path = inifile.get("log","path")

		# connection variables
		self.received = []

		# game setting
		self.alive = True

		# inform format
		self.inform_info = Inform()
		self.inform_format = self.inform_info.get_Inform_format()

	def set_name(self, name:str) -> None:
		self.name = name
	
	def set_log(self) -> None:
		# logger setting
		util.check_directory(self.log_path)
		self.logger = logging.getLogger(self.name)
		self.logger.setLevel(logging.DEBUG)
		self.log_handler = logging.FileHandler(self.log_path + self.name + ".log", mode="a", encoding="utf-8")
		self.logger.addHandler(self.log_handler)
		self.log_fmt = logging.Formatter("%(message)s")
		self.log_handler.setFormatter(self.log_fmt)
	
	def set_human_flag(self, human_flag:bool) -> None:
		self.human_flag = human_flag

	def set_role(self, role:str) -> None:
		self.role = role
	
	def dead(self) -> None:
		self.alive = False
	
	def add_receive(self,response:str) -> None:
		self.received.append(response)
	
	def get_receive(self) -> str:
		return self.received.pop(0)
	
	def write_log(self, message:str) -> None:
		self.logger.info(message)