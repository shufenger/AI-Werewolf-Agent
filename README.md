这是一个基于大语言模型（LLM）的多智能体（Multi-Agent）狼人杀模拟游戏。项目支持使用 DeepSeek、通义千问、豆包、以及 Kimi 等多种模型扮演不同的角色。
支持自定义人数和不同ai模型，可在本项目的基础上增加或删减，需要自己提供api key游玩，下一步将更新更多角色（如果把更需要思考的身份分配给豆包会很有节目效果）

## 目录结构
* **main.py** - 游戏主入口。
* **config/** - 包含 API 密钥及基础模型配置。
* **agents/** - AI 玩家智能体（Agent）定义。
* **engine/** - 控制狼人杀交替夜白交替、结算投票、死伤逻辑的核心引擎。
* **prompts/** - 包含预言家、女巫、平民及狼人的提示词模板。
* **utils/** - 提供可靠提取大模型回复中 JSON 部分的工具函数。

## 安装与快速启动

1. 克隆本项目：
   ```bash
   git clone https://github.com/your-username/AI-Werewolf-Agent.git
   cd AI-Werewolf-Agent
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 复制 `.env` 配置文件模板，并填写对应的 API Key：
   ```bash
   cp .env.example .env  
   ```
   或者直接在根目录下创建 `.env` 文件并填入您的 Key。

4. 启动模拟：
   ```bash
   python main.py
   ```