import streamlit as st
from src.process.train_process import process_train
from form_recognizer import process_inference_file, process_inference_excel
from src.benchmark.benchmarking import run_bench
import tempfile
import os
import threading

def interface():
    st.title("Interface de Traitement et Inférence")

    st.header("Benchmark")
    results_path = "./results"
    if check_files_in_directory(results_path):
        if st.button("Lancer Benchmark"):

            threading.Thread(target=run_dash_server, daemon=True).start()
            dash_url = "http://localhost:8080"
            st.markdown(f"Benchmark lancé! [Ouvrez ici]({dash_url}).")
    else:
        st.write("Aucun fichier de résultat trouvé pour le benchmark.")

    # Section Prétraitement
    st.header("Prétraitement")
    preprocess_path = st.text_input("Chemin pour preprocess:")
    force = st.checkbox("Force l'exécution de preprocess")

    if st.button("Exécuter Prétraitement"):
        execute_preprocess(preprocess_path, force)

    # Section Inférence (Fichier)
    st.header("Inférence - Fichier")
    inference_file_path = st.file_uploader("Chemin pour inference file:", type=['png', 'jpg', 'jpeg'])
    ocr_file = st.selectbox("OCR à utiliser:", ['google', 'trocr', 'tesseract'], key='ocr_file')
    nb_ocr_file = st.number_input("Nombre d'OCR à traiter (fichier):", min_value=1, value=5)
    benchmark_file = st.checkbox("Activer le benchmark (fichier)")

    if st.button("Exécuter Inférence (Fichier)"):
        execute_inference_file(inference_file_path, nb_ocr_file, ocr_file, benchmark_file)

    # Section Inférence (Excel)
    st.header("Inférence - Excel")
    inference_excel_path = st.file_uploader("Chemin pour inference excel:", type=['xlsx', 'xls', 'ods', 'csv'])

    ocr = st.selectbox("OCR à utiliser:", ['google', 'trocr', 'tesseract'], key='ocr_excel')
    nb_files_excel = st.number_input("Nombre de formulaires à traiter (Excel):", min_value=1, value=1)
    nb_ocr_excel = st.number_input("Nombre d'OCR à traiter (Excel):", min_value=1, value=5)
    benchmark_excel = st.checkbox("Activer le benchmark (Excel)")

    if st.button("Exécuter Inférence (Excel)"):
        execute_inference_excel(inference_excel_path, nb_files_excel, nb_ocr_excel, ocr, benchmark_excel)

def run_dash_server():
    os.system('python src/benchmark/dash_benchmarks.py')

def check_files_in_directory(directory):
    return any(os.path.isfile(os.path.join(directory, f)) for f in os.listdir(directory))

def execute_preprocess(path, force=False):
    st.write(f"Exécution de preprocess sur {path}")
    if force:
        st.write("Option --force activée")
    process_train(path, force)

def execute_inference_excel(path_excel, nb_files, nb_ocr, ocr, benchmark=False):
    if benchmark:
        st.write("Benchmark activé")
    df = process_inference_excel(path_excel, ocr, nb_files, nb_ocr)
    print(df)
    st.dataframe(df)

    acquisition_path = './data/excel/Acquisition.xlsx'
    acquisition_ods_path = './data/excel/Acquisition.ods'
    os.system(f'libreoffice --headless --convert-to ods {acquisition_path} --outdir ./data/excel')

    run_bench('./data/excel/verite_terrain.ods', './data/excel/Acquisition.ods')
    run_dash_server()

def execute_inference_file(uploaded_file, nb_ocr, ocr, benchmark=False):
    if uploaded_file is not None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)

            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.write(f"Exécution de inference sur le fichier {temp_file_path}")
            if benchmark:
                st.write("Benchmark activé")

            df = process_inference_file(temp_file_path, nb_ocr, ocr)
            st.dataframe(df)
    else:
        st.error("Aucun fichier fourni.")

if __name__ == "__main__":
    interface()
