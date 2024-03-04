# check_pkl_files
# process_train
# keep_common_inliers
# save_descriptors
# load_models

import os
import time
from collections import defaultdict
import numpy as np
import cv2
import pickle
from src.superpoint.superpoint import initialize_superpoint
from src.process.process import process_form_folder

def check_pkl_files(folder_path):
    """
    Verifies whether each sub-folder in the specified directory contains at least two '.pkl' files.
    
    :param folder_path: str
        Path to the main directory.
    :return: bool
        Returns False if any sub-folder contains less than two '.pkl' files, else True.
    """
    try:
        # Iterating over each folder in the specified directory
        for form_folder in os.listdir(folder_path):
            form_folder_path = os.path.join(folder_path, form_folder)
            
            if os.path.isdir(form_folder_path):  # Checking if the path is a directory
                pkl_files_count = 0  # Counter for '.pkl' files
                
                # Iterating over each file in the sub-folder
                for filename in os.listdir(form_folder_path):
                    if filename.endswith('.pkl'):  # Checking the file extension
                        pkl_files_count += 1  # Incrementing the counter
                
                # If less than two '.pkl' files are found, return False
                if pkl_files_count < 2:
                    return False
                    
        # If every sub-folder has at least two '.pkl' files, return True
        return True
        
    except Exception as e:
        print(f"An error occurred while processing the directories: {e}")
        return False
    
def process_train(folder_path, force):
    
    if not force and check_pkl_files(folder_path) == True:
            print(f"No processing is required on the directory: {folder_path}, as it already contains at least two '.pkl' files in each sub-folder.")
    else:
        superpoint = initialize_superpoint()

        # For training
        print("==> Starting training phase...")
        start_time = time.time()
        
        for form_folder in os.listdir(folder_path):
            form_folder_path = os.path.join(folder_path, form_folder)
        
            if os.path.isdir(form_folder_path):        
                ## Superpoint
                keypoints_list, descriptors_list, desc_ref, kp_ref = process_form_folder(form_folder_path, superpoint)
            
                new_desc, new_kp = keep_common_inliers(desc_ref, descriptors_list, kp_ref, keypoints_list)
                print(new_desc.shape)
                print(new_kp.shape)
                ## Save descriptors
                save_descriptors(new_desc, new_kp, form_folder, form_folder_path)
                print('save')
        print(f"==> Training phase completed. Total time taken: {time.time() - start_time:.2f} seconds.")


def keep_common_inliers(ref_desc, desc_list, kp_ref, kp_list):
    # Initialise un histogramme pour compter les inliers pour chaque descripteur de référence
    histogram = defaultdict(int)

    # Prépare les descripteurs et les keypoints de référence pour le traitement
    # Transpose les matrices pour que les descripteurs/keypoints soient des vecteurs colonnes
    ref_kp = np.float32(kp_ref.T)
    ref_desc = np.float32(ref_desc.T)

    # Initialise le Brute Force Matcher pour les comparaisons de descripteurs
    bf = cv2.BFMatcher(cv2.NORM_L2)

    # Itère sur chaque liste de descripteurs pour trouver les correspondances avec les descripteurs de référence
    for i in range(1, len(desc_list)):
        # Effectue le matching des descripteurs en utilisant k-NN
        matches = bf.knnMatch(ref_desc, np.float32(desc_list[i].T), k=2)
        
        # Applique le test de ratio pour filtrer les bonnes correspondances
        good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]
        print(f'Number of good matches with image {i}: {len(good_matches)}')
        
        # Prépare les points pour l'estimation de l'homographie
        src_pts = np.float32([[kp_ref[0, m.queryIdx], kp_ref[1, m.queryIdx]] for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([[kp_list[i][0, m.trainIdx], kp_list[i][1, m.trainIdx]] for m in good_matches]).reshape(-1, 1, 2)
        
        # Estime l'homographie et identifie les inliers
        _, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        
        # Met à jour l'histogramme avec les descripteurs de référence qui sont inliers
        for j, m in enumerate(good_matches):
            if mask[j]:
                histogram[m.queryIdx] += 1
    
    # Trie les descripteurs de référence en fonction de leur fréquence d'apparition comme inliers
    sorted_indices = sorted(range(len(ref_desc)), key=lambda i: histogram[i], reverse=True)
    
    # Sélectionne les 1000 meilleurs descripteurs et leurs keypoints correspondants
    top_1000_desc = [ref_desc[i] for i in sorted_indices[:1000]]
    top_1000_kp = [ref_kp[i] for i in sorted_indices[:1000]]

    # Retourne les descripteurs et keypoints sélectionnés
    return np.array(top_1000_desc).T, np.array(top_1000_kp).T

def save_descriptors(descriptors, keypoints_list, form_name, form_folder_path):
    """Save descriptors to a file."""

    print(f"==> Saving descriptors for form: {form_name}...")
    start_time = time.time()

    # Create directory if it doesn't exist
    if not os.path.exists(form_folder_path):
        os.makedirs(form_folder_path)
        
    # Save Descriptors
    descriptor_file_path = os.path.join(form_folder_path, f"{form_name}_descriptors.pkl")
    with open(descriptor_file_path, 'wb') as f:
        pickle.dump(descriptors, f)
        
    # Save Keypoints
    descriptor_file_path = os.path.join(form_folder_path, f"{form_name}_keypoints.pkl")
    with open(descriptor_file_path, 'wb') as f:
        pickle.dump(keypoints_list, f)

    print(f"==> Descriptors and Keypoints saved. Time taken: {time.time() - start_time:.2f} seconds.")

def load_models(folder_path):
    print("==> Loading descriptors...")
    start_time = time.time()
    trained_models = {}
    
    for form_folder in os.listdir(folder_path):
        descriptor_model_path = os.path.join(folder_path, form_folder, f"{form_folder}_descriptors.pkl")
        
        if os.path.exists(descriptor_model_path):
            # Load Descriptors
            with open(descriptor_model_path, 'rb') as f:
                descriptors = pickle.load(f)

        keypoints_model_path = os.path.join(folder_path, form_folder, f"{form_folder}_keypoints.pkl")
        
        if os.path.exists(keypoints_model_path):
            # Load Descriptors
            with open(keypoints_model_path, 'rb') as f:
                keypoints = pickle.load(f)


        trained_models[form_folder] = {'desc': descriptors, 'kp': keypoints}
            
    print(f"==> Descriptors loaded. Time taken: {time.time() - start_time:.2f} seconds.")
    
    return trained_models