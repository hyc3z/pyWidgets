import time

from PyQt5.QtGui import QPixmap, QImage
from pygame import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape, portrait
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import *
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.shapes import Drawing
from reportlab.platypus import Paragraph, Table, TableStyle, Image

# 注册字体

pdfmetrics.registerFont(TTFont('SimSun', 'font/simsun.ttf'))


class PdfUtils:

    def __init__(self):
        pass

    @staticmethod
    def draw_title2(titlestr: str):
        style = getSampleStyleSheet()
        ct = style['Normal']
        ct.fontName = 'SimSun'
        ct.fontSize = 15
        # 设置行距
        ct.leading = 40
        # 颜色
        # ct.textColor =colors.blueviolet
        ct.textColor = colors.HexColor(0x215294)
        # 居中
        ct.alignment = 1
        # 添加标题并居中
        title = Paragraph(titlestr, ct)
        return title
# 绘制标题
    @staticmethod
    def draw_title1(titlestr:str):
        style = getSampleStyleSheet()
        ct = style['Normal']
        ct.fontName = 'SimSun'
        ct.fontSize = 30
        # 设置行距
        ct.leading = 40
        # 颜色
        # ct.textColor =colors.blueviolet
        ct.textColor =colors.HexColor(0x215294)
        # 居中
        ct.alignment = 1
        # 添加标题并居中
        title = Paragraph(titlestr, ct)
        return title

    @staticmethod
    def draw_title(titlestr:str):
        style = getSampleStyleSheet()
        ct = style['Normal']
        ct.fontName = 'SimSun'
        ct.fontSize = 20
        # 设置行距
        ct.leading = 40
        # 颜色
        ct.textColor = colors.blue
        # ct.textColor = colors.HexColor(0x215294)
        # 居中
        ct.alignment = 1
        # 添加标题并居中
        title = Paragraph(titlestr, ct)
        return title
    # 绘制内容
    @staticmethod
    def draw_text(textstr:str):
        style = getSampleStyleSheet()
        # 常规字体(非粗体或斜体)
        ct = style['Normal']
        # 使用的字体s
        ct.fontName = 'SimSun'
        ct.fontSize = 12
        # 设置自动换行
        ct.wordWrap = 'CJK'
        # 居中对齐
        ct.alignment = 1
        # 第一行开头空格
        # 设置行距
        ct.leading = 30
        text = Paragraph(textstr, ct)
        return text

    @staticmethod
    def draw_para(textstr:str):
        style = getSampleStyleSheet()
        # 常规字体(非粗体或斜体)
        ct = style['Normal']
        # 使用的字体s
        ct.fontName = 'SimSun'
        ct.fontSize = 12
        # 设置自动换行
        ct.wordWrap = 'CJK'
        # 居中对齐
        ct.alignment = 0
        # 第一行开头空格
        ct.firstLineIndent = 24
        # 设置行距
        ct.leading = 15
        text = Paragraph(textstr, ct)
        return text

    @staticmethod
    def draw_claim(textstr: str):
        style = getSampleStyleSheet()
        # 常规字体(非粗体或斜体)
        ct = style['Normal']
        # 使用的字体s
        ct.fontName = 'SimSun'
        ct.fontSize = 10
        # 设置自动换行
        ct.wordWrap = 'CJK'
        # 居中对齐
        ct.alignment = 0
        # 第一行开头空格
        ct.firstLineIndent = 24
        # 设置行距
        ct.leading = 15
        text = Paragraph(textstr, ct)
        return text

    @staticmethod
    def calc_verti_length(str, fontsize):
        size_o = int(len(str)/36+1)*fontsize
        print(size_o)
        return  size_o

    @staticmethod
    def draw_table(args, width=None):
        if width is None:

            # col_width = 440/w
            col_width = 540/len(args[0])
            # col_width = w*7
        else:
            col_width = width
        style = [
            ('FONTNAME', (0, 0), (-1, -1), 'SimSun'), # 字体
            ('BACKGROUND', (0, 0), (-1, 0), '#d5dae6'), # 设置第一行背景颜色
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), # 对齐
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'), # 对齐
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey), # 设置表格框线为grey色，线宽为0.5
        ]
        table = Table(args, colWidths=col_width, style=style)
        return table

    # 创建图表
    @staticmethod
    def draw_bar(bar_data, ax, items):
        drawing = Drawing(500, 250)
        bc = VerticalBarChart()
        bc.x = 35
        bc.y = 100
        bc.height = 120
        bc.width = 350
        bc.data = bar_data
        bc.strokeColor = colors.black
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = 100
        bc.valueAxis.valueStep = 10
        bc.categoryAxis.labels.dx = 8
        bc.categoryAxis.labels.dy = -10
        bc.categoryAxis.labels.angle = 20
        bc.categoryAxis.categoryNames = ax
    # 图示
        leg = Legend()
        leg.fontName = 'SimSun'
        leg.alignment = 'right'
        leg.boxAnchor = 'ne'
        leg.x = 465
        leg.y = 220
        leg.dxTextSpace = 10
        leg.columnMaximum = 3
        leg.colorNamePairs = items
        drawing.add(leg)
        drawing.add(bc)
        return drawing


if __name__ == "__main__":

    taskDict = {}


    c = canvas.Canvas("G:/report.pdf", pagesize=portrait(A4))
    # c.setFont("song",12)
    a = Image("logo_zjdxyxy.png", width=175, height=38)
    b = Image("logo_window.png", width=100, height=38)
    print(A4)
    a.drawOn(c, 75, 750)
    num = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    c.drawString(265, 770, "No." + num)
    b.drawOn(c, 400, 750)
    title = PdfUtils.draw_title("测距用户")
    title=PdfUtils.draw_title1("美容测距报告")
    baseline = 700
    title.wrapOn(c, 440, baseline)
    title.drawOn(c, 75, baseline)
    delta = 0
    # c.drawString(260, 720, "测距用户")
    data = [
        ('姓名', '性别', '年龄', '身高', '体重'),
        ("张三", "男", 18, 150, 55),
    ]
    delta += 20
    table = PdfUtils.draw_table(data)
    table.wrapOn(c, 75, baseline - delta)
    table.drawOn(c, 75, baseline - delta)
    delta += 20 * 5
    str_bingshi = "病史：{}".format("很多小伙伴纠结于这个一百天的时间，我觉得完全没有必要，也违背了我最初放这个大纲上来的初衷，我是觉得这个学习大纲还不错，自学按照这个来也能相对系统的学习知识，而不是零散细碎的知识最后无法整合，每个人的基础以及学习进度都不一样，没有必要纠结于一百天这个时间，甭管你是用三个月还是用一年来学习这些东西，最后学到了不就是收获吗？何必纠结于这一百天，觉得这一百天学习不完我就放弃了呢？（另，项目后面没有更新完，大家可以按照这个框架去学习，没有更新完的大家可以自行找资料。）")
    para = PdfUtils.draw_para("{}".format(str_bingshi))
    para.wrapOn(c, 440, baseline - delta)
    para.drawOn(c, 75, baseline - delta)
    delta += PdfUtils.calc_verti_length(str_bingshi, 12)
    title2 = PdfUtils.draw_title("测距结果")
    title2.wrapOn(c, 440, baseline - delta)
    title2.drawOn(c, 75, baseline - delta)
    # delta += PdfUtils.calc_verti_length(str_bingshi, 12)
    piclimit = 150
    text_h = 12
    for i in range(1, 10):
        name = "pic/image{}.png".format(i)
        print(name)
        tempimg = QImage()
        ret = tempimg.load(name)
        if ret:
            hwratio = tempimg.height() / tempimg.width()
            print(hwratio)
            if tempimg.height() > piclimit:
                w = piclimit/ hwratio
                h = piclimit
            else:
                w = piclimit
                h = piclimit * hwratio
            tempimg = Image(name, width=w , height=h)
            if i%2 == 1:
                if i >1:
                    delta += piclimit
                    delta += text_h
                pos =  baseline - delta - h
                if pos <= piclimit:
                    c.showPage()
                    delta = 0
                    baseline = 750
                tempimg.drawOn(c, 75, baseline - delta - h)
            else:
                tempimg.drawOn(c, 300, baseline - delta - h)
    c.save()