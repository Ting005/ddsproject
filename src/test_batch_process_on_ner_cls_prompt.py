# %pip install -q -U google-genai
from google import genai
from tqdm import tqdm
import json
from helper import load_yaml_config, read_prompt
import pdb


# loading config
config = load_yaml_config('../configs/config.yaml')
api_key = config.api_keys.genimi
model_name = config.model.name
ner_prompt = read_prompt(config.prompts.ner)
cls_prompt = read_prompt(config.prompts.cls)


# Batch processing on getting news categoriesation.

if __name__ == '__main__':
	# api_key = 'AIzaSyDG6GempgUfY721G_a96KlZELzlirZyr74'
	client = genai.Client(api_key=api_key)
	
	reader = open('../data/output1.jsonl', 'r')
	lines = reader.readlines()
	reader.close()

	writer = open('../data/output1_cls.jsonl', 'a+')

	for idx, line in enumerate(tqdm(lines, total=len(lines)), start=1):
		print(idx)
		obj = json.loads(line)
		link = obj['link'].strip()
		content =  obj['content'].strip()
		query = cls_prompt.replace('{article}', content)
		# pdb.set_trace()
		response = client.models.generate_content( model=model_name, contents=query)
		print(response.text)
		instance = {'link': link, 'content': content, 'cls_resp': response.text}
		# writer.write(json.dumps(instance, ensure_ascii=False) + "\n")

		


    
        