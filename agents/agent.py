from prompts.role_prompts import get_system_prompt
from utils.json_utils import extract_json

class Agent:
    def __init__(self, name, role, client, model_name):
        self.name = name
        self.role = role
        self.client = client            
        self.model_name = model_name
        self.is_alive = True
        self.memory = []
        
        self.system_prompt = get_system_prompt(self.name, self.role)

    def act(self, instruction, available_targets):
        """调用大模型做出行动"""
        context = "\n".join(self.memory)
        user_prompt = (
            f"【历史记录】:\n{context}\n\n"
            f"【当前指令】: {instruction}\n"
            f"【当前可选目标】: {available_targets}\n"
            "请直接输出你的 JSON 决策："
        )

        print(f"\n[等待 {self.name}({self.role}) 思考中...]")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            raw_text = response.choices[0].message.content
            parsed_data = extract_json(raw_text)
            
            print(f"  model: {self.model_name} 💭 Inner Thought: {parsed_data.get('thought')}")
            return parsed_data
            
        except Exception as e:
            print(f"  ❌ API调用失败: {e}")
            return {"thought": "出错", "speak": "", "action": "None"}

    def perceive(self, message):
        """接收系统广播或他人发言，存入记忆"""
        self.memory.append(message)