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
        self.day = 0
        self.next_index = 0 # player index
        self.received = []
        self.player_map = {}    #key: player_index, value: name
        self.player_role = {}   # key: player_index, value: role
        self.alive_list = []    # alive player index
        self.dead_list = []     # dead player index
        self.vote_result = {}
        self.attacked = None    # store sttacked agent index
        self.game_continue = True

        # load
        self.all_role = {role:inifile.getint("game",role) for role in self.role_info.role_list if inifile.getint("game",role) != 0}
        util.check_role(inifile=self.inifile, role_list=self.all_role)
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
            message = f"他のプレイヤーの接続を待っています..."
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
    
    def inform_game_setting(self, player:Player):
        # set info and send (human: inform game information, AI: initialize information)

        # set game setting after reset
        player.inform_info.reset_values()
        player.inform_info.update_roleNumMap(role_num_map=self.all_role)
        player.inform_info.update_player_num(self.player_num)
        player.inform_info.update_daily_time_limit(daily_time_limit=self.daily_time_limit)
        player.inform_info.update_seed(seed=self.seed)
        player.inform_info.update_connection_interval(connection_interval=self.connection_interval)
        inform_rule = f"""---------------------------ルール説明---------------------------\n今回のゲームのルールは以下のようになっています。\n役職：{list(self.all_role_ja.keys())}\n1日の会話時間:{self.daily_time_limit}秒"""
        player.inform_info.update_human_message(message=inform_rule)

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

            self.print_info(player=player)
            
            data = self.conversation_inform(player=player)
            
            print(data)
            
            message = f"他のプレイヤーの確認を待っています..."
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

    def get_divine_list(self, player:Player) -> str:
        divine_list = [str(alive_player) for alive_player in self.alive_list if player.index != alive_player]
        return ",".join(divine_list)
    
    def get_divine_result(self, index:int) -> str:
        return "白" if self.get_player_role(index=index) != self.role_info.werewolf else "黒"
    
    def get_attack_list(self, player:Player) -> str:
        attack_list = [str(alive_player) for alive_player in self.alive_list if self.get_player_role(alive_player) != self.role_info.werewolf]
        return ",".join(attack_list)
    
    def get_vote_list(self, player:Player) -> str:
        vote_list = [str(alive_player) for alive_player in self.alive_list if alive_player != player.index]
        return ",".join(vote_list)
    
    def get_alive_string(self) -> str:
        alive_str = map(str,self.alive_list)
        return ",".join(alive_str)

    def vote(self, player:Player, lock:threading.Lock) -> None:
        # set game setting after reset
        player.inform_info.reset_values()
        player.inform_info.update_human_message(message=messages.vote.format(player_list=self.get_vote_list(player=player)))
        player.inform_info.update_request(request=player.inform_info.request_class.vote)

        # send
        response_index = self.conversation_inform(player=player)
        response_index = int(response_index["agent_info"]["message"])

        with lock:
            self.vote_result.setdefault(response_index,0)
            self.vote_result[response_index] += 1
        
        player.inform_info.update_human_message(message=messages.waiting_confirm)
        player.inform_info.update_request(request=player.inform_info.request_class.inform)
        self.send_inform(player=player)
    
    def decide_vote(self) -> str:
        print(self.vote_result)
        data = pandas.Series(self.vote_result)
        target = data[data == data.max()].index.tolist()

        print(target)

        if len(target) == 1:
            target = target[0]
        else:
            target = util.random_select(data=data)
        
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

        if target == player.name:
            # update information
            hanged_player = self.get_player_index(name=target)

            self.alive_list.remove(hanged_player)
            self.dead_list.append(hanged_player)
            _ = self.player_role.pop(player.index,None)

            player.dead()
    
    def unique_action(self, player:Player) -> None:
        # set game setting after reset
        player.inform_info.reset_values()
        player.inform_info.update_request(request=player.inform_info.request_class.inform_check)

        if player.role == self.role_info.seer:
            player.inform_info.update_human_message(message=messages.divine_seer.format(player_list=self.get_divine_list(player=player)))
        elif player.role == self.role_info.werewolf:
            player.inform_info.update_human_message(message=messages.attack_werewolf.format(player_list=self.get_attack_list(player=player)))
        else:
            player.inform_info.update_human_message(message=messages.camouflage_villager.format(player_list=self.get_alive_string())) # camouflage
        
        # send
        response = self.conversation_inform(player=player)
        response_index = int(self.get_message(response=response))

        if player.role == self.role_info.seer:
            player.inform_info.update_human_message(message=messages.divine_result.format(player_name=self.get_player_name(index=response_index), role=self.get_divine_result(index=response_index)))
        elif player.role == self.role_info.werewolf:
            player.inform_info.update_human_message(message=messages.camouflage_check)
        else:
            player.inform_info.update_human_message(message=messages.camouflage_check)
        
        _ = self.conversation_inform(player=player)

    def night_action(self, player:Player) -> None:
        # set game setting after reset
        player.inform_info.reset_values()
        player.inform_info.update_human_message(message=messages.night)
        player.inform_info.update_request(request=player.inform_info.request_class.inform)
        self.send_inform(player=player)

        self.unique_action(player=player)

        player.inform_info.update_human_message(message=messages.waiting_confirm)
        player.inform_info.update_request(request=player.inform_info.request_class.inform)
        self.send_inform(player=player)
    
    def morning_action(self, player:Player) -> None:
        # infrom attackd player
        player.inform_info.reset_values()

        if self.attacked == None:
            player.inform_info.update_human_message(message=messages.morning_safe)
        else:
            player.inform_info.update_human_message(message=messages.morning_cruel.format(player_name=self.get_player_name(index=self.attacked)))

        player.inform_info.update_request(request=player.inform_info.request_class.inform_check)

        _ = self.conversation_inform(player=player)

    def check_game_state(self) -> bool:
        role_list = list(self.player_role.values())

        werewolf_team = role_list.count(self.role_info.werewolf)

        if werewolf_team >= len(role_list) or werewolf_team == 0:
            return False
        
        return True
    
    def update_game_state(self) -> None:
        self.game_continue = self.check_game_state()

    def finish_game(self, player:Player) -> None:
        # reset inform info
        player.inform_info.reset_values()

        # set request
        player.inform_info.update_request(request=player.inform_info.request_class.finish)
        
        player.send_inform(socket=player.socket, address=player.address)

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