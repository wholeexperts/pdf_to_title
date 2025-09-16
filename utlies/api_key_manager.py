import os
import json
from typing import Dict, Optional


class APIKeyManager:
    """API密钥管理器，用于存储和读取不同模型提供商的API密钥"""

    def __init__(self, key_file_path: str = "api_keys.json"):
        self.key_file_path = key_file_path
        self.keys = self._load_keys()

    def _load_keys(self) -> Dict[str, str]:
        """从文件加载API密钥"""
        if os.path.exists(self.key_file_path):
            try:
                with open(self.key_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_keys(self):
        """保存API密钥到文件"""
        try:
            with open(self.key_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.keys, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise Exception(f"无法保存API密钥到文件: {e}")

    def get_key(self, provider: str) -> Optional[str]:
        """获取指定提供商的API密钥"""
        return self.keys.get(provider)

    def set_key(self, provider: str, api_key: str):
        """设置指定提供商的API密钥"""
        self.keys[provider] = api_key
        self._save_keys()

    def remove_key(self, provider: str):
        """删除指定提供商的API密钥"""
        if provider in self.keys:
            del self.keys[provider]
            self._save_keys()

    def list_providers(self) -> list:
        """列出所有已配置密钥的提供商"""
        return list(self.keys.keys())