inform_rule = """
				-------------------ルール説明-------------------\n
				今回のゲームのルールは以下のようになっています。\n
				役職：{all_role:s}
                1日の会話時間:{daily_time_limit:d}秒
            """

confirm = "確認したら「OK」ボタンを押してください。"

waiting_confirm = "他のプレイヤーの確認を待っています..."

inform_role = "あなたの役職は「{role:s}」です。\n" + confirm

divine_seer = """
占い師のあなたは{player_list:s}の中から1人を占うことができます。
占いたい人の名前を入力してください:
"""

divine_result = """
占いの結果、{player_name:s}さんは{role:s}でした。
""" + confirm

attack_werewolf = """"
人狼のあなたは{player_list:s}の中から1人を襲撃することができます。
襲撃したい人の名前を入力してください:
"""

camouflage_villager = """
占い師が誰かバレないようにするために、あなたには占い師と同じ行動をとって頂きます。
{player_list:s}の中から無作為に1人の名前を入力してください:
"""

camouflage_check = """
他のプレイヤーが確認をしています。
""" + confirm

vote = """
投票の時間です。
{player_list:s}の中から投票したい人物の番号を入力してください:
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