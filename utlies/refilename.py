import os
import re
from .naming_manager import NamingManager
from .config import DEFAULT_NAMING_FORMAT


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


def generate_new_filename(pdf_path: str, title: str, first_author: str) -> str:
    """
    根据原始PDF路径、标题和第一作者，生成新的安全文件名
    格式: {title}_{first_author}.pdf
    """
    # 使用命名管理器生成文件名（保持向后兼容）
    manager = NamingManager(DEFAULT_NAMING_FORMAT)
    return manager.generate_filename(pdf_path, title, [first_author])


# 示例使用
# if __name__ == "__main__":
#     pdf_path = r"C:/Users/CQF/Desktop/1-s2.0-S095070512300881X-main.pdf"
#     title = "From Easy to Hard: Progressive Active Learning Framework for Infrared Small Target Detection with Single Point Supervision"
#     authors = ['Chuang Yu', 'Jinmiao Zhao', 'Yunpeng Liu', 'Sicheng Zhao', 'Yimian Dai', 'Xiangyu Yue']

#     new_name = generate_new_filename(pdf_path, title, authors[0])
#     print("新文件名:", new_name)
#     # 输出示例: From_Easy_to_Hard_Progressive_Active_Learning_Framework_for_Infrared_Small_Target_Detection_with_Single_Point_Supervision_Chuang_Yu.pdf