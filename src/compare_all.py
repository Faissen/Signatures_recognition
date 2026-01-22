import os # For file path operations
# Import utility functions
from src.db_utils import get_connection
from src.signature_utils import extract_features, compare_descriptors 

# Path to the folder containing all stored signatures
DATABASE_PATH = "signatures_db"

# Signature we want to compare against the database
query_signature = "generated_signatures/signature_to_check.png"

# Extract features from the query signature
# _ means we ignore the keypoints variable
# query_desc will hold the descriptors of the query signature
_, query_desc, query_quality = extract_features(query_signature)

results = [] # To store similarity results

# Loop through all signatures in the database
# listdir gets all files in the specified directory
for filename in os.listdir(DATABASE_PATH):
    # join to get full file path
    file_path = os.path.join(DATABASE_PATH, filename)

    # Skip non-image files
    # endswith checks file extensions
    # if not checks if the condition is false
    if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
        continue # Skip to next file

    # Extract features from the database signature
    _, db_desc, db_quality = extract_features(file_path)

    # Compare descriptors and compute similarity
    similarity = compare_descriptors(query_desc, db_desc)
    # Append result as (filename, similarity) tuple
    results.append((filename, similarity))

# Sort results by similarity (highest first)
# lambda x: x[1] accesses the similarity score in the tuple
# reverse=True sorts in descending order
results.sort(key=lambda x: x[1], reverse=True)

# Print results
print("Similarity results:")
for name, score in results:
    print(f"{name}: {score:.3f}")

# Best match
best_match = results[0] # First item after sorting
print("\nBest match:", best_match)
