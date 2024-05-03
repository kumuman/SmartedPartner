import requests
import json
import os


# For prerequisites running the following sample, visit https://help.aliyun.com/document_detail/611472.html
from http import HTTPStatus
import dashscope


def call_with_messages(messages):
    messages = [{'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': messages}]

    response = dashscope.Generation.call(
        dashscope.Generation.Models.qwen_turbo,
        messages=messages,
        result_format='message',  # set the result to be "message" format.
        api_key='sk-IANIL0bbyr',
    )
    if response.status_code == HTTPStatus.OK:
        print(f"response:{response}")
        output = response.get("output", {})
        choices = output.get("choices", {})
        choices_message = choices[0].get("message", {})
        print(f"choices_message:{choices_message}")
        content = choices_message["content"]
        print(f"content:{content}")
    else:
        print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))

    return content


def get_access_token():
    """
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    """
    API_Key = "KHZomKMDfviGpOkUkZfXX0p7"
    Secret_Key = "TC3PLoWyQVckWAA7WdSJirYSbtHu0HIO"
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_Key}&client_secret={Secret_Key}".format(API_Key=API_Key,Secret_Key=Secret_Key)

    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")

def yiyan_api(message,access_token,use4=False):
    if use4:
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token=" + access_token
    else:
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token=" + access_token
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    try:
        result = json.loads(response.text)["result"]
    except:
        print(response.text)
    # print(result)
    return result

def yiyan_embedding(input_text):
    if input_text=="":
        input_text="  "
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/embeddings/embedding-v1?access_token=" + get_access_token()

    payload = json.dumps({
        "input": [input_text]
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    result = json.loads(response.text)["data"][0]["embedding"]
    return result

def main():
    embed = yiyan_embedding()
    print(embed)
if __name__ == '__main__':
    main()