import os
from datetime import datetime

class GameLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.public_logs = []      # 公开的发言和系统播报
        self.detailed_logs = []    # 包含内心想法的详细上帝视角日志
        
        # 确保日志存储目录存在
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        # 生成带当前时间戳的日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = os.path.join(self.log_dir, f"werewolf_session_{timestamp}.txt")

    def log_public(self, message):
        """记录公开的游戏事件与发言"""
        # 移除可能重复的喇叭图标，统一输出格式
        clean_msg = message.replace("📢 ", "")
        formatted_message = f"📢 [系统/发言] {clean_msg}"
        self.public_logs.append(formatted_message)
        self.detailed_logs.append(formatted_message)

    def log_private(self, player_name, role, action_type, decision_data):
        """记录玩家的私密决策与心路历程"""
        thought = decision_data.get("thought", "无内心想法")
        action = decision_data.get("action", "None")
        speak = decision_data.get("speak", "")
        
        private_entry = (
            f"🕵️‍♂️ [私有数据] {player_name} ({role}) - 阶段: {action_type}\n"
            f"    💭 真实想法: {thought}\n"
            f"    🎯 选择行动: {action}\n"
        )
        if speak:
            private_entry += f"    🗣️ 拟定发言: {speak}\n"
            
        self.detailed_logs.append(private_entry)

    def save_to_file(self):
        """将对局数据写入到本地文件中"""
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write("=============================================\n")
                f.write("         🐺 狼人杀 自动对局复盘记录 🐺        \n")
                f.write(f"         生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=============================================\n\n")
                
                f.write("--- 📜 第一部分：公开对局广播 ---\n")
                for log in self.public_logs:
                    f.write(log + "\n")
                    
                f.write("\n\n--- 🔍 第二部分：详细心路历程 (上帝复盘视角) ---\n")
                for d_log in self.detailed_logs:
                    f.write(d_log + "\n")
                    
            print(f"\n💾 [系统提示] 本局对局记录已保存至: {self.filename}")
        except Exception as e:
            print(f"\n❌ 保存对局日志失败: {e}")