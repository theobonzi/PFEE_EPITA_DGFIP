import os
import pandas as pd

from src.process.train_process import process_train 
from src.process.inference_process import inference, run_all
from src.ocr.ocr_process import draw_boxes

def save_result_csv(dataframe, file):
    
    if file:
        path_csv = 'dataframe_file_result.csv' 
    else:
        path_csv = 'dataframe_all_result.csv'

    dataframe.to_csv(path_csv, index=False)
    print(f"Result in {path_csv} file.")

def process_inference_file(path, nb_ocr, ocr):
    match_form, _, image = inference(path, path_models='./data/forms_ref')
    print(f"Form: {match_form}")
    img, strings, df = draw_boxes(ocr, image, match_form, nb_ocr)
    save_result_csv(df, file=True)

    return df


def process_inference_excel(path_excel, ocr, nb_files, nb_ocr):    

    df = run_all(path=path_excel, path_model='./data/forms_ref', ocr=ocr, nb_forms=nb_files, nb_ocr=nb_ocr)
    
    return df