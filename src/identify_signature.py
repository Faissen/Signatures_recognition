import os
from signature_utils import extract_features, compare_descriptors
import json # To handle JSON files

def compare_all_signatures(query_signature_path, database_path="../generated_signatures"):
    """
    Compares a new signature against all signatures stored in a folder.
    Returns the top 3 most similar matches.
    """

    # 1. Extract descriptors from the new signature
    _, query_desc, query_quality = extract_features(query_signature_path)

    if not query_quality:
        return {
            "status": "error",
            "message": "The new signature has low quality."
        }

    results = []  # List to store (filename, similarity)

    # 2. Loop through all stored signatures
    for filename in os.listdir(database_path):

        # Build full file path
        file_path = os.path.join(database_path, filename)

        # Skip non-image files
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        # Extract descriptors from stored signature
        _, db_desc, db_quality = extract_features(file_path)

        # Compute similarity score
        similarity = compare_descriptors(query_desc, db_desc)

        # Save result
        results.append((filename, similarity))

    # 3. Sort results by similarity (highest first)
    results.sort(key=lambda x: x[1], reverse=True)

    # 4. Get the top 3 matches
    top_3 = results[:3]

    # Path for JSON file
    # Define the path to the JSON mapping file
    mapping_path = os.path.join(os.path.dirname(__file__), "..", "signature_names.json")
    # Get absolute path
    mapping_path = os.path.abspath(mapping_path)

    # Read the mapping file
    with open(mapping_path, "r", encoding="utf-8") as f:
        name_map = json.load(f)

    # Replace filenames with real names
    top_3_named = []
    for filename, score in top_3:
        owner = name_map.get(filename, "Unknown") # Default to "Unknown" if not found
        top_3_named.append((owner, score))

    return {
    "top_3_matches": top_3_named}