import os
import errno
import configparser
import random
import datetime
import time

from werewolf import settings, game_master
from werewolf.settings import Role

def read_text(path:str):
    with open(path,"r",encoding="utf-8") as f:
        return f.read().splitlines()

def random_seed() -> int:
     # 乱数の設定
    now = datetime.datetime.now()
    seed = int(time.mktime(now.timetuple()))
    random.seed(seed)

    return seed

def random_shuffle(data:list) -> None:
    random.shuffle(data)

def random_select(data:list):
    return random.choice(data)

def is_json_complate(responces:bytes) -> bool:

    try:
        responces = responces.decode("utf-8")
    except:
        return False
    
    if responces == "":
        return False

    cnt = 0

    for word in responces:
        if word == "{":
            cnt += 1
        elif word == "}":
            cnt -= 1
    
    return cnt == 0

def check_config(config_path:str) -> configparser.ConfigParser:

    if not os.path.exists(config_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_path)
    
    return configparser.ConfigParser()

def check_role(inifile:configparser.ConfigParser, all_role:dict) -> None:
    player_num = inifile.getint("game","player_num")
    cnt_num = 0

    for role_num in all_role.values():
        cnt_num += role_num
    
    if player_num != cnt_num:
        raise ValueError(f"The number of players:{player_num} and the number of roles:{cnt_num} are different in config.ini. ")

def check_max_thread(player_num:int) -> None:
    limit = min(32, (os.cpu_count() or 1) + 4)  # same as ThreadPoolExecutor init

    if player_num > limit:
        raise ValueError(f"The number of players:{player_num} is over than limit:{limit} ")

def get_status_map(player_index:list, alive_list:list) -> dict:
    result = {}

    for index in player_index:
        if index in alive_list:
            result[index] = "ALIVE"
        else:
            result[index] = "DEAD"
    
    return result

def check_directory(directory_path:str) -> None:
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)