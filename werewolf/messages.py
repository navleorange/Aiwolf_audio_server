inform_rule = """
				------------------------ルール説明------------------------\n
今回のゲームのルールは以下のようになっています。\n
	役職
    {all_role:s}
1日の会話時間:{daily_time_limit:d}秒
ゲーム開始時(初夜)の占い：あり
ゲーム開始時(初夜)の襲撃：なし
"""

confirm = "確認したら「OK」ボタンを押してください。\n"

waiting_confirm = "他のプレイヤーの確認を待っています..."

inform_role = "あなたの役職は「{role:s}」です。\n" + confirm

buddy_info = "仲間は{buddy_list:s}です。"

divine_seer = """
占い師のあなたは1人を占うことができます。
占いたい人の名前を入力してください
"""

divine_result = """
占いの結果、{player_name:s}さんは{role:s}でした。
""" + confirm

attack_werewolf = """
人狼のあなたは1人を襲撃することができます。
襲撃したい人の名前を入力してください
"""

camouflage_villager = """
占い師が誰かバレないようにするために、\nあなたには占い師と同じ行動をとって頂きます。
プレイヤーの中から無作為に1人の名前を入力してください
"""

psychic_medium = """
昨日吊られた{player_name:s}さんは{psychic_result:s}でした。
"""

guard_guard = """
狩人のあなたは1人を守ることができます。
守りたい人の名前を入力してください
"""

camouflage_check = """
他のプレイヤーが確認をしています。
""" + confirm

vote = """
投票の時間です。
プレイヤーの中から投票したい人物を入力してください
"""

hang = """
投票の結果、「{player_name:s}」さんが処刑されることとなりました。
残念ながら{player_name:s}さんはここでお別れとなります
""" + confirm

night = """
恐ろしい夜がやってきました...
"""

morning_safe = """
おはようございます！
昨晩は特に何もなく平和な夜でしたね！
""" + confirm

morning_cruel = """
おはようございます。
今朝起きると、{player_name:s}さんが無残な姿で倒れていました...
""" + confirm

villager_win = """
人狼が全て消え去り、村人だけの世界になりました！
村人陣営の処理です！
"""

werewolf_win = """
人狼が村を支配し、人狼の楽園となりました！
人狼陣営の勝利です！
"""

time_out = "time out..."