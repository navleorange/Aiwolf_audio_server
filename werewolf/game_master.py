import json
import time
import configparser
import threading

from lib import (
    util,
)

from .player import Player
from .settings import Role
from . import messages
import numpy as np
import pandas

class GameMaster:
    def __init__(self, inifile:configparser.ConfigParser, server, seed:int) -> None:
        # init
        # load settings
        self.connection = server
        self.inifile = inifile
        self.player_num = inifile.getint("game","player_num")
        self.daily_time_limit = inifile.getint("game","daily_time_limit")
        self.connection_interval = inifile.getint("game","connection_interval")
        self.count_down_time = inifile.getint("game","count_down_time")
        self.vote_tie = inifile.get("vote","tie_vote")
        self.seed = seed

        # init inform formta
        self.role_info = Role()

        # init game settings
        self.day = 1    # current day
        self.next_index = 0 # player index
        self.received = []
        self.player_map = {}    #key: player_index, value: name
        self.player_role = {}   # key: player_index, value: role
        self.alive_list = []    # alive player index
        self.dead_list = []     # dead player index
        self.vote_result = {}
        self.attacked_latest = None    # store sttacked agent index
        self.guard_latest = None        # store guarded agent index
        self.hanged_latest = None   # store hanged agent index
        self.game_continue = True
        self.villager_win = False
        self.werewolf_win = False

        # load
        self.all_role = {role:inifile.getint("game",role) for role in self.role_info.role_list if inifile.getint("game",role) != 0}
        util.check_role(inifile=self.inifile, all_role=self.all_role)
        self.allocate_role_list = self.all_role.copy()
        self.all_role_ja = {self.role_info.translate_ja(role=role):self.all_role[role] for role in self.all_role.keys()}

    def accept_entry(self, lock:threading.Lock) -> Player:
        # await tcp connection
        client_socket, (client_address, client_port) = self.connection.accept()

        # init player information
        new_player = Player(inifile=self.inifile,socket=client_socket, address=client_address, port=client_port,index=self.next_index)

        # set request information after reset
        new_player.inform_info.reset_values()
        new_player.inform_info.update_human_message(message="あなたの名前を入力してください！")
        new_player.inform_info.update_request(request=new_player.inform_info.request_class.base_info)

        # get client information(name, human_flag)
        agent_info = self.conversation_inform(player=new_player)
        agent_info = agent_info["agent_info"]

        new_player.set_name(agent_info["name"])
        new_player.set_human_flag(agent_info["human_flag"])

        # thread safe
        with lock:
            self.next_index += 1
        
        # game setting
        self.player_map[new_player.index] = new_player.name
        self.alive_list.append(new_player.index)

        if new_player.human_flag:
            message = f"他のプレイヤーの接続を待っています...\n"
            new_player.inform_info.update_human_message(message=message)
            new_player.inform_info.update_request(request=new_player.inform_info.request_class.inform)
            self.send_inform(player=new_player)

        return new_player
    
    def allocate_role(self, player:Player, lock:threading.Lock) -> None:

        # thread safe
        with lock:
            # randomly select a role and inform that
            selected_role = util.random_select(list(self.allocate_role_list.keys()))
            self.allocate_role_list[selected_role] -= 1
            
            # delete role
            if self.allocate_role_list[selected_role] == 0: _ = self.allocate_role_list.pop(selected_role, None)

            player.set_role(role=selected_role)
            self.player_role[player.index] = selected_role
    
    def get_inform_role(self) -> str:
        inform_role = ""
        text_format = "\t{role:s}×{num:d}\n"

        for role in self.all_role.keys():
            role_num = self.all_role[role]
            inform_role += text_format.format(role=self.role_info.translate_ja(role=role), num=role_num)
        
        return inform_role
    
    def inform_game_setting(self, player:Player):
        # set info and send (human: inform game information, AI: initialize information)

        # set game setting after reset
        player.inform_info.reset_values()
        player.inform_info.update_roleNumMap(role_num_map=self.all_role)
        player.inform_info.update_player_num(self.player_num)
        player.inform_info.update_daily_time_limit(daily_time_limit=self.daily_time_limit)
        player.inform_info.update_seed(seed=self.seed)
        player.inform_info.update_connection_interval(connection_interval=self.connection_interval)
        player.inform_info.update_human_message(message= messages.inform_rule.format(all_role=self.get_inform_role(), daily_time_limit=self.daily_time_limit))

        # set request
        player.inform_info.update_request(request=player.inform_info.request_class.inform_check)
        # send game setting information
        _ = self.conversation_inform(player=player)

        # reset inform info
        player.inform_info.reset_values()
        player.inform_info.update_role(role=player.role)

        if player.human_flag:
            # set information
            player.inform_info.update_initialize(agent_index=player.index, day=self.day, exist_rolelist=list(self.all_role.keys()), status_map=util.get_status_map(self.player_map.keys(),alive_list=self.alive_list))
            player.inform_info.update_human_message(message=messages.inform_role.format(role=self.role_info.translate_ja(role=player.role)))

            player.inform_info.update_request(request=player.inform_info.request_class.role)
            
            _ = self.conversation_inform(player=player)
            
            message = f"他のプレイヤーの確認を待っています...\n"
            player.inform_info.update_human_message(message=message)
            player.inform_info.update_request(request=player.inform_info.request_class.inform)


            self.send_inform(player=player)
        else:
            self.send_inform(player=player)
    
    def count_down(self, player:Player) -> None:

        # set game setting after reset
        player.inform_info.reset_values()
        player.inform_info.update_request(request=player.inform_info.request_class.inform)

        player.inform_info.update_human_message(message="それでは楽しくゲームを始めましょう！")
        self.send_inform(player=player)
        time.sleep(1)

        for past in range(self.count_down_time):
            player.inform_info.update_human_message(message=str(self.count_down_time - past) + "\n")
            self.send_inform(player=player)
            time.sleep(1)

        player.inform_info.update_human_message(message="スタート!\n")
        self.send_inform(player=player)

    def provide_talk_info(self, player:Player) -> None:
        # set game setting after reset
        player.inform_info.reset_values()
        player.inform_info.update_talk(daily_time_limit=self.daily_time_limit, connection_interval=self.connection_interval)

        self.send_inform(player=player)
    
    def convert_audio(self, player:Player, agent_info) -> None:
        #print(agent_info["agent_info"]["audio"])
        voice = np.array(agent_info["agent_info"]["audio"]["voice"])
        results = player.whisper.transcribe(audio=voice)

        message = ""
        for result in results:
            message += result[4] + "\n"
        
        # set game setting after reset
        player.inform_info.reset_values()
        player.inform_info.update_human_message(message=message)
        player.inform_info.update_request(request=player.inform_info.request_class.inform)

        self.send_inform(player=player)

    def get_player_role(self, index:int) -> str:
        return self.player_role[index]

    def get_player_name(self, index:int) -> str:
        return self.player_map[index]
    
    def get_player_index(self, name:str) -> int:
        result = [player_index for player_index, player_name in self.player_map.items() if player_name == name]
        return result[0]

    def get_divine_index(self, player:Player) -> list:
        divine_list = [alive_player for alive_player in self.alive_list if player.index != alive_player]
        return divine_list
    
    def get_divine_name(self, player:Player) -> list:
        divine_list = self.get_divine_index(player=player)
        divine_name = [self.get_player_name(index=index) for index in divine_list]
        return divine_name
    
    def get_divine_result(self, index:int) -> str:
        return "白" if not self.get_player_role(index=index) in self.role_info.divine_werewolf else "黒"
    
    def get_psychic_result(self) -> str:
        return "白" if not self.get_player_role(index=self.hanged_latest) in self.role_info.divine_werewolf else "黒"
    
    def get_attack_index(self, player:Player) -> list:
        attack_list = [alive_player for alive_player in self.alive_list if self.get_player_role(alive_player) != self.role_info.werewolf]
        return attack_list
    
    def get_attack_name(self, player:Player) -> list:
        attack_list = self.get_attack_index(player=player)
        attack_name = [self.get_player_name(index=index) for index in attack_list]
        return attack_name
    
    def get_vote_index(self, player:Player) -> list:
        vote_list = [alive_player for alive_player in self.alive_list if alive_player != player.index]
        return vote_list
    
    def get_vote_name(self, player:Player) -> list:
        vote_list = self.get_vote_index(player=player)
        vote_name = [self.get_player_name(index=index) for index in vote_list]
        return vote_name
    
    def get_vote_str(self, player:Player) -> str:
        vote_list = self.get_vote_index(player=player)
        vote_list = list(map(str,vote_list))
        return ",".join(vote_list)
    
    def get_alive_name(self) -> list:
        alive_name = [self.get_player_name(index=index) for index in self.alive_list]
        return alive_name

    def vote(self, player:Player, lock:threading.Lock) -> None:

        if not player.alive:
            return

        # set game setting after reset
        player.inform_info.reset_values()
        if self.player_num != 1:
            player.inform_info.update_target_index_list(target_index_list=self.get_vote_index(player=player))
            player.inform_info.update_target_name_list(target_name_list=self.get_vote_name(player=player))
        else:
            # this use only test
            player.inform_info.update_target_index_list(target_index_list=[98,99,100])
            player.inform_info.update_target_name_list(target_name_list=["a","b","c"])

        player.inform_info.update_human_message(message=messages.vote.format(player_list=self.get_vote_str(player=player)))
        player.inform_info.update_request(request=player.inform_info.request_class.vote)

        # send
        response_name = self.conversation_inform(player=player)

        # throw out audio
        while response_name["request"] == player.inform_info.request_class.convert_server_format(request=player.inform_info.request_class.convert_audio):
            # resend
            response_name = self.conversation_inform(player=player)

        response_index = self.get_player_index(name=response_name["agent_info"]["message"])

        with lock:
            self.vote_result.setdefault(response_index,0)
            self.vote_result[response_index] += 1
        
        player.inform_info.update_human_message(message=messages.waiting_confirm)
        player.inform_info.update_request(request=player.inform_info.request_class.inform)
        self.send_inform(player=player)
    
    def decide_vote(self) -> str:
        print(self.vote_result)
        max_value = max(list(self.vote_result.values()))

        target_list = []

        for vote in self.vote_result.keys():
            if self.vote_result[vote] == max_value:
                target_list.append(vote)
        

        print(target_list)

        if len(target_list) == 1:
            target = target_list[0]
        else:
            target = util.random_select(data=target_list)
        
        return self.get_player_name(index=target)
    
    def vote_inform(self, player:Player, target:str) -> None:
         # set game setting after reset
        player.inform_info.reset_values()
        player.inform_info.update_human_message(message=messages.hang.format(player_name=target))
        player.inform_info.update_request(request=player.inform_info.request_class.inform_check)

        # send
        _ = self.conversation_inform(player=player)

        player.inform_info.update_human_message(message=messages.waiting_confirm)
        player.inform_info.update_request(request=player.inform_info.request_class.inform)
        self.send_inform(player=player)

        self.vote_result.clear()

        if target == player.name:
            # update information
            self.alive_list.remove(player.index)
            self.dead_list.append(player.index)
            self.hanged_latest = player.index

            player.dead()
    
    def unique_action(self, player:Player) -> None:
        # set game setting after reset
        player.inform_info.reset_values()
        role_message = ""

        if player.role == self.role_info.seer:
            player.inform_info.update_target_index_list(target_index_list=self.get_divine_index(player=player))
            player.inform_info.update_target_name_list(target_name_list=self.get_divine_name(player=player))
            player.inform_info.update_request(request=player.inform_info.request_class.divine)
            role_message = messages.night + messages.divine_seer
        elif player.role == self.role_info.werewolf:
            player.inform_info.update_target_index_list(target_index_list=self.get_attack_index(player=player))
            player.inform_info.update_target_name_list(target_name_list=self.get_attack_name(player=player))
            player.inform_info.update_request(request=player.inform_info.request_class.attack)
            role_message = messages.night + messages.attack_werewolf
        elif player.role == self.role_info.guard:
            player.inform_info.update_target_index_list(target_index_list=self.get_attack_index(player=player))
            player.inform_info.update_target_name_list(target_name_list=self.get_attack_name(player=player))
            role_message = messages.night + messages.guard_guard
            player.inform_info.update_request(request=player.inform_info.request_class.guard)
        else:
            player.inform_info.update_target_index_list(target_index_list=self.alive_list)
            player.inform_info.update_target_name_list(target_name_list=self.get_alive_name())
            role_message = messages.night + messages.camouflage_villager
            player.inform_info.update_request(request=player.inform_info.request_class.divine_lie)
        
        # send
        player.inform_info.update_human_message(message=role_message)
        response_name = self.conversation_inform(player=player)
        response_index = self.get_player_index(name=response_name["agent_info"]["message"])

        player.inform_info.update_request(request=player.inform_info.request_class.inform_check)

        if player.role == self.role_info.seer:
            player.inform_info.update_human_message(message=messages.divine_result.format(player_name=self.get_player_name(index=response_index), role=self.get_divine_result(index=response_index)))
        elif player.role == self.role_info.werewolf:
            self.attacked_latest = response_index
            player.inform_info.update_human_message(message=messages.camouflage_check)
        elif player.role == self.role_info.guard:
            self.guard_latest = response_index
            player.inform_info.update_human_message(message=messages.camouflage_check)
        else:
            player.inform_info.update_human_message(message=messages.camouflage_check)
        
        _ = self.conversation_inform(player=player)

    def night_action(self, player:Player) -> None:
        if not player.alive:
            return

        # set game setting after reset
        player.inform_info.reset_values()
        player.inform_info.update_human_message(message=messages.night)
        player.inform_info.update_request(request=player.inform_info.request_class.inform)
        self.send_inform(player=player)

        self.unique_action(player=player)

        player.inform_info.update_human_message(message=messages.waiting_confirm)
        player.inform_info.update_request(request=player.inform_info.request_class.inform)
        self.send_inform(player=player)
    
    def first_day_night(self, player:Player) -> None:
        if player.role == self.role_info.seer:
            player.inform_info.update_target_index_list(target_index_list=self.get_divine_index(player=player))
            player.inform_info.update_target_name_list(target_name_list=self.get_divine_name(player=player))
            player.inform_info.update_request(request=player.inform_info.request_class.divine)
            role_message = messages.night + messages.divine_seer
        else:
            player.inform_info.update_target_index_list(target_index_list=self.alive_list)
            player.inform_info.update_target_name_list(target_name_list=self.get_alive_name())
            role_message = messages.night + messages.camouflage_villager
            player.inform_info.update_request(request=player.inform_info.request_class.divine_lie)
        
        # send
        player.inform_info.update_human_message(message=role_message)
        response_name = self.conversation_inform(player=player)
        response_index = self.get_player_index(name=response_name["agent_info"]["message"])

        player.inform_info.update_request(request=player.inform_info.request_class.inform_check)

        if player.role == self.role_info.seer:
            player.inform_info.update_human_message(message=messages.divine_result.format(player_name=self.get_player_name(index=response_index), role=self.get_divine_result(index=response_index)))
        else:
            player.inform_info.update_human_message(message=messages.camouflage_check)
        
        _ = self.conversation_inform(player=player)
    
    def morning_action(self, player:Player) -> None:
        # infrom attackd player
        player.inform_info.reset_values()

        if self.attacked_latest == None or self.attacked_latest == self.guard_latest:
            player.inform_info.update_human_message(message=messages.morning_safe)
        else:
            # inform
            player.inform_info.update_human_message(message=messages.morning_cruel.format(player_name=self.get_player_name(index=self.attacked_latest)))
            player.inform_info.update_request(request=player.inform_info.request_class.inform_check)
            _ = self.conversation_inform(player=player)

            # update information
            self.alive_list.remove(self.attacked_latest)
            self.dead_list.append(self.attacked_latest)

            if player.role == self.role_info.medium:
                role_message = messages.night + messages.psychic_medium.format(player_name=self.get_player_name(index=self.hanged_latest), psychic_result=self.get_psychic_result())
                player.inform_info.update_request(request=player.inform_info.request_class.psychic)
            else:
                role_message = messages.camouflage_check
            
            player.inform_info.update_human_message(message=role_message)

            # update information
            if player.index == self.attacked_latest:
                player.dead()

        player.inform_info.update_request(request=player.inform_info.request_class.inform_check)

        _ = self.conversation_inform(player=player)

    def check_game_continue(self) -> bool:
        werewolf_team = 0
        werewolf_cnt = 0

        for player in self.alive_list:
            player_role = self.get_player_role(index=player)

            if player_role in self.role_info.werewolf_team:
                werewolf_team += 1
            
            if player_role == self.role_info.werewolf:
                werewolf_cnt += 1

        villager_team = len(self.alive_list) - werewolf_team
        half = int((10*len(self.alive_list))/2)
        werewolf_team *= 10

        print(self.alive_list)
        print(werewolf_team)
        print(half)

        if werewolf_team >= half:
            print("few villager")
            self.werewolf_win = True
            return False
        
        if werewolf_cnt == 0:
            print("no werewolf")
            self.villager_win = True
            return False

        return True
    
    def update_game_state(self) -> None:
        self.game_continue = self.check_game_continue()

    def finish_game(self, player:Player) -> None:
        # reset inform info
        player.inform_info.reset_values()
        player.inform_info.update_request(request=player.inform_info.request_class.inform_check)

        final_message = ""

        if self.villager_win:
            final_message = messages.villager_win
        else:
            final_message = messages.werewolf_win
        
        player.inform_info.update_human_message(message=final_message)
        
        _ = self.conversation_inform(player=player)

        # set request
        player.inform_info.update_request(request=player.inform_info.request_class.finish)

        self.send_inform(player=player)

    def send_inform(self, player:Player) -> None:
        # update inform_fomat
        player.inform_info.update_inform_format()

        # send
        self.connection.send(socket=player.socket, address=player.address, message=json.dumps(player.inform_format,separators=(",",":")))
    
    def print_info(self, player:Player) -> None:
        player.inform_info.update_inform_format()
        print(json.dumps(player.inform_format,separators=(",",":")))

    def receive_json(self, player:Player) -> None:
        return json.loads(self.connection.receive(socket=player.socket, address=player.address))
    
    def get_message(self, response) -> str:
        return response["agent_info"]["message"]

    def conversation_inform(self, player:Player) -> str:
        # update inform_fomat
        player.inform_info.update_inform_format()

        # send and receive
        return json.loads(self.connection.conversation(socket=player.socket, address=player.address, message=json.dumps(player.inform_format,separators=(",",":"))))