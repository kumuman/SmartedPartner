import gradio as gr
import loguru

from src.CnImageCorrectWritingDemo import get_composition
from src.Tools import generate_gist, generate_paper, geneate_test, gen_requirement, save_knowledge_func
from src.generate_question import generate_question, verify_answer, update_question
from src.model import ChatGLMClient
from src.mainTabUtils import predict, handle_file_upload
from subject_tutor.Chinese import answer_skills, daily_ana, translate_classic_sentences
from subject_tutor.English import get_daily_quotes, get_translate, text_process
from subject_tutor.math import plot_function, plot_geometry



subject_types = [
    '语文',
    '数学',
    '英语',
    '物理',
    '化学',
    '生物',
    '历史',
    '地理',
    '政治',
    '计算机'
]
single_choices = ['A', 'B', 'C', 'D']


bot_img = 'assets/bot.ico'
user_img = 'assets/user.ico'

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    artical = gr.State(value="output_img.png")
    model = gr.State(value=ChatGLMClient())
    question_status = gr.State(value={
        'index': 0,
        'question_type': None
    })
    gr.Markdown("# Welcome to SmartedPartner! 🌟🚀")
    gr.Markdown("为教育降本增效的AI应用")

    with gr.Tab("🔥️主页"):
        gr.Markdown("## 此处为聊天解疑区")
        with gr.Row(equal_height=True):
            with gr.Column(scale=1):
                with gr.Accordion(label="知识库", open=True, visible=True):
                    index_files = gr.Files(label=(
                        "上传"), type="file",
                        file_types=[".pdf", ".docx", ".pptx", ".epub", ".xlsx", ".txt", "text", "image"])

            with gr.Column(scale=12):
                with gr.Row():
                    chatbot = gr.Chatbot(
                        label="ChatGPT",
                        sanitize_html=False,
                        show_label=False,
                        avatar_images=[user_img, bot_img],
                        show_share_button=False,
                        bubble_full_width=False
                    )
                with gr.Row():
                    img = gr.Image(label='拍照答疑', source="upload", type='filepath')
                with gr.Row():
                    msg = gr.Textbox(
                        scale=24,
                        show_label=False,
                        placeholder="在这里输入"
                    )
                    submitBtn = gr.Button(
                        scale=1,
                        value="发送",
                        variant='primary'
                    )

        index_files.upload(handle_file_upload, inputs=index_files, outputs=index_files)

        msg.submit(predict,
                   inputs=[
                       model,
                       msg,
                       chatbot,
                       index_files,
                       img],
                   outputs=[msg, chatbot])
        submitBtn.click(predict,
                        inputs=[
                            model,
                            msg,
                            chatbot,
                            index_files,
                            img],
                        outputs=[msg, chatbot])
    with gr.Tab("📖题目生成"):
        gr.Markdown("# 智能题目生成助手")
        with gr.Row(equal_height=True):
            with gr.Column(scale=1):
                question_type = gr.Radio(
                    choices=["选择题", "简答题"],
                    type="value",
                    value="选择题",
                    interactive=True,
                    label="题目类型",
                    show_label=True)

                subject_type = gr.Radio(
                    choices=subject_types,
                    type="value",
                    value="历史",
                    interactive=True,
                    label="科目类型",
                    show_label=True)
                desc_input = gr.Textbox(lines=5, placeholder="请描述你想要生成的题库，例如：有关中国外交的近代史",
                                        label="题库描述")

                generate_button = gr.Button(value="生成题目", variant="primary")

                remove_button = gr.ClearButton(value="移除题目", variant="stop")

            with gr.Column(scale=12):
                show_question = gr.Textbox(
                    interactive=False,
                    lines=5,
                    label="题目及答案",
                    show_label=True)
                # 选择题组件
                answer_choices = gr.Radio(
                    choices=[],
                    min_width=10,
                    interactive=True,
                    label="选择题",
                    show_label=True,
                    visible=False)
                # 填空题组件
                answer_short = gr.Textbox(
                    lines=8,
                    placeholder="请输入你的答案",
                    visible=False,
                    label="填空题",
                    interactive=True,
                    show_label=True
                )
                with gr.Row():
                    get_answer = gr.Button(value='查看答案')
                    upload_answer = gr.Button(value="提交")
                    next_question = gr.Button(value="下一题")

        generate_button.click(fn=generate_question,
                              inputs=[model, question_type, subject_type, desc_input],
                              outputs=[answer_choices, answer_short, show_question, question_status])

        upload_answer.click(fn=verify_answer,
                            inputs=[question_status, answer_choices, answer_short],
                            outputs=[show_question]
                            )
        get_answer.click(fn=verify_answer,
                         inputs=[question_status, answer_choices, answer_short],
                         outputs=[show_question])

        next_question.click(fn=update_question,
                            inputs=[question_status],
                            outputs=[show_question, answer_choices, answer_short, question_status])
    with gr.Tab("🛠️教学工具箱"):
        gr.Markdown("## 此处为服务师生的教学工具箱")
        with gr.Row():
            with gr.Column():
                with gr.Accordion(label="ppt生成", open=False):
                    ppt_topic = gr.Textbox(label="PPT生成",
                                           placeholder="请描述你想要生成的ppt题目，例如：有关中国外交的近代史",
                                           show_label=True)
                    requirement_button = gr.Button("分析需求",variant="primary")
                    AI_gen_requirement_text = gr.Text(label="AI给出的细化建议", show_label=True)
                    knowledge_content = gr.Textbox(label="请输入关于PPT主题更细化的一些信息", show_label=True)
                    sub_num = gr.Slider(1, 10, value=2, step=1, label="子主题个数", show_label=True)
                    mode = gr.Dropdown(choices=[1, 2], label="模板选择", show_label=True)
                    generate_ppt_button = gr.Button(value="生成PPT", variant="primary")
                    ppt_files = gr.components.File(label='ppt文件存放处')

                    requirement_button.click(fn=gen_requirement, inputs=[ppt_topic], outputs=[AI_gen_requirement_text])
                    generate_ppt_button.click(fn=save_knowledge_func, inputs=[ppt_topic,knowledge_content,mode,sub_num],
                                              outputs=[ppt_files])
                with gr.Accordion(label="考点生成", open=False):
                    exam_grade = gr.Textbox(lines=1, placeholder="请描述你的年级",
                                            label="年级")
                    exam_subject = gr.Textbox(lines=1, placeholder="请描述你想要生成的学科",
                                              label="学科")
                    exam_chapter = gr.Textbox(lines=1, placeholder="请描述你想要生成相关内容的章节",
                                              label="章节")
                    generate_exam_button = gr.Button(value="生成考点文件", variant="primary")
                    exam_files = gr.components.File(label='考点文件存放处')

                    generate_exam_button.click(fn=geneate_test, inputs=[model, exam_grade, exam_subject, exam_chapter],
                                               outputs=exam_files)
            with gr.Column():
                with gr.Accordion(label="试卷生成", open=False):
                    paper_topic_input = gr.Textbox(lines=3, placeholder="请描述你想要生成的试卷主题，例如：经典力学",
                                                   label="试卷主题")
                    subject_input = gr.Textbox(lines=1, placeholder="请描述你想要生成的试卷科目，例如：数学",
                                               label="试卷科目")
                    type_input = gr.Radio(choices=['选择题', '填空题', '解答题'],
                                          type="value",
                                          value="选择题",
                                          interactive=True,
                                          label="题目类型",
                                          show_label=True)
                    number_input = gr.Textbox(placeholder="请描述你想要生成的试卷科目，例如：数学",
                                              value='6',
                                              label="题目数量",
                                              lines=1)
                    generate_paper_button = gr.Button(value="生成试卷", variant="primary")
                    paper_files = gr.components.File(label='试卷文件存放处')
                with gr.Accordion(label="课堂流程设计", open=False):
                    class_subject = gr.Textbox(lines=3, placeholder="请输入您这节课学科",
                                               label="学科")
                    class_grade = gr.Textbox(lines=3, placeholder="请输入您学生所在年级",
                                             label="年级")
                    class_content = gr.Textbox(lines=3, placeholder="请输入您这节课课程主要内容",
                                               label="课程内容")
                    generate_class_button = gr.Button(value="生成课堂流程概要", variant="primary")
                    class_files = gr.components.File(label='课堂概要文件存放处')

                    generate_class_button.click(fn=generate_gist,
                                                inputs=[model, class_subject, class_grade, class_content],
                                                outputs=class_files)


        generate_paper_button.click(fn=generate_paper,
                                    inputs=[model, paper_topic_input, subject_input, type_input, number_input],
                                    outputs=[paper_files])
    with gr.Tab("📔语文辅导"):
        gr.Markdown("## 此处为语文专属辅导区")
        with gr.Row():
            with gr.Column():
                with gr.Accordion(label="作文分析模块", open=False):
                    with gr.Row():
                        composition_img_1 = gr.Image(label='作文图片上传', source="upload", type='filepath')
                        composition_img_2 = gr.Image(label='作文图片上传', source="upload", type='filepath')
                        composition_img_3 = gr.Image(label='作文图片上传', source="upload", type='filepath')

                    composition_topic = gr.Textbox(label="作文主题",lines=2)
                    composition_button = gr.Button(value="处理", variant="primary")
                    composition_files = gr.components.File(label='作文处理结果存放处')

                    composition_button.click(fn=get_composition,
                                             inputs=[composition_img_1,
                                                     composition_img_2,
                                                     composition_img_3,
                                                     composition_topic,
                                                     artical],
                                             outputs=composition_files)
                with gr.Accordion(label="文言文模块", open=False):
                    classic_context = gr.Textbox(label="文言文句子翻译",
                                                 placeholder="请输入您想要翻译的句子",
                                                 lines=3)
                    translate_classic_btn = gr.Button(value="翻译生成", variant="primary")
                    output_classic_context = gr.Textbox(label="翻译结果",
                                                        placeholder="此处将展示翻译结果及相似例题",
                                                        lines=5)

                    translate_classic_btn.click(fn=translate_classic_sentences,
                                                inputs=[model, classic_context],
                                                outputs=output_classic_context)

            with gr.Column():
                with gr.Accordion(label="文学素养模块", open=False):
                    gr.Markdown("## 每日一句，积累文学素养")
                    ana_img = gr.Image(label='封面', source="upload", type='filepath')
                    ana_context = gr.Textbox(label="金句展示", placeholder="此处将展示每日金句", lines=3)
                    generate_ana = gr.Button(value="生成", variant="primary")

                    generate_ana.click(fn=daily_ana, inputs=None, outputs=[ana_img, ana_context])
                with gr.Accordion(label="阅读理解模块", open=False):
                    comprehension = gr.Dropdown(choices=["记叙文",
                                                         "说明文",
                                                         "议论文",
                                                         "小说",
                                                         "散文",
                                                         "诗歌",
                                                         "常见写作方法表现手法"],
                                                multiselect=False,
                                                label="答题技巧",
                                                interactive=True
                                                )
                    comprehension_output = gr.Textbox(label="答题技巧",
                                                      lines=5,
                                                      placeholder="此处展示所选模块的技巧内容"
                                                      )
                    comprehension.change(fn=answer_skills,
                                         inputs=comprehension,
                                         outputs=comprehension_output
                                         )
    with gr.Tab("📐数学辅导"):
        gr.Markdown("## 此处为数学专属辅导区")
        with gr.Row():
            with gr.Column():
                with gr.Accordion(label="函数模块", open=False):
                    func_input = gr.Textbox(label="函数表达式",
                                            placeholder="请输入函数完整表达式。"
                                                        "例如:y=x*x+2*x-3;y=x+3(多个函数请用英文分号分隔)",
                                            lines=2,
                                            show_label=True,
                                            interactive=True
                                            )
                    generate_func = gr.Button(variant="primary",
                                              value="生成函数图形"
                                              )
                    func_img = gr.Image(label="图形绘制区", type="pil")
            with gr.Column():
                with gr.Accordion(label="几何模块", open=False):
                    shape_input = gr.Dropdown(label="选择几何形状",
                                              choices=["三角形", "矩形", "圆形"],
                                              value="三角形",
                                              show_label=True,
                                              interactive=True)
                    # 根据选择的形状，显示相应的参数输入框
                    shape_params = gr.Textbox(label="形状参数",
                                              placeholder="请输入形状的参数，"
                                                          "例如三角形需要三个点坐标:(0.7, 0.1);(0.9, 0.3);(0.7, 0.4)使用英语分号分隔坐标"
                                                          "矩形需要左上角坐标以及长和高:(0.2, 0.2); 0.2;0.4"
                                                          "圆需要圆心以及半径:(0.5, 0.5); 0.3",
                                              lines=3,
                                              show_label=True,
                                              interactive=True)
                    generate_geom = gr.Button(variant="primary",
                                              value="生成几何图形"
                                              )
                    geom_img = gr.Image(label="图形绘制区", type="pil")

                # 将按钮与函数绑定
        generate_geom.click(fn=plot_geometry, inputs=[shape_input, shape_params], outputs=geom_img)
        generate_func.click(fn=plot_function,
                            inputs=func_input,
                            outputs=func_img)
    with gr.Tab("🔤外语辅导"):
        gr.Markdown("## 此处为外语专属辅导区")
        with gr.Row():
            with gr.Column():
                with gr.Accordion(label="外语翻译模块", open=False):
                    translate_input = gr.Textbox(label="翻译", lines=5, placeholder="请输入您想要翻译的句子")
                    language_target_type = gr.Dropdown(label="目标语种选择",
                                                       choices=["中文", "英文", "韩文", "日文", "法文", "俄文"],
                                                       multiselect=True)
                    translate = gr.Button(value="翻译", variant="primary")
                    translate_output = gr.Textbox(label="翻译结果", lines=5)

                    translate.click(fn=get_translate, inputs=[translate_input, language_target_type],
                                    outputs=translate_output)

            with gr.Column():
                with gr.Accordion(label="英语素养模块", open=False):
                    quote_img = gr.Image(label='封面', source="upload", type='filepath')
                    quote_audio = gr.Audio(label='语音', source="upload", type='filepath')
                    quote_context = gr.Textbox(label="金句名言",
                                               placeholder="此处将展示生成的英文金句名言以及对应的翻译结果", lines=5)
                    generate_quote = gr.Button(value="生成", variant="primary")

                    generate_quote.click(fn=get_daily_quotes, inputs=None,
                                         outputs=[quote_img, quote_audio, quote_context])

        with gr.Accordion(label="作文内容分析处理模块", open=False):
            text_input = gr.Textbox(label="文本分析", lines=5, placeholder="请输入您想要分析的句子")
            dispose_button = gr.Button(value="处理", variant="primary")
            dispose_output = gr.Textbox(label="处理结果", lines=5)

            dispose_button.click(fn=text_process, inputs=[model, text_input], outputs=dispose_output)

demo.queue()
if __name__ == '__main__':
    demo.launch(inbrowser=True,share=True)
