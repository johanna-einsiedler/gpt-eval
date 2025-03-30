import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
import numpy as np
from itertools import groupby
import itertools
import re

def read_in_material_lists(root_dir):
    # Initialize a list to hold DataFrames
    df_sum = pd.DataFrame()
    dfs = []
    models = []
    failures =pd.DataFrame()
    # Walk through all subdirectories and files in the root directory
    for root, dirs, files in os.walk(root_dir):
        for file in files:
       
            # Only process CSV files
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                model = os.path.basename(os.path.dirname(file_path))  # Get only the last directory
                print(model)
                # Read the CSV file and append it to the list of DataFrames
                df = pd.read_csv(file_path)
                material_columns = ['materials.Text', 'materials.Data',
                'materials.Images', 'materials.Audio files', 'materials.Video files',
                'materials.Virtual labs or sandbox environments']
                tool_columns =  ['tools.Coding', 'tools.Spreadsheets',\
                'tools.Text editor', 'tools.PDF viewer', 'tools.Presentation software',\
                'tools.Web Browser', 'tools.Image Generator']
                relevant_columns = material_columns + tool_columns
                #print("Number of NA observations in relevant columns: ", df[relevant_columns].apply(lambda col: ((col != 'Required') & (col != 'Not Required')).sum().max()))
                failures = pd.concat([failures,pd.Series(df[relevant_columns].apply(
                    lambda row: ((row.str.lower() != 'required') & (row.str.lower() != 'not required')).sum(), 
                    axis=0
                ), name=model)], axis=1)
                print('unique values relevant columns ', pd.unique(df[relevant_columns].values.ravel()))
                df_binary = (df[relevant_columns] =='Required').astype(int)
                #print(df_binary.shape)

                if df_sum.shape[0]==0:
                    df_sum=df_binary
                else:
                    df_sum = df_sum.add(df_binary, fill_value=0)
                model = os.path.basename(os.path.dirname(file_path))
                models.append(model)
                dfs.append(df_sum)
    df_combined = pd.concat(dfs, axis=1,  keys=models)
    df_all = pd.concat([df[['task_id','occupation']], df_sum], axis=1)

    failures.index = failures.index.str.replace('materials.', '', regex=True).str.replace('tools.', '', regex=True)

    return [ df_sum, df_combined, df_all, failures]


def overview_per_occupation(df, df_automatable, df_all, df_sum, df_combined):
    df.rename(columns={'title':'occupation'}, inplace=True)
    df = df[df['occupation'].isin(df_all['occupation'])]

    df_automatable.rename(columns={'title':'occupation'}, inplace=True)
    df_automatable = df_automatable[df_automatable['occupation'].isin(df_all['occupation'])]

    tool_columns = [col for col in df_sum.columns if col.startswith('tool')]
    material_columns = [col for col in df_sum.columns if col.startswith('material')]
    relevant_columns = [item for item in material_columns if 'other' not in item.lower()] + [item for item in tool_columns if 'other' not in item.lower()]


    multiindex_tuples = [('Tools', col.replace("tools.", "").strip()) if 'tool' in col else ('Materials', col.replace("materials.", "").strip()) for col in relevant_columns]
    
    # Get the unique values at the highest level (level_1 in this case)
    num_models = len(df_combined.columns.get_level_values(0).unique())

    counts_per_occupation = df.groupby('occupation').size()
    count_label_per_occupation = df_automatable.groupby('occupation').size()
    # subset to only have tasks with at least one 1 label
    overview_per_occupation = pd.concat([df_all['occupation'],(df_sum>=num_models/2)],axis=1).groupby('occupation').sum()
    overview_per_occupation.columns = pd.MultiIndex.from_tuples(multiindex_tuples, names=['Materials','Tools'])
    overview_per_occupation['Core tasks per occupation'] = counts_per_occupation
    #overview_per_occupation['Labeled as automatable'] = count_label_per_occupation
    overview_per_occupation['\% labeled as automatable']  = (count_label_per_occupation/counts_per_occupation*100).astype(int)
    

    overview_per_occupation = overview_per_occupation[['Core tasks per occupation','\% labeled as automatable','Materials','Tools']]
    overview_per_occupation.columns.names = [None, None]
    overview_per_occupation.index.rename('Occupation', inplace=True)

    #print(overview_per_occupation)
    begin_sideways = """\\begin{sidewaystable}

        \\centering  
        \\resizebox*{\\textheight}{!}{%


        \\begin{threeparttable}[t]
        """
    end_sideways ="""\\end{threeparttable}
}

  \\end{sidewaystable}"""
    # Convert the DataFrame to LaTeX format
    latex_code = overview_per_occupation.to_latex(
        escape=False,   # Allows LaTeX special characters like '&' to appear correctly
        multicolumn=True,  # Adds multi-column support in the output for the column names
        header=True,    # Include the header row (column labels)
        index=True,      # Include the index (row labels)
        column_format='lcc|ccccccccccccc',
        caption ='Overview of number of core tasks per category as well as the materials and tools needed.'
    )
    overall_string = begin_sideways + latex_code.replace('\\begin{table}','').replace('\\end{table}','') + end_sideways
    with open("../../results/tables/occupation_overview.tex", "w") as f:
        f.write(overall_string)

    print("LaTeX code saved to ../../results/tables/occupation_overview.tex")
def add_line(ax, xpos, ypos):
    line = plt.Line2D([ypos, ypos+ .2], [xpos, xpos], color='black', transform=ax.transAxes)
    line.set_clip_on(False)
    ax.add_line(line)

def label_len(my_index,level):
    labels = my_index.get_level_values(level)
    return [(k, sum(1 for i in g)) for k,g in groupby(labels)]

def label_group_bar_table(ax, df):
    xpos = -.2
    scale = 1./df.index.size
    for level in range(df.index.nlevels):
        pos = df.index.size
        for label, rpos in label_len(df.index,level):
            add_line(ax, pos*scale, xpos)
            pos -= rpos
            lypos = (pos + .5 * rpos)*scale
            ax.text(xpos+.1, lypos, label, ha='center', transform=ax.transAxes) 
        add_line(ax, pos*scale , xpos)
        xpos -= .2

def corr_matrix_models(df_combined):
        # Get unique higher-level groups
    group_names = df_combined.columns.get_level_values(0).unique()
    relevant_columns = df_combined.columns.get_level_values(1).unique()
    # Dictionary to store pairwise correlation matrices
    corr_matrices = []
    relevant_columns = [s.replace(" or sandbox environments","") for s in relevant_columns]# Compute pairwise correlations and stack them horizontally
    multiindex_tuples = [('Tools', col.replace("tools.", "").strip()) if 'tool' in col else ('Materials', col.replace("materials.", "").strip()) for col in relevant_columns]
    for grp1, grp2 in itertools.combinations(group_names, 2):
        df_grp1 = df_combined[grp1]
        df_grp2 = df_combined[grp2]
        
        # Compute correlation between features of the two groups
        corr_matrix = df_grp1.corrwith(df_grp2, axis=0).to_frame()
        corr_matrix.columns = [f"{grp1} \n vs. {grp2}"]  # Rename column
        corr_matrices.append(corr_matrix)

    # Combine all pairwise correlation matrices horizontally
    corr_combined = pd.concat(corr_matrices, axis=1)
    #corr_combined.index.name = None
    corr_combined.set_index(pd.MultiIndex.from_tuples(multiindex_tuples),inplace=True)
    corr_combined = corr_combined.swaplevel(0, 1).dropna(how='all')
    # Plot single heatmap
    fig = plt.figure(figsize = (15, 7))
    ax = fig.add_subplot(111)
    #plt.figure(figsize=(12, 6))
    sns.heatmap(corr_combined, annot=True, cmap="coolwarm", fmt=".2f", cbar=True)

    #Below 3 lines remove default labels
    labels = ['' for item in ax.get_yticklabels()]

    ax.set_yticklabels(labels)
    ax.set_ylabel('')

    label_group_bar_table(ax, corr_combined)
    fig.subplots_adjust(bottom=.1*corr_combined.index.nlevels)
    plt.subplots_adjust(bottom=0.2)  # Increase bottom margin
    plt.tight_layout()  # Adjust layout automatically

    plt.title("Pairwise Correlation between requirements assessments")
    save_path = "../../results/figures/correlation_requirements_models.pdf"
    plt.savefig(save_path) 
    print("saved figure to ", save_path)

def failure_table(failures):
    #print(failures)
    latex_code = failures.to_latex(
        escape=False,   # Allows LaTeX special characters like '&' to appear correctly
        #multicolumn=True,  # Adds multi-column support in the output for the column names
        header=True,    # Include the header row (column labels)
        index=True,      # Include the index (row labels)
        column_format='lcccccc',
        caption ="Number of instances where the models did not return 'Required' or 'Not Required' for the materials and tools."
    )
    with open("../../results/tables/material_tools_failure_count.tex", "w") as f:
        f.write(latex_code)
        print("LaTeX code saved to ../../results/tables/material_tools_failure_count.tex")



if __name__ == "__main__":
    
        # Define the root directory
    root_dir = '../../data/exam_approach/material_lists/'
    #df = '../../data/task_lists/business_and_financial_operations_occupations_CORE.csv'
    df_sum, df_combined, df_all, failures = read_in_material_lists(root_dir)
    failure_table(failures)
    print(df_all.shape)
    df = pd.read_csv('../../data/task_lists/business_and_financial_operations_occupations_CORE.csv')
    df_automatable = pd.read_csv('../../data/task_lists/business_and_financial_operations_occupations_CORE_automatable.csv')

    print(df.shape)
    overview_per_occupation(df, df_automatable,df_all, df_sum, df_combined)
    corr_matrix_models(df_combined)