import hashlib
import random

import loguru
import requests

from src.model import ChatGLMClient
from src.presets import english_writing

quotesurl = "https://api.oioweb.cn/api/common/OneDayEnglish"
headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
}
language_type = {
  "中文": "zh",
  "英文": "en",
  "韩文": "kor",
  "日文": "jp",
  "法文": "fra",
  "俄文": "ru"
}
appid = "20240322002001174"
secret_key = "rKMgWktJbmLgcOsuODBd"
query = "What is the security flaw of CBC-MAC?"
translate_url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
from_lang = "auto"

def get_daily_quotes():
    response = requests.get(url=quotesurl, headers=headers).json()
    status = response["code"]
    if status==200:
        content_en = response["result"]["content"]
        content_zh = response["result"]["note"]
        content = content_en+'\n'+content_zh
        loguru.logger.debug(content)

        img = response["result"]["img"]
        voice = response["result"]["tts"]

        return img,voice,content

def generate_sign(appid, query, salt, secret_key):
    sign_str = f"{appid}{query}{salt}{secret_key}"
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    return sign

def get_translate(query, to_lang):
    loguru.logger.debug(to_lang)
    response = []
    salt = str(random.randint(32768, 65536))
    sign = generate_sign(appid, query, salt, secret_key)
    for to in to_lang:
        params = {
            "q": query,
            "from": from_lang,
            "to": language_type[to],
            "appid": appid,
            "salt": salt,
            "sign": sign
        }
        loguru.logger.debug(params)
        resp = requests.get(translate_url, params=params).json()['trans_result'][0]['dst']
        response.append(f'{to}: {resp}')

    loguru.logger.debug(response)

    return '\n\n'.join(response)

def text_process(model,text_input):
    prompts = english_writing.format(instruction=text_input)
    response = model.get_answer_at_once(prompts,[])
    loguru.logger.debug(response)
    return response





if __name__=='__main__':
    text = """
    Title: Embracing Junior High School Life

    Junior high school life is an exciting journey filled with new experiences and challenges. As a student, I have found it to be a time of growth and discovery, both academically and personally.
    
    Academically, junior high school introduces us to a wider range of subjects, from the sciences to the humanities. The courses are more rigorous and demand a higher level of critical thinking and problem-solving skills. This has helped me to develop a deeper understanding of the subjects and improve my academic performance.
    
    Beyond the classroom, junior high school also offers a range of extracurricular activities that enrich our lives. Whether it's participating in a sports team, joining a club, or volunteering in the community, these activities provide us with opportunities to develop new skills, make friends, and contribute to society.
    
    Personally, junior high school has been a time of self-discovery. It's a phase where we start to form our own opinions and identities. We learn to navigate through social situations, handle peer pressure, and develop a sense of independence. These experiences help us to grow into more confident and resilient individuals.
    
    In conclusion, junior high school life is a transformative period that prepares us for the challenges of high school and beyond. It's a time to embrace new opportunities, learn from our mistakes, and grow into the best version of ourselves. I am grateful for the experiences and lessons that junior high school has taught me, and I look forward to the adventures that lie ahead."""
    model = ChatGLMClient()
    text_process(model,text)