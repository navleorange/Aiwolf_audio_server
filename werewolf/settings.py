class Role():
	def __init__(self) -> None:
		# init role name
		self.villager = "villager"
		self.seer = "seer"
		self.medium = "medium"	# 前日に吊られた人の役職を知ることができる
		self.guard = "guard"
		self.werewolf = "werewolf"
		self.possessed = "possessed"

		# team
		self.villager_team = [self.villager, self.seer, self.medium, self.guard]
		self.werewolf_team = [self.werewolf, self.possessed]

		self.role_list = [self.villager,self.seer,self.medium,self.guard,self.werewolf,self.possessed]
		self.role_translate = {self.villager:"村人",self.seer:"占い師",self.medium:"霊能者",self.guard:"狩人",self.werewolf:"人狼",self.possessed:"狂人"}
	
	def translate_ja(self, role:str) -> str:

		if self.role_translate.get(role,None) == None:
			raise ValueError(f"{role} is not exist role")

		return self.role_translate.get(role)

class Request:
	def __init__(self) -> None:
		# RandomTalkAgent request
		self.request = "request"
		self.initialize = "initialize"
		self.name = "name"
		self.role = "role"
		self.daily_initialize = "daily_initialize"
		self.daily_finish = "daily_finish"
		self.talk = "talk"
		self.vote = "vote"
		self.whisper = "whisper"
		self.finish = "finish"

		# add request
		self.inform = "inform"	# not need player check
		self.inform_check = "inform_check"	# need player check

		# request from client
		self.base_info = "base_info"
		self.time_sync = "time_sync"
		self.convert_audio = "convert_audio"

		# {key:self variable value:RandomTalkAgent send format}
		self.convert_request = {self.initialize:"INITIALIZE",self.name:"NAME",self.role:"ROLE",self.daily_initialize:"DAILY_INITIALIZE",self.daily_finish:"DAILY_FINISH",self.talk:"TALK",self.vote:"VOTE",self.whisper:"WHISPER",self.finish:"FINISH",
			  					self.inform:"INFORM", self.time_sync:"TIME_SYNCHRONIZE", self.base_info:"BASEINFO", self.inform_check:"INFORMCHECK",self.convert_audio:"CONVERTAUDIO"
								}


		# RandomTalkAgent format (just init)
		self._random_request = dict()

		# add format (just init)
		self._add_request = {}

	def get_request_format(self) -> dict:
		self._random_request.update(self._add_request)
		return self._random_request.copy()
	
	def convert_local_format(self, request:str) -> str:
		keys = [key for key, value in self.convert_request.items() if value == request]
		if keys:
			return keys[0]
		return None
	
	def convert_server_format(self, request:str) -> str:

		if self.convert_request.get(request,None) == None:
			raise ValueError(f"{request} is not exist request")
		
		return self.convert_request.get(request)

class GameInfo:
	def __init__(self) -> None:
		# RandomTalkAgent gameInfo
		self.agent = "agent"
		self.attackVoteList = "attackVoteList"
		self.attackedAgent = "attackedAgent"
		self.cursedFox = "cursedFox"
		self.day = "day"
		self.divineResult = "divineResult"
		self.englishTalkList = "englishTalkList"
		self.executedAgent = "executedAgent"
		self.existingRoleList = "existingRoleList"
		self.guardedAgent = "guardedAgent"
		self.lastDeadAgentList = "lastDeadAgentList"
		self.latestAttackVoteList = "latestAttackVoteList"
		self.latestExecutedAgent = "latestExecutedAgent"
		self.latestVoteList = "latestVoteList"
		self.mediumResult = "mediumResult"
		self.remainTalkMap = "remainTalkMap"
		self.remainWhisperMap = "remainWhisperMap"
		self.roleMap = "roleMap"
		self.role = "role"
		self.statusMap = "statusMap"
		self.talkList = "talkList"
		self.voteList = "voteList"
		self.gameSetting = "gameSetting"

		# add info
		self.vote_index_list = "voteIndexList"
		self.vote_name_list = "voteNameList"

		# RandomTalkAgent format (just init)
		self._random_gameInfo_format = {self.agent:None,self.attackVoteList:None,self.attackedAgent:None,self.cursedFox:None,self.day:None,self.divineResult:None,
				  self.englishTalkList:None,self.executedAgent:None,self.existingRoleList:None,self.guardedAgent:None,self.lastDeadAgentList:None,self.latestAttackVoteList:None,
				  self.latestExecutedAgent:None,self.latestVoteList:None,self.mediumResult:None,self.remainTalkMap:None,self.remainWhisperMap:None,self.roleMap:None,
				  self.role:None,self.statusMap:None,self.talkList:None,self.voteList:None,self.gameSetting:None}

		# add format (just init)
		self._add_gameInfo_format = {self.vote_index_list:None,self.vote_name_list:None}

	def get_gameInfo_format(self) -> dict:
		self._random_gameInfo_format.update(self._add_gameInfo_format)
		return self._random_gameInfo_format.copy()

class GameSetting:
	def __init__(self) -> None:
		# RandomTalkAgent gameSetting
		self.enableNoAttack = "enableNoAttack"
		self.enableNoExecution = "enableNoExecution"
		self.enableRoleRequest = "enableRoleRequest"
		self.maxAttackRevote = "maxAttackRevote"
		self.maxRevote = "maxRevote"
		self.maxSkip = "maxSkip"
		self.maxTalk = "maxTalk"
		self.maxTalkTurn = "maxTalkTurn"
		self.maxWhisper = "maxWhisper"
		self.maxWhisperTurn = "maxWhisperTurn"
		self.playerNum = "playerNum"
		self.randomSeed = "randomSeed"
		self.roleNumMap = "roleNumMap"
		self.talkOnFirstDay = "talkOnFirstDay"
		self.timeLimit = "timeLimit"
		self.validateUtterance = "validateUtterance"
		self.votableInFirstDay = "votableInFirstDay"
		self.voteVisible = "voteVisible"
		self.whisperBeforeRevote = "whisperBeforeRevote"

		# add gameSetting
		self.daily_time_limit = "dailyTimeLimit"
		self.connection_interval = "connection_interval"

		# RandomTalkAgent format (just init)
		self._random_gameSetting_format = {self.enableNoAttack:None,self.enableNoExecution:None,self.enableRoleRequest:None,self.maxAttackRevote:None,self.maxRevote:None,self.maxSkip:None,self.maxTalk:None,self.maxTalkTurn:None,self.maxWhisper:None,self.maxWhisperTurn:None,self.playerNum:None,self.randomSeed:None,self.roleNumMap:None,self.talkOnFirstDay:None,self.timeLimit:None,self.validateUtterance:None,self.votableInFirstDay:None,self.voteVisible:None,self.whisperBeforeRevote:None}

		# add format (just init)
		self._add_gameSetting_format = {self.daily_time_limit:None,self.connection_interval:None}
	
	def get_gameSetting_format(self) -> dict:
		self._random_gameSetting_format.update(self._add_gameSetting_format)
		return self._random_gameSetting_format.copy()
	
class TalkHistory:
	def __init__(self) -> None:
		# RandomTalkAgent talkHistory
		self.agent = "agent"
		self.day = "day"
		self.idx = "idx"
		self.text = "text"
		self.turn = "turn"

		# RandomTalkAgent format (just init)
		self._random_talkHistory_format = {self.agent:None,self.day:None,self.idx:None,self.text:None,self.turn:None}

		# add format (just init)
		self._add_talkHistory_format = dict()
	
	def get_talkHistory_format(self) -> dict:
		self._random_talkHistory_format.update(self._add_talkHistory_format)
		return self._random_talkHistory_format.copy()

class Inform:
	def __init__(self) -> None:
		self.gameInfo = "gameInfo"
		self.gameSetting = "gameSetting"
		self.request = "request"
		self.talkHistory = "talkHistory"
		self.whisperHistory = "whisperHistory"
		self.human_message = "humanMessage"

		# class instance
		self.gameInfo_class = GameInfo()
		self.gameSetting_class = GameSetting()
		self.request_class = Request()
		self.talkHistory_class = TalkHistory()
		self.whisperHistory_class = None
		self.human_message_class = None

		self.gameInfo_value = None
		self.gameSetting_value = None
		self.request_value = None
		self.talkHistory_value = None
		self.whisperHistory_value = None
		self.human_message_value = None


		# RandomTalkAgent json format (just init)
		self._random_inform_format = {self.gameInfo:self.gameInfo_value,self.gameSetting:self.gameSetting_value,self.request:self.request_value,self.talkHistory:self.talkHistory_value,self.whisperHistory:self.whisperHistory_value,
									self.human_message:self.human_message_value
									}

		# add format (just init)
		self._add_inform_format = dict()
	
	def get_Inform_format(self) -> dict:
		self._random_inform_format.update(self._add_inform_format)
		return self._random_inform_format
	
	def check_gameInfo_value(self) -> None:
		if self.gameInfo_value == None:
			self.gameInfo_value = self.gameInfo_class.get_gameInfo_format()
	
	def check_gameSetting_value(self) -> None:
		if self.gameSetting_value == None:
			self.gameSetting_value = self.gameSetting_class.get_gameSetting_format()

	def check_request_value(self) -> None:
		if self.request_value == None:
			self.request_value = self.request_class.get_request_format()
	
	def update_seed(self, seed:int) -> None:
		self.check_gameSetting_value()
		self.gameSetting_value[self.gameSetting_class.randomSeed] = seed
	
	def update_player_num(self, player_num:int) -> None:
		self.check_gameSetting_value()
		self.gameSetting_value[self.gameSetting_class.playerNum] = player_num
	
	def update_connection_interval(self, connection_interval:int) -> None:
		self.check_gameSetting_value()
		self.gameSetting_value[self.gameSetting_class.connection_interval] = connection_interval
	
	def update_daily_time_limit(self, daily_time_limit:int) -> None:
		self.check_gameSetting_value()
		self.gameSetting_value[self.gameSetting_class.daily_time_limit] = daily_time_limit
	
	def update_roleNumMap(self, role_num_map:dict) -> None:
		self.check_gameSetting_value()
		self.gameSetting_value[self.gameSetting_class.roleNumMap] = role_num_map

	def update_request(self, request:str) -> None:
		self.check_gameInfo_value()
		self.request_value = self.request_class.convert_server_format(request=request)
	
	def update_human_message(self,message:str) -> None:
		self.human_message_value = message
	
	def update_initialize(self, agent_index:int, day:int, exist_rolelist:list, status_map:dict) -> None:
		self.check_gameInfo_value()
		self.gameInfo_value[self.gameInfo_class.agent] = agent_index
		self.gameInfo_value[self.gameInfo_class.day] = day
		self.gameInfo_value[self.gameInfo_class.existingRoleList] = exist_rolelist
		self.gameInfo_value[self.gameInfo_class.statusMap] = status_map
	
	def update_role(self, role:str) -> None:
		self.check_gameInfo_value()
		self.gameInfo_value[self.gameInfo_class.role] = role
	
	def update_vote_index_list(self, vote_index_list:list) -> None:
		self.check_gameInfo_value()
		self.gameInfo_value[self.gameInfo_class.vote_index_list] = vote_index_list
	
	def update_vote_name_list(self, vote_name_list:list) -> None:
		self.check_gameInfo_value()
		self.gameInfo_value[self.gameInfo_class.vote_name_list] = vote_name_list

	def update_talk(self, daily_time_limit:int, connection_interval:int) -> None:
		self.update_daily_time_limit(daily_time_limit=daily_time_limit)
		self.update_connection_interval(connection_interval=connection_interval)
		self.update_request(request=self.request_class.talk)
	
	def append_talk_history(self, history:dict) -> None:
		# check_history_value
		self._random_inform_format[self.talkHistory].append(history)
	
	def update_inform_format(self) -> None:
		self._random_inform_format[self.gameInfo] = self.gameInfo_value
		self._random_inform_format[self.gameSetting] = self.gameSetting_value
		self._random_inform_format[self.request] = self.request_value
		self._random_inform_format[self.talkHistory] = self.talkHistory_value
		self._random_inform_format[self.whisperHistory] = self.whisperHistory_value
		self._random_inform_format[self.human_message] = self.human_message_value
	
	def reset_values(self) -> None:
		self.gameInfo_value = None
		self.gameSetting_value = None
		self.request_value = None
		self.talkHistory_value = None
		self.whisperHistory_value = None
		self.human_message_value = None
		self.update_inform_format()