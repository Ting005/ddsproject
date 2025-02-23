from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough, RunnableSequence
from helper import load_yaml_config, read_prompt
from scrape_articles import dynamic_web_page_scrape_and_process

import os
import pdb

# loading config
config = load_yaml_config('../configs/config.yaml')
api_key = config.api_keys.genimi
model_name = config.model.name
str_ner_prompt = read_prompt(config.prompts.ner)
str_cls_prompt = read_prompt(config.prompts.cls)

os.environ["GOOGLE_API_KEY"] = api_key
 

def negative_news_detection(article):
    # Initialize the Google Gemini LLM
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.7)
    input_data = {"article": article}

    # Step 1: Generate entities, triplets from article
    ner_prompt = PromptTemplate.from_template(str_ner_prompt)
    ner_chain = ner_prompt | llm
    sequential_chain = RunnableSequence(
                            {"article": RunnablePassthrough()} | ner_chain
                        )
    result = sequential_chain.invoke(input_data)
    print('Extracted key entities, and relationships:')
    print(result.content)

    # Step 2: Getting article classifed, into types of financial crime
    cls_prompt = PromptTemplate.from_template(str_cls_prompt)
    cls_chain = cls_prompt | llm
    sequential_chain = RunnableSequence(
                            {"article": RunnablePassthrough()} | cls_chain
                        )
    result = sequential_chain.invoke(input_data)
    print('Prediction of types of financial crime:')
    print(result.content)


if __name__ == '__main__':
    test_url = "https://www.straitstimes.com/singapore/courts-crime/bangladesh-probes-sporean-tycoon-for-financial-crimes-his-lawyers-call-it-a-smear-campaign"
    print('getting article content for url:', test_url)
    article = dynamic_web_page_scrape_and_process(test_url)
    # article = '''
    # Philippines welcomes removal from money laundering ‘grey list’The South-east Asia nation had been on the Financial Action Task Force list since 2021.PHOTO: ST FILE UPDATED Feb 22, 2025, 05:09 PMThanks for sharing!MANILA - The Philippines on Feb 22 praised its removal from a global financial “grey list” of countries under increased monitoring for money laundering and terrorism financing, a status that can hamper global financial transactions. The South-east Asian nation had been on the Financial Action Task Force (FATF) list, which identifies countries “working with it to correct deficiencies in their financial systems”, since 2021.“The (FATF) removed the Philippines from its increased monitoring following a successful on-site visit, and updated its statements on ‘high-risk and other monitored jurisdictions’,” the Paris-based group said after a Feb 21 vote at its annual plenary.The FATF, an international organisation that coordinates global efforts to crack down on money laundering and terrorism financing, includes representatives from nearly 40 countries such as the US, China and South Africa.In a statement on Feb 22, the Anti-Money Laundering Council in Manila hailed the FATF decision as a “milestone” that would bring a litany of benefits.“The Philippines’ exit from the FATF grey list is expected to facilitate faster and lower-cost cross-border transactions, reduce compliance barriers, and enhance financial transparency,” it said.The move would also provide relief for more than two million Filipinos who work overseas and send remittances home each year, the council added.
    # It singled out President Ferdinand Marcos’ 2023 signing of an executive order targeting money laundering and “counter-terrorism financing” as having played a key role in the decision.In 2024, Mr Marcos also banned offshore gaming operators, known locally as Pogos, which were said to be used as fronts by organised crime groups for human trafficking, money laundering, online fraud, kidnappings and even murder.But rights groups have accused the government of filing “baseless” charges against civil society groups to improve its standing with the FATF.“This move by FATF, we are afraid, will be taken as a stamp of approval by the government and will thus very likely embolden them to continue, even intensify, the harassment,” Human Rights Watch senior researcher Carlos Conde told AFP on Feb 22.“While we recognise the need to stamp out money laundering – and FATF did acknowledge the supposed improvements the Philippine government did in this regard – there clearly is a need for the government to adhere to international human rights standards as it pursues this campaign.” AFPMore on this TopicAsset recovery a priority in Singapore’s anti-money laundering regime: PM Wong Non-financial sectors in S’pore at higher risk of money laundering: Report  Join ST's Telegram channel and get the latest breaking news delivered to you.PhilippinesFinancial crimesMoney launderingThanks for sharing!
    # '''
    # print(article)
    negative_news_detection(article=article)

