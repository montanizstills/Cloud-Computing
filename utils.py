import os


def get_absolute_directory_path(folder_name):
    current_dir = os.path.abspath(__file__)
    while not os.path.exists(os.path.join(current_dir, folder_name)):
        current_dir = os.path.dirname(current_dir)
    return os.path.join(current_dir, folder_name)
