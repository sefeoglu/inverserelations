import os
import json
import sys
from qwikidata.sparql import return_sparql_query_results
import time
from tqdm import tqdm
def read_json(path):
    with open(path, 'r', encoding="utf-8") as f:
        data = json.load(f)
    return data

def write_json(data, path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_label(id):

    label_query = """
                SELECT ?item ?itemLabel
                WHERE {
                VALUES ?item { wd:"""+id+""" }
                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
                }
                LIMIT 1
                """
    
    return label_query
def get_propLabel(pid):
    sparql = """
                SELECT ?property ?propertyLabel 
                WHERE {
                VALUES ?property { wd:"""+pid+""" }
                SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
                }
                LIMIT 1
            """
    return sparql
    
def sparql_query(qid):
    prob_query = """
                    SELECT ?object 
                    WHERE {
                    wd:""" + qid + """ schema:description  ?object .
                    
                    OPTIONAL {FILTER(LANG(?object) = "en") }
                    }
                    LIMIT 10
                """
    
    return prob_query

def query_wikidata(sparql_query):
    """
    Query Wikidata SPARQL endpoint and return results.
    """

    try:
        results = return_sparql_query_results(sparql_query)
        # print(results)
        return results
    except Exception as e:
        print(f"Error querying Wikidata: {e}")
        return None
    
def clean_entity_info(entity_info, type):
    # Implement any necessary cleaning or processing of the entity_info here
    if type == 'item':
        label_sparql = get_label(entity_info)
    else:
        label_sparql = get_propLabel(entity_info)
    results = query_wikidata(label_sparql)
    if results and 'results' in results and 'bindings' in results['results'] and len(results['results']['bindings']) > 0:
        return results['results']['bindings']
    else:
        return None

def retrieve_entity_information(qid):

    sparql = sparql_query(qid)
    results = query_wikidata(sparql)
    if results and 'results' in results and 'bindings' in results['results'] and len(results['results']['bindings']) > 0:
        #results['results']['bindings'][0]['prop']['value'].split('/')[-1]
        return True, results['results']['bindings']
    else:
        return False, None
    

def all_get_entity_information(data, file):
    new_data = []
    for item in tqdm(data, desc="Processing entities"):
        qid_1 = item['h'][1]
        qid_2 = item['t'][1]
        # print(item.keys())
        
        has_info, result = retrieve_entity_information(qid_1)
        
        if has_info:
            item['has_info_head'] = True
            item['head_info'] = result
        else:
            item['has_info_head'] = False
            item['head_info'] = None
        time.sleep(1)
        has_info, result = retrieve_entity_information(qid_2)

        if has_info:
            item['has_info_tail'] = True
            item['tail_info'] = result
        else:
            item['has_info_tail'] = False
            item['tail_info'] = None
        new_data.append(item)
        time.sleep(1)  # To avoid overwhelming the SPARQL endpoint
        write_json(new_data, file)
    return new_data

def get_id(uri):
    # print(uri)
    return uri.split('/')[-1]

def trace_data(info_list):
    triples = []

    for triple in tqdm(info_list):
       
        subject = get_id(triple['subject']['value'])
        predicate = get_id(triple['predicate']['value'])
        object = ''
        if 'object' in triple.keys():
            object = get_id(triple['subject']['value'])

        if 'Q' in subject:
            subject_label = clean_entity_info(subject, 'item')
            if subject_label is not None:
                subject = subject_label[0]['itemLabel']['value']
        time.sleep(1.0)
        if 'P' in predicate:
            predicate_label =  clean_entity_info(predicate, 'prop')
            if predicate_label is not  None:
                predicate = predicate_label[0]['propertyLabel']['value']
                # print(predicate_label)
            # print(predicate)
        clean_triple = {'object':subject, 'predicate':predicate}
        # print(clean_triple)
        time.sleep(1.0)
    
        if clean_triple not in triples:
            triples.append(clean_triple)
        # break

    return triples

def change_all_ids_to_labels(input_data, out_path):
    # input_data = read_json(input_path)
    out_data = []

    for item in tqdm(input_data):
        head_info = item['head_info']
        tail_info = item['tail_info']
        if head_info is not None:
            item['head_clean'] = trace_data(head_info)
        if tail_info is not None: 
            item['tail_clean'] = trace_data(tail_info)
        out_data.append(item)
        write_json(out_data, out_path)
        # break


if __name__ == "__main__":

    # all_data = read_json('/Users/sefika/phd_projects/converse_relations/data/cleaned_asymetrics.json')[3000:]
    # out_file_path = "/Users/sefika/phd_projects/converse_relations/results/new_en_entity_triples_7json"

    # new_data = all_get_entity_information(all_data, out_file_path)
    # new_data =  change_all_ids_to_labels(all_data[155:], out_file_path)
    new_data = []
    out_file_path = f"/Users/sefika/phd_projects/converse_relations/results/new_en_entity_triples_part_all.json"

    for file_idx in range(1, 8):

        all_data = read_json(f'/Users/sefika/phd_projects/converse_relations/results/new_en_entity_triples_{file_idx}.json')

        new_data.extend(all_data)

    write_json(new_data, out_file_path)

    print("Done")