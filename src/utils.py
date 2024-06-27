import sys
import os
import dill
import pickle

from src.exception import CustomException

def save_object(file_path, save_obj):
    try:
        dir_path=os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "wb") as file:
            dill.dump(save_obj, file)
    
    except Exception as e:
        raise CustomException(e, sys)

def load_object(file_path):
    try:
        with open(file_path, "rb") as file:
            return pickle.load(file)
    
    except Exception as e:
        raise CustomException(e, sys)