import json

# 模型配置
MODEL_CONFIGS = {
    "zhipu": {
        "name": "智谱AI",
        "provider": "zhipu",
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "models": {
            "glm-4.5-flash": {"max_tokens": 2048, "temperature": 0.4},
            "glm-4": {"max_tokens": 2048, "temperature": 0.4},
            "glm-3-turbo": {"max_tokens": 1024, "temperature": 0.4}
        }
    },
    "openai": {
        "name": "OpenAI",
        "provider": "openai",
        "base_url": "https://api.openai.com/v1",
        "models": {
            "gpt-4o-mini": {"max_tokens": 2048, "temperature": 0.4},
            "gpt-4o": {"max_tokens": 2048, "temperature": 0.4},
            "gpt-3.5-turbo": {"max_tokens": 1024, "temperature": 0.4}
        }
    },
    "aliyun": {
        "name": "阿里云",
        "provider": "aliyun",
        "base_url": "https://dashscope.aliyuncs.com/api/v1",
        "models": {
            "qwen-plus": {"max_tokens": 2048, "temperature": 0.4},
            "qwen-turbo": {"max_tokens": 2048, "temperature": 0.4}
        }
    },
    "moonshot": {
        "name": "月之暗面",
        "provider": "moonshot",
        "base_url": "https://api.moonshot.cn/v1",
        "models": {
            "moonshot-v1-8k": {"max_tokens": 2048, "temperature": 0.4},
            "moonshot-v1-32k": {"max_tokens": 2048, "temperature": 0.4},
            "moonshot-v1-128k": {"max_tokens": 2048, "temperature": 0.4}
        }
    }
}

# 命名格式配置
NAMING_FORMATS = {
    "title_author": {
        "name": "标题_作者",
        "format": "{title}_{first_author}",
        "description": "使用标题和第一作者命名，例如: Machine_Learning_John_Smith.pdf"
    },
    "author_title": {
        "name": "作者_标题",
        "format": "{first_author}_{title}",
        "description": "使用第一作者和标题命名，例如: John_Smith_Machine_Learning.pdf"
    },
    "title_authors": {
        "name": "标题_所有作者",
        "format": "{title}_{all_authors}",
        "description": "使用标题和所有作者命名，例如: Machine_Learning_John_Smith_et_al.pdf"
    },
    "year_title_author": {
        "name": "年份_标题_作者",
        "format": "{year}_{title}_{first_author}",
        "description": "使用年份、标题和第一作者命名，例如: 2024_Machine_Learning_John_Smith.pdf"
    },
    "author_year_title": {
        "name": "作者_年份_标题",
        "format": "{first_author}_{year}_{title}",
        "description": "使用第一作者、年份和标题命名，例如: John_Smith_2024_Machine_Learning.pdf"
    }
}

# 默认设置
DEFAULT_MODEL = "zhipu"
DEFAULT_MODEL_NAME = "glm-4.5-flash"
DEFAULT_NAMING_FORMAT = "title_author"

# 提取提示词
EXTRACTION_PROMPT = """你是一个论文助手，会将我输入论文的前十几行文件，输出论文的标题以及作者。回复是记得使用json格式返回，格式如下：
{
  "title": "论文标题",
  "authors": ["作者1", "作者2", ...],
  "year": "年份（如果有）"
}"""