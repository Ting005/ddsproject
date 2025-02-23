# Install required package
# %pip install -q -U google-genai

from google import genai
from tqdm import tqdm
import json
import pdb

# Batch processing for extracting key entities and relationships (triplets) from news articles

def load_data(file_path):
    """Loads JSON lines from a file."""
    with open(file_path, 'r') as file:
        return file.readlines()

def save_data(file_path, data):
    """Appends JSON lines to a file."""
    with open(file_path, 'a+') as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")

QUERY_PROMPT = '''
  ### Task: Adverse News Screening for Financial Crime Surveillance  
  
  Your objective is to extract and structure key financial crime intelligence from a news article by performing **entity disambiguation, relationship extraction**, and **summary generation** while capturing **news source metadata**.  

  ---  

  ### Instructions:  
  
  #### 1. Entity Standardization  
  
  **Individuals:**  
  - Resolve ambiguities using contextual clues (e.g., "John Smith (CTO of StartupX)" vs. "John Smith (Senator)").  
  - Standardize names to a **canonical form** (e.g., "Dr. Smith" → "John Smith").  
  - Maintain a **mentions array** for all detected name variations.  
  
  **Organizations:**  
  - Normalize aliases to official names (e.g., "MSFT" → "Microsoft").  
  - Identify **parent-subsidiary relationships** where applicable.  
  
  **Amounts & Transactions:**  
  - Extract all **monetary expressions** (e.g., "$2.4M", "114 million Rupees") and link them to **relevant entities/events**.  
  
  ---  
  
  #### 2. Relationship Extraction  
  
  Extract **explicit and implicit relationships** in **triplet format**:  
  ⟨Subject, Predicate, Object⟩  

  **Relationship Categories:**  
  
  - **Person-Person:** Accomplice Of, Associate Of, Relative Of, Alias Of, Legal Representative Of  
  - **Person-Organization:** Founder Of, CEO Of, Board Member Of, Shareholder Of, Employee Of, Beneficiary Of  
  - **Organization-Organization:** Subsidiary Of, Partner Of, Supplier Of, Client Of, Sanctioned By  
  - **Entity-Crime:** Accused Of, Convicted Of, Investigated For, Linked To, Witness To  
  - **Entity-Regulator:** Reported By, Watchlisted By, Regulated By, Fined By  
  - **Others:** Affiliation (Person-Organization), Financial/Transaction (Company-Company), Regulatory/Legal (Agency-Entity), Geopolitical (Country-Organization)  
  
  ---  
  
  #### 3. Summarization Guidelines  
  
  - **Prioritize entities** with multiple relationship ties.  
  - **Emphasize direct contextual evidence** (e.g., quotes, official statements).  
  - Maintain a **neutral, third-person tone**.  
  
  ---  
  
  ### 4. Output Schema (JSON Format)  
  
  ```json
  {{
    "entities": {{
      "individuals": [
        {{
          "canonical_name": "John Doe",
          "disambiguation": "CEO of XYZ Corp",
          "mentions": ["John Doe", "Mr. Doe", "he"]
        }}
      ],
      "organizations": [
        {{
          "canonical_name": "XYZ Corp",
          "aliases": ["XYZ Corporation", "the firm"],
          "sector": "Finance"
        }}
      ]
    }},
    "relationships": [
      {{
        "subject": "John Doe",
        "predicate": "is_ceo_of",
        "object": "XYZ Corp",
        "evidence": ["John Doe, the CEO of XYZ Corp, was investigated..."]
      }},
      {{
        "subject": "XYZ Corp",
        "predicate": "sanctioned_by",
        "object": "OFAC",
        "evidence": ["The US Treasury's OFAC sanctioned XYZ Corp for money laundering."]
      }},
      {{
        "subject": "John Doe",
        "predicate": "investigated_for",
        "object": "Fraud",
        "evidence": ["Authorities have launched a probe into John Doe over fraud allegations."]
      }}
    ],
    "summary": "John Doe, CEO of XYZ Corp, is under investigation for fraud. XYZ Corp has been sanctioned by OFAC for financial misconduct.",
    "news_source": {{
      "name": "Reuters",
      "publish_date": "2025-02-20"
    }}
  }}
  ```
  
  ### Here is the input article:
  {{ article }}
  Your response is:
'''

if __name__ == '__main__':
    API_KEY = 'AIzaSyDG6GempgUfY721G_a96KlZELzlirZyr74'
    client = genai.Client(api_key=API_KEY)
    
    input_file = '../data/output1.jsonl'
    output_file = '../data/output1_ner.jsonl'
    
    lines = load_data(input_file)
    
    for idx, line in enumerate(tqdm(lines, total=len(lines)), start=1):
        print(f'Processing {idx}/{len(lines)}')
        
        obj = json.loads(line)
        link = obj['link'].strip()
        content = obj['content'].strip()
        query = QUERY_PROMPT.replace('{{ article }}', content)
        
        # Uncomment below line for debugging
        # pdb.set_trace()
        
        response = client.models.generate_content(model="gemini-2.0-flash", contents=query)
        print(response.text)
        
        result = {'link': link, 'content': content, 'ner_resp': response.text}
        save_data(output_file, result)