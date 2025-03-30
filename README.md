# gpt_eval

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Repo for the LLM evaluation experiments

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.


--------

## Pipeline

## Filter relevant tasks
filter_exposure.py

Default: Filter all tasks that belong to the category "Business and Financial Operations Occupations" (SOC code 13-0000), are core tasks and have been labeled as "automatable" by at least one labeler.

- Reading Task Data: The script reads task data from a TSV file (full_labelset.tsv) into a pandas DataFrame.
- Filtering by Occupation Group: It filters the task data based on the SOC code (Standard Occupational Classification), specifically for a chosen occupation group (e.g., "Business and Financial Operations Occupations").
- Merging Labels: It merges task-specific labels from various CSV files located in a specified folder. The labels are identified by a naming convention in the CSV files, and each file corresponds to a different labeler.
- Data Filtering: It applies additional filters on the DataFrame based on label values (e.g., filtering tasks with certain label values such as label_JE:1, label_MR:1).
- Core vs. Supplemental Task Filtering: If specified, the script can filter tasks based on their task type (e.g., "Core" tasks only).
Results are saved in '../data/task_lists/{occupation_group.replace(" ", "_").lower()}_{core_label}_automatable.csv'


### Generate list of required matrials
create_materials_lists.py
This script evaluates whether various occupational tasks can be assessed through a remote exam. It takes a dataset of tasks, generates AI-driven evaluations using multiple models (GPT-4o, Claude 3.7 Sonnet, GPT-3.5 Turbo, Gemini 2.0 Flash, and DeepSeek Chat), and determines:

✅ Remote Feasibility – Can the task be tested online?
✅ Required Tools – Identifies software needed (e.g., Python, Excel, Web Browser).
✅ Required Materials – Lists necessary digital assets (e.g., CSV files, PDFs, images).
✅ Practical Exam Feasibility– Is it possible to create a practical exam for the task?

How It Works:
Reads a CSV file containing a list of occupational tasks.

Generates AI-driven evaluations for each task using a structured prompt.

Saves the output (tools, materials, and feasibility assessments) in structured CSV files per model.
Results are saved in ../../data/exam_approach/material_lists/{model}/.


### Exclude tasks that do require specific materials or tools
filter_tools_materials.py

Default: exclude presentation software, image generation, images, audio files, video files and virtual labs or sandboxes

It excludes tasks that involve certain tools (e.g., presentation software, image generators) or materials (e.g., images, audio, video, virtual labs).

The script walks through a directory containing CSV files, reads each file, and checks the tasks for any that meet the exclusion criteria. It aggregates all the excluded tasks across different models and identifies the tasks that are excluded in every model. Finally, the script saves the list of these universally excluded tasks into a CSV file for further analysis or reporting.

Saves a list of ids of excluded tasks to the folder exclusion_lists.

### Build prompt parts
build_prompt_parts.py


- The script reads the list of tasks (CSV files) from a specified directory.

- It checks for tasks that need to be excluded based on certain criteria (like tools and materials).

- For each task, it generates prompts for various aspects of the exam, including:

    - Overview of the exam

    - Instructions for the candidate

    - Required materials for the exam

    - Submission requirements

    - Evaluation guide

    - Grading criteria

The results from the prompts are saved back into CSV files, where each file corresponds to a model and contains the details of the generated exam.

Result Storage: The generated exam details (prompts, answers, etc.) are saved in directories corresponding to different models (e.g., GPT-4, Claude-3_7-Sonnet). If the overwrite flag is set to False, the script ensures new tasks are appended to existing files rather than overwriting them.











