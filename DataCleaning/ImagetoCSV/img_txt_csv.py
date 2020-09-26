#!/usr/local/bin/python3.6

import os
import sys

import pyocr
import pyocr.builders
from PIL import Image as PI

import csv


def img_txt(image):
    # input is a PIL Image object, output is a string of that image.

    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print('No OCR tool found.')
        sys.exit(1)

    tool = tools[0]
    english = tool.get_available_languages()[0]

    txt = tool.image_to_string(
        image,
        lang=english,
        builder=pyocr.builders.TextBuilder()
    )
    return txt


input_path = "/Users/payaj/Downloads/img_test"
output_path = "/Users/payaj/Downloads/img_test"
files = os.listdir("/Users/payaj/Downloads/img_test")


os.chdir(input_path)

output = []
for i in range(0, len(files)):
    print(files[i])
    img = PI.open(files[i])

    width = img.size[0]
    height = img.size[1]

    img_presenter = img.crop((0, 1129, 1742, 1685))
    img_return_to = img.crop((1744, 1129, width, 1685))

    # img_presenter = img.crop((0, 429, 650, 629))
    # img_return_to = img.crop((655, 429, width, 629))

    print(i)
    ID = ''
    Presenter = ''
    ReturnTo = ''
    ID = str(files[i][:16]) + 'P'
    Presenter = img_txt(img_presenter)
    ReturnTo = img_txt(img_return_to)

    args = ID, Presenter, ReturnTo

    with open('/Users/payaj/Downloads/test_.csv', 'a') as outfile:
        writer = csv.writer(outfile)
        if i == 0:
            writer.writerow(
                ['ID', 'Presenter', 'ReturnTo'])
        # writer.writerow(args)
        writer.writerow([str(s) for s in args])
