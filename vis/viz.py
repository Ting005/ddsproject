import json
import pdb
from tqdm import tqdm
from collections import Counter
import json5
import re
from openai import OpenAI
import networkx as nx
import webbrowser
import matplotlib.pyplot as plt
from helper import correct_json_errors
from pyvis.network import Network


def get_publish_dates():
    dates = {}
    error_formatted_count = 0
    
    with open('../data/raw/output1_ner.json', 'r') as reader:
        for line in tqdm(reader.readlines()):
            try:
                obj = json.loads(line)
                ner = obj.get('ner_resp', '').replace('```json', '').replace('```', '').strip()
                parsed_json = correct_json_errors(ner)
                
                if parsed_json:
                    dates[obj['link']] = parsed_json.get('news_source', {}).get('publish_date', 'Unknown')
                else:
                    error_formatted_count += 1
            except json.JSONDecodeError:
                print("Error: Failed to parse JSON")
                error_formatted_count += 1

    print(f"Total formatting errors: {error_formatted_count}")
    return dates


def visualize_graph(data, title="Entity Relationship Graph"):
    G = nx.DiGraph()
    
    # Add nodes
    for individual in data.get("entities", {}).get("individuals", []):
        G.add_node(individual["name"], title=individual.get("role", "Unknown"), color='blue')
    
    for organization in data.get("entities", {}).get("organizations", []):
        G.add_node(organization, title="Organization", color='red')
    
    # Add edges with relationships
    for relation in data.get("relationships", []):
        entity_1 = relation["entity_1"]
        entity_2 = relation["entity_2"]
        relationship = relation["relationship"]
        G.add_edge(entity_1, entity_2, label=relationship)

    if len(G.nodes) == 0:
        print("Warning: No nodes were added to the graph. Check input data.")
        return
    
    # Create PyVis network
    net = Network(height="800px", width="100%", directed=True, notebook=True)
    net.from_nx(G)

    try:
        net.show_buttons(filter_=["physics"])
    except AttributeError:
        print("Warning: .show_buttons() failed, continuing without it.")

    # Customize edges
    for edge in net.edges:
        edge["arrows"] = "to"
        edge["font"] = {"size": 14, "color": "black"}
    
    # Save and display graph
    output_file = "entity_relationship_graph.html"
    net.save_graph(output_file)

    # Append summary below the graph
    summary_html = f"<p style='font-size:16px; color:black; font-weight:bold;'>{data.get('summary', 'No summary available')}</p>"
    with open(output_file, "a") as f:
        f.write(summary_html)
    
    webbrowser.open(output_file)
    print(f"Graph visualization saved and opened: {output_file}")


if __name__ == '__main__':
    dates = get_publish_dates()
    print("Collected publish dates:", dates)

    error_formatted_count = 0
    lst_types = {}

    with open('../data/raw/output1_cls.json', 'r') as reader:
        for line in tqdm(reader.readlines()):
            try:
                obj = json.loads(line)
                cls_resp = obj.get('cls_resp', '').replace('```json', '').replace('```', '').strip()
                parsed_json = correct_json_errors(cls_resp)

                if parsed_json:
                    date = dates.get(obj['link'])
                    if not date:
                        continue

                    parsed_json['date'] = date
                    print(json.dumps(parsed_json, indent=4))

                    month_key = date[:7]
                    if month_key in lst_types:
                        lst_types[month_key].extend(parsed_json.get('detailed_classification', []))
                    else:
                        lst_types[month_key] = parsed_json.get('detailed_classification', [])

                else:
                    error_formatted_count += 1

            except json.JSONDecodeError:
                print("Error: Failed to parse JSON")
                error_formatted_count += 1

    for k, v in lst_types.items():
        lst_types[k] = Counter(v)
        print(k, lst_types[k])

    print(f"Total classification formatting errors: {error_formatted_count}")
