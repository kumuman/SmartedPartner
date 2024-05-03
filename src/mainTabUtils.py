import datetime
import os
import traceback

import gradio as gr
from loguru import logger

from src.image_extract import extract_text
from src.presets import STANDARD_ERROR_MSG, PROMPT_TEMPLATE


def predict(model,inputs,chatbot,files=None,image=None):

    logger.debug(image)
    if image is not None:
        img_text, _ = extract_text(image)
        img_text = ''.join(img_text)
        message = img_text + '\n' + inputs
    else:
        message = inputs

    logger.debug(message)
    logger.debug(files)
    message, display_append, format_inputs, chatbot = prepare_inputs_chat(
        inputs=message,
        files=files[0] if files else None,
        reply_language="中文",
        chatbot=chatbot
    )
    logger.debug(message)
    logger.debug(format_inputs)
    try:
        logger.debug("不使用流式传输")
        AI_response = model.get_answer_at_once(
            format_inputs,
            []
        )
        # AI_response = model.bailian_llm(format_inputs)
        logger.debug(AI_response)
        chatbot.append((inputs, AI_response))

        return "",chatbot
    except Exception as e:
        traceback.print_exc()
        status_text = STANDARD_ERROR_MSG + str(e)
        return status_text , chatbot



from src.index_process import construct_index

def prepare_inputs_chat(
        inputs,
        files,
        reply_language,
        chatbot
):
    display_append = []
    fake_inputs = inputs

    if files:
        from langchain.vectorstores.base import VectorStoreRetriever
        msg = "获取索引中……"
        logger.info(msg)
        index = construct_index(files=files)
        assert index is not None, "获取索引失败"
        msg = "索引获取成功，生成回答中……"
        logger.info(msg)
        k = 5
        retriever = VectorStoreRetriever(
            vectorstore=index,
            search_type="similarity",
            search_kwargs={"k": k}
        )
        try:
            relevant_documents = retriever.get_relevant_documents(fake_inputs)
        except:
            return prepare_inputs_chat(
                fake_inputs,
                files,
                reply_language,
                chatbot,
            )
        reference_results = [
            [d.page_content.strip("�"), os.path.basename(d.metadata["source"])]
            for d in relevant_documents
        ]
        reference_results = add_source_numbers(reference_results)
        display_append = add_details(reference_results)
        display_append = "\n\n" + "".join(display_append)
        real_inputs = (
            replace_today(PROMPT_TEMPLATE)
            .replace("{query_str}", fake_inputs)
            .replace("{context_str}", "\n\n".join(reference_results))
            .replace("{reply_language}", reply_language)
        )
    else:
        real_inputs = inputs

    return fake_inputs, display_append, real_inputs, chatbot


def handle_file_upload(files):
    if files:
        construct_index(files[0])
    return gr.Files.update()


def add_source_numbers(lst, source_name="Source", use_source=True):
    if use_source:
        return [
            f'[{idx + 1}]\t "{item[0]}"\n{source_name}: {item[1]}'
            for idx, item in enumerate(lst)
        ]
    else:
        return [f'[{idx + 1}]\t "{item}"' for idx, item in enumerate(lst)]


def add_details(lst):
    nodes = []
    for index, txt in enumerate(lst):
        brief = txt[:25].replace("\n", "")
        nodes.append(f"<details><summary>{brief}...</summary><p>{txt}</p></details>")
    return nodes


def replace_today(prompt):
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    return prompt.replace("{current_date}", today)

