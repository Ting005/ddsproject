import json
from helper import correct_json_errors
import pdb
from tqdm import tqdm

# post processing cls / ner responses.


if __name__ == '__main__':
    error_formated_cnt = 0
    with open('../data/raw/output1_ner.jsonl', 'r') as reader:
        for line in tqdm(reader.readlines()):
            obj = json.loads(line)
            ner = obj['ner_resp'].replace('```json', '').replace('```', '').strip()
            # print(ner)
            parsed_json = correct_json_errors(ner)
            if parsed_json:
                # pdb.set_trace
                print(parsed_json['news_source']['publish_date'])
                # print(json.dumps(parsed_json, indent=4))
                # pdb.set_trace()
            else:
                error_formated_cnt += 1

    print(error_formated_cnt)
