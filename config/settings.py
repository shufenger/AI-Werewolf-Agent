import os
from dotenv import load_dotenv

load_dotenv()

# DeepSeek 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-deepseek-api-key")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

# 阿里云通义千问配置
ALIYUN_API_KEY = os.getenv("ALIYUN_API_KEY", "your-aliyun-api-key")
ALIYUN_BASE_URL = os.getenv("ALIYUN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

# 字节跳动豆包配置
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "your-doubao-api-key")
DOUBAO_BASE_URL = os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")

# Moonshot (Kimi) 配置
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "your-kimi-api-key")
KIMI_BASE_URL = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")

