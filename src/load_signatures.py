# Import libraries
import os # For file handling
import psycopg2 # For PostgreSQL connection
from faker import Faker # For generating fake names
from src.db_utils import get_connection # Import DB connection utility
from src.feature_extraction import extract_features  # Import feature extraction function

SIGNATURE_DIR = "generated_signatures" # Directory containing signature images
fake = Faker()

def insert_signature(person_name, image_path, descriptors, quality):
    """Insert a signature record into PostgreSQL."""
    connection = get_connection() # Establish DB connection
    cursor = connection.cursor() # Create cursor object to interact with DB

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

def load_all_signatures():
    """Load all signatures from folder and insert into DB."""
    files = os.listdir(SIGNATURE_DIR) # List all files in the signature directory

    for filename in files:
        if not filename.lower().endswith(".png"): # Only process PNG files
            continue

        image_path = os.path.join(SIGNATURE_DIR, filename)

        # Extract features
        _, descriptors, quality = extract_features(image_path)
        # _ is used to ignore the first return value (image) since we don't need it here
        #  because we only need descriptors and quality.

        # Generate a random person name
        person_name = fake.name()

        # Insert into DB
        insert_signature(person_name, image_path, descriptors, quality)

        print(f"Inserted: {filename} → {person_name} | Quality: {quality}")

    print("All signatures inserted successfully.")

if __name__ == "__main__":
    load_all_signatures()
