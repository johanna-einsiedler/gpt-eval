import pandas as pd
import os
from collections import Counter

# Main script entry point
if __name__ == "__main__":

    # Determine the path to the data directory from command-line arguments (if provided), or set a default path
    if len(sys.argv) > 1:
        path_to_data = sys.argv[1]
    else:
        path_to_data = '../../data/exam_approach/material_lists/'
    
    # Check whether we should overwrite the existing files (default is True)
    if len(sys.argv) > 2:
        overwrite = sys.argv[3]
    else:
        overwrite = True

    # List of tools and materials to exclude
    exclusion_tools = ['Presentation software', 'Image Generator']
    exclusion_tools = ['tools.' + item for item in exclusion_tools]  # Modify tool names to match the column names
    
    exclusion_materials = ['Images', 'Audio files', 'Video files', 'Virtual labs or sandbox environments']
    exclusion_materials = ['materials.' + item for item in exclusion_materials]  # Modify material names to match the column names

    excluded_tasks = []  # List to store tasks that need to be excluded
    models = []  # List to store model names (folders)

    # Walk through all subdirectories and files in the root directory
    for root, dirs, files in os.walk(path_to_data):
        for file in files:
            # Only process CSV files
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)  # Get the full file path
                
                # Get the name of the model by extracting the last directory in the file path
                model = os.path.basename(os.path.dirname(file_path))  
                models.append(model)  # Add the model name to the list of models

                # Read the CSV file into a DataFrame
                df = pd.read_csv(file_path)
                print('Overall ', df.shape[0], ' tasks in the data')  # Print the number of tasks in the file

                # Filter out tasks based on the exclusion tools
                excluded_ids = list(df.loc[(df[exclusion_tools] == 'Required').sum(axis=1) >= 1, 'task_id'])
                print('After filtering exclusion tools ', len(excluded_ids), ' tasks excluded')

                # Further filter out tasks based on the exclusion materials
                excluded_ids = excluded_ids + list(df.loc[(df[exclusion_materials] == 'Required').sum(axis=1) >= 1, 'task_id'])
                excluded_ids = list(set(excluded_ids))  # Remove duplicates
                print('After filtering exclusion materials ', len(excluded_ids), ' tasks excluded')

                # Add the excluded tasks to the main excluded task list
                excluded_tasks = excluded_tasks + excluded_ids

    # Count the number of times each task has been excluded across all models
    count_exclusion = Counter(excluded_tasks)

    # Filter to keep only the tasks that have been excluded in all models
    exclusion_list_final = [key for key, value in count_exclusion.items() if value == len(models)]
    
    # Output the number of models processed and the number of tasks excluded
    print(len(models))
    print('Excluded ', len(exclusion_list_final), ' tasks')

    # Save the list of excluded tasks to a CSV file
    pd.DataFrame(exclusion_list_final).to_csv('../../data/exam_approach/exclusion_lists/presentation_image_audio_video_virtual_all.csv')

