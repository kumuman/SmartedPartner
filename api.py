from fastapi import FastAPI, Request
from transformers import AutoTokenizer, AutoModel
import uvicorn, json, datetime
import torch

DEVICE = "cuda"
DEVICE_ID = "0"
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE


def torch_gc():
    if torch.cuda.is_available():
        with torch.cuda.device(CUDA_DEVICE):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()


app = FastAPI()


@app.post("/")
async def create_item(request: Request):
    global model, tokenizer
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    prompt = json_post_list.get('prompt')
    history = json_post_list.get('history')
    max_length = json_post_list.get('max_length')
    top_p = json_post_list.get('top_p')
    temperature = json_post_list.get('temperature')
    response, history = model.chat(tokenizer,
                                   prompt,
                                   history=history,
                                   max_length=12288,
                                   temperature=0.95)
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    answer = {
        "response": response,
        "history": history,
        "status": 200,
        "time": time
    }
    log = "[" + time + "] " + '", prompt:"' + prompt + '", response:"' + repr(response) + '"'
    print(log)
    torch_gc()
    return answer


if __name__ == '__main__':
    tokenizer = AutoTokenizer.from_pretrained("ChatGLM3-6b", trust_remote_code=True)
    model = AutoModel.from_pretrained("ChatGLM3-6b", trust_remote_code=True).cuda()
    # 多显卡支持，使用下面三行代替上面两行，将num_gpus改为你实际的显卡数量
    # model_path = "THUDM/chatglm2-6b"
    # tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    # model = load_model_on_gpus(model_path, num_gpus=2)
    model.eval()
    # paper_TEMPLATE = """
    # 请根据以下步骤和提示，帮助学生解决提供的数学方程：
    # 1.首先，请确认提供的表达式是否为一个方程。如果是方程，请识别方程中的未知数（例如：x, y, z等）。简要解释方程的结构和含义，帮助学生理解方程所表达的关系。
    # 2.判断方程的类型（如线性方程、二次方程、指数方程等）。根据方程类型，提供相应的解题策略或公式（例如：移项、合并同类项、使用公式求解等）。
    # 3.展示方程求解的详细步骤，包括每个步骤的操作和原因。如果方程需要多个步骤才能求解，请按照逻辑顺序逐步展示。
    # 4.在求解完成后，将解代入原方程进行验证，确保解的准确性。解释解的含义，并说明它如何满足原方程的条件。
    # 5.提供一到两个练习题，让学生尝试自己求解。

    # 待求解的方程如下：
    # 2*x + 5 = 0
    # """
    # response,_ = model.chat(tokenizer,paper_TEMPLATE,[],temperature=0.95,)
    # print(f'response :{response}')
    uvicorn.run(app, host='0.0.0.0', port=8000, workers=1)
