import loguru
import requests

from src.image_extract import extract_text
from src.model import ChatGLMClient
from src.presets import narration, expository, argumentation, noval, prose, poetry, expression, classic_translate, \
    CHINESE_ESSAY_SCORING_TEMPLATE

url = "https://api.oioweb.cn/api/common/yiyan"
headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
}

def answer_skills(index):
    if index=="记叙文":
        return narration
    elif index=="说明文":
        return expository
    elif index=="议论文":
        return argumentation
    elif index=="小说":
        return noval
    elif index=="散文":
        return prose
    elif index=="诗歌":
        return poetry
    elif index=="常见写作方法表现手法":
        return expression

def daily_ana():
    response = requests.get(url=url, headers=headers).json()
    status = response["code"]
    if status == 200:
        author = response["result"]["author"]
        content = response["result"]["content"]

        content = content+'-'*6+author
        pic_url = response["result"]["pic_url"]

        loguru.logger.debug(content)

        return pic_url,content

def translate_classic_sentences(model,classic_sentences):
    prompts = classic_translate.format(sentences=classic_sentences)
    response = model.get_answer_at_once(prompts,[])
    loguru.logger.debug(response)
    return response

def analyze_composition(model,composition_img):
    composition = extract_text(composition_img)
    loguru.logger.debug(composition)
    prompts = CHINESE_ESSAY_SCORING_TEMPLATE.format(instruction=composition)
    response = model.get_answer_at_once(prompts,[])
    loguru.logger.debug(response)
    return response



if __name__=='__main__':
    model = ChatGLMClient()
    compositon_path = '../作文.jpg'
    analyze_composition(model,compositon_path)
