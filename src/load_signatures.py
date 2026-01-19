# Import libraries
import os # For file handling
import json # For JSON handling
import psycopg2 # For PostgreSQL connection
from src.db_utils import get_connection # Import DB connection utility
from src.signature_utils import extract_features  # Import feature extraction function

# Define constants
SIGNATURE_DIR = "generated_signatures" # Directory containing signature images
NAME_MAP_FILE = "signature_names.json" # JSON file mapping image filenames to person names

# Load the name mapping created during signature generation
# r as in read mode
with open(NAME_MAP_FILE, "r", encoding="utf-8") as f:
    name_map = json.load(f)

# Function to insert signature data into the database
def insert_signature(person_name, image_path, descriptors, quality):
    """Insert a signature record into PostgreSQL."""
    # Establish DB connection
    connection = get_connection()
    cursor = connection.cursor() # Create cursor object to navigate the database

    cursor.execute(
        """
        INSERT INTO signatures (
            person_name, 
            image_path, 
            descriptors, 
            quality)
        VALUES (%s, %s, %s, %s)
        """,
        (person_name, image_path, psycopg2.Binary(descriptors), quality)
    )

    # Commit changes and close connection
    connection.commit()
    cursor.close()
    connection.close()

# Function to load all signatures from the directory and insert into DB
def load_all_signatures():
    """Load all signatures from folder and insert into DB."""
    files = os.listdir(SIGNATURE_DIR) # List all files in the signature directory

    for filename in files:
        if not filename.lower().endswith(".png"): # Only process PNG files
            continue

        # Full path to the image
        image_path = os.path.join(SIGNATURE_DIR, filename)

        # Get the original name used during generation
        person_name = name_map.get(filename, "Unknown") # Default to "Unknown" if not found

        # Extract ORB descriptors + quality flag
        # _ as we don't need keypoints here since we only store descriptors because 
        # they are sufficient for matching
        _, descriptors, quality = extract_features(image_path)

        # Insert into DB
        insert_signature(person_name, image_path, descriptors, quality)

        print(f"Inserted: {filename} → {person_name} | Quality: {quality}")

    print("All signatures inserted successfully.")

# Run the loading function when this script is executed directly
if __name__ == "__main__":
    load_all_signatures()
