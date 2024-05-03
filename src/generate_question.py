import json
import os.path

from loguru import logger
import gradio as gr
from src.model import ChatGLMClient
from src.presets import SINGLE_CHOICE_TEMPLATE, SHORT_ANSWER_TEMPLATE

max_retry = 3

def write_json(questions,file_path):
    # 将JSON数据写入文件
    global json_data
    json_data= questions
    with open(file_path, "w") as file:
        json.dump(questions, file, indent=4)


def read_json(file_path):
    # 读取JSON文件中的数据
    global json_data
    with open(file_path, "r") as file:
        json_data = json.load(file)
    return json_data


def generate_question(model, question_type, subject_type, topic):
    file_path = "question/"+question_type+subject_type+topic+'.json'
    if question_type == '选择题':
        logger.info('选择题')
        format_inputs = SINGLE_CHOICE_TEMPLATE.format(
            topic=topic,
            subject=subject_type
        )
        if os.path.exists(file_path):
            AI_response = read_json(file_path)
        else:
            AI_response = model.bailian_llm(format_inputs)
            write_json(AI_response, file_path)
        logger.debug(AI_response)
        options = ['A.' + AI_response[0]['A'],
                   'B.' + AI_response[0]['B'],
                   'C.' + AI_response[0]['C'],
                   'D.' + AI_response[0]['D']]
        question = AI_response[0]['question']
        index = 0

        return [gr.update(choices=options, visible=True),  # 选择题更新选项
                gr.update(visible=False),  # 简答题不更新选项
                gr.update(value=question),
                {
                    'index': index,
                    'question_type': question_type
                }]

    elif question_type == '简答题':
        logger.info('简答题')
        inputs = "用户的指令：请随机给出5个{topic}的题目, 该题目的所属科目是{subject}".format(
            topic=topic,
            subject=subject_type
        )
        format_inputs = SHORT_ANSWER_TEMPLATE+inputs
        logger.info(format_inputs)
        for attempt in range(max_retry):
            try:
                if os.path.exists(file_path):
                    AI_response = read_json(file_path)
                else:
                    AI_response = model.bailian_llm(format_inputs)
                    write_json(AI_response, file_path)
                break  # 如果生成文本成功，退出循环
            except Exception as e:
                logger.error(f"文本生成失败：{e}")
                if attempt < max_retry - 1:
                    logger.info(f"重试生成文本，尝试次数：{attempt + 1}/{max_retry}")
                    continue  # 继续下一次循环进行重试
                else:
                    logger.error("无法生成文本，已达到最大重试次数")
                    raise  # 如果达到最大重试次数仍然失败，则抛出异常
        logger.debug(AI_response)
        question = AI_response[0]['question']
        index = 0
        return [gr.update(visible=False),  # 选择题更新选项
                gr.update(visible=True),  # 简答题不更新选项
                gr.update(value=question),
                {
                    'index': index,
                    'question_type': question_type
                }]
    else:
        logger.error('未选择题型')



def verify_answer(question_status, answer_choices, answer_short):
    index = question_status['index']
    answer = json_data[index]['answer']
    logger.info(f'answer:{answer}')
    logger.info(f'choices:{answer_choices}')
    if question_status['question_type']=='选择题':
        if answer_choices[0] == answer:
            gr.Info("回答正确")
            return f'''答案：\n{json_data[index]['answer']}\n解析：\n{json_data[index]['explanation']}'''
        else:
            gr.Info("回答错误")
            return f'''答案：\n{json_data[index]['answer']}\n解析：\n{json_data[index]['explanation']}'''
    elif question_status['question_type']=='简答题':
        gr.Info("请检查答案")
        return f'''答案：\n{json_data[index]['answer']}'''



def update_question(question_status):
    index = question_status['index'] + 1
    if (index >=10 and question_status['question_type']=='选择题') \
        or (index>=5 and question_status['question_type']=='简答题'):
        index = 0
    logger.info(question_status)
    logger.info(f'index:{index}')
    question = json_data[index]['question']
    if question_status['question_type']=='选择题':
        options = ['A.' + json_data[index]['A'],
                   'B.' + json_data[index]['B'],
                   'C.' + json_data[index]['C'],
                   'D.' + json_data[index]['D']]
        return [gr.update(value=question),
                gr.update(choices=options, visible=True),  # 选择题更新选项
                gr.update(visible=False),  # 简答题不更新选项
                {
                    'index': index,
                    'question_type': question_status['question_type']
                }]
    elif question_status['question_type']=='简答题':
        return [gr.update(value=question),
                gr.update(visible=False),  # 选择题不更新选项
                gr.update(visible=True),  # 简答题更新选项
                {
                    'index': index,
                    'question_type': question_status['question_type']
                }]


if __name__ == '__main__':
    model = ChatGLMClient()
    question_type = input(f'question_type:')
    subject_type = input(f'subject_type:')
    topic = input(f'topic:')
    respoonse = generate_question(model, question_type, subject_type, topic)

    print(f'response :{respoonse}')
