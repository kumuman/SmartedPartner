import loguru
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.patches import Polygon, Rectangle, Circle
from PIL import Image

# 设置字体，确保中文字符显示正常
plt.rcParams['font.family'] = 'Microsoft YaHei'  # 设置为你系统中已有的中文字体


def plot_function(expressions, x_range=(-10, 10), num_points=1000):
    expressions_list = [esp.split("=")[1] for esp in expressions.split(";")]
    fig, ax = plt.subplots()
    x = np.linspace(x_range[0], x_range[1], num_points)

    for expression in expressions_list:
        y = eval(expression)
        ax.plot(x, y, label=expression)  # 将函数表达式作为标签

    ax.legend(loc='upper left')  # 图例放置在左上方
    ax.set_xlabel("x 轴", ha='left', va='top', position=(1, 0))  # x 轴标签放置在数轴末尾
    ax.set_ylabel("y 轴", ha='left', va='top', position=(0, 1))  # y 轴标签放置在数轴末尾
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.set_xlim(x_range)

    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    pil_image = Image.frombytes('RGB', canvas.get_width_height(), canvas.tostring_rgb())

    return pil_image


def plot_geometry(shape, params):
    # 创建一个图形和轴
    fig, ax = plt.subplots()
    axis_list = list(map(eval, params.split(';')))
    loguru.logger.debug(axis_list)
    if shape == '三角形':
        # 绘制一个绿色的三角形
        triangle_points = np.array(axis_list)
        triangle = plt.Polygon(triangle_points, color='green', fill=False)
        ax.add_patch(triangle)

    elif shape == '矩形':
        # 绘制一个红色的矩形

        rect = plt.Rectangle(axis_list[0],axis_list[1],axis_list[2], color='red', fill=False)
        ax.add_patch(rect)

    elif shape == '圆形':
        # 绘制一个蓝色的圆
        circle = plt.Circle(axis_list[0],axis_list[1], color='blue', fill=False)
        ax.add_patch(circle)

    # 设置坐标轴,调整轴的范围
    ax.relim()  # 重置轴的限制
    ax.autoscale_view()  # 自动缩放视图范围

    # 将图形转换为 PIL 图像
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    pil_image = Image.frombytes('RGB', canvas.get_width_height(), canvas.tostring_rgb())

    return pil_image


if __name__ == "__main__":
    # Example usage:
    expressions = "y=2*x - 3;y=x**2 + 2*x - 1"  # 多个函数表达式
    pil_image = plot_geometry("矩形", "(0.7, 0.1);0.3;0.4")
    pil_image.show()  # 显示图像
