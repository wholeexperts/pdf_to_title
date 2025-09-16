from zai import ZaiClient, ZhipuAiClient
from .model_manager import ModelManager
from .config import DEFAULT_MODEL, DEFAULT_MODEL_NAME

# 保持向后兼容的函数接口
def extract_txt_to_LLM(context):
    """
    使用大语言模型提取论文信息的向后兼容接口
    返回: (title, authors)
    """
    try:
        manager = ModelManager(DEFAULT_MODEL, DEFAULT_MODEL_NAME)
        title, authors, _ = manager.extract_info(context)
        return title, authors
    except Exception as e:
        # 如果出现任何错误，返回默认值以保持向后兼容
        return "未知标题", ["未知作者"]

api_key = "070c035c2ba14e988a52dc45314b92f0.O3P7ZRCo3LVmTYiK"

# 直接设置 API Key
base_URL = "https://open.bigmodel.cn/api/paas/v4/"
client = ZhipuAiClient(api_key=api_key, base_url=base_URL)

#该函数的主要作用就是：将pdf_to_text函数的输出，利用大模型解析为json输出标题以及作者名称

prompt_assistant = "你是一个论文助手，会将我输入论文的前十几行文件，输出论文的标题以及作者。回复是记得使用json格式返回，格式如下：\n{\n  \"title\": \"论文标题\",\n  \"authors\": [\"作者1\", \"作者2\", ...]\n}"
def extract_txt_to_LLM(context):
    response = client.chat.completions.create(
    model="glm-4.5-flash",
    messages=[
        {"role": "assistant", "content":prompt_assistant },
        {"role": "user", "content":context}
    ],
    max_tokens=2048,
    temperature=0.4,
    thinking={
        "type": "disabled",    # 启用深度思考模式
    }
    )
    context = response.choices[0].message.content

    title = context.split('"title": "')[1].split('",')[0]
    authors = context.split('"authors": [')[1].split(']')[0].replace('"', '').split(',')
    authors = [author.strip() for author in authors]
    # print("Title:", title)
    # print("Authors:", authors)

    return title, authors