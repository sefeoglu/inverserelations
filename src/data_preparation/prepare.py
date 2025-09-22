import os
import json
import sys
from qwikidata.sparql import return_sparql_query_results
import time
def read_json(path):
    with open(path, 'r', encoding="utf-8") as f:
        data = json.load(f)
    return data

def write_json(data, path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
def sparql_query(qid_1, qid_2):
        prob_query = """SELECT ?prop ?from ?to
                    WHERE {
                            VALUES (?from ?to) { (wd:"""+qid_1+""" wd:"""+qid_2+""") }
                            {
                                ?from ?prop ?to .
                            }
                            UNION
                            {
                                ?to ?prop ?from .
                            }
                            FILTER(STRSTARTS(STR(?prop), STR(wdt:)))
                        }"""
        return prob_query
def query_wikidata(sparql_query):
    """
    Query Wikidata SPARQL endpoint and return results.
    """

    try:
        results = return_sparql_query_results(sparql_query)
        print(results)
        return results
    except Exception as e:
        print(f"Error querying Wikidata: {e}")
        return None
    
def check_relation(qid_1, qid_2):
    sparql = sparql_query(qid_1, qid_2)
    results = query_wikidata(sparql)
    if results and 'results' in results and 'bindings' in results['results'] and len(results['results']['bindings']) > 0:
        #results['results']['bindings'][0]['prop']['value'].split('/')[-1]
        return True, results['results']['bindings']
    else:
        return False, None
def all_data_reannotate(data, file):
    new_data = []
    for item in data:
        qid_1 = item['h'][1]
        qid_2 = item['t'][1]
        # print(item.keys())
        
        has_relation, prop = check_relation(qid_1, qid_2)
        if has_relation:
            item['has_relation'] = True
            item['relation_prop_wiki'] = prop
        else:
            item['has_relation'] = False
            item['relation_prop_wiki'] = None
        new_data.append(item)
        time.sleep(1)  # To avoid overwhelming the SPARQL endpoint
        write_json(new_data, file)
    return new_data
def report_not_match(data, file):
    count = 0
    relations = []
    for item in data:
        if item['r_pid'] != item['relation_prop_wiki'] and item['has_relation']:
            count += 1
            relations.append(item)
    print(f"Total not match: {count}")
    write_json(relations, file)
    return count
if __name__ == "__main__":

    val_data = read_json('val_wiki.json')
    train_data = read_json('train_wiki.json')
    relations = read_json('pid2name.json')
    train_new, val_new, val_rel = [],[],[]
    for key, values in val_data.items():
        for value in values:
            value['relation'] = relations[key][0]
            value['relation_definition'] = relations[key][1]
            value['r_pid'] = key
            
            val_new.append(value)
            val_rel.append(key)
 
    for key, values in train_data.items():
        for value in values:
            value['relation'] = relations[key][0]
            value['relation_definition'] = relations[key][1]
            value['r_pid'] = key
            train_new.append(value)
    
    train_new = all_data_reannotate(train_new, file='./train_wiki_checked_1.json')
    val_new = all_data_reannotate(val_new, file='./val_wiki_checked_1.json')

    print("Done")