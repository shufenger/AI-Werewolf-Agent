import random
from openai import OpenAI
from agents.agent import Agent
from utils.game_logger import GameLogger
import config.settings as settings

class GameEngine:
    def __init__(self):
        # 初始化各个模型客户端
        deepseek_client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY, 
            base_url=settings.DEEPSEEK_BASE_URL
        )
        aliyun_client = OpenAI(
            api_key=settings.ALIYUN_API_KEY, 
            base_url=settings.ALIYUN_BASE_URL
        )
        doubao_client = OpenAI(
            api_key=settings.DOUBAO_API_KEY, 
            base_url=settings.DOUBAO_BASE_URL
        )
        kimi_client = OpenAI(
            api_key=settings.KIMI_API_KEY, 
            base_url=settings.KIMI_BASE_URL
        )
        
        roles_pool = ["狼人", "狼人", "狼人", "女巫", "预言家", "平民", "平民", "平民"]
        random.shuffle(roles_pool)
        self.players = []
        for i in range(8):
            player_name = f"Player_{i+1}"
            assigned_role = roles_pool[i]
            
            if assigned_role == "狼人":
                wolf_model_choices = [
                    (deepseek_client, "deepseek-chat"),
                    (kimi_client, "moonshot-v1-8k")
                ]
                chosen_client, chosen_model = random.choice(wolf_model_choices)
                
            elif assigned_role == "预言家":
                chosen_client = deepseek_client
                chosen_model = "deepseek-chat"
                
            elif assigned_role == "女巫":
                chosen_client = kimi_client
                chosen_model = "moonshot-v1-8k"
                
            else: 
                peasant_model_choices = [
                    (aliyun_client, "qwen-plus"),
                    (doubao_client, "ep-20260317150641-wl7hd") 
                ]
                chosen_client, chosen_model = random.choice(peasant_model_choices)
            
            self.players.append(
                Agent(
                    name=player_name, 
                    role=assigned_role, 
                    client=chosen_client, 
                    model_name=chosen_model
                )
            )   
        self.history = []
        self.witch_has_heal = True
        self.witch_has_poison = True
        self.logger = GameLogger()

    def broadcast(self, message):
        """全屏广播并写入所有人的记忆"""
        print(f"\n📢 【法官播报】: {message}")
        for p in self.players:
            p.perceive(message)
            self.logger.log_public(message)

    def get_alive_players(self):
        return [p for p in self.players if p.is_alive]

    def get_alive_names(self):
        return [p.name for p in self.get_alive_players()]

    def run_game(self):
        print("====== 🐺 狼人杀游戏开始 ======")
        alive_names_str = ", ".join(self.get_alive_names())
        self.broadcast(f"游戏开始。当前场上玩家有：{alive_names_str}。")
        
        all_wolves = [p for p in self.players if p.role == "狼人"]
        wolf_names = [w.name for w in all_wolves]
        
        for w in all_wolves:
            other_wolves = [name for name in wolf_names if name != w.name]
            if other_wolves:
                w.memory.append(f"【系统私有提示】：游戏开始！你的狼人同伴是：{', '.join(other_wolves)}。请在白天互相掩护，或者为了做身份适度互踩，但千万别真把同伴投出局了！")
            else:
                w.memory.append("【系统私有提示】：游戏开始！你是场上唯一的一匹孤狼，没有同伴，请小心行事！")

        day_count = 1

        while True:
            self.broadcast(f"\n========== ⏳ 【第 {day_count} 天】 ==========")

            # 一、天黑行动
            self.broadcast("天黑请闭眼。狼人请行动...")
            alive_wolves = [p for p in self.players if p.role == "狼人" and p.is_alive]
            kill_target = None
            
            if alive_wolves:
                head_wolf = alive_wolves[0] 
                alive_names = self.get_alive_names()
                
                print(f"  🐺 [头狼 {head_wolf.name} 正在决定击杀目标...]")
                wolf_decision = head_wolf.act("现在是夜晚，你作为头狼，请代表狼队选择你要击杀的玩家名字。", alive_names)
                self.logger.log_private(head_wolf.name, head_wolf.role, "夜晚刀人决策", wolf_decision)
                kill_target = wolf_decision.get("action")
                
                if kill_target and kill_target in alive_names:
                    night_log = f"【昨晚的狼队私密行动】：你的狼队在昨晚选择刀了【{kill_target}】。如果他明天播报死亡，那是你们的杰作。如果他没死，说明他被女巫救了！白天请继续伪装。"
                else:
                    night_log = "【昨晚的狼队私密行动】：你的狼队昨晚放弃了刀人（空刀）。明天播报的任何死者都与你们无关，可能是女巫盲毒的！"
                
                for w in alive_wolves:
                    w.memory.append(night_log)

            # 预言家行动
            seers = [p for p in self.players if p.role == "预言家" and p.is_alive]
            if seers:
                seer = seers[0]
                self.broadcast("预言家请睁眼...")
                
                seer_instruct = "现在是夜晚，轮到预言家行动。请在 action 字段输入你要查验的存活玩家名字。"
                seer_decision = seer.act(seer_instruct, self.get_alive_names())
                self.logger.log_private(seer.name, seer.role, "夜晚验人决策", seer_decision)
                check_target = seer_decision.get("action")
                
                seer_private_log = "【昨晚你的私密查验记录】：\n"
                if check_target and check_target in self.get_alive_names():
                    target_role = next((p.role for p in self.players if p.name == check_target), "未知")
                    target_faction = "狼人" if target_role == "狼人" else "好人"
                    
                    print(f"  👁️ 预言家查验了 {check_target}，结果为: {target_faction}")
                    seer_private_log += f"你查验了【{check_target}】，系统告诉你他的真实阵营是：【{target_faction}】！\n如果是好人（金水），白天请发给他好人身份并保护他；如果是狼人（查杀），白天请立刻号召所有人投票驱逐他！"
                else:
                    print("  👁️ 预言家放弃了查验（或查验了无效目标）。")
                    seer_private_log += "你昨晚放弃了查验，或者选择了一个无效的目标，因此没有获得任何信息。"
                
                seer.memory.append(seer_private_log)

            # 女巫行动
            witches = [p for p in self.players if p.role == "女巫" and p.is_alive]
            poison_target = None
            witch_private_log = "【昨晚你的私密行动记录】：\n"

            if witches:
                witch = witches[0]
                self.broadcast("女巫请睁眼...")
                
                w_instruct = "现在是夜晚，轮到女巫行动。\n"
                if self.witch_has_heal:
                    w_instruct += f"今晚 【{kill_target}】 被狼人杀害了。\n"
                    if kill_target == witch.name and day_count > 1:
                        w_instruct += "注意：今晚死的是你，且已不是第一天，规则限制你不能自救。\n"
                else:
                    w_instruct += "你的解药已用过，无法得知今晚谁被杀。\n"
                    
                w_instruct += f"状态情报 => 解药：{'可用' if self.witch_has_heal else '不可用'} | 毒药：{'可用' if self.witch_has_poison else '不可用'}。\n"
                w_instruct += "请在 action 字段做出决定（heal / 目标名字 / None）。"
                
                witch_decision = witch.act(w_instruct, self.get_alive_names())
                self.logger.log_private(witch.name, witch.role, "夜晚用药决策", witch_decision)
                w_action = witch_decision.get("action", "None")
                
                if w_action == "heal":
                    if self.witch_has_heal:
                        if kill_target == witch.name and day_count > 1:
                            print("  ❌ 规则限制：除了第一晚女巫不能自救！解药施放失败。")
                            witch_private_log += "你试图自救，但规则不允许（第一天以后不可自救），解药使用失败。\n"
                        else:
                            saved_player = kill_target
                            kill_target = None 
                            self.witch_has_heal = False
                            print(f"  ✨ 女巫使用了解药，复活了 {saved_player}！")
                            witch_private_log += f"你使用了解药，成功救活了【{saved_player}】。由于他被狼刀过，他大概率是好人（银水），你在白天发言时要暗中保护他，或者适时起跳女巫身份报出他的银水身份！\n"
                    else:
                        print("  ❌ 女巫解药已耗尽，动作无效。")
                        witch_private_log += "你试图使用解药，但你的解药已经用过了。\n"
                        
                elif w_action != "None" and w_action in self.get_alive_names():
                    if self.witch_has_poison:
                        poison_target = w_action
                        self.witch_has_poison = False
                        print(f"  🧪 女巫使用了毒药，目标锁定 => {poison_target}")
                        witch_private_log += f"你使用了毒药，毒杀了【{poison_target}】。如果他明天播报死亡，那是你的杰作。\n"
                    else:
                        print("  ❌ 女巫毒药已耗尽，动作无效。")
                        witch_private_log += "你试图使用毒药，但你的毒药已经用过了。\n"
                else:
                    witch_private_log += "你今晚什么都没做（既没用解药，也没用毒药）。因此，明天播报的死者绝对是被狼人杀的，与你无关！\n"
                
                witch.memory.append(witch_private_log)

            # 二、天亮死人播报
            self.broadcast("天亮了。")
            dead_this_night = []
            
            if kill_target:
                dead_this_night.append(kill_target)
            if poison_target and poison_target != kill_target:
                dead_this_night.append(poison_target)
                
            if not dead_this_night:
                self.broadcast("昨晚是平安夜，没有任何人死亡！")
            else:
                for p in self.players:
                    if p.name in dead_this_night and p.is_alive:
                        p.is_alive = False
                dead_str = " 和 ".join(dead_this_night)
                self.broadcast(f"昨晚，【{dead_str}】 死亡了！")
                
            # 胜负结算 1 (已修正：加入预言家判断)
            wolves_alive = sum(1 for p in self.players if p.is_alive and p.role == "狼人")
            good_guys_alive = sum(1 for p in self.players if p.is_alive and p.role in ["平民", "女巫", "预言家"])

            if wolves_alive == 0:
                self.broadcast("🎉 所有的狼人都已死亡，【平民/好人阵营】获胜！")
                break
            elif good_guys_alive == 0:
                self.broadcast("🩸 好人数量为0，【狼人阵营】获胜！")
                break

            # 三、发言环节
            self.broadcast("现在进入白天发言环节。")
            alive_players = self.get_alive_players()
            for p in alive_players:
                instruction = (
                    "现在轮到你发言，请结合局势推理或伪装，向大家讲话。\n"
                    "【极其重要限制】：你必须仅依据上方【历史记录】中已经真实发生的发言和事件进行分析。若其他玩家尚未在历史记录中留下他们的发言，说明他们今天还没有发过言，你绝对不能捏造、假设或提及他们所谓的言论！"
                )
                decision = p.act(instruction, "None")
                self.logger.log_private(p.name, p.role, "白天发言思考", decision)
                speak_content = decision.get("speak", "（沉默）")
                self.broadcast(f"[{p.name}] 发言：{speak_content}")

            # 四、投票环节
            self.broadcast("发言结束，现在进入投票环节。得票最高者将被驱逐出局。")
            votes = []
            abstain_count = 0 
            alive_names = self.get_alive_names()
            public_vote_records = []

            for p in alive_players:
                instruction = (
                    "请根据刚才的发言，选择你要投票驱逐的玩家。\n"
                    "你必须从可选目标中选一个。\n"
                    "如果你认为局势不明，不想投票给任何人，请在 action 字段填入 'None' 或 '弃票'。"
                )
                decision = p.act(instruction, alive_names + ["None", "弃票"])
                self.logger.log_private(p.name, p.role, "白天投票选择", decision)
                vote_target = decision.get("action")
                
                if vote_target in ["None", "弃票", None, "", "null"]:
                    public_vote_records.append(f"{p.name} 选择了弃票")
                    print(f"{p.name} 选择了 => 弃票")
                    abstain_count += 1
                elif vote_target in alive_names:
                    public_vote_records.append(f"{p.name} 投票给了 => {vote_target}")
                    print(f"{p.name} 投票给了 => {vote_target}")
                    votes.append(vote_target)
                else:
                    public_vote_records.append(f"{p.name} 投了无效票({vote_target})，视为弃票")
                    print(f"{p.name} 投了无效票({vote_target})，视为弃票")
                    abstain_count += 1

            if not votes:
                self.broadcast("投票结束。所有人均弃票或投出无效票，本轮为平安日，无人出局。")
            else:
                vote_counts = {}
                for v in votes:
                    vote_counts[v] = vote_counts.get(v, 0) + 1
                    
                max_votes = max(vote_counts.values())
                total_votes = len(votes)
                
                if abstain_count >= total_votes:
                    self.broadcast(f"投票结束。弃票数({abstain_count})大于等于有效投票数({total_votes})，根据规则投票无效，本轮为平安日，无人出局。")
                    continue
                
                candidates = [name for name, count in vote_counts.items() if count == max_votes]
                vote_details = ", ".join([f"{name}: {count}票" for name, count in vote_counts.items()])
                print(f"  [上帝视角] 最终票型: {vote_details}")
                print(f"  [上帝视角] 弃票数: {abstain_count}")
                
                if len(candidates) > 1:
                    tie_names = " 和 ".join(candidates)
                    self.broadcast(f"投票结束。最高票数为 {max_votes} 票，【{tie_names}】 平票！\n根据规则，平票时无人出局，本轮为平安日。")
                else:
                    evicted = candidates[0]
                    self.broadcast(f"投票结束。【{evicted}】 以 {max_votes} 票当选，被驱逐出局！")
                    for p in self.players:
                        if p.name == evicted:
                            p.is_alive = False

            # 五、胜负结算 2
            wolves_alive = sum(1 for p in self.players if p.is_alive and p.role == "狼人")
            good_guys_alive = sum(1 for p in self.players if p.is_alive and p.role in ["平民", "女巫", "预言家"])

            if wolves_alive == 0:
                self.broadcast("🎉 所有的狼人都已被驱逐，【平民/好人阵营】获胜！")
                self.logger.save_to_file()
                break
            elif good_guys_alive == 0:
                self.broadcast("🩸  好人数量剩余0，【狼人阵营】获胜！")
                self.logger.save_to_file()
                break

            self.broadcast("游戏继续，即将进入下一个夜晚...\n")
            day_count += 1