from pptx import Presentation
from pptx.chart.data import ChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches
import os, sys


class bnc_report_ppt(object):
#    def __init__(self, object):
# self.url = object['para_my_url']['bn_2dfire_function_api']
# self.connection = object['para_connection']

    def create_ppt(self, data):
        # create presentation with 1 slide ------
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)
        title = slide.shapes.title
        subtitle = slide.placeholders[1]

        title.text = "Hello, World!"
        subtitle.text = "python-pptx was here!"
        # define chart data ---------------------
        chart_data = ChartData()
        chart_data.categories = ['East', 'West', 'Midwest']
        chart_data.add_series('Series 1', (19.2, 21.4, 16.7))

        # add chart to slide --------------------
        x, y, cx, cy = Inches(2), Inches(2), Inches(6), Inches(4.5)
        slide.shapes.add_chart(
            XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
        )
        file_path='chart-011.pptx'
        prs.save(file_path)

        with open(file_path, 'rb') as fp:
            data = fp.read().encode('base64')
        return data
