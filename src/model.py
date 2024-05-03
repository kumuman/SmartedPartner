import json
from http import HTTPStatus

import dashscope
import requests



class ChatGLMClient():
    def __init__(self):
        self.url = 'http://localhost:8000'
        self.header = {
            'Content-Type': 'application/json'
        }
        self.use_RAG = False

    def get_answer_at_once(self, query, history):
        data = {
            'prompt': query,
            'history': history
        }
        response = requests.post(url=self.url, json=data, headers=self.header).json()

        return response['response']

    def get_answer_stream_iter(self, query, history):
        data = {
            'prompt': query,
            'history': history
        }
        response = requests.post(url=self.url, json=data, headers=self.header).json()

        yield response['response']


    # 调用阿里云百炼大模型API
    def bailian_llm(query, history=[]):
        # 构造LLM输入
        messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}]
        for hist in history:
            messages.append({'role': 'user', 'content': hist[0]})
            messages.append({'role': 'assistant', 'content': hist[1]})
        messages.append({'role': 'user', 'content': query})


        response = dashscope.Generation.call(
            dashscope.Generation.Models.qwen_turbo,
            messages=messages,
            result_format='message',  # set the result to be "message" format.
            api_key='sk-IANIL0bbyr',
        )
        if response.status_code == HTTPStatus.OK:
            output = response.get("output", {})
            choices = output.get("choices", {})
            choices_message = choices[0].get("message", {})
            content_json = json.loads(choices_message["content"].split("```json\n")[1].rsplit("\n```", 1)[0])
            return content_json
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))




if __name__ == '__main__':
    model = ChatGLMClient()
    inputs = input("")
    response = model.get_answer_at_once(inputs,[])
    print(f'response:{response}')
