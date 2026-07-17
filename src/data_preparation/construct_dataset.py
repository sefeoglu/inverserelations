import os
import json
import sys
import argparse
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from qwikidata.sparql import return_sparql_query_results

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from utils import read_json, write_json


def build_sparql_query(qid_1: str, qid_2: str) -> str:
    """
    Build SPARQL query to find relations between two Wikidata entities.
    
    Args:
        qid_1: First entity QID (e.g., 'Q42')
        qid_2: Second entity QID (e.g., 'Q159')
        
    Returns:
        SPARQL query string
    """
    query = f"""SELECT ?prop ?from ?to
        WHERE {{
            VALUES (?from ?to) {{ (wd:{qid_1} wd:{qid_2}) }}
            {{
                ?from ?prop ?to .
            }}
            UNION
            {{
                ?to ?prop ?from .
            }}
            FILTER(STRSTARTS(STR(?prop), STR(wdt:)))
        }}"""
    return query


def query_wikidata(sparql_query: str, max_retries: int = 3, retry_delay: float = 2.0) -> Optional[dict]:
    """
    Query Wikidata SPARQL endpoint with retry logic.
    
    Args:
        sparql_query: SPARQL query string
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        
    Returns:
        Query results or None if failed
    """
    for attempt in range(max_retries):
        try:
            results = return_sparql_query_results(sparql_query)
            return results
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠ Query failed (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"  Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"✗ Query failed after {max_retries} attempts: {e}")
                return None
    
    return None


def check_relation(qid_1: str, qid_2: str, max_retries: int = 3) -> Tuple[bool, Optional[List]]:
    """
    Check if relation exists between two entities in Wikidata.
    
    Args:
        qid_1: First entity QID
        qid_2: Second entity QID
        max_retries: Maximum number of SPARQL query retries
        
    Returns:
        Tuple of (has_relation: bool, properties: Optional[List])
    """
    sparql = build_sparql_query(qid_1, qid_2)
    results = query_wikidata(sparql, max_retries=max_retries)
    
    if results and 'results' in results and 'bindings' in results['results']:
        bindings = results['results']['bindings']
        if len(bindings) > 0:
            return True, bindings
    
    return False, None


def annotate_data(
    data: List[dict],
    output_file: str,
    delay: float = 1.0,
    max_retries: int = 3,
    save_interval: int = 10,
    verbose: bool = True
) -> List[dict]:
    """
    Annotate data with Wikidata relation information.
    
    Args:
        data: List of data items to annotate
        output_file: Path to save annotated data
        delay: Delay between queries in seconds (default: 1.0)
        max_retries: Max retries per SPARQL query
        save_interval: Save every N items (default: 10)
        verbose: Print progress messages
        
    Returns:
        Annotated data list
    """
    new_data = []
    
    for idx, item in enumerate(data, 1):
        qid_1 = item['h'][1] if isinstance(item.get('h'), (list, tuple)) else item['h']
        qid_2 = item['t'][1] if isinstance(item.get('t'), (list, tuple)) else item['t']
        
        if verbose:
            print(f"[{idx}/{len(data)}] Checking relation: {qid_1} <-> {qid_2}...", end=" ")
        
        has_relation, prop = check_relation(qid_1, qid_2, max_retries=max_retries)
        
        item['has_relation'] = has_relation
        item['relation_prop_wiki'] = prop
        
        if verbose:
            status = "✓ Found" if has_relation else "✗ Not found"
            print(status)
        
        new_data.append(item)
        
        # Save progress every N items
        if idx % save_interval == 0:
            write_json(new_data, output_file)
            if verbose:
                print(f"  → Saved {idx} items")
        
        # Delay to avoid overwhelming the endpoint
        if idx < len(data):
            time.sleep(delay)
    
    # Final save
    write_json(new_data, output_file)
    
    return new_data


def create_enriched_data(
    data_dict: Dict[str, List[dict]],
    relations: Dict[str, List[str]]
) -> List[dict]:
    """
    Create enriched dataset by adding relation information.
    
    Args:
        data_dict: Dictionary with relation PIDs as keys and item lists as values
        relations: Dictionary mapping PID to [relation_name, definition]
        
    Returns:
        List of enriched items
    """
    enriched_data = []
    
    for pid, items in data_dict.items():
        if pid not in relations:
            print(f"⚠ Warning: PID {pid} not found in relations file")
            continue
        
        relation_name, relation_def = relations[pid][0], relations[pid][1]
        
        for item in items:
            item['relation'] = relation_name
            item['relation_definition'] = relation_def
            item['r_pid'] = pid
            enriched_data.append(item)
    
    return enriched_data


def report_mismatches(data: List[dict], output_file: str, verbose: bool = True) -> int:
    """
    Find and report items where original relation PID doesn't match Wikidata results.
    
    Args:
        data: Annotated data list
        output_file: Path to save mismatches report
        verbose: Print summary information
        
    Returns:
        Count of mismatches
    """
    mismatches = []
    
    for item in data:
        # Only check items that have relations and were successfully queried
        if item.get('has_relation') and item.get('relation_prop_wiki'):
            original_pid = item.get('r_pid')
            wiki_props = item.get('relation_prop_wiki', [])
            
            # Extract property IDs from wiki results
            wiki_prop_ids = [
                prop['prop']['value'].split('/')[-1] 
                for prop in wiki_props
            ]
            
            # Check if original PID matches any wiki properties
            if original_pid and original_pid not in wiki_prop_ids:
                mismatches.append(item)
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"Mismatch Report")
        print(f"{'='*70}")
        print(f"Total items with mismatches: {len(mismatches)}")
        print(f"Percentage: {(len(mismatches)/len(data)*100):.2f}%")
        print(f"Report saved to: {output_file}")
        print(f"{'='*70}\n")
    
    write_json(mismatches, output_file)
    
    return len(mismatches)


def main():
    parser = argparse.ArgumentParser(
        description="Enrich dataset with Wikidata relation information via SPARQL queries.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python src/data_preparation/construct_dataset.py \\
    --train-data train_wiki.json \\
    --val-data val_wiki.json \\
    --relations pid2name.json

  # Custom output directory
  python src/data_preparation/construct_dataset.py \\
    --train-data train_wiki.json \\
    --val-data val_wiki.json \\
    --relations pid2name.json \\
    --output-dir ./annotated_data

  # With custom query delay and retry settings
  python src/data_preparation/construct_dataset.py \\
    --train-data train_wiki.json \\
    --val-data val_wiki.json \\
    --relations pid2name.json \\
    --delay 2.0 \\
    --max-retries 5

  # Generate mismatch reports
  python src/data_preparation/construct_dataset.py \\
    --train-data train_wiki.json \\
    --val-data val_wiki.json \\
    --relations pid2name.json \\
    --report-mismatches

  # Minimal output (quiet mode)
  python src/data_preparation/construct_dataset.py \\
    --train-data train_wiki.json \\
    --val-data val_wiki.json \\
    --relations pid2name.json \\
    --quiet
        """
    )

    # Required arguments
    parser.add_argument(
        '--train-data',
        type=str,
        required=True,
        help='Path to training data JSON file'
    )
    parser.add_argument(
        '--val-data',
        type=str,
        required=True,
        help='Path to validation data JSON file'
    )
    parser.add_argument(
        '--relations',
        type=str,
        required=True,
        help='Path to relations/PID mapping JSON file'
    )

    # Optional arguments
    parser.add_argument(
        '--output-dir',
        type=str,
        default='.',
        help='Directory where annotated datasets will be saved (default: current directory)'
    )
    parser.add_argument(
        '--train-output',
        type=str,
        default='train_fewrel.json',
        help='Output filename for annotated training data (default: train_fewrel.json)'
    )
    parser.add_argument(
        '--val-output',
        type=str,
        default='val_fewrel.json',
        help='Output filename for annotated validation data (default: val_fewrel.json)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between SPARQL queries in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--max-retries',
        type=int,
        default=3,
        help='Maximum retry attempts per SPARQL query (default: 3)'
    )
    parser.add_argument(
        '--save-interval',
        type=int,
        default=10,
        help='Save progress every N items (default: 10)'
    )
    parser.add_argument(
        '--report-mismatches',
        action='store_true',
        help='Generate mismatch reports comparing original PIDs with Wikidata results'
    )
    parser.add_argument(
        '--mismatch-output-dir',
        type=str,
        default='.',
        help='Directory where mismatch reports will be saved (default: same as output-dir)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress messages'
    )

    args = parser.parse_args()

    # Set verbose flag
    verbose = not args.quiet

    # Validate input files
    print("Validating input files...")
    for file_path, name in [
        (args.train_data, "Training data"),
        (args.val_data, "Validation data"),
        (args.relations, "Relations")
    ]:
        if not os.path.exists(file_path):
            parser.error(f"{name} file not found: {file_path}")

    try:
        if verbose:
            print("=" * 70)
            print("WIKIDATA ANNOTATION PIPELINE")
            print("=" * 70)
            print(f"Training data: {args.train_data}")
            print(f"Validation data: {args.val_data}")
            print(f"Relations file: {args.relations}")
            print(f"Output directory: {args.output_dir}")
            print(f"Query delay: {args.delay}s")
            print(f"Max retries: {args.max_retries}")
            print(f"Report mismatches: {args.report_mismatches}")
            print("=" * 70)
            print()

        # Load input data
        if verbose:
            print("Loading input files...")
        train_data = read_json(args.train_data)
        val_data = read_json(args.val_data)
        relations = read_json(args.relations)

        if verbose:
            print(f"✓ Loaded {len(train_data)} training data groups")
            print(f"✓ Loaded {len(val_data)} validation data groups")
            print(f"✓ Loaded {len(relations)} relation definitions")
            print()

        # Enrich data with relation information
        if verbose:
            print("Enriching datasets with relation metadata...")
        train_enriched = create_enriched_data(train_data, relations)
        val_enriched = create_enriched_data(val_data, relations)

        if verbose:
            print(f"✓ Created {len(train_enriched)} training items")
            print(f"✓ Created {len(val_enriched)} validation items")
            print()

        # Build output paths
        train_output_path = os.path.join(args.output_dir, args.train_output)
        val_output_path = os.path.join(args.output_dir, args.val_output)

        # Annotate data with Wikidata information
        if verbose:
            print("Querying Wikidata SPARQL endpoint...")
            print("(This may take a while depending on dataset size)")
            print()

        print("Annotating training data...")
        train_annotated = annotate_data(
            train_enriched,
            train_output_path,
            delay=args.delay,
            max_retries=args.max_retries,
            save_interval=args.save_interval,
            verbose=verbose
        )

        print("\nAnnotating validation data...")
        val_annotated = annotate_data(
            val_enriched,
            val_output_path,
            delay=args.delay,
            max_retries=args.max_retries,
            save_interval=args.save_interval,
            verbose=verbose
        )

        if verbose:
            print(f"\n✓ Training data saved to: {train_output_path}")
            print(f"✓ Validation data saved to: {val_output_path}")

        # Generate mismatch reports if requested
        if args.report_mismatches:
            print("\nGenerating mismatch reports...")
            
            mismatch_dir = args.mismatch_output_dir if args.mismatch_output_dir else args.output_dir
            train_mismatch_path = os.path.join(mismatch_dir, 'train_mismatches.json')
            val_mismatch_path = os.path.join(mismatch_dir, 'val_mismatches.json')

            train_mismatch_count = report_mismatches(
                train_annotated,
                train_mismatch_path,
                verbose=verbose
            )
            val_mismatch_count = report_mismatches(
                val_annotated,
                val_mismatch_path,
                verbose=verbose
            )

            if verbose:
                print(f"Training mismatches: {train_mismatch_count}")
                print(f"Validation mismatches: {val_mismatch_count}")

        if verbose:
            print("\n" + "=" * 70)
            print("✓ Pipeline completed successfully!")
            print("=" * 70)

    except FileNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(f"✗ Error: Missing expected key - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
