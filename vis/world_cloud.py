import matplotlib.pyplot as plt
import json
from wordcloud import WordCloud
import pandas as pd
import json5
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import re
import pdb

nltk.download('punkt_tab')

def clean_article(text: str) -> str:
    """
    Cleans the given article text by removing unrelated content such as disclaimers, promotions, and legal terms.
    :param text: Raw article text
    :return: Cleaned article text
    """
    # Define patterns to remove common unrelated content
    patterns_to_remove = [
        r'Catch up on the news that everyone’s talking about',
        r'Thank you!',
        r'Sign up',
        r'By signing up, I accept SPH Media.*?',
        r'Yes, I would also like to receive SPH Media Group.*?',
        r'For more information on scams, members of the public can visit.*?',
        r'Anyone with information on such scams may call.*?'
    ]
    
    # Remove defined patterns
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.DOTALL)
    
    # Remove extra whitespace and blank lines
    text = re.sub(r'\n+', '\n', text).strip()
    
    another_unwanted = [
        "Join ST's WhatsApp Channel and get the latest news and must-reads.Money launderingSingapore crimeFinancial crimesCrimeThanks for sharing!",
        "Join ST's Telegram channel and get the latest breaking news delivered to you.CrimeFinancial crimesNigeriaThanks for sharing!",
        "Join ST's WhatsApp Channel and get the latest news and must-reads.Singapore courtsCrimeFinancial crimesThanks for sharing!",
        "Join ST's WhatsApp Channel and get the latest news and must-reads.Money launderingSingapore crimeFinancial crimesCrimeThanks for sharing!"
        ]

    for rr in another_unwanted:
        text = text.replace(rr, "")
    
    return text


def correct_json_errors(json_str: str):
    """
    Attempts to fix common JSON errors such as:
    - Missing quotes around keys
    - Trailing commas
    - Single quotes instead of double quotes
    """
    try:
        return json5.loads(json_str)  # Try parsing with json5 (handles more flexible JSON)
    except Exception:
        pass  # If json5 fails, attempt manual correction

    # Fix single quotes around keys and strings
    json_str = re.sub(r"(\s|[{,])'([^']+?)'(\s*[:])", r'\1"\2"\3', json_str)  # Keys
    json_str = re.sub(r"(:\s*)'([^']+?)'", r'\1"\2"', json_str)  # String values
    
    # Remove trailing commas before closing brackets or braces
    json_str = re.sub(r",\s*([\]}])", r"\1", json_str)

    try:
        return json.loads(json_str)  # Try standard JSON parsing
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return None  # Return None if parsing fails


# Function to generate and display a basic word cloud
def generate_word_cloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()

# Sample text for word cloud
def word_cloud_from_text(text):
    generate_word_cloud(text)

# Generate word cloud from a text file
def word_cloud_from_file(file_path):
    with open(file_path, "r") as file:
        text = file.read()
    generate_word_cloud(text)

# Generate word cloud from a CSV file column
def word_cloud_from_csv(file_path, column_name):
    df = pd.read_csv(file_path)
    text = " ".join(df[column_name].dropna())  # Combine all text in the column
    generate_word_cloud(text)

if __name__ == "__main__":
    # Example usage
    resasons = ''
    content = ''
    lst_key_terms = []
    cnt = 0
    lines = open('../data/output1_cls.jsonl', 'r').readlines()
    for l in lines:
        obj = json.loads(l)
        cls_resp = obj['cls_resp'].replace('```json', '').replace('```', '').replace('```', '').strip()
        prd_cat = correct_json_errors(cls_resp)
        if prd_cat:
            if 'Fraud' in prd_cat['detailed_classification']:
                # prd_cat['reasoning']
                key_terms = prd_cat['key_terms']
                print(key_terms)
                lst_key_terms.extend(key_terms)
                # pdb.set_trace()
                # cls_text = clean_article(prd_cat['reasoning'])
                # content +=' '.join(cls_text.split('\n')[0:-1])
                cnt += 1

    # words = word_tokenize(content)
    # # Load stopwords list
    # stop_words = set(stopwords.words('english'))
    # stop_words.add('said')
    # # Remove stopwords
    # filtered_words = [word for word in words if word.lower() not in stop_words]
    # # Reconstruct the cleaned text
    # cleaned_text = ' '.join(filtered_words)


    word_cloud_from_text(' '.join(lst_key_terms))
    # word_cloud_from_file("sample.txt")
    # word_cloud_from_csv("data.csv", "column_name")
