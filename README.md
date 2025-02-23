financial_fraud_detection/
│── prompts/                                    # Store all prompt templates  
│   ├── ner_prompt.txt                          # Entity extraction prompt    
│   ├── cls_prompt.txt                          # Prediction & categorisation prompt 
│   ├── self_reflection.txt                     # TBD 
│── data/                                       # Store raw and processed data  
│   ├── output1_cls.jsonl/                      # Batch processed result for prediction of categoires
│   ├── output1_ner.jsonl/                      # Batch processed result for entity, relationship, summarisation from articles
│   ├── output1.jsonl                           # Crawled content for articles
│   ├── straittimes_financial_crimes.txt        # Links crawled for startstimes financial crime from April 2024 to Feb 2025
│── config/                                     # Configurations & environment settings  
│   ├── configs.yaml                            # API keys, model settings  
│── src/                                        # Experiments scripts
│   ├── call_websrc.py                          # Experiment on genimi web service call
│   ├── helper.py                               # Helper functions     
│   ├── scrape_articles.py                      # scriping straitstime articles
│   ├── test_agent.py                           # testing on agents with langchain
│   ├── test_batch_process_on_ner_cls_prompt.py #batch testing on ner, cls on crawled article content 
│   ├── test_on_ner_prompt_w_nvm.py             # testing on nvidia nvm web service
│── vis/                                        # Experiments on visualization
│   ├── diagram.py
│   ├── viz.py
│── requirements.txt                            # Dependencies  
│── README.md                                   # Project documentation  
