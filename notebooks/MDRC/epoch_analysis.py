import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
import ast
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from scipy import stats
import numpy as np
import pandas as pd
import matplotlib.ticker as ticker
import matplotlib.lines as mlines
from adjustText import adjust_text
# current_directory = os.getcwd()

path_test_data = '../../data/exam_approach/test_results/claude-3-7-sonnet-20250219/'
path_epoch = '../../data/external/epoch_ai/'

#####
# Get scores for each occupation category
#####

# Define a dictionary with occupation categories as keys and file names as values
files_score = {
    "business_and_financial_operations": "scores_only_business_and_financial_operations_occupations.csv",
    "computer_and_mathematical": "scores_only_computer_and_mathematical_occupations.csv",
    "management": "scores_only_management_occupations.csv"
}
# Initialize an empty list to store DataFrames
dataframes = []
# Loop through the dictionary to process each file
for category, file_name in files_score.items():
    df = pd.read_csv(path_test_data + file_name)
    # Remove the 'Unnamed: 0' column
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    # Add the 'occupation_category' column
    df['occupation_category'] = category
    # Append the processed DataFrame to the list
    dataframes.append(df)

# Concatenate all DataFrames into one
all_exams = pd.concat(dataframes, ignore_index=True)
all_exams.head()

reverse_mapping = {
    'score_claude_sonnet': 'Claude 3.7 Sonnet',
    'score_chatgpt4o': 'GPT-4o',
    'score_deepseek': 'DeepSeek Chat',
    'score_gemini_flash_15': 'Gemini 1.5 Flash',
    'score_gemini_flash': 'Gemini 2.0 Flash',
    'score_claude_haiku': 'Claude 3.5 Haiku',
    'score_chatgpt35': 'GPT-3.5 Turbo',
    'score_claude_sonnet_35': 'Claude 3.5 Sonnet',
    'score_gemini_25': 'Gemini 2.5',
    'score_chatgpt_o3': 'GPT o3'
}


# # List of columns to calculate the mean for
# columns = ['score_gemini_25', 'score_gemini_flash', 'score_gemini_flash_15', 
#            'score_chatgpt_o3', 'score_chatgpt4o', 
#            'score_chatgpt35']

# # Dictionary to store the means
# means = {}

# # Loop through each column and calculate the mean
# for col in columns:
#     means[col] = all_exams[col].mean(skipna=True)

# # Print the results
# print(means)
#####
# Get models that are covered in the epoch data
#####

# Select family of models to focus on
model_family = ["GPT", "Claude",  "Gemini", "DeepSeek"]
# Later on see if we add open weights. Also, do we want to include Mistral or Grok
# model_family += ["Llama", "Qwen"]

df_model_info = pd.read_csv(path_epoch + 'notable_ai_models.csv')
df_model_info = df_model_info[df_model_info['Model'].str.contains('|'.join(model_family), case=False, na=False)]

print(df_model_info['Model'].to_list())

df_model_info[['Model', 'Training compute (FLOP)']]

df_model_benchmark = pd.read_csv(path_epoch + 'benchmark_data/benchmarks_runs.csv')
df_model_benchmark.tail(20)

model_family_lower = [model.lower() for model in model_family]

# Filter the DataFrame based on whether any keyword is in the 'model' column
df_model_benchmark = df_model_benchmark[
    df_model_benchmark['model'].str.lower().str.contains('|'.join(model_family_lower), na=False) |
    (df_model_benchmark['model'] == 'o3-2025-04-16_high')
]

'o3-2025-04-16_high' in df_model_benchmark['model'].to_list()

df_model_benchmark = df_model_benchmark.sort_values(by='model', ascending=True)
df_model_benchmark
#####
# Map our ai key to each model, first value is for benchmark the other for model info
#####

model_dict = {
    "claude-3-7-sonnet-20250219": ["claude-3-7-sonnet-20250219", "Claude 3.7 Sonnet"],
    "gpt-4o": ["gpt-4o-2024-08-06", "GPT-4o"],
    "deepseek-chat": ["DeepSeek-V3", "DeepSeek-V3"],
    "gemini-1.5-flash": ["gemini-1.5-flash-002", "Gemini 1.5 Pro"],
    "gemini-2.0-flash": ["gemini-2.0-flash-001", "NA"],
    # "claude-3-5-haiku-202410": ["claude-3-5-haiku-20241022", "Claude 3.5 Sonnet"],
    "claude-3-5-sonnet-202410": ["claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet"],
    "gpt-3.5-turbo-0125": ['gpt-3.5-turbo-0125', "GPT-3.5 Turbo"],
    "gemini-2.5-pro-preview-03-25": ["gemini-2.5-flash-preview-04-17", "NA"],
    "o3-2025-04-16": ["o3-2025-04-16_high", "NA"]
}


# Define the columns for the new DataFrame
columns = [
    "model", "Publication date", "Organization", "Organization categorization",
    "Parameters", "Training compute (FLOP)", "Training time (hours)",
    "Training compute cost (2023 USD)", "Model accessibility",
    "MATH level 5", "GPQA diamond", "OTIS Mock AIME 2024-2025",
    "FrontierMath-2025-02-28-Public", "FrontierMath-2025-02-28-Private",
    "SWE-Bench verified"
]
# Pivot df_model_benchmark to make 'task' the columns and 'Best score (across scorers)' the values
df_model_benchmark_pivot = df_model_benchmark.pivot_table(
    index='model', 
    columns='task', 
    values='Best score (across scorers)', 
    aggfunc='first'
).reset_index()

df_model_benchmark

df_model_benchmark_pivot 

# Rename the index column to 'model'
df_model_benchmark_pivot.columns.name = None  # Remove the name of the columns
df_model_benchmark_pivot = df_model_benchmark_pivot.rename_axis(None, axis=1)

df_model_benchmark_pivot

# Iterate over the model_dict
data = []
for model_key, values in model_dict.items():
    # Extract the second value from the dict list for df_model_info lookup
    model_info_key = values[1]
    # Extract the first value from the dict list for df_model_benchmark lookup
    model_benchmark_key = values[0]
    print(model_key, model_info_key, model_benchmark_key)
    
    # Get the row from df_model_info matching the model_info_key
    info_row = df_model_info[df_model_info['Model'] == model_info_key]
    
    # Get the row from the pivoted df_model_benchmark matching the model_benchmark_key
    benchmark_row = df_model_benchmark_pivot[df_model_benchmark_pivot['model'] == model_benchmark_key]
    
    # Extract the required values from df_model_info and df_model_benchmark
    row = {
        "model": model_key,
        "Publication date": info_row['Publication date'].values[0] if not info_row.empty else None,
        "Organization": info_row['Organization'].values[0] if not info_row.empty else None,
        "Organization categorization": info_row['Organization categorization'].values[0] if not info_row.empty else None,
        "Parameters": info_row['Parameters'].values[0] if not info_row.empty else None,
        "Training compute (FLOP)": info_row['Training compute (FLOP)'].values[0] if not info_row.empty else None,
        "Training time (hours)": info_row['Training time (hours)'].values[0] if not info_row.empty else None,
        "Training compute cost (2023 USD)": info_row['Training compute cost (2023 USD)'].values[0] if not info_row.empty else None,
        "Model accessibility": info_row['Model accessibility'].values[0] if not info_row.empty else None,
        "MATH level 5": benchmark_row['MATH level 5'].values[0] if not benchmark_row.empty else None,
        "GPQA diamond": benchmark_row['GPQA diamond'].values[0] if not benchmark_row.empty else None,
        "OTIS Mock AIME 2024-2025": benchmark_row['OTIS Mock AIME 2024-2025'].values[0] if not benchmark_row.empty else None,
        "FrontierMath-2025-02-28-Public": benchmark_row['FrontierMath-2025-02-28-Public'].values[0] if not benchmark_row.empty else None,
        "FrontierMath-2025-02-28-Private": benchmark_row['FrontierMath-2025-02-28-Private'].values[0] if not benchmark_row.empty else None,
        "SWE-Bench verified": benchmark_row['SWE-Bench verified'].values[0] if not benchmark_row.empty else None
    }
    
    # Append the row to the data list
    data.append(row)

# Create the new DataFrame
df_model_bench = pd.DataFrame(data, columns=columns)

# Update the publication date and FLOPs that are nor available in latest csv file (check notion from sources)
df_model_bench.loc[df_model_bench['model'] == "gemini-2.0-flash", "Publication date"] = "2025-02-05"
df_model_bench.loc[df_model_bench['model'] == "gemini-2.0-flash", "Training compute (FLOP)"] = 2.43e+25
df_model_bench.loc[df_model_bench['model'] == "gpt-3.5-turbo-0125", "Training compute (FLOP)"] = 2.58e+24
df_model_bench.loc[df_model_bench['model'] == "gpt-3.5-turbo-0125", "Training compute (FLOP)"] = 2.58e+24
df_model_bench.loc[df_model_bench['model'] == "gemini-2.5-pro-preview-03-25", "Publication date"] = "2025-03-01"
df_model_bench.loc[df_model_bench['model'] == "o3-2025-04-16", "Publication date"] = "2025-01-31"
df_model_bench.loc[df_model_bench['model'] == "gemini-2.5-pro-preview-03-25", "Training compute (FLOP)"] = 5.6e+25
df_model_bench.loc[df_model_bench['model'] == "o3-2025-04-16", "Training compute (FLOP)"] = 8e+25 # taken from https://www.lesswrong.com/posts/NXTkEiaLA4JdS5vSZ/what-o3-becomes-by-2028

df_model_bench.loc[df_model_bench['model'] == "gemini-2.0-flash", "Organization"] = 'Google DeepMind'
df_model_bench.loc[df_model_bench['model'] == "gemini-2.5-pro-preview-03-25", "Organization"] = 'Google DeepMind'
df_model_bench.loc[df_model_bench['model'] == "o3-2025-04-16", "Organization"] = 'OpenAI'


organization_markers = {
    "Anthropic": "o",  # Circle
    "OpenAI": "s",     # Square
    "Google DeepMind": "D",  # Diamond
    "DeepSeek": "^"       # Triangle
}

df_model_bench

######
# Now add the data from exams and plot
######


# plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("viridis")

# Color palette for the plots
color_palette = ['#FFBD59', '#38B6FF', '#8E3B46', '#E0777D','#739E82']


# 1. First, let's map the model names between dataframes
model_mapping = {
    'claude-3-7-sonnet-20250219': 'score_claude_sonnet',
    'gpt-4o': 'score_chatgpt4o',
    'deepseek-chat': 'score_deepseek',
    'gemini-1.5-flash': 'score_gemini_flash_15',
    'gemini-2.0-flash': 'score_gemini_flash',
    "claude-3-5-sonnet-202410": 'score_claude_sonnet_35',
    'claude-3-5-haiku-202410': 'score_claude_haiku',
    'gpt-3.5-turbo-0125': 'score_chatgpt35',
    'gemini-2.5-pro-preview-03-25': 'score_gemini_25',
    'o3-2025-04-16': 'score_chatgpt_o3'
}




# Reverse mapping for display names
reverse_mapping = {
    'score_claude_sonnet': 'Claude 3.7 Sonnet',
    'score_chatgpt4o': 'GPT-4o',
    'score_deepseek': 'DeepSeek Chat',
    'score_gemini_flash_15': 'Gemini 1.5 Flash',
    'score_gemini_flash': 'Gemini 2.0 Flash',
    'score_claude_haiku': 'Claude 3.5 Haiku',
    'score_chatgpt35': 'GPT-3.5 Turbo',
    'score_claude_sonnet_35': 'Claude 3.5 Sonnet',
    'score_gemini_25': 'Gemini 2.5',
    'score_chatgpt_o3': 'GPT o3'
}
color_palette = ['#FFBD59', '#38B6FF', '#8E3B46', '#E0777D', '#739E82']

# 2. Handle NaN values in scores more carefully
# Instead of replacing with 0, we'll use mask to ignore NaN in calculations
score_columns = [col for col in all_exams.columns if col.startswith('score_')]

# 3. Convert publication date to datetime
df_model_bench['Publication date'] = pd.to_datetime(df_model_bench['Publication date'], errors='coerce')

# Sort the model bench by publication date
df_model_bench_sorted = df_model_bench.sort_values(by='Publication date', na_position='last')

# 4. Calculate average score for each model across all tasks (ignoring NaN)
avg_scores = {}
std_scores = {}
occupation_categories = all_exams['occupation_category'].unique()

for model_name, score_col in model_mapping.items():
    # Use nanmean and nanstd to properly handle missing values
    avg_scores[model_name] = all_exams[score_col].mean(skipna=True)
    std_scores[model_name] = all_exams[score_col].std(skipna=True)

# Create dataframe with average scores and model info
avg_scores_df = pd.DataFrame(list(avg_scores.items()), columns=['model', 'avg_score'])
avg_scores_df['std_score'] = avg_scores_df['model'].map(std_scores)
avg_scores_df = pd.merge(avg_scores_df, df_model_bench[['model', 'Publication date', 'Training compute (FLOP)']], 
                         on='model', how='left')

# 5. Calculate category-specific performance metrics for each model
# Create a dataframe to hold category-specific scores
category_scores_data = []

for model_name, score_col in model_mapping.items():
    for category in occupation_categories:
        if pd.notna(category):  # Skip NaN categories
            category_data = all_exams[all_exams['occupation_category'] == category]
            
            # Calculate mean and std for this model and category (ignoring NaNs)
            mean_score = category_data[score_col].mean(skipna=True)
            std_score = category_data[score_col].std(skipna=True)
            min_score = category_data[score_col].min(skipna=True)
            max_score = category_data[score_col].max(skipna=True)
            q1_score = category_data[score_col].quantile(0.25)
            q3_score = category_data[score_col].quantile(0.75)
            
            # Only add if there are valid scores
            if not pd.isna(mean_score):
                category_scores_data.append({
                    'model': model_name,
                    'display_name': reverse_mapping.get(score_col, model_name),
                    'category': category,
                    'mean_score': mean_score,
                    'std_score': std_score,
                    'min_score': min_score,
                    'max_score': max_score,
                    'q1_score': q1_score,
                    'q3_score': q3_score,
                    'count': category_data[score_col].count()
                })

# Create dataframe from the collected data
category_scores_df = pd.DataFrame(category_scores_data)

df_model_bench

# Add publication date and FLOP info
category_scores_df = pd.merge(
    category_scores_df,
    df_model_bench[['model', 'Publication date', 'Training compute (FLOP)', 'MATH level 5', 'Organization']],
    on='model',
    how='left'
)

# 6. Update the main model benchmark dataframe with average scores
for model_name in df_model_bench['model']:
    if model_name in avg_scores:
        # Add columns for overall average score
        df_model_bench.loc[df_model_bench['model'] == model_name, 'avg_all_tasks_score'] = avg_scores[model_name]
        df_model_bench.loc[df_model_bench['model'] == model_name, 'std_all_tasks_score'] = std_scores[model_name]
        
        # Add columns for category-specific average scores
        for category in occupation_categories:
            if pd.notna(category):
                category_subset = category_scores_df[(category_scores_df['model'] == model_name) & 
                                                   (category_scores_df['category'] == category)]
                if not category_subset.empty:
                    col_name = f'avg_score_{category}'
                    df_model_bench.loc[df_model_bench['model'] == model_name, col_name] = category_subset['mean_score'].values[0]


df_model_bench

columns_of_interest = [
    "MATH level 5", "GPQA diamond", "OTIS Mock AIME 2024-2025", "FrontierMath-2025-02-28-Private",
    "avg_all_tasks_score", "avg_score_business_and_financial_operations", 
    "avg_score_computer_and_mathematical", "avg_score_management"
]

# Filter the DataFrame to include only the columns of interest
df_filtered = df_model_bench[columns_of_interest]

# Compute the correlation matrix
correlation_matrix = df_filtered.corr()

# Plot the heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", cbar=True)
plt.title("Correlation Heatmap")
plt.show()

# Define the two groups of columns
group_1 = ["avg_all_tasks_score", "avg_score_business_and_financial_operations", 
           "avg_score_computer_and_mathematical", "avg_score_management"]
group_2 = ["MATH level 5", "GPQA diamond", "OTIS Mock AIME 2024-2025", "FrontierMath-2025-02-28-Private"]

# Filter the DataFrame to include only the columns of interest
df_filtered = df_model_bench[group_1 + group_2]

# Compute the correlation matrix
correlation_matrix = df_filtered.corr()

correlation_matrix

y_labels = ["All tasks", "Business and Finance tasks", "Computer and Mathematical tasks", "Management tasks"]
x_labels = ["Math level 5", "GPQA diamond\n(PhD level science)", "OTIS\n(Math Olympiad)", "Frontier Math"]

# Select only the correlations between group_1 and group_2
correlation_subset = correlation_matrix.loc[group_1, group_2]

# Plot the heatmap
plt.figure(figsize=(10, 8))
heatmap = sns.heatmap(
    correlation_subset, 
    annot=True, 
    cmap="seismic_r",  # Red for negative, blue for positive, white for zero
    fmt=".2f", 
    cbar=True, 
    center=0,  # Center the colormap at zero
    linewidths=0.5,  # Add gridlines for better readability
    annot_kws={"fontsize": 20},
    cbar_kws={"label": "Correlation"}
)
colorbar = heatmap.collections[0].colorbar
colorbar.ax.yaxis.label.set_size(16)
colorbar.ax.tick_params(labelsize=16)

plt.xticks(ticks=range(len(x_labels)), labels=x_labels, fontsize=16, rotation=45, ha="center")
# Adjust the y-axis tick positions to move them down
ax = heatmap
y_ticks = ax.get_yticks()  # Get current y-tick positions
ax.set_yticks([tick + 0.05 for tick in y_ticks])  # Shift ticks down by 0.5
ax.set_yticklabels(y_labels, fontsize=16, va="center")  # Set labels with vertical alignment

plt.title("Correlation Between Task Exam Performance and Previous Benchmarks\n", fontsize=16)
plt.savefig('../../results/figures/correlation_task_benchmarks.png',bbox_inches='tight')
plt.show()


# 7. Get proper model ordering for plots based on publication date
models_with_dates = df_model_bench.dropna(subset=['Publication date']).copy()
model_order = models_with_dates.sort_values('Publication date')['model'].tolist()

# For models without dates, add them at the end
models_without_dates = [m for m in df_model_bench['model'] if m not in model_order and m in model_mapping]
model_order.extend(models_without_dates)

# Function to get display names
def get_display_name(model_name):
    score_col = model_mapping.get(model_name)
    if score_col:
        return reverse_mapping.get(score_col, model_name)
    return model_name

# 8. Create model display names dictionary
model_display_names = {model: get_display_name(model) for model in model_order}

# VISUALIZATION 1: Bar plot of model performance by category
def plot_category_performance():
    plt.figure(figsize=(15, 8))
    
    # Prepare data for plotting
    plot_data = []
    for model in model_order:
        for category in occupation_categories:
            if pd.notna(category):
                subset = category_scores_df[(category_scores_df['model'] == model) & 
                                           (category_scores_df['category'] == category)]
                if not subset.empty:
                    plot_data.append({
                        'model': model_display_names[model],
                        'category': category,
                        'score': subset['mean_score'].values[0]
                    })
    
    plot_df = pd.DataFrame(plot_data)
    
    # Only proceed if we have data
    if not plot_df.empty:
        # Convert to pivot format for grouped bar chart
        pivot_df = plot_df.pivot(index='model', columns='category', values='score')
        
        # Plot
        ax = pivot_df.plot(kind='bar', figsize=(15, 8), width=0.8, color=color_palette)
        
        plt.title('Model Performance by Occupation Category', fontsize=14)
        plt.xlabel('Model', fontsize=12)
        plt.ylabel('Average Score (0-100)', fontsize=12)
        plt.grid(True, alpha=0.3, axis='y')
        plt.legend(title='Occupation Category', fontsize=10)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Add value labels on bars
        for container in ax.containers:
            ax.bar_label(container, fmt='%.1f', fontsize=8)
        
        return plt
    
    return None

category_scores_df.columns

marker_legend_handles = [
    mlines.Line2D([], [], color='black', marker='o', linestyle='None', markersize=10, label='Anthropic'),
    mlines.Line2D([], [], color='black', marker='s', linestyle='None', markersize=10, label='OpenAI'),
    mlines.Line2D([], [], color='black', marker='D', linestyle='None', markersize=10, label='Google DeepMind'),
    mlines.Line2D([], [], color='black', marker='^', linestyle='None', markersize=10, label='DeepSeek')
]

# VISUALIZATION 7: Scatter performance vs time by category
def plot_scatter_performance_vs_time_by_category():
    # We'll use category-level data instead of average scores
    time_data = category_scores_df.dropna(subset=['Publication date']).copy()
    
    if time_data.empty:
        return None
    
    plt.figure(figsize=(12, 8))
    
    # Track which models we've already labeled to avoid duplicates
    labeled_models = set()
    texts = [] 
    
    # Plot each category with a different color
    categories = time_data['category'].unique()
    
    for i, category in enumerate(categories):
        category_subset = time_data[time_data['category'] == category]
        
        # Group by model to handle error bars
        models = category_subset['model'].unique()
        for model in models:
            model_data = category_subset[category_subset['model'] == model]
            
            # Determine the marker type based on the organization
            organization = model_data['Organization'].iloc[0] if not model_data.empty else "Other"
            marker = organization_markers.get(organization, "o")  # Default to circle if not found
            
            # Check if we should label this model
            should_label = model not in labeled_models
            if should_label:
                labeled_models.add(model)
            
            # Scatter plot for this category and model
            plt.scatter(
                model_data['Publication date'], 
                model_data['mean_score'],
                s=150,
                c=color_palette[i % len(color_palette)],
                marker=marker,  # Use the marker type based on the organization
                label=category.replace('_', ' ').title() if model == models[0] else "",  # Only label once per category
                alpha=0.7
            )
            
            # Add error bars for standard deviation
            plt.errorbar(
                model_data['Publication date'], 
                model_data['mean_score'],
                yerr=model_data['std_score'],
                fmt='none',
                ecolor='gray',
                capsize=5,
                alpha=0.5
            )
            
            # Add model labels, but only once per model
            if should_label:
                for _, row in model_data.iterrows():
                    text = plt.text(
                        row['Publication date'], 
                        row['mean_score'], 
                        get_display_name(row['model']),
                        fontsize=12
                    )
                    texts.append(text)  # Add text to the list for adjustment
    adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', alpha=0.5), fontsize=12)
    # Add trend lines for each category
    for i, category in enumerate(categories):
        category_subset = time_data[time_data['category'] == category]
        
        if len(category_subset) > 1:
            # Convert dates to numeric for trend line
            x_numeric = np.array([(d - pd.Timestamp('2022-01-01')).days for d in category_subset['Publication date']])
            y = category_subset['mean_score'].values
            
            # Only add trend line if we have enough data points
            if len(x_numeric) > 1:
                z = np.polyfit(x_numeric, y, 1)
                p = np.poly1d(z)
                
                # Generate points for trend line
                x_range = np.linspace(min(x_numeric), max(x_numeric), 100)
                x_dates = [pd.Timestamp('2022-01-01') + pd.Timedelta(days=int(x)) for x in x_range]
                
                plt.plot(x_dates, p(x_range), '--', color=color_palette[i % len(color_palette)], alpha=0.7)
    
    plt.xlabel('Publication Date', fontsize=14)
    plt.ylabel('Average Score by Category', fontsize=14)
    plt.title('Model Performance Over Time by Occupation Category', fontsize=16)
    
    # Format x-axis to show dates nicely
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(MonthLocator(interval=3))
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    
    # Despine - remove top and right spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    # Add legend
    # Add the marker legend
    # Add the marker legend for organizations
    organization_legend = plt.legend(handles=marker_legend_handles, title='Organization', fontsize=12, loc='lower right')

    # Add the color legend for categories
    category_legend = plt.legend(title='Occupation Category', fontsize=12, loc='upper left')

    # Ensure both legends are displayed
    plt.gca().add_artist(organization_legend)
    
    plt.tight_layout()
    
    return plt


# VISUALIZATION 8: Scatter performance vs compute by category
def plot_scatter_performance_vs_compute_by_category():
    # We'll use category-level data instead of average scores
    compute_data = category_scores_df.dropna(subset=['Training compute (FLOP)']).copy()
    
    if compute_data.empty:
        return None
    
    plt.figure(figsize=(12, 8))
    
    # Track which models we've already labeled to avoid duplicates
    labeled_models = set()
    texts = [] 
    
    # Plot each category with a different color
    categories = compute_data['category'].unique()
    
    for i, category in enumerate(categories):
        category_subset = compute_data[compute_data['category'] == category]
        
        # Group by model to handle error bars
        models = category_subset['model'].unique()
        for model in models:
            model_data = category_subset[category_subset['model'] == model]
            
            # Determine the marker type based on the organization
            organization = model_data['Organization'].iloc[0] if not model_data.empty else "Other"
            marker = organization_markers.get(organization, "o")  # Default to circle if not found
            
            # Check if we should label this model
            should_label = model not in labeled_models
            if should_label:
                labeled_models.add(model)
            
            # Scatter plot for this category and model
            plt.scatter(
                model_data['Training compute (FLOP)'], 
                model_data['mean_score'],
                s=150,
                c=color_palette[i % len(color_palette)],
                marker=marker,  # Use the marker type based on the organization
                label=category.replace('_', ' ').title() if model == models[0] else "",  # Only label once per category
                alpha=0.7
            )
            
            # Add error bars for standard deviation
            plt.errorbar(
                model_data['Training compute (FLOP)'], 
                model_data['mean_score'],
                yerr=model_data['std_score'],
                fmt='none',
                ecolor='gray',
                capsize=5,
                alpha=0.5
            )
            
            # Add model labels, but only once per model

            if should_label:
                for _, row in model_data.iterrows():
                    text = plt.text(
                        row['Training compute (FLOP)'], 
                        row['mean_score'], 
                        get_display_name(row['model']),
                        fontsize=12
                    )
                    texts.append(text)  # Add text to the list for adjustment
    adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', alpha=0.5), fontsize=12)
    plt.xlabel('Training Compute (FLOP)', fontsize=14)
    plt.ylabel('Average Score by Category', fontsize=14)
    plt.title('Model Performance vs Training Compute by Occupation Category', fontsize=16)
    
    # Log scale for x-axis since compute varies by orders of magnitude
    plt.xscale('log')
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    
    # Format x-axis to show scientific notation nicely
    formatter = ticker.LogFormatter(10, labelOnlyBase=False)
    plt.gca().xaxis.set_major_formatter(formatter)
    
    # Despine - remove top and right spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    # Add legend
    organization_legend = plt.legend(handles=marker_legend_handles, title='Organization', fontsize=12, loc='lower right')

    # Add the color legend for categories
    category_legend = plt.legend(title='Occupation Category', fontsize=12, loc='upper left')

    # Ensure both legends are displayed
    plt.gca().add_artist(organization_legend)
    
    plt.tight_layout()
    
    return plt





def analyze_correlations():
    """
    Calculate correlations, R², and p-values for model performance vs. time and vs. compute
    across different occupation categories.
    
    Returns a DataFrame with the analysis results.
    """
    results = []
    
    # Categories to analyze
    categories = category_scores_df['category'].unique()
    
    # Analyze correlation with publication date
    time_data = category_scores_df.dropna(subset=['Publication date']).copy()
    
    # Convert publication dates to numeric values (days since a reference date)
    if not time_data.empty:
        time_data['date_numeric'] = [(d - pd.Timestamp('2022-01-01')).days for d in time_data['Publication date']]
    
    # Analyze correlation with compute
    compute_data = category_scores_df.dropna(subset=['Training compute (FLOP)']).copy()
    
    # Transform compute to log scale
    if not compute_data.empty:
        compute_data['log_compute'] = np.log10(compute_data['Training compute (FLOP)'])
    
    # Analyze by category
    for category in categories:
        # Time analysis
        if not time_data.empty:
            cat_time_data = time_data[time_data['category'] == category]
            
            if len(cat_time_data) > 1:  # Need at least 2 points for correlation
                x = cat_time_data['date_numeric'].values
                y = cat_time_data['mean_score'].values
                
                # Pearson correlation
                r_time, p_time = stats.pearsonr(x, y)
                
                # Linear regression
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                r_squared_time = r_value**2
                
                # Store results
                results.append({
                    'Category': category.replace('_', ' ').title(),
                    'Metric': 'Time (Publication Date)',
                    'Correlation': r_time,
                    'R-squared': r_squared_time,
                    'p-value': p_time,
                    'Slope': slope,
                    'Intercept': intercept
                })
        
        # Compute analysis
        if not compute_data.empty:
            cat_compute_data = compute_data[compute_data['category'] == category]
            
            if len(cat_compute_data) > 1:  # Need at least 2 points for correlation
                x = cat_compute_data['log_compute'].values  # Using log scale
                y = cat_compute_data['mean_score'].values
                
                # Pearson correlation
                r_compute, p_compute = stats.pearsonr(x, y)
                
                # Linear regression
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                r_squared_compute = r_value**2
                
                # Store results
                results.append({
                    'Category': category.replace('_', ' ').title(),
                    'Metric': 'Log Training Compute (FLOP)',
                    'Correlation': r_compute,
                    'R-squared': r_squared_compute,
                    'p-value': p_compute,
                    'Slope': slope,
                    'Intercept': intercept
                })
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort by category and metric
    results_df = results_df.sort_values(['Category', 'Metric'])
    
    # Add overall correlations across all categories (pooled data)
    if not time_data.empty and len(time_data) > 1:
        x = time_data['date_numeric'].values
        y = time_data['mean_score'].values
        r_time, p_time = stats.pearsonr(x, y)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        r_squared_time = r_value**2
        
        results_df = pd.concat([results_df, pd.DataFrame([{
            'Category': 'ALL CATEGORIES',
            'Metric': 'Time (Publication Date)',
            'Correlation': r_time,
            'R-squared': r_squared_time,
            'p-value': p_time,
            'Slope': slope,
            'Intercept': intercept
        }])])
    
    if not compute_data.empty and len(compute_data) > 1:
        x = compute_data['log_compute'].values
        y = compute_data['mean_score'].values
        r_compute, p_compute = stats.pearsonr(x, y)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        r_squared_compute = r_value**2
        
        results_df = pd.concat([results_df, pd.DataFrame([{
            'Category': 'ALL CATEGORIES',
            'Metric': 'Log Training Compute (FLOP)',
            'Correlation': r_compute,
            'R-squared': r_squared_compute,
            'p-value': p_compute,
            'Slope': slope,
            'Intercept': intercept
        }])])
    
    # Format the numeric columns
    results_df['Correlation'] = results_df['Correlation'].map('{:.4f}'.format)
    results_df['R-squared'] = results_df['R-squared'].map('{:.4f}'.format)
    results_df['p-value'] = results_df['p-value'].map('{:.4f}'.format)
    results_df['Slope'] = results_df['Slope'].map('{:.6f}'.format)
    results_df['Intercept'] = results_df['Intercept'].map('{:.4f}'.format)
    
    return results_df

results_df = analyze_correlations()


results_df
# Execute all visualizations
# summary_table = generate_summary_table()
# print("Summary Statistics:")
# print(summary_table.to_string(index=False))

# Plot 1: Bar plot of model performance by category
plot1 = plot_category_performance()
plt.savefig('../../results/figures/bar_plot_performance_by_category.png', bbox_inches='tight')
plt.show()

plot7 = plot_scatter_performance_vs_time_by_category()
plt.savefig('../../results/figures/scatter_performace_vs_time_by_occcategory.png', bbox_inches='tight')
plt.show()

plot_scatter_performance_vs_compute_by_category()
plt.savefig('../../results/figures/scatter_performace_vs_compute_by_occcategory.png', bbox_inches='tight')
plt.show()
















###########
##### OLD
############



# VISUALIZATION 2: Performance over time with box plots by category
def plot_performance_over_time():
    # Filter for models with publication dates
    time_data = category_scores_df.dropna(subset=['Publication date']).copy()
    
    if time_data.empty:
        return None
    
    # Create a figure with subplots for each category
    categories = time_data['category'].unique()
    fig, axes = plt.subplots(len(categories), 1, figsize=(15, 5*len(categories)), sharex=True)
    
    if len(categories) == 1:
        axes = [axes]  # Make axes iterable if there's only one category
    
    for i, category in enumerate(categories):
        category_data = time_data[time_data['category'] == category]
        
        # Get unique publication dates
        pub_dates = sorted(category_data['Publication date'].unique())
        
        # Prepare box plot data
        boxplot_data = []
        date_labels = []
        
        for date in pub_dates:
            date_models = category_data[category_data['Publication date'] == date]
            
            for model in date_models['model'].unique():
                model_data = date_models[date_models['model'] == model]
                
                # Add model's data for this date and category
                if not model_data.empty:
                    boxplot_data.append({
                        'date': date,
                        'model': model_display_names.get(model, model),
                        'mean': model_data['mean_score'].values[0],
                        'std': model_data['std_score'].values[0],
                        'min': model_data['min_score'].values[0],
                        'max': model_data['max_score'].values[0],
                        'q1': model_data['q1_score'].values[0],
                        'q3': model_data['q3_score'].values[0]
                    })
                    date_labels.append(date)
        
        boxplot_df = pd.DataFrame(boxplot_data)
        
        if not boxplot_df.empty:
            ax = axes[i]
            
            # Create custom box plots
            for j, (_, row) in enumerate(boxplot_df.iterrows()):
                # Box plot elements
                box_color = color_palette[j % len(color_palette)]
                whisker_color = 'black'
                
                # Draw the box
                ax.fill_between([j-0.25, j+0.25], [row['q1'], row['q1']], [row['q3'], row['q3']], 
                                color=box_color, alpha=0.7)
                
                # Draw the median line
                ax.plot([j-0.25, j+0.25], [row['mean'], row['mean']], color='black', linewidth=2)
                
                # Draw the whiskers
                ax.plot([j, j], [row['min'], row['q1']], color=whisker_color, linewidth=1.5)
                ax.plot([j, j], [row['q3'], row['max']], color=whisker_color, linewidth=1.5)
                
                # Draw caps on whiskers
                ax.plot([j-0.1, j+0.1], [row['min'], row['min']], color=whisker_color, linewidth=1.5)
                ax.plot([j-0.1, j+0.1], [row['max'], row['max']], color=whisker_color, linewidth=1.5)
            

                # Set x-ticks with model names and FLOP
                # Set x-ticks with model names
                ax.set_xticks(range(len(boxplot_df)))
                ax.set_xticklabels([f"{row['model']}\n{row['date'].strftime('%Y-%m')}" 
                                for _, row in boxplot_df.iterrows()], rotation=45, ha='right')
            ax.set_title(f"Performance in {category.replace('_', ' ').title()} Category", fontsize=12)
            ax.set_ylabel('Score', fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # Set y-axis limits
            ax.set_ylim(0, 100)
    
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.3)
    fig.suptitle('Model Performance Over Time by Category', fontsize=16, y=1.02)
    
    return plt

# VISUALIZATION 3: Performance vs Training Compute (FLOP)
def plot_performance_vs_flop():
    # Filter for models with FLOP data
    flop_data = category_scores_df.dropna(subset=['Training compute (FLOP)']).copy()
    
    if flop_data.empty:
        return None
    
    # Create a figure with subplots for each category
    categories = flop_data['category'].unique()
    fig, axes = plt.subplots(len(categories), 1, figsize=(15, 5*len(categories)), sharex=True)
    
    if len(categories) == 1:
        axes = [axes]  # Make axes iterable if there's only one category
    
    for i, category in enumerate(categories):
        category_data = flop_data[flop_data['category'] == category]
        
        # Prepare box plot data
        boxplot_data = []
        
        # Group by FLOP and model
        for flop in category_data['Training compute (FLOP)'].unique():
            flop_models = category_data[category_data['Training compute (FLOP)'] == flop]
            
            for model in flop_models['model'].unique():
                model_data = flop_models[flop_models['model'] == model]
                
                # Add model's data for this FLOP and category
                if not model_data.empty:
                    boxplot_data.append({
                        'flop': flop,
                        'log_flop': np.log10(flop) if flop > 0 else 0,
                        'model': model_display_names.get(model, model),
                        'category': category,  # Add category to make identifiers unique
                        'display_name': f"{model_display_names.get(model, model)} ({category})",  # Combined name
                        'mean': model_data['mean_score'].values[0],
                        'std': model_data['std_score'].values[0],
                        'min': model_data['min_score'].values[0],
                        'max': model_data['max_score'].values[0],
                        'q1': model_data['q1_score'].values[0],
                        'q3': model_data['q3_score'].values[0]
                    })
        
        boxplot_df = pd.DataFrame(boxplot_data)
        
        if not boxplot_df.empty:
            # Sort by log_flop for proper ordering
            boxplot_df = boxplot_df.sort_values('log_flop')
            
            ax = axes[i]
            
            # Create custom box plots
            for j, (_, row) in enumerate(boxplot_df.iterrows()):
                # Box plot elements
                box_color = color_palette[j % len(color_palette)]
                whisker_color = 'black'
                
                # Draw the box
                ax.fill_between([j-0.25, j+0.25], [row['q1'], row['q1']], [row['q3'], row['q3']], 
                                color=box_color, alpha=0.7)
                
                # Draw the median line
                ax.plot([j-0.25, j+0.25], [row['mean'], row['mean']], color='black', linewidth=2)
                
                # Draw the whiskers
                ax.plot([j, j], [row['min'], row['q1']], color=whisker_color, linewidth=1.5)
                ax.plot([j, j], [row['q3'], row['max']], color=whisker_color, linewidth=1.5)
                
                # Draw caps on whiskers
                ax.plot([j-0.1, j+0.1], [row['min'], row['min']], color=whisker_color, linewidth=1.5)
                ax.plot([j-0.1, j+0.1], [row['max'], row['max']], color=whisker_color, linewidth=1.5)
            
            # Set x-ticks with model names and FLOP
            ax.set_xticks(range(len(boxplot_df)))
            ax.set_xticklabels([f"{row['model']}\n{row['log_flop']:.1f} log FLOP" 
                              for _, row in boxplot_df.iterrows()], rotation=45, ha='right')
            
            ax.set_title(f"Performance in {category.replace('_', ' ').title()} Category", fontsize=12)
            ax.set_ylabel('Score', fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # Set y-axis limits
            ax.set_ylim(0, 100)
    
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.3)
    fig.suptitle('Model Performance vs Training Compute (FLOP) by Category', fontsize=16, y=1.02)
    
    return plt

# VISUALIZATION 4: Scatter plot of performance vs Math benchmark score
def plot_performance_vs_math():
    # Filter for models with Math benchmark scores
    math_data = category_scores_df.dropna(subset=['MATH level 5']).copy()
    
    if math_data.empty:
        return None
    
    plt.figure(figsize=(12, 8))
    
    # Prepare scatter plot data
    categories = math_data['category'].unique()
    
    for i, category in enumerate(categories):
        category_subset = math_data[math_data['category'] == category]
        
        # Plot category data
        plt.scatter(
            category_subset['MATH level 5'], 
            category_subset['mean_score'],
            s=100,  # size
            c=color_palette[i % len(color_palette)],  # color
            label=category.replace('_', ' ').title(),
            alpha=0.7
        )
        
        # Add model labels
        for _, row in category_subset.iterrows():
            plt.annotate(
                get_display_name(row['model']),
                (row['MATH level 5'], row['mean_score']),
                fontsize=8,
                xytext=(5, 5),
                textcoords='offset points'
            )
    
    # Add trend line for overall data
    if len(math_data) > 1:
        z = np.polyfit(math_data['MATH level 5'], math_data['mean_score'], 1)
        p = np.poly1d(z)
        x_range = np.linspace(math_data['MATH level 5'].min(), math_data['MATH level 5'].max(), 100)
        plt.plot(x_range, p(x_range), '--k', alpha=0.5)
        
        # Calculate correlation
        corr = np.corrcoef(math_data['MATH level 5'], math_data['mean_score'])[0, 1]
        plt.text(0.05, 0.95, f'Correlation: {corr:.2f}', transform=plt.gca().transAxes)
    
    plt.xlabel('MATH Level 5 Score', fontsize=12)
    plt.ylabel('Average Task Score', fontsize=12)
    plt.title('Relationship Between Math Benchmark and Task Performance', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(title='Occupation Category')
    plt.tight_layout()
    
    return plt

# VISUALIZATION 5: Performance vs Time - Scatter with trendline
def plot_scatter_performance_vs_time():
    # Filter for models with publication dates
    time_data = avg_scores_df.dropna(subset=['Publication date']).copy()
    
    if time_data.empty:
        return None
    
    plt.figure(figsize=(12, 6))
    
    # Scatter plot
    plt.scatter(
        time_data['Publication date'], 
        time_data['avg_score'],
        s=100,
        c=color_palette[0],
        alpha=0.7
    )
    
    # Add model labels
    for _, row in time_data.iterrows():
        plt.annotate(
            get_display_name(row['model']),
            (row['Publication date'], row['avg_score']),
            fontsize=9,
            xytext=(5, 5),
            textcoords='offset points'
        )
    
    # Add error bars for standard deviation
    plt.errorbar(
        time_data['Publication date'], 
        time_data['avg_score'],
        yerr=time_data['std_score'],
        fmt='none',
        ecolor='gray',
        capsize=5
    )
    
    # Add trend line
    if len(time_data) > 1:
        # Convert dates to numeric for trend line
        x_numeric = np.array([(d - pd.Timestamp('2022-01-01')).days for d in time_data['Publication date']])
        y = time_data['avg_score'].values
        
        z = np.polyfit(x_numeric, y, 1)
        p = np.poly1d(z)
        
        # Generate points for trend line
        x_range = np.linspace(min(x_numeric), max(x_numeric), 100)
        x_dates = [pd.Timestamp('2022-01-01') + pd.Timedelta(days=int(x)) for x in x_range]
        
        plt.plot(x_dates, p(x_range), '--k', alpha=0.5)
    
    plt.xlabel('Publication Date', fontsize=12)
    plt.ylabel('Average Score Across All Tasks', fontsize=12)
    plt.title('Model Performance Over Time', fontsize=14)
    plt.grid(True, alpha=0.3)
    
    # Format x-axis to show dates nicely
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    return plt

# VISUALIZATION 6: Performance vs FLOP - Scatter with trendline
def plot_scatter_performance_vs_flop():
    # Filter for models with FLOP data
    flop_data = avg_scores_df.dropna(subset=['Training compute (FLOP)']).copy()
    
    if flop_data.empty:
        return None
    
    plt.figure(figsize=(12, 6))
    
    # Add log FLOP column
    flop_data['log_flop'] = np.log10(flop_data['Training compute (FLOP)'])
    
    # Scatter plot
    plt.scatter(
        flop_data['log_flop'], 
        flop_data['avg_score'],
        s=100,
        c=color_palette[1],
        alpha=0.7
    )
    
    # Add model labels
    for _, row in flop_data.iterrows():
        plt.annotate(
            get_display_name(row['model']),
            (row['log_flop'], row['avg_score']),
            fontsize=9,
            xytext=(5, 5),
            textcoords='offset points'
        )
    
    # Add error bars for standard deviation
    plt.errorbar(
        flop_data['log_flop'], 
        flop_data['avg_score'],
        yerr=flop_data['std_score'],
        fmt='none',
        ecolor='gray',
        capsize=5
    )
    
    # Add trend line
    if len(flop_data) > 1:
        x = flop_data['log_flop'].values
        y = flop_data['avg_score'].values
        
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        
        # Generate points for trend line
        x_range = np.linspace(min(x), max(x), 100)
        
        plt.plot(x_range, p(x_range), '--k', alpha=0.5)
        
        # Calculate correlation
        corr = np.corrcoef(x, y)[0, 1]
        plt.text(0.05, 0.95, f'Correlation: {corr:.2f}', transform=plt.gca().transAxes)
    
    plt.xlabel('Log₁₀(Training Compute FLOP)', fontsize=12)
    plt.ylabel('Average Score Across All Tasks', fontsize=12)
    plt.title('Model Performance vs Training Compute', fontsize=14)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    return plt


# VISUALIZATION 7: Scatter performance vs time by category
def plot_scatter_performance_vs_time_by_category():
    # We'll use category-level data instead of average scores
    time_data = category_scores_df.dropna(subset=['Publication date']).copy()
    
    if time_data.empty:
        return None
    
    plt.figure(figsize=(12, 8))
    
    # Plot each category with a different color
    categories = time_data['category'].unique()
    labeled_models = set()
    for i, category in enumerate(categories):
        category_subset = time_data[time_data['category'] == category]
        
        # Group by model to handle error bars
        models = category_subset['model'].unique()
        for model in models:
            model_data = category_subset[category_subset['model'] == model]
            
            should_label = model not in labeled_models
            if should_label:
                labeled_models.add(model)

            # Scatter plot for this category and model
            plt.scatter(
                model_data['Publication date'], 
                model_data['mean_score'],
                s=100,
                c=color_palette[i % len(color_palette)],
                label=category.replace('_', ' ').title() if model == models[0] else "",  # Only label once per category
                alpha=0.7
            )
            
            # Add error bars for standard deviation
            plt.errorbar(
                model_data['Publication date'], 
                model_data['mean_score'],
                yerr=model_data['std_score'],
                fmt='none',
                ecolor='gray',
                capsize=5,
                alpha=0.5
            )
            
            # Add model labels
            if should_label:
                for _, row in model_data.iterrows():
                    plt.annotate(
                        get_display_name(row['model']),
                        (row['Publication date'], row['mean_score']),
                        fontsize=9,
                        xytext=(5, 5),
                        textcoords='offset points'
                    )
    
    # Add trend lines for each category
    for i, category in enumerate(categories):
        category_subset = time_data[time_data['category'] == category]
        
        if len(category_subset) > 1:
            # Convert dates to numeric for trend line
            x_numeric = np.array([(d - pd.Timestamp('2022-01-01')).days for d in category_subset['Publication date']])
            y = category_subset['mean_score'].values
            
            # Only add trend line if we have enough data points
            if len(x_numeric) > 1:
                z = np.polyfit(x_numeric, y, 1)
                p = np.poly1d(z)
                
                # Generate points for trend line
                x_range = np.linspace(min(x_numeric), max(x_numeric), 100)
                x_dates = [pd.Timestamp('2022-01-01') + pd.Timedelta(days=int(x)) for x in x_range]
                
                plt.plot(x_dates, p(x_range), '--', color=color_palette[i % len(color_palette)], alpha=0.7)
    
    plt.xlabel('Publication Date', fontsize=12)
    plt.ylabel('Average Score by Category', fontsize=12)
    plt.title('Model Performance Over Time by Occupation Category', fontsize=14)
    # plt.grid(True, alpha=0.3)
    
    # Format x-axis to show dates nicely
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    # Add legend
    plt.legend(title='Occupation Category')
    
    plt.tight_layout()
    
    return plt


def plot_scatter_performance_vs_compute_by_category():
    # We'll use category-level data instead of average scores
    compute_data = category_scores_df.dropna(subset=['Training compute (FLOP)']).copy()
    
    if compute_data.empty:
        return None
    
    plt.figure(figsize=(12, 8))
    
    # Track which models we've already labeled to avoid duplicates
    labeled_models = set()
    
    # Plot each category with a different color
    categories = compute_data['category'].unique()
    
    for i, category in enumerate(categories):
        category_subset = compute_data[compute_data['category'] == category]
        
        # Group by model to handle error bars
        models = category_subset['model'].unique()
        for model in models:
            model_data = category_subset[category_subset['model'] == model]
            
            # Check if we should label this model
            should_label = model not in labeled_models
            if should_label:
                labeled_models.add(model)
                
            # Scatter plot for this category and model
            plt.scatter(
                model_data['Training compute (FLOP)'], 
                model_data['mean_score'],
                s=150,
                c=color_palette[i % len(color_palette)],
                label=category.replace('_', ' ').title() if model == models[0] else "",  # Only label once per category
                alpha=0.7
            )
            
            # Add error bars for standard deviation
            plt.errorbar(
                model_data['Training compute (FLOP)'], 
                model_data['mean_score'],
                yerr=model_data['std_score'],
                fmt='none',
                ecolor='gray',
                capsize=5,
                alpha=0.5
            )
            
            # Add model labels, but only once per model
            if should_label:
                for _, row in model_data.iterrows():
                    plt.annotate(
                        get_display_name(row['model']),
                        (row['Training compute (FLOP)'], row['mean_score']),
                        fontsize=12,
                        xytext=(5, 5),
                        textcoords='offset points'
                    )
                    # Only label the first instance of this model
                    break
    
    # # Add trend lines for each category
    # for i, category in enumerate(categories):
    #     category_subset = compute_data[compute_data['category'] == category]
        
    #     if len(category_subset) > 1:
    #         # Use log scale for trend line since compute is likely in orders of magnitude
    #         x = np.log10(category_subset['Training compute (FLOP)'].values)
    #         y = category_subset['mean_score'].values
            
    #         # Only add trend line if we have enough data points
    #         if len(x) > 1:
    #             # Linear fit in log space
    #             z = np.polyfit(x, y, 1)
    #             p = np.poly1d(z)
                
    #             # Generate points for trend line
    #             x_range = np.linspace(min(x), max(x), 100)
    #             compute_values = 10**x_range
                
    #             plt.plot(compute_values, p(x_range), '--', color=color_palette[i % len(color_palette)], alpha=0.7)

    
    
    plt.xlabel('Training Compute (FLOP)', fontsize=14)
    plt.ylabel('Average Score by Category', fontsize=14)
    plt.title('Model Performance vs Training Compute by Occupation Category', fontsize=16)
    
    # Log scale for x-axis since compute varies by orders of magnitude
    plt.xscale('log')
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    
    # Format x-axis to show scientific notation nicely
    import matplotlib.ticker as ticker
    formatter = ticker.LogFormatter(10, labelOnlyBase=False)
    plt.gca().xaxis.set_major_formatter(formatter)
    
    # Despine - remove top and right spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    # Add legend
    plt.legend(title='Occupation Category')
    
    plt.tight_layout()
    
    return plt

# Generate summary statistics table
def generate_summary_table():
    # Create a summary dataframe for display
    summary_data = []
    
    for model in model_order:
        model_info = df_model_bench[df_model_bench['model'] == model].iloc[0] if model in df_model_bench['model'].values else {}
        
        row = {
            'Model': model_display_names.get(model, model),
            'Publication Date': model_info.get('Publication date', np.nan),
            'Avg Score (All Tasks)': model_info.get('avg_all_tasks_score', np.nan),
            'Math Level 5': model_info.get('MATH level 5', np.nan)
        }
        
        # Add category scores
        for category in occupation_categories:
            if pd.notna(category):
                col_name = f'avg_score_{category}'
                row[f'{category.replace("_", " ").title()}'] = model_info.get(col_name, np.nan)
        
        summary_data.append(row)
    
    summary_df = pd.DataFrame(summary_data)
    
    # Format the dataframe for display
    pd.set_option('display.float_format', '{:.2f}'.format)
    
    return summary_df




df_model_bench



######
# Old plots/other ways to plot
######

plot4 = plot_performance_vs_math()
plt.show()

# plot2 = plot_performance_over_time()
# plt.show()

# plot3 = plot_performance_vs_flop()
# plt.show()
# plot5 = plot_scatter_performance_vs_time()
# plt.show()


# Create a dataframe for category scores with standard deviations
category_scores_data = []
for model, categories in category_scores.items():
    for category, score in categories.items():
        category_scores_data.append({
            'model': model,
            'category': category,
            'score': score,
            'std': category_stds[model][category]
        })
category_scores_df = pd.DataFrame(category_scores_data)
category_scores_df = pd.merge(category_scores_df, df_model_bench[['model', 'Publication date']], on='model', how='left')



# 5. Calculate average scores by occupation category
category_scores = {}
for model_name, score_col in model_mapping.items():
    category_scores[model_name] = {}
    for category in occupation_categories:
        category_scores[model_name][category] = all_exams[all_exams['occupation_category'] == category][score_col].mean()

# Create a dataframe for category scores
category_scores_data = []
for model, categories in category_scores.items():
    for category, score in categories.items():
        category_scores_data.append({
            'model': model,
            'category': category,
            'score': score
        })
category_scores_df = pd.DataFrame(category_scores_data)
category_scores_df = pd.merge(category_scores_df, df_model_bench[['model', 'Publication date']], on='model', how='left')

# 6. Function to format the y-axis of log scale plots
def format_y_axis(y, _):
    if y == 0:
        return '0'
    exponent = int(np.log10(y))
    return f'10^{exponent}'

# 7. Now let's create the visualizations

# Figure 1: Average score by model release date
plt.figure(figsize=(12, 6))
scatter = plt.scatter(avg_scores_df['Publication date'], 
                      avg_scores_df['avg_score'] * 100,  # Convert to percentage
                      s=100, 
                      alpha=0.7)

# Add model names as annotations
for i, model in enumerate(avg_scores_df['model']):
    date = avg_scores_df['Publication date'].iloc[i]
    score = avg_scores_df['avg_score'].iloc[i] * 100
    if pd.notnull(date):  # Only add labels for models with valid dates
        plt.annotate(model.split('-')[0],  # Use just the base model name
                     (date, score),
                     xytext=(5, 5),
                     textcoords='offset points',
                     fontsize=9)

plt.title('Average Model Performance vs. Release Date', fontsize=14)
plt.xlabel('Publication Date', fontsize=12)
plt.ylabel('Average Score (%)', fontsize=12)
plt.grid(True, alpha=0.3)
plt.ylim(0, 100)
plt.show()



# Figure 2: Average score by training compute
plt.figure(figsize=(12, 6))
valid_compute = avg_scores_df[avg_scores_df['Training compute (FLOP)'].notna()]

if not valid_compute.empty:
    scatter = plt.scatter(valid_compute['Training compute (FLOP)'], 
                          valid_compute['avg_score'] * 100,
                          s=100, 
                          alpha=0.7)
    
    # Add model names as annotations
    for i, model in enumerate(valid_compute['model']):
        compute = valid_compute['Training compute (FLOP)'].iloc[i]
        score = valid_compute['avg_score'].iloc[i] * 100
        plt.annotate(model.split('-')[0],
                     (compute, score),
                     xytext=(5, 5),
                     textcoords='offset points',
                     fontsize=9)
    
    plt.title('Average Model Performance vs. Training Compute', fontsize=14)
    plt.xlabel('Training Compute (FLOP) - Log Scale', fontsize=12)
    plt.ylabel('Average Score (%)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 100)
    plt.xscale('log')
    
    # Format x-axis for log scale
    plt.gca().xaxis.set_major_formatter(FuncFormatter(format_y_axis))
    plt.tight_layout()

plt.close()


plt.figure(figsize=(15, 8))

# Get models with dates for proper ordering
models_with_dates = avg_scores_df.dropna(subset=['Publication date'])
model_order = models_with_dates.sort_values('Publication date')['model'].tolist()

# For models without dates, add them at the end
models_without_dates = [m for m in avg_scores_df['model'] if m not in model_order]
model_order.extend(models_without_dates)

# Handle case where some models might be missing (robust plotting)
available_models = category_scores_df['model'].unique()
model_order = [m for m in model_order if m in available_models]

# Get all categories
all_categories = category_scores_df['category'].unique()

# Reshape data for better plotting
plot_data = pd.pivot_table(
    category_scores_df,
    values='score',
    index='model',
    columns='category'
).reset_index()

# Reorder based on publication date
plot_data['model_order'] = plot_data['model'].map({m: i for i, m in enumerate(model_order)})
plot_data = plot_data.sort_values('model_order').drop('model_order', axis=1)

# Plot
ax = plot_data.set_index('model').loc[model_order].plot(
    kind='bar',
    figsize=(15, 8),
    width=0.8
)

plt.title('Model Performance by Occupation Category', fontsize=14)
plt.xlabel('Model', fontsize=12)
plt.ylabel('Average Score (0-1)', fontsize=12)
plt.grid(True, alpha=0.3, axis='y')
plt.legend(title='Occupation Category', fontsize=10)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

plt.show()


# Figure 4: Scatter plot of scores by task colored by occupation category
plt.figure(figsize=(15, 10))

# Melt the dataframe to get it in the right format for a scatter plot
melted_scores = pd.melt(
    all_exams,
    id_vars=['task_id', 'occupation_category', 'occupation', 'task_description'],
    value_vars=score_columns,
    var_name='score_column',
    value_name='score'
)

# Map score columns back to model names
reverse_mapping = {v: k for k, v in model_mapping.items()}
melted_scores['model'] = melted_scores['score_column'].map(reverse_mapping)

# Merge with model bench to get publication dates
melted_scores = pd.merge(
    melted_scores,
    df_model_bench[['model', 'Publication date', 'MATH level 5']],
    on='model',
    how='left'
)

# Create a scatter plot for tasks with valid dates
valid_data = melted_scores.dropna(subset=['Publication date'])

# Create a color map for categories
categories = valid_data['occupation_category'].unique()
colors = sns.color_palette("husl", len(categories))
category_color = {cat: color for cat, color in zip(categories, colors)}

# Plot each category with a different color
for category in categories:
    category_data = valid_data[valid_data['occupation_category'] == category]
    plt.scatter(
        category_data['Publication date'],
        category_data['score'] * 100,  # Convert to percentage
        alpha=0.6,
        label=category,
        color=category_color[category],
        s=50
    )

plt.title('Task Scores by Model Publication Date', fontsize=14)
plt.xlabel('Publication Date', fontsize=12)
plt.ylabel('Task Score (%)', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend(title='Occupation Category')
# plt.ylim(0, 100)

# Format x-axis to display dates properly
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()



# Figure 5: Correlation between MATH benchmark and task performance
plt.figure(figsize=(12, 8))

# Get data with valid MATH scores
math_data = melted_scores.dropna(subset=['MATH level 5'])

if not math_data.empty:
    # For each category, plot separately
    for category in categories:
        category_data = math_data[math_data['occupation_category'] == category]
        plt.scatter(
            category_data['MATH level 5'] * 100,  # Convert to percentage
            category_data['score'] * 100,
            alpha=0.6,
            label=category,
            color=category_color[category],
            s=50
        )

    # Add a linear regression line for all data
    all_x = math_data['MATH level 5'] * 100
    all_y = math_data['score'] * 100
    
    # Only add regression if we have enough data points
    if len(all_x) > 1:
        m, b = np.polyfit(all_x, all_y, 1)
        plt.plot(all_x, m*all_x + b, color='black', linestyle='--', alpha=0.7)
        
        # Calculate correlation
        correlation = np.corrcoef(all_x, all_y)[0, 1]
        plt.text(0.05, 0.95, f'Correlation: {correlation:.2f}', 
                 transform=plt.gca().transAxes, fontsize=10,
                 verticalalignment='top')

    plt.title('Task Performance vs. MATH Level 5 Benchmark', fontsize=14)
    plt.xlabel('MATH Level 5 Score (%)', fontsize=12)
    plt.ylabel('Task Score (%)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(title='Occupation Category')
    # plt.xlim(0, 100)
    # plt.ylim(0, 100)
    plt.tight_layout()
    plt.show()



# Figure 6: Heatmap of model performance across occupation categories
plt.figure(figsize=(14, 8))

# Create a pivot table for the heatmap
heatmap_data = category_scores_df.pivot(index='model', columns='category', values='score')

# Order models by publication date where available
ordered_models = []
for model in model_order:
    if model in heatmap_data.index:
        ordered_models.append(model)

heatmap_data = heatmap_data.loc[ordered_models]

# Plot the heatmap
sns.heatmap(heatmap_data * 100, annot=True, fmt='.1f', cmap='viridis', 
            linewidths=.5, cbar_kws={'label': 'Average Score (%)'})

plt.title('Model Performance Across Occupation Categories', fontsize=14)
plt.xlabel('Occupation Category', fontsize=12)
plt.ylabel('Model', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()




# Figure 7: Performance improvement over time
plt.figure(figsize=(14, 7))

# Get earliest model as baseline
earliest_model = df_model_bench_sorted.iloc[0]['model'] if not df_model_bench_sorted.empty else None

if earliest_model is not None and earliest_model in reverse_mapping.values():
    # Find the corresponding score column
    earliest_score_col = next((k for k, v in reverse_mapping.items() if v == earliest_model), None)
    
    if earliest_score_col is not None:
        # Calculate improvement for each model compared to earliest
        improvement_data = []
        
        for model, score_col in model_mapping.items():
            # Skip the earliest model itself
            if model == earliest_model:
                continue
                
            # Get average scores for both models
            earliest_scores = all_exams[earliest_score_col]
            current_scores = all_exams[score_col]
            
            # Calculate improvement (in percentage points)
            improvements = current_scores - earliest_scores
            
            # Add to our dataset
            for category in occupation_categories:
                category_improvements = improvements[all_exams['occupation_category'] == category]
                improvement_data.append({
                    'model': model,
                    'category': category,
                    'improvement': category_improvements.mean() * 100  # Convert to percentage points
                })
        
        if improvement_data:
            # Create dataframe
            improvement_df = pd.DataFrame(improvement_data)
            
            # Add publication dates
            improvement_df = pd.merge(
                improvement_df,
                df_model_bench[['model', 'Publication date']],
                on='model',
                how='left'
            )
            
            # Sort by publication date
            improvement_df = improvement_df.sort_values('Publication date', na_position='last')
            
            # Plot
            pivot_improvement = improvement_df.pivot(index='model', columns='category', values='improvement')
            
            ax = pivot_improvement.plot(kind='bar', figsize=(14, 7), width=0.8)
            
            plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            plt.title(f'Performance Improvement Compared to {earliest_model.split("-")[0]}', fontsize=14)
            plt.xlabel('Model', fontsize=12)
            plt.ylabel('Improvement (percentage points)', fontsize=12)
            plt.grid(True, alpha=0.3, axis='y')
            plt.legend(title='Occupation Category', fontsize=10)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()



# Overall average scores (table format)
print("Overall Average Scores by Model:")
model_avg_scores = avg_scores_df.sort_values('avg_score', ascending=False)[['model', 'avg_score']]
model_avg_scores['avg_score'] = model_avg_scores['avg_score'] * 100  # Convert to percentage
print(model_avg_scores.to_string(index=False, float_format=lambda x: f'{x:.2f}%'))
print("\n")

# Average scores by category (table format)
print("Average Scores by Occupation Category:")
for category in occupation_categories:
    print(f"\n{category.replace('_', ' ').title()}:")
    cat_scores = category_scores_df[category_scores_df['category'] == category]
    cat_scores = cat_scores.sort_values('score', ascending=False)[['model', 'score']]
    cat_scores['score'] = cat_scores['score'] * 100  # Convert to percentage
    print(cat_scores.to_string(index=False, float_format=lambda x: f'{x:.2f}%'))

# Calculate year-over-year improvement
if not df_model_bench_sorted.empty:
    print("\nYear-over-Year Improvement:")
    for category in occupation_categories:
        yearly_data = category_scores_df[category_scores_df['category'] == category].copy()
        yearly_data['year'] = yearly_data['Publication date'].dt.year
        
        # Filter out NaN years
        yearly_data = yearly_data.dropna(subset=['year'])
        
        if not yearly_data.empty:
            yearly_avg = yearly_data.groupby('year')['score'].mean()
            
            if len(yearly_avg) > 1:
                years = sorted(yearly_data['year'].unique())
                for i in range(1, len(years)):
                    current_year = years[i]
                    prev_year = years[i-1]
                    
                    if prev_year in yearly_avg.index and current_year in yearly_avg.index:
                        improvement = (yearly_avg[current_year] - yearly_avg[prev_year]) * 100
                        print(f"{category.replace('_', ' ').title()}: {prev_year} to {current_year}: {improvement:.2f} percentage points")


df_model_info[df_model_info['Model'] == "GPT-3.5 Turbo"]

new_df

# Display the new DataFrame
print(new_df)
# Create the new DataFrame
new_df = pd.DataFrame(data, columns=columns)

# Display the new DataFrame
print(new_df)


df_model_benchmark

df_model_info.columns

df_model_benchmark['task'].unique()
df_model_info

'Publication date', 'Organization', 'Organization categorization',
'Parameters'
'Training compute (FLOP)'
'Training time (hours)'
'Training compute cost (2023 USD)'
'Model accessibility',

df_model_benchmark

'MATH level 5', 'GPQA diamond', 'OTIS Mock AIME 2024-2025',
'FrontierMath-2025-02-28-Public',
'FrontierMath-2025-02-28-Private', 'SWE-Bench verified'

print(df_model_benchmark['model'].unique())


df_model_info.columns

df_model_info['Training compute (FLOP)']

df_model_benchmark = pd.read_csv(path_epoch + 'benchmark_data/benchmarks_runs.csv')

df_model_benchmark.columns

df_model_benchmark['model']

keywords = ["gpt", "claude", "llama", "qwen grok", "gemini", "deepseek"]

# Filter the DataFrame based on whether any keyword is in the 'model' column
df_model_benchmark = df_model_benchmark[
    df_model_benchmark['model'].str.lower().str.contains('|'.join(keywords), na=False)
]

df_model_benchmark = df_model_benchmark.sort_values(by='model', ascending=True)

print(df_model_benchmark['model'].unique())

# Display the sorted DataFrame
print(df_model_benchmark)


'claude-3-7-sonnet-20250219' in filtered_benchmark['model'].to_list()
'gpt-4o' in filtered_benchmark['model'].to_list()
'gemini-1.5-flash' in filtered_benchmark['model'].to_list()
'gemini-1.5-flash' in filtered_benchmark['model'].to_list()
'claude-3-5-haiku-202410' in filtered_benchmark['model'].to_list()
'gpt-3.5-turbo-0125' in filtered_benchmark['model'].to_list()

print(filtered_benchmark['model'].to_list())

df_model_info.columns

