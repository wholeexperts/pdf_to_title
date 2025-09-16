import json
from typing import Dict, Any, Tuple, Optional
from .config import MODEL_CONFIGS, EXTRACTION_PROMPT
from .api_key_manager import APIKeyManager


class ModelManager:
    """模型管理器，支持多种大语言模型提供商"""

    def __init__(self, provider: str = "zhipu", model_name: str = "glm-4.5-flash"):
        self.provider = provider
        self.model_name = model_name
        self.config = MODEL_CONFIGS.get(provider, MODEL_CONFIGS["zhipu"])
        self.api_key_manager = APIKeyManager()
        self.client = None  # 不在初始化时创建客户端

    def _initialize_client(self):
        """根据提供商初始化客户端"""
        # 获取API密钥
        api_key = self.api_key_manager.get_key(self.provider)
        if not api_key:
            raise ValueError(f"请先设置 {self.config['name']} 的API密钥")

        if self.provider == "zhipu":
            try:
                from zai import ZhipuAiClient
                return ZhipuAiClient(
                    api_key=api_key,
                    base_url=self.config["base_url"]
                )
            except ImportError:
                raise ImportError("请安装 zai 包以使用智谱AI模型")
        
        elif self.provider == "openai":
            try:
                from openai import OpenAI
                return OpenAI(
                    api_key=api_key,
                    base_url=self.config["base_url"]
                )
            except ImportError:
                raise ImportError("请安装 openai 包以使用OpenAI模型")
        
        elif self.provider == "aliyun":
            try:
                from openai import OpenAI  # 阿里云兼容OpenAI接口
                return OpenAI(
                    api_key=api_key,
                    base_url=self.config["base_url"]
                )
            except ImportError:
                raise ImportError("请安装 openai 包以使用阿里云模型")
        
        elif self.provider == "moonshot":
            try:
                from openai import OpenAI  # Moonshot兼容OpenAI接口
                return OpenAI(
                    api_key=api_key,
                    base_url=self.config["base_url"]
                )
            except ImportError:
                raise ImportError("请安装 openai 包以使用Moonshot模型")
        
        else:
            raise ValueError(f"不支持的模型提供商: {self.provider}")

    def _get_client(self):
        """获取客户端实例，如果不存在则创建"""
        if self.client is None:
            self.client = self._initialize_client()
        return self.client

    def extract_info(self, context: str) -> Tuple[str, list, Optional[str]]:
        """
        使用大语言模型提取论文信息
        返回: (title, authors, year)
        """
        # 确保客户端已初始化
        client = self._get_client()
        
        if self.provider == "zhipu":
            return self._extract_with_zhipu(context)
        else:
            return self._extract_with_openai(context)

    def _extract_with_zhipu(self, context: str) -> Tuple[str, list, Optional[str]]:
        """使用智谱AI模型提取信息"""
        client = self._get_client()
        model_config = self.config["models"][self.model_name]
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "assistant", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": context}
            ],
            max_tokens=model_config["max_tokens"],
            temperature=model_config["temperature"],
            thinking={
                "type": "disabled",
            }
        )
        return self._parse_response(response.choices[0].message.content)

    def _extract_with_openai(self, context: str) -> Tuple[str, list, Optional[str]]:
        """使用OpenAI兼容接口的模型提取信息"""
        client = self._get_client()
        model_config = self.config["models"][self.model_name]
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "assistant", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": context}
            ],
            max_tokens=model_config["max_tokens"],
            temperature=model_config["temperature"]
        )
        return self._parse_response(response.choices[0].message.content)

    def _parse_response(self, response_content: str) -> Tuple[str, list, Optional[str]]:
        """解析模型响应"""
        try:
            # 尝试直接解析JSON
            import json
            data = json.loads(response_content)
            title = data.get("title", "")
            authors = data.get("authors", [])
            year = data.get("year", None)
            return title, authors, year
        except json.JSONDecodeError:
            # 如果JSON解析失败，使用原来的字符串解析方法
            try:
                title = response_content.split('"title": "')[1].split('",')[0]
                authors_str = response_content.split('"authors": [')[1].split(']')[0]
                authors = [author.strip().strip('"') for author in authors_str.split(',')]
                year = None
                if '"year": "' in response_content:
                    year = response_content.split('"year": "')[1].split('"')[0]
                return title, authors, year
            except Exception:
                raise ValueError("无法解析模型响应内容")

    @classmethod
    def list_providers(cls) -> Dict[str, str]:
        """列出所有支持的提供商"""
        return {key: config["name"] for key, config in MODEL_CONFIGS.items()}

    @classmethod
    def list_models(cls, provider: str) -> Dict[str, Dict]:
        """列出指定提供商的所有模型"""
        if provider in MODEL_CONFIGS:
            return MODEL_CONFIGS[provider]["models"]
        return {}

    def set_api_key(self, api_key: str):
        """设置当前提供商的API密钥"""
        self.api_key_manager.set_key(self.provider, api_key)
        # 重置客户端，以便下次使用时重新初始化
        self.client = None