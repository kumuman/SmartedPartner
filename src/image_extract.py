from paddleocr import PaddleOCR, draw_ocr
from PIL import Image

def extract_text(img_path):

    # Paddleocr目前支持的多语言语种可以通过修改lang参数进行切换
    # 例如`ch`, `en`, `fr`, `german`, `korean`, `japan`
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")  # need to run only once to download and load model into memory
    result = ocr.ocr(img_path, cls=True)
    i=0
    all_values = []
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            i=i+1
            all_values.append(line[1][0])

    output = all_values

    # 显示结果
    # 如果本地没有simfang.ttf，可以在doc/fonts目录下下载

    result = result[0]
    image = Image.open(img_path).convert('RGB')
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    im_show = draw_ocr(image, boxes, txts, scores, font_path='doc/fonts/simfang.ttf')
    im_show = Image.fromarray(im_show)
    output_img = 'result.jpg'
    im_show.save(output_img)

    return output, output_img

if __name__== '__main__':
    img_path = '../试题.png'
    output ,output_img = extract_text(img_path)
    output=''.join(output)
    print(output)