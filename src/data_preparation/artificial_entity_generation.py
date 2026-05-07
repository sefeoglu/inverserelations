"""
Bulk Artificial Entity Generation Script

This script efficiently processes large JSON files to generate artificial/fake entities
for sensitive information. It uses Microsoft Presidio for PII detection and Faker
for generating realistic fake data with progress tracking and batch processing.
Dependencies:
    pip install presidio-analyzer presidio-anonymizer faker tqdm
"""

import argparse
from ast import arg
import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from tqdm import tqdm
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_anonymizer.operators import Operator, OperatorType
from faker import Faker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FakerOperator(Operator):
    """Custom Presidio operator that uses Faker to generate synthetic data."""

    def __init__(self):
        super().__init__()
        self.fake = Faker()

    def operate(self, text: str, params: dict = None) -> str:
        """
        Generate fake data based on entity type.

        Args:
            text: Original text to replace
            params: Dictionary containing 'entity_type' key

        Returns:
            Synthetic data matching the entity type
        """
        params = params or {}
        entity_type = params.get("entity_type")

        if entity_type == "PERSON":
            return self.fake.name()
        elif entity_type == "CREDIT_CARD":
            return self.fake.credit_card_number()
        elif entity_type == "DATE_TIME":
            return str(self.fake.date())
        elif entity_type == "LOCATION":
            return self.fake.city()
        elif entity_type == "EMAIL":
            return self.fake.email()
        elif entity_type == "PHONE_NUMBER":
            return self.fake.phone_number()
        elif entity_type == "URL":
            return self.fake.url()
        else:
            return f"<{entity_type or 'ANONYMIZED'}>"

    def validate(self, params: dict = None) -> None:
        """Validate operator parameters."""
        pass

    def operator_name(self) -> str:
        """Return the operator name."""
        return "faker_operator"

    def operator_type(self) -> OperatorType:
        """Return the operator type."""
        return OperatorType.Anonymize


class BulkEntityAnonymizer:
    """Efficient bulk processing of entity anonymization."""

    def __init__(self, language: str = "en", batch_size: int = 100):
        """
        Initialize the bulk anonymizer.

        Args:
            language: Language for analysis (default: 'en')
            batch_size: Number of items to process before logging progress
        """
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self.anonymizer.add_anonymizer(FakerOperator)
        self.language = language
        self.batch_size = batch_size
        self.stats = {
            "total_processed": 0,
            "entities_found": 0,
            "no_entities": 0,
            "errors": 0
        }

    def anonymize_text(self, text: str) -> Tuple[str, bool]:
        """
        Anonymize a single text.

        Args:
            text: Text to anonymize

        Returns:
            Tuple of (anonymized_text, has_entities)
        """
        try:
            results = self.analyzer.analyze(text=text, language=self.language)

            if not results:
                return text, False

            fake_version = self.anonymizer.anonymize(
                text=text,
                analyzer_results=results,
                operators={"DEFAULT": OperatorConfig("faker_operator", {})}
            )

            return fake_version.text, True

        except Exception as e:
            logger.warning(f"Error anonymizing text '{text}': {str(e)}")
            return text, False

    def anonymize_entity_pair(self, entity_1: str, entity_2: str) -> List[Dict[str, str]]:
        """
        Anonymize a pair of entities.

        Args:
            entity_1: First entity
            entity_2: Second entity

        Returns:
            List of dictionaries with original and artificial data
        """
        artificial_data = []

        for entity in [entity_1, entity_2]:
            fake_text, has_entities = self.anonymize_text(entity)

            artificial_data.append({
                "Original": entity,
                "Artificial": fake_text
            })

            if has_entities:
                self.stats["entities_found"] += 1
            else:
                self.stats["no_entities"] += 1

        return artificial_data

    def log_progress(self, current: int, total: int) -> None:
        """Log progress statistics."""
        if current % self.batch_size == 0 and current > 0:
            logger.info(
                f"Processed {current}/{total} items | "
                f"Entities found: {self.stats['entities_found']} | "
                f"No entities: {self.stats['no_entities']} | "
                f"Errors: {self.stats['errors']}"
            )


def read_json(file_path: str) -> Any:
    """
    Read JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {str(e)}")
        raise


def write_json(data: Any, file_path: str, create_backup: bool = True) -> None:
    """
    Write data to JSON file with optional backup.

    Args:
        data: Data to write
        file_path: Destination file path
        create_backup: Whether to backup existing file
    """
    dirpath = os.path.dirname(file_path)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)

    # Create backup if file exists
    if create_backup and os.path.exists(file_path):
        backup_path = f"{file_path}.backup"
        if not os.path.exists(backup_path):
            os.rename(file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"Successfully wrote {len(data)} items to {file_path}")
    except IOError as e:
        logger.error(f"Failed to write to {file_path}: {str(e)}")
        raise


def process_bulk_output(
    input_path: str,
    output_path: str,
    head_field: str = "head",
    tail_field: str = "tail"
) -> None:
    """
    Process bulk output JSON file with entity label fields.

    Reads input JSON, anonymizes 'head' and 'tail' fields,
    and writes results to output file.

    Args:
        input_path: Path to input JSON file
        output_path: Path to output JSON file
        sub_label_field: Field name for subject entity (default: 'head')
        obj_label_field: Field name for object entity (default: 'tail')
    """
    logger.info(f"Starting bulk output processing...")
    logger.info(f"Input: {input_path}")
    logger.info(f"Output: {output_path}")

    # Read input data
    try:
        data = read_json(input_path)
        logger.info(f"Loaded {len(data)} items")
    except Exception as e:
        logger.error(f"Failed to load input file: {str(e)}")
        return

    anonymizer = BulkEntityAnonymizer()
    new_data = []

    # Process each item
    for idx, item in enumerate(tqdm(data, desc="Processing bulk output"), 1):
        try:
            entity_1 = item.get(head_field, "")
            entity_2 = item.get(tail_field, "")

            if not entity_1 or not entity_2:
                logger.warning(
                    f"Item {idx}: Missing required fields "
                    f"({head_field}, {tail_field})"
                )
                new_data.append(item)
                continue

            artificial_data = anonymizer.anonymize_entity_pair(entity_1, entity_2)
            item["artificial_data"] = artificial_data
            new_data.append(item)

            anonymizer.log_progress(idx, len(data))

        except Exception as e:
            logger.error(f"Error processing item {idx}: {str(e)}")
            anonymizer.stats["errors"] += 1
            new_data.append(item)
            continue

    # Write output
    try:
        write_json(new_data, output_path)
        logger.info("Processing complete!")
        logger.info(f"Statistics: {anonymizer.stats}")
    except Exception as e:
        logger.error(f"Failed to write output: {str(e)}")


def process_cleaned_asymmetrics(
    input_path: str,
    output_path: str,
    head_field: str = "h",
    tail_field: str = "t",
    head_index: int = 0,
    tail_index: int = 0
) -> None:
    """
    Process cleaned asymmetrics JSON file with head and tail fields.

    Reads input JSON, anonymizes entities from specified indices,
    and writes results to output file.

    Args:
        input_path: Path to input JSON file
        output_path: Path to output JSON file
        head_field: Field name for head entity (default: 'h')
        tail_field: Field name for tail entity (default: 't')
        head_index: Index in head array (default: 0)
        tail_index: Index in tail array (default: 0)
    """
    logger.info(f"Starting asymmetrics processing...")
    logger.info(f"Input: {input_path}")
    logger.info(f"Output: {output_path}")

    # Read input data
    try:
        data = read_json(input_path)
        logger.info(f"Loaded {len(data)} items")
    except Exception as e:
        logger.error(f"Failed to load input file: {str(e)}")
        return

    anonymizer = BulkEntityAnonymizer()
    new_data = []

    # Process each item
    for idx, item in enumerate(tqdm(data, desc="Processing asymmetrics"), 1):
        try:
            head_list = item.get(head_field, [])
            tail_list = item.get(tail_field, [])

            if not head_list or not tail_list:
                logger.warning(f"Item {idx}: Missing required fields ({head_field}, {tail_field})")
                new_data.append(item)
                continue

            entity_1 = head_list[head_index] if len(head_list) > head_index else ""
            entity_2 = tail_list[tail_index] if len(tail_list) > tail_index else ""

            if not entity_1 or not entity_2:
                logger.warning(f"Item {idx}: Cannot extract entities at indices")
                new_data.append(item)
                continue

            artificial_data = anonymizer.anonymize_entity_pair(entity_1, entity_2)
            item["artificial_data"] = artificial_data
            new_data.append(item)

            anonymizer.log_progress(idx, len(data))

        except Exception as e:
            logger.error(f"Error processing item {idx}: {str(e)}")
            anonymizer.stats["errors"] += 1
            new_data.append(item)
            continue

    # Write output
    try:
        write_json(new_data, output_path)
        logger.info("Processing complete!")
        logger.info(f"Statistics: {anonymizer.stats}")
    except Exception as e:
        logger.error(f"Failed to write output: {str(e)}")


def process_streaming_output(
    input_path: str,
    output_path: str,
    head_field: str = "head",
    tail_field: str = "tail",
    chunk_size: int = 10000
) -> None:
    """
    Process large JSON files using streaming to reduce memory usage.

    Args:
        input_path: Path to input JSONL or JSON file
        output_path: Path to output JSONL file
        sub_label_field: Field name for head entity
        obj_label_field: Field name for tail entity
        chunk_size: Number of items to keep in memory before writing
    """
    logger.info(f"Starting streaming processing...")
    logger.info(f"Input: {input_path}")
    logger.info(f"Output: {output_path}")

    anonymizer = BulkEntityAnonymizer()
    chunk = []
    total_items = 0

    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            with open(output_path, "w", encoding="utf-8") as outfile:

                for line in tqdm(infile, desc="Processing streaming"):
                    try:
                        item = json.loads(line)

                        entity_1 = item.get(head_field, "")
                        entity_2 = item.get(tail_field, "")

                        if entity_1 and entity_2:
                            artificial_data = anonymizer.anonymize_entity_pair(
                                entity_1, entity_2
                            )
                            item["artificial_data"] = artificial_data

                        chunk.append(item)
                        total_items += 1

                        # Write chunk when it reaches size limit
                        if len(chunk) >= chunk_size:
                            for chunk_item in chunk:
                                outfile.write(json.dumps(chunk_item, ensure_ascii=False) + "\n")
                            chunk = []
                            logger.info(f"Processed {total_items} items, flushed chunk to disk")

                    except json.JSONDecodeError as e:
                        logger.warning(f"Skipping malformed JSON line: {str(e)}")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing item: {str(e)}")
                        anonymizer.stats["errors"] += 1
                        continue

                # Write remaining items
                if chunk:
                    for chunk_item in chunk:
                        outfile.write(json.dumps(chunk_item, ensure_ascii=False) + "\n")

        logger.info("Streaming processing complete!")
        logger.info(f"Total items: {total_items}")
        logger.info(f"Statistics: {anonymizer.stats}")

    except IOError as e:
        logger.error(f"File I/O error: {str(e)}")


def main():
    """Main execution function with example usage."""
    logger.info("=" * 70)
    logger.info("EXAMPLE 1: Processing bulk output format")
    logger.info("=" * 70)
    parser  = argparse.ArgumentParser(description="Process bulk output JSON file.")
    parser.add_argument(
        "--input",
        type=str,
        default="../zenodo/reversingarrows/original_fewrel_inverse.json",
        help="Path to input JSON file containing bulk output data.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="../zenodo/reversingarrows/synthetic_fewrel_inverse.json",
        help="Path to output JSON file for processed data.",
    )

    args = parser.parse_args()

    process_bulk_output(
        input_path=args.input,
        output_path=args.output,
        head_label_field="head",
        tail_label_field="tail"
    )


if __name__ == "__main__":
    main()
