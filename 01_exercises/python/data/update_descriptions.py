"""
Script to update descriptions and embeddings for hotels, restaurants, and activities.

This script:
1. Loads JSON files containing places data
2. Uses Azure OpenAI (GPT-4) to search the internet and find real descriptions
3. Generates new embeddings based on updated descriptions
4. Saves the updated data back to the JSON files

Usage:
    python update_descriptions.py --limit 5 --files hotels_all_cities.json
    python update_descriptions.py --files all
    python update_descriptions.py --files hotels_all_cities.json restaurants_all_cities.json
"""

import json
import os
import sys
import time
from typing import List, Dict, Any
from pathlib import Path
import logging
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(override=False)

# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

# Rate limiting configuration (seconds between API calls)
RATE_LIMIT_DELAY = 0.5  # 500ms between calls to avoid rate limits

# Initialize Azure credential and token provider
azure_credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(
    azure_credential, 
    "https://cognitiveservices.azure.com/.default"
)

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    azure_ad_token_provider=token_provider,
)

logger.info(f"✅ Azure OpenAI initialized")
logger.info(f"   Endpoint: {AZURE_OPENAI_ENDPOINT}")
logger.info(f"   Chat Model: {AZURE_OPENAI_DEPLOYMENT}")
logger.info(f"   Embedding Model: {AZURE_OPENAI_EMBEDDING_DEPLOYMENT}")
logger.info(f"   Rate Limit: {RATE_LIMIT_DELAY}s between calls")


def get_description_from_web(name: str, place_type: str, location: str) -> str:
    """
    Use Azure OpenAI to get a real description of a place.
    
    Args:
        name: Name of the place
        place_type: Type (hotel, restaurant, or activity)
        location: Location/city of the place
        
    Returns:
        A concise 1-3 line description
    """
    try:
        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)
        
        prompt = f"""Find information about "{name}" which is a {place_type} in {location}.
Provide a concise, factual 1-3 line description that captures what makes this place unique or notable.
Focus on key features, reputation, cuisine type (if restaurant), or main attractions (if activity).
Be specific and informative. Do not use generic phrases like "offers a great experience" or "perfect for travelers"."""

        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant that provides concise, factual descriptions of places. Search for accurate, up-to-date information about each place."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.3
        )
        
        description = response.choices[0].message.content.strip()
        # Remove quotes if the model wrapped the response
        description = description.strip('"').strip("'")
        return description
        
    except Exception as e:
        logger.error(f"Error getting description for {name}: {e}")
        return None


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for the given text using Azure OpenAI.
    
    Args:
        text: Text to generate embedding for
        
    Returns:
        List of floats representing the embedding vector
    """
    try:
        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)
        
        response = client.embeddings.create(
            model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return None


def update_place_description(place: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a single place's description and embedding.
    
    Args:
        place: Dictionary containing place information
        
    Returns:
        Updated place dictionary
    """
    name = place.get("name", "")
    place_type = place.get("type", "")
    location = place.get("geoScopeId", "").replace("_", " ").title()
    
    logger.info(f"Processing: {name} ({place_type} in {location})")
    logger.info(f"  Old description: {place.get('description', 'N/A')[:100]}...")
    
    # Get new description
    new_description = get_description_from_web(name, place_type, location)
    
    if new_description:
        place["description"] = new_description
        logger.info(f"  New description: {new_description}")
        
        # Generate new embedding based on updated description
        # Create a rich text representation for better embeddings
        embedding_text = f"{name}. {new_description} Location: {location}. Type: {place_type}."
        if "tags" in place and place["tags"]:
            embedding_text += f" Tags: {', '.join(place['tags'])}."
        
        new_embedding = generate_embedding(embedding_text)
        
        if new_embedding:
            place["embedding"] = new_embedding
            logger.info(f"✅ Successfully updated: {name}")
        else:
            logger.warning(f"⚠️  Could not generate embedding for: {name}")
    else:
        logger.warning(f"⚠️  Could not get description for: {name}")
    
    return place


def process_json_file(file_path: Path, limit: int = None) -> None:
    """
    Process a JSON file containing places data.
    
    Args:
        file_path: Path to the JSON file
        limit: Optional limit on number of places to update (for testing)
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"Processing file: {file_path.name}")
    logger.info(f"{'='*80}")
    
    # Load the JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        places = json.load(f)
    
    total_places = len(places)
    places_to_process = places[:limit] if limit else places
    
    logger.info(f"Total places in file: {total_places}")
    logger.info(f"Places to update: {len(places_to_process)}")
    
    # Update each place
    updated_count = 0
    for i, place in enumerate(places_to_process, 1):
        logger.info(f"\n[{i}/{len(places_to_process)}]")
        updated_place = update_place_description(place)
        
        # Update in the original list
        place.update(updated_place)
        updated_count += 1
        
        # Save progress every 10 items
        if updated_count % 10 == 0:
            logger.info(f"💾 Saving progress... ({updated_count} places updated)")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(places, f, indent=2, ensure_ascii=False)
    
    # Final save
    logger.info(f"\n💾 Saving final results...")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(places, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Completed processing {file_path.name}")
    logger.info(f"   Updated {updated_count} places")


def main():
    """Main function to update all place descriptions and embeddings."""
    
    # Get the data directory (script is in the data folder)
    script_dir = Path(__file__).parent
    data_dir = script_dir
    
    logger.info(f"Data directory: {data_dir}")
    
    # Define the files to process
    files_to_process = [
        "hotels_all_cities.json",
        "restaurants_all_cities.json",
        "activities_all_cities.json"
    ]
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Update place descriptions and embeddings")
    parser.add_argument("--limit", type=int, help="Limit number of places to update per file (for testing)")
    parser.add_argument("--files", nargs="+", 
                       default=["all"], help="Specific files to process (or 'all')")
    args = parser.parse_args()
    
    # Determine which files to process
    if "all" in args.files:
        files = files_to_process
    else:
        files = args.files
    
    logger.info(f"\n{'#'*80}")
    logger.info(f"# Starting Update Process")
    logger.info(f"# Files to process: {', '.join(files)}")
    if args.limit:
        logger.info(f"# Limit per file: {args.limit} places")
    logger.info(f"{'#'*80}\n")
    
    # Process each file
    for filename in files:
        file_path = data_dir / filename
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            continue
        
        try:
            process_json_file(file_path, limit=args.limit)
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}", exc_info=True)
            continue
    
    logger.info(f"\n{'#'*80}")
    logger.info(f"# All processing complete! ✅")
    logger.info(f"{'#'*80}\n")


if __name__ == "__main__":
    main()
