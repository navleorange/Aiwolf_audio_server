import configparser
import threading
import concurrent.futures
import time

from lib import (
    util,
    server
)
from werewolf import game_master
import json
import os

def gpu() -> None:
	os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
	os.environ["CUDA_VISIBLE_DEVICES"] = "5"

def game_prepare() -> game_master.GameMaster:
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

	return aiwolf_admin

def main():
	gpu()

	# load or init 
	aiwolf_admin = game_prepare()

	# execute game
	lock = threading.Lock()
	player_list = []

	# connectino with player
	print("server listening...")
	with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
		futures = [executor.submit(aiwolf_admin.accept_entry, lock) for _ in range(aiwolf_admin.player_num)]
		player_list = [future.result() for future in concurrent.futures.as_completed(futures)]
	
	print("allocate")
	# allocate_role
	with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
		futures = [executor.submit(aiwolf_admin.allocate_role, player, lock) for player in player_list]
		_ = [future.result() for future in concurrent.futures.as_completed(futures)]
	
	print("inform")
	# inform_game_setting
	with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
		futures = [executor.submit(aiwolf_admin.inform_game_setting, player) for player in player_list]
		_ = [future.result() for future in concurrent.futures.as_completed(futures)]
	
	print("count_down")
	# inform_game_setting
	with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
		futures = [executor.submit(aiwolf_admin.count_down, player) for player in player_list]
		_ = [future.result() for future in concurrent.futures.as_completed(futures)]
	
	# game loop
	while aiwolf_admin.game_continue:
		start_time = time.time()
		end_time = start_time + aiwolf_admin.daily_time_limit

		if aiwolf_admin.day == 1:
			# only day 1 night
			print("first night")
			with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
				futures = [executor.submit(aiwolf_admin.first_day_night, player) for player in player_list]
				_ = [future.result() for future in concurrent.futures.as_completed(futures)]
		else:
			print("night")
			with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
				futures = [executor.submit(aiwolf_admin.night_action, player) for player in player_list]
				_ = [future.result() for future in concurrent.futures.as_completed(futures)]
		
		print("morning")
		with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
			futures = [executor.submit(aiwolf_admin.morning_action, player) for player in player_list]
			_ = [future.result() for future in concurrent.futures.as_completed(futures)]
		
		if aiwolf_admin.day != 1:
			if not aiwolf_admin.check_game_continue():
				aiwolf_admin.game_continue = False
				break
			
		aiwolf_admin.day += 1

		# with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
		# 	_ = [executor.submit(aiwolf_admin.connection.set_time_out, player.socket, player.address, aiwolf_admin.daily_time_limit) for player in player_list]
		# 	futures = [executor.submit(aiwolf_admin.provide_talk_info, player) for player in player_list]
		# 	_ = [future.result() for future in concurrent.futures.as_completed(futures)]

		while time.time() < end_time:

			# print("talk")
			# with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
			# 	for player in player_list:
			# 		future = executor.submit(aiwolf_admin.connection.receive_time_out, player.socket, player.address)
			# 		if future.result() != None:
			# 			agent_info = future.result()
			# 			aiwolf_admin.convert_audio(player=player, agent_info=json.loads(agent_info))
			pass
		
		print("vote")
		with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
			_ = [executor.submit(aiwolf_admin.connection.restore_time_out, player.socket, player.address) for player in player_list]
			futures = [executor.submit(aiwolf_admin.vote, player, lock) for player in player_list]
			_ = [future.result() for future in concurrent.futures.as_completed(futures)]

		print("vote inform")
		with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
			target = aiwolf_admin.decide_vote()
			futures = [executor.submit(aiwolf_admin.vote_inform, player, target) for player in player_list]
			_ = [future.result() for future in concurrent.futures.as_completed(futures)]
		
		if not aiwolf_admin.check_game_continue():
			aiwolf_admin.game_continue = False
			break

	print("finish")
	with concurrent.futures.ThreadPoolExecutor(max_workers=aiwolf_admin.player_num) as executor:
		futures = [executor.submit(aiwolf_admin.finish_game, player) for player in player_list]
		_ = [future.result() for future in concurrent.futures.as_completed(futures)]
	
	aiwolf_admin.connection.close()

if __name__ == "__main__":
	main()