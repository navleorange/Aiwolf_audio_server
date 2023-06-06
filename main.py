import configparser
import threading
import concurrent.futures
import time

from lib import (
    util,
    server
)
from werewolf import game_master
from typing import Tuple
import json
import os

def gpu() -> None:
	os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
	os.environ["CUDA_VISIBLE_DEVICES"] = "5"

def game_prepare() -> Tuple[configparser.ConfigParser, game_master.GameMaster]:
	# read config.ini
	config_path = "./res/config.ini"
	inifile = util.check_config(config_path=config_path)
	inifile.read(config_path,"utf-8")

	# game setting
	seed = util.random_seed()
	aiwolf_server = server.TCP(inifile=inifile)
	aiwolf_admin = game_master.GameMaster(inifile=inifile, server=aiwolf_server, seed=seed)

	# init thread
	util.check_max_thread(inifile.getint("game","player_num"))

	return inifile, aiwolf_admin

def main():
	gpu()

	# load or init 
	inifile, aiwolf_admin = game_prepare()

	# execute game
	lock = threading.Lock()
	player_list = []

	# connectino with player
	print("server listening...")
	with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
		for _ in range(aiwolf_admin.player_num):
			future = executor.submit(aiwolf_admin.accept_entry, lock)
			player_list.append(future.result())
	
	print("allocate")
	# allocate_role
	with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
		for player in player_list:
			future = executor.submit(aiwolf_admin.allocate_role, player, lock)
			#print(future.result())
	
	print("inform")
	# inform_game_setting
	with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
		for player in player_list:
			future = executor.submit(aiwolf_admin.inform_game_setting, player)
			#print(future.result())
	
	print("count_down")
	# inform_game_setting
	with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
		for player in player_list:
			future = executor.submit(aiwolf_admin.count_down, player)
			#print(future.result())
	
	# game loop
	while aiwolf_admin.game_continue:
		start_time = time.time()
		end_time = start_time + aiwolf_admin.daily_time_limit

		with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
			for player in player_list:
				future = executor.submit(aiwolf_admin.provide_talk_info, player)
				print(future.result())
			pass

		while time.time() < end_time:

			print("talk")
			with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
				for player in player_list:
					future = executor.submit(aiwolf_admin.connection.receive, player.socket, player.address)
					if future.result() != None:
						agent_info = future.result()
						aiwolf_admin.convert_audio(player=player, agent_info=json.loads(agent_info))
		
		print("vote")
		with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
			futures = [executor.submit(aiwolf_admin.vote, player, lock) for player in player_list]
			_ = [future.result() for future in concurrent.futures.as_completed(futures)]

		print("vote inform")
		with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
			target = aiwolf_admin.decide_vote()
			futures = [executor.submit(aiwolf_admin.vote_inform, player, target) for player in player_list]
			_ = [future.result() for future in concurrent.futures.as_completed(futures)]
		
		if not aiwolf_admin.check_game_state():
			aiwolf_admin.game_continue = False
			break
		
		print("night")
		with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
			futures = [executor.submit(aiwolf_admin.night_action, player) for player in player_list]
			_ = [future.result() for future in concurrent.futures.as_completed(futures)]
		
		print("morning")
		with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
			target = aiwolf_admin.decide_vote()
			for player in player_list:
				future = executor.submit(aiwolf_admin.morning_action, player)
		
		aiwolf_admin.update_game_state()

	print("finish")
	with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
		for player in player_list:
			future = executor.submit(aiwolf_admin.finish_game, player)
	
	aiwolf_admin.connection.close()

if __name__ == "__main__":
	main()