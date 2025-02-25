import os

def count_inner_folders(main_folder):
    counts = {}
    for subfolder in os.listdir(main_folder):
        subfolder_path = os.path.join(main_folder, subfolder)
        if os.path.isdir(subfolder_path):
            counts[subfolder] = sum(os.path.isdir(os.path.join(subfolder_path, item)) for item in os.listdir(subfolder_path))
    return counts

# main_folder = "./parsed_cases_2"
main_folder = "./parsed_cases"
inner_folder_counts = count_inner_folders(main_folder)
print(inner_folder_counts)
