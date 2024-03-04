import pandas as pd
import numpy as np
from PIL import Image, ImageDraw
import time
import tqdm

def extract_text_from_image(cropped_image, model, processor):

    # Convertir l'image PIL en tensor de pixels pour le modèle TrOCR
    pixel_values = processor(cropped_image, return_tensors="pt").pixel_values

    # Générer les IDs à partir du modèle
    generated_ids = model.generate(pixel_values, max_new_tokens=100)

    # Décoder les IDs en texte
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    return generated_text.strip() or ""

def draw_boxes_on_image_trocr(image, json_data, nb_ocr, model, processor):
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    elif isinstance(image, str):
        image = Image.open(image)

    draw = ImageDraw.Draw(image)
    strings = []
    data_dict = {}
    images = []
    labels_list = []
    start = time.time()
    i = 0
    for item in json_data:
        for annotation in item['annotations']:
            for result in tqdm.tqdm(annotation['result'], desc='Select boxes for ocr'):
                if result['type'] == 'labels':
                    if (i > nb_ocr):
                        break
                    value = result['value']
                    x = value['x'] * image.width / 100
                    y = value['y'] * image.height / 100
                    width = value['width'] * image.width / 100
                    height = value['height'] * image.height / 100
                    padding = 5

                    cropped = image.crop((x - padding, y - padding, x + width + padding, y + height + padding))
                    images.append(cropped)
                    labels = value['labels']
                    if labels:
                        extracted_text = extract_text_from_image(cropped, model, processor)
                        data_dict[labels[0]] = extracted_text
                    i+=1

    print(f'END TIME: {time.time() - start} secondes')
    df = pd.DataFrame([data_dict])
    return image, strings, df