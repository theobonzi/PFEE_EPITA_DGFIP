import argparse
from src.process.train_process import process_train 
from form_recognizer import process_inference_file, process_inference_excel

def execute_preprocess(path, force=False):
    print(f"Exécution de preprocess sur {path}")
    if force:
        print("Option --force activée")
    process_train(path, force)

def execute_inference_excel(path, nb_file, nb_ocr, ocr, benchmark=False):
    if benchmark:
        print("Benchmark activé")

    ocrs = ['google', 'trocr', 'tesseract']

    assert ocr in ocrs, f"L'OCR spécifié '{ocr}' n'est pas dans la liste des OCRs autorisés: '{ocrs}'"
    print(f'OCR: {ocr}')
    process_inference_excel(path, ocr, nb_files=nb_file, nb_ocr=nb_ocr)

def execute_inference_file(path, nb_ocr, ocr, benchmark=False):
    print(f"Exécution de inference sur {path}")
    if benchmark:
        print("Benchmark activé")

    ocrs = ['google', 'trocr', 'tesseract']
    assert ocr in ocrs, f"L'OCR spécifié '{ocr}' n'est pas dans la liste des OCRs autorisés: '{ocrs}'"
    print(f'OCR: {ocr}')
    process_inference_file(path=path, nb_ocr=nb_ocr, ocr=ocr)

def parse_command_line():
    parser = argparse.ArgumentParser(description='Parser pour ligne de commande.')

    parser.add_argument('-preprocess', metavar='PREPROCESS_PATH', type=str, help='Chemin pour preprocess')
    parser.add_argument('--force', action='store_true', help='Force l\'exécution de preprocess')

    parser.add_argument('-inference_file', metavar='INFERENCE_FILE_PATH', type=str, help='Chemin pour inference file')
    parser.add_argument('-inference_excel', metavar='INFERENCE_EXCEL_PATH', type=str, help='Chemin pour inference excel')

    parser.add_argument('-ocr', metavar='OCR', type=str, default='google', help='OCR à utiliser (google or trocr or tesseract)')
    parser.add_argument('-nb_files', metavar='NB_FILES', type=int, default=1, help='Nombre de formulaires à traiter (uniquement avec inference)')
    parser.add_argument('-nb_ocr', metavar='NB_OCR', type=int, default=5, help='Nombre d\'OCR à traiter (uniquement avec inference)')

    parser.add_argument('-benchmark', action='store_true', help='Activer le benchmark (uniquement avec inference)')
    args = parser.parse_args()

    if args.force and not args.preprocess:
        parser.error("L'option --force nécessite -preprocess.")


    if (args.benchmark) and not (args.inference_file):
        parser.error("L'option -benchmark ou -nb_ocr nécessite -inference.")

    return args

def main():
    args = parse_command_line()

    if args.preprocess:
        execute_preprocess(args.preprocess, args.force)

    if args.inference_file:
        execute_inference_file(args.inference_file, args.nb_ocr, args.ocr, args.benchmark)

    if args.inference_excel:
        execute_inference_excel(args.inference_excel ,args.nb_files, args.nb_ocr, args.ocr, args.benchmark)

if __name__ == "__main__":
    main()