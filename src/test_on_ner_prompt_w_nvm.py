import re
from openai import OpenAI
from tqdm import tqdm
import json
import pdb

from pyvis.network import Network
import networkx as nx


API_KEY = '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'


def load_prompt_template(template_path):
    """Loads the prompt template from a file."""
    with open(template_path, "r", encoding="utf-8") as file:
        return file.read()
    

def call_nim_svc(query):
    # query = "Which number is larger, 9.11 or 9.8?"
    client = OpenAI(
        base_url = "https://integrate.api.nvidia.com/v1",
        api_key = API_KEY
    )
    completion = client.chat.completions.create(
        model="meta/llama-3.3-70b-instruct", #deepseek-ai/deepseek-r1
        messages=[{
                "role": "user",
                "content": query
            }],
        temperature=0.6,
        top_p=0.7,
        max_tokens=4096,
        stream=True
    )
    response = ''
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")
            response += chunk.choices[0].delta.content
    return response


def extract_json_from_text(text):
    match = re.search(r'```json(.*?)```', text, re.DOTALL)
    if match:
        json_content = match.group(1)
        try:
            return json.loads(json_content)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format"}
    return {"error": "No JSON found in text"}


if __name__ == '__main__':
    article_text = json.load(open('../data/raw/output.json', 'r'))[0]['content']

    # Load the prompt
    template_path = "../prompts/entity_extraction.txt"
    prompt_template = load_prompt_template(template_path)
    # Format the template with dynamic values
    query = prompt_template.replace("{{ article }}", article_text)
    pdb.set_trace()
    response = call_nim_svc(query=query)
    pdb.set_trace()
