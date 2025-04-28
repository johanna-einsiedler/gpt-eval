import numpy as np
import pandas as pd
import openpyxl 
import os

gpts_path = '../data/external/gpts-are-gpts/'
soc_path = '../data/external/soc_data/'

def read_tsv(path):
    """
    Reads a TSV (Tab-Separated Values) file and returns a pandas DataFrame.
    
    Parameters:
    path (str): Path to the TSV file.
    
    Returns:
    pd.DataFrame: The loaded DataFrame.
    """
    return pd.read_csv(path, delimiter="\t")


def filter_dataframe(df, conditions, condition_type=None):
    """
    Filters a DataFrame based on multiple column conditions.
    
    Parameters:
    df (pd.DataFrame): The DataFrame to filter.
    conditions (dict): A dictionary where keys are column names and values are filter values (single value or list).
    condition_type (str, optional): Determines how conditions are combined:
        - None (default): Uses OR logic (at least one condition must be met).
        - 'strict': Uses AND logic (all conditions must be met).
    
    Returns:
    pd.DataFrame: The filtered DataFrame.
    """
    if not conditions:
        return df  # Return the original DataFrame if no conditions are provided

    condition_list = []

    for col, val in conditions.items():
        if isinstance(val, list):
            condition = df[col].isin(val)
        else:
            condition = df[col] == val
        condition_list.append(condition)

    if condition_type == 'strict':
        final_condition = condition_list[0]
        for cond in condition_list[1:]:
            final_condition &= cond  # AND logic (all conditions must be met)
    else:
        final_condition = condition_list[0]
        for cond in condition_list[1:]:
            final_condition |= cond  # OR logic (at least one condition must be met)

    return df[final_condition]


def filter_occupation_group(df, occupation_group):
    """
    Filters tasks based on occupation group using SOC codes.
    
    Parameters:
    df (pd.DataFrame): The DataFrame containing task data.
    occupation_group (str): The occupation group to filter for.
    
    Returns:
    pd.DataFrame: Filtered DataFrame containing tasks for the specified occupation group.
    """
    print(f"Filtering for occupation group: {occupation_group}")
    
    # Extract the first two digits of SOC codes for higher-level categorization
    df['SOC-2digit'] = df['O*NET-SOC Code'].astype(str).str.split('-').str[0]
    
    # Load SOC code definitions
    soc = pd.read_excel(soc_path + "soc_2018_definitions.xlsx")
    
    # Filter to only major SOC categories
    soc = soc[soc['SOC Group'] == 'Major']
    soc['SOC-2digit'] = soc['SOC Code'].astype(str).str.split('-').str[0]
    # Merge occupation data
    df = df.merge(soc, how='left', on='SOC-2digit')
    df.drop(['SOC Definition','SOC Group','SOC Code'], axis=1, inplace=True)

    # Filter for the specific occupation group
    df = df[df['SOC Title'] == occupation_group]
    print(f"Resulting DataFrame contains {df.shape[0]} tasks")

    df.rename(columns={'O*NET-SOC Code': 'soc_code', 'Task ID': 'task_id', 'Task': 'task','Task Type':'task_type',\
                       'Title':'title'}, inplace=True)
    
    print(" There are ", len(df['title'].unique()), " occupations in this group.")
    print("There are ", df.shape[0], " task pertaining to ", occupation_group)
    print("On average an occupation has ", df['title'].value_counts().mean(), ' tasks listed.')
    print("The minimum number of tasks is ", df['title'].value_counts().min())
    print("The maximum number of tasks is ", df['title'].value_counts().max())
    print("Share of Core vs. Supplemental tasks ", df['task_type'].value_counts()/df.shape[0])
    return df

def get_labels(df, folder_path):
    """
    Merges label data from CSV files in a specified folder into a given DataFrame.

    This function iterates over all files in `folder_path`, extracts a labeler name 
    from each filename (assuming it's the last part of the filename before the extension),
    and merges label data into `df` based on the 'task_id' column.

    Parameters:
    -----------
    df : pd.DataFrame
        The main DataFrame containing 'task_id' to merge labels into.
    
    folder_path : str
        The path to the folder containing CSV files with label data.

    Returns:
    --------
    pd.DataFrame
        The updated DataFrame with new label columns added.

    Notes:
    ------
    - Assumes that CSV filenames follow a naming pattern where the last part before 
      the `.csv` extension represents the labeler name (e.g., `file_MC.csv` → label column `label_MC`).
    - Each CSV file must contain at least the columns: 'task_id' and 'label_<labeler_name>'.
    - Uses a left join to merge labels, keeping all rows from `df` and adding available labels.
    - If a file cannot be read, it is skipped.

    Example Usage:
    --------------
    >>> df_main = pd.DataFrame({'task_id': [1, 2, 3]})
    >>> updated_df = get_labels(df_main, "path/to/label_files")
    """
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path) and file_path.endswith('.csv'):  # Ensure it's a valid CSV file
            try:
                # Extract filename without extension
                filename = os.path.basename(file_path).split('.')[0]
                
                # Extract the last part of the filename as labeler name
                labeler_name = filename.split('_')[-1]

                print('Reading:', file_path)
                labels = pd.read_csv(file_path)
        
                # Merge label data into the main DataFrame
                df = df.merge(labels[['task_id', f'label_{labeler_name}']], how='left', on='task_id')

            except Exception as e:
                print(f"Skipping {filename} due to error: {e}")
                continue 

    return df

if __name__ == "__main__":
    # Define filtering criteria
    #occupation_group = "Business and Financial Operations Occupations"
    #occupation_group = "Legal Occupations"
    occupation_group ="Architecture and Engineering Occupations"

    #condition_type = None  # Use 'strict' for AND filtering
    #condition_label = 'AND' if condition_type else 'OR'
    #label_dict = {'label_JE':1,'label_MR':1}
    core_only = True


    df = read_tsv('../data/external/gpts-are-gpts/full_labelset.tsv')
    # drop unnecessary columns
    #df.drop(['human_exposure_agg','gpt4_exposure','gpt4_exposure','gpt_3_relevant','gpt4_automation', 'alpha','beta','gamma','automation','human_labels'],axis=1,inplace=True)
    #print(df.columns)

    # Apply filters
    df = filter_occupation_group(df, occupation_group=occupation_group)
    print("There are ", df.shape[0], " tasks within ", occupation_group)
    df.to_csv(f'../data/task_lists/{occupation_group.replace(" ", "_").lower()}.csv')

    core_label = 'CORE' if core_only else ''
    # filter core vs. supplemental
    if core_only:
        df=df[df['task_type'] =='Core']
        print("There are ", df.shape[0]," CORE tasks within ", occupation_group)

    save_path = f'../data/task_lists/{occupation_group.replace(" ", "_").lower()}_{core_label}.csv'
    df.to_csv(save_path, index=False)


    # # # read in labels & filter exposure
    # folder_path ='../data/manual_automation_labels/'
    # df = get_labels(df, folder_path)
    # df = filter_dataframe(df, label_dict, condition_type)
    # print("There are ", df.shape[0]," tasks with the desired exposure scores within ", occupation_group)


    # # # Save the filtered DataFrame as CSV
    # save_path = f'../data/task_lists/{occupation_group.replace(" ", "_").lower()}_{core_label}_automatable.csv'
    # df.to_csv(save_path, index=False)
    # print(f"Saved to {save_path}")
