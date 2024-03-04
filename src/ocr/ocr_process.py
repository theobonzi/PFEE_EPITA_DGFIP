import os
import json
from io import BytesIO
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw
import tqdm
from src.ocr.ocr_trocr import draw_boxes_on_image_trocr
from src.ocr.ocr_google import draw_boxes_on_image_google
from src.ocr.ocr_tesseract import draw_boxes_on_image_tesseract

def draw_boxes(ocr, img_path, good_forms, nb_ocr=0, model=None, processor=None):
    base_path = "json_labels"
    image_file_name = f"{good_forms}.json"
    
    full_path_json = os.path.join(base_path, image_file_name)
    with open(full_path_json, 'r') as json_file:
        data = json.load(json_file)
    
    print(ocr)
    if ocr == 'google':
        img, strings, df = draw_boxes_on_image_google(img_path, data, nb_ocr)
    elif ocr == 'trocr':
        img, strings, df = draw_boxes_on_image_trocr(img_path, data, nb_ocr, model, processor)
    elif ocr == 'tesseract':
        img, strings, df = draw_boxes_on_image_tesseract(img_path, data, nb_ocr)

    return img, strings, df

