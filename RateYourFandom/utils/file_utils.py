import os

def ensure_folder(path):
    os.makedirs(path, exist_ok=True)

def project_root():
    return os.path.dirname(os.path.abspath(__file__))