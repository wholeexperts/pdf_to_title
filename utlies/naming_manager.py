import os
import re
from typing import List, Optional
from .config import NAMING_FORMATS


class NamingManager:
    """命名管理器，支持多种文件命名格式"""

    def __init__(self, format_type: str = "title_author"):
        self.format_type = format_type
        self.format_config = NAMING_FORMATS.get(format_type, NAMING_FORMATS["title_author"])

    def generate_filename(self, 
                         pdf_path: str, 
                         title: str, 
                         authors: List[str], 
                         year: Optional[str] = None) -> str:
        """
        根据指定格式生成新的文件名
        
        Args:
            pdf_path: 原始PDF文件路径
            title: 论文标题
            authors: 作者列表
            year: 发表年份（可选）
        """
        # 提取原文件扩展名
        _, ext = os.path.splitext(pdf_path)
        
        # 获取第一作者
        first_author = authors[0] if authors else "Unknown_Author"
        
        # 获取所有作者
        all_authors = "_et_al" if len(authors) > 1 else first_author
        if len(authors) > 1:
            all_authors = f"{authors[0]}_et_al"
        
        # 根据格式生成文件名主体
        format_string = self.format_config["format"]
        new_name_base = format_string.format(
            title=title,
            first_author=first_author,
            all_authors=all_authors,
            year=year if year else "Unknown_Year"
        )
        
        # 清理文件名
        safe_name = self.sanitize_filename(new_name_base)
        
        # 拼接扩展名
        new_filename = safe_name + ext.lower()
        
        return new_filename

    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 200) -> str:
        """
        清理文件名：移除非法字符，替换空格，截断长度
        """
        # Windows 和大多数系统中非法的字符
        illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'
        filename = re.sub(illegal_chars, '_', filename)
        # 替换多个空格或特殊空白符为单下划线
        filename = re.sub(r'\s+', '_', filename)
        # 去除首尾下划线
        filename = filename.strip('_')
        # 限制长度
        if len(filename) > max_length:
            filename = filename[:max_length]
        return filename

    @classmethod
    def list_formats(cls) -> dict:
        """列出所有支持的命名格式"""
        return NAMING_FORMATS