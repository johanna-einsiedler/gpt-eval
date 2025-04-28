from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import anthropic
import google.generativeai as genai
import os
import requests
from google import genai as ggenai


dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# load openai api key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def take_test(row, system_prompt_template, exam, model):

        # test_prompt = test_prompt_template.format(
        #     answer_instructions=row['answer_instructions'],
        #     answer_materials=row['answer_materials'],
        #     answer_materialscandidateonly=row['answer_materialscandidateonly'],
        #     answer_submission=row['answer_submission']
        # )

        system_prompt = system_prompt_template.format(occupation=row['occupation'])
        response = query_agent(system_prompt, exam, model)

        return response



def query_agent(system_prompt, user_prompt, model):

        if 'gemini' in model:
            #client = ggenai.Client()
            #if model in client.models.list():
            response =query_gemini(system_prompt, user_prompt, model)
            #else:
             #   response =query_gemini(system_prompt, user_prompt)

        if 'gpt' in model:
            # Retrieve the list of available models
            #client = OpenAI()
            # Extract model IDs
            #model_ids =client.models.list()
            #if model in model_ids:
            response =query_chatgpt(system_prompt, user_prompt, model)
            #else:
             #   response =query_chatgpt(system_prompt, user_prompt)
        if 'deepseek' in model:
            #client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
            #model_ids = client.models.list()
            #if model in model_ids:
            response =query_deepseek(system_prompt, user_prompt, model)
            #else:
             #   response =query_deepseek(system_prompt, user_prompt)
        if 'claude' in model:
            #client = anthropic.Anthropic()
            #model_ids = client.models.list(limit=20)
            #if model in model_ids:
            response =query_claude(system_prompt, user_prompt, model)
            #else:
             #   response =query_claude(system_prompt, user_prompt)
        try:
            return response
        except Exception as e:
            print("Model not currently available")
            return None

        


def query_gemini(system_prompt, user_prompt, model='gemini-2.0-flash-thinking-exp', temperature=0):
    """
    Queries the Gemini API with a system and user prompt.

    Args:
        row: A dictionary-like object (e.g., a Pandas Series) containing data for prompt formatting.
        system_prompt_template: A string template for the system prompt.
        test_prompt_template: A string template for the user prompt.
        model: The Gemini model to use (e.g., "gemini-pro").
        temperature: The temperature parameter for response generation.

    Returns:
        The generated response as a string, or None if an error occurs.
    """
    print("Quering Gemini: ", model)

    try:
        genai.configure(api_key=GOOGLE_API_KEY) # Ensure GOOGLE_API_KEY is defined
        model_gen = genai.GenerativeModel(model)
        
        response = model_gen.generate_content(
            contents=[system_prompt, user_prompt],
            generation_config=genai.GenerationConfig(temperature=temperature, max_output_tokens=4096)
        )

        return response.text

    except Exception as e:
        print(f"Error: {e}")
        return None

def query_deepseek(system_prompt, user_prompt, model="deepseek-chat", temperature=0):
    print("Quering DeepSeek: ", model)
    try:
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")


        
        message = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature
        )

        return message.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return None
    


def query_chatgpt(system_prompt, user_prompt, model="gpt-4o", temperature=0):
    print("Quering ChatGPT: ", model)

    try:

        client = OpenAI(
            api_key=OPENAI_API_KEY
        )

        message = client.chat.completions.create(
            messages=[
                {"role": "developer", "content": system_prompt},
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model=model,
            temperature=temperature,
            max_tokens =4096
        )
        return message.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return None

def query_claude(system_prompt, user_prompt, model="claude-3-7-sonnet-20250219", temperature=0):
    print("Querying Claude: ", model)

    try:
        client = anthropic.Anthropic(
        # defaults to os.environ.get("ANTHROPIC_API_KEY")
        api_key=ANTHROPIC_API_KEY
        )

        message = client.messages.create(
            model=model,
            max_tokens=8192,
            system = system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
        )
        out = message.content[0].text
        return out
    except Exception as e:
        print(f"Error: {e}")
        return None
