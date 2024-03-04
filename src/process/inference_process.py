import cv2
import numpy as np
import time
import re
import os
import contextlib
import io
import pandas as pd
from src.process.process import process_single_image, resise_image, display_images, choose_good_excel, append_df_to_excel, get_paths_dict
from src.ocr.ocr_process import draw_boxes
from src.process.train_process import load_models
from src.superpoint.superpoint import initialize_superpoint
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

def find_best_match(image_path, trained_models, superpoint):
    max_matches = 0
    best_matching_form = None
    best_kp_ref = None
    best_good_matches = None

    print(f"==> Finding best matching form for image: {image_path}...")
    start_time = time.time()

    keypoints, descriptors = process_single_image(image_path, superpoint, display=False)
    descriptors = np.ascontiguousarray(descriptors)

    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)


    for form_name, model_data in trained_models.items():
        desc_ref = model_data['desc']
        kp_ref = model_data['kp']

        matches = bf.knnMatch(np.float32(descriptors).T, np.float32(desc_ref).T, k=2)
        good_matches = [m for m, n in matches if m.distance < 0.70 * n.distance]

        nb_good_matches = len(good_matches)
        print(f"{nb_good_matches} good matches found for form {form_name}.")
        
        if nb_good_matches > max_matches:
            max_matches = nb_good_matches
            best_matching_form = form_name
            best_good_matches = good_matches
            best_kp_ref = kp_ref

    print(keypoints.shape)
    print(best_kp_ref.shape)
    
    src_pts = np.float32([[keypoints[0, m.queryIdx], keypoints[1, m.queryIdx]] for m in best_good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([[best_kp_ref[0, m.trainIdx], best_kp_ref[1, m.trainIdx]] for m in best_good_matches]).reshape(-1, 1, 2)
            
    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    
    image = cv2.imread(image_path, 0)
    image = resise_image(image)

    print(best_kp_ref.shape)

    height, width = image.shape
    transformed_image = cv2.warpPerspective(image, H, (width, height))

    img_rgb = cv2.cvtColor(transformed_image, cv2.COLOR_BGR2RGB)

    print(f"==> Best matching form found. Time taken: {time.time() - start_time:.2f} seconds.")
    return best_matching_form, keypoints, img_rgb

def inference(test_image_path, path_models):
    superpoint = initialize_superpoint()
    trained_models = load_models(path_models)
    print("==> Starting inference phase...")
    start_time = time.time()

    best_matching_form, keypoints, img = find_best_match(test_image_path, trained_models, superpoint)

    print(f"The best matching form for the test image is {best_matching_form}.")
    print(f"==> Inference phase completed. Total time taken: {time.time() - start_time:.2f} seconds.")  

    return best_matching_form, keypoints, img

def run_all(path, path_model, ocr, nb_forms=20, nb_ocr=5, verbose=False):
    counter = 0

    dict_spi_path = get_paths_dict(path)

    df = None

    model = None
    processor = None
    if ocr == 'trocr':
        processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-handwritten")
        model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-handwritten")

    for spi, path_recto in dict_spi_path.items():
        if counter >= nb_forms:
            break
        print(f"=====> {counter}/{nb_forms}")
        path_verso = re.sub(r'_R\.jpg$', '_V.jpg', path_recto)

        print(spi)
        new_recto = os.path.join('../../Data/POC/', path_recto)
        new_verso = os.path.join('../../Data/POC/', path_verso)
        print(f'Recto: {path_recto} | File exist: {os.path.exists(new_recto)}')
        print(f'Recto: {path_verso} | File exist: {os.path.exists(new_verso)}')

        temp_stdout = io.StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            match_form_R, keypoints_R, image_R = inference(test_image_path=new_recto, path_models=path_model)
            match_form_V, keypoints_V, image_V = inference(test_image_path=new_verso, path_models=path_model)

        if 'recto' not in match_form_R or 'verso' not in match_form_V:
            raise ValueError("Error: Either 'recto' or 'verso' not found.")
        else:
            print('Good superpoint')        
            
        print(match_form_R)

        img_R, strings_R, df_R = draw_boxes(ocr, image_R, match_form_R, nb_ocr, model=model, processor=processor)
        img_V, strings_V, df_V = draw_boxes(ocr, image_V, match_form_V, nb_ocr, model=model, processor=processor)

        if verbose:
            display_images(img_R, img_V, title1=match_form_R, title2=match_form_V)

        df_concatenated = pd.concat([df_R.reset_index(drop=True), df_V.reset_index(drop=True)], axis=1)
        df = df_concatenated

        sheet_name = choose_good_excel(match_form_R)

        append_df_to_excel(df_concatenated, excel_path=f'./data/excel/Acquisition_{ocr}.xlsx', sheet_name=sheet_name)

        counter += 1
    return df