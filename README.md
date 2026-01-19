Signature Recognition Project

Project Goal

The goal of this project is to build a complete signature recognition system capable of:
- Generating realistic synthetic signatures
- Extracting image descriptors using ORB (OpenCV)
- Evaluating signature quality
- Storing signatures, names, and descriptors in a PostgreSQL database
- Preparing the foundation for future identity‑verification models

This project demonstrates an end‑to‑end workflow combining Python, computer vision, ETL, PostgreSQL, and data engineering.

Project Workflow

The project follows a full pipeline:
1. Signature Generation
- Creates synthetic handwritten signatures using a cursive font
- Adds noise, blur, rotation, and contrast variation
- Saves each signature as a PNG file
- Stores the associated person name in signature_names.json

2. Feature Extraction
- Uses ORB (Oriented FAST and Rotated BRIEF) to detect keypoints
- Generates 32‑byte descriptors for each signature
- Evaluates signature quality based on descriptor count

3. Database Modeling
A PostgreSQL table stores:
- Person name
- Image path
- ORB descriptors (BYTEA)
- Quality flag
- Timestamp

4. ETL Pipeline
- Reads all generated signatures
- Loads the name mapping from JSON
- Extracts descriptors
- Inserts each signature into the database

5. Signature Comparison (Core Logic Ready)
- Compares two signatures using BFMatcher
- Computes a similarity score between 0 and 1
- Forms the basis for a future verification system

Database Modeling Decisions
Table: signatures
* Column	Type	Description
* id	SERIAL PK	- Unique identifier
* person_name	VARCHAR(255)	- Name associated with the signature
* image_path	TEXT	- File path of the signature image
* descriptors	BYTEA	ORB - Descriptor vectors
* quality	BOOLEAN	- Whether the signature has sufficient quality
* created_at	TIMESTAMP	- Auto‑generated timestamp

Key Design Choices
- BYTEA is ideal for storing binary ORB descriptors
- VARCHAR(255) ensures consistent name formatting
- BOOLEAN allows filtering low‑quality signatures
- SERIAL provides a simple, reliable primary key

Signature Generation Details
Each signature is created with:
- Random name (Faker)
- Random font size and position
- Random rotation (–10° to +10°)
- Gaussian noise
- Speckle noise
- Blur
- Contrast variation
- Images are saved in generated_signatures/
- Names are stored in signature_names.json
Example:
json
{
  "signature_1.png": "John Smith",
  "signature_2.png": "Maria Costa"
}

Feature Extraction

The ORB algorithm is used to:
- Detect keypoints
- Compute descriptors
- Evaluate signature quality
- Signatures with fewer than 20 descriptors are marked as low quality.

ETL Pipeline

The script load_signatures.py:
- Loads the JSON name mapping
- Reads each signature image
- Extracts ORB descriptors
- Evaluates quality
- Inserts everything into PostgreSQL

Example output:
Inserted: signature_12.png → Maria Costa | Quality: True

Signature Comparison

The comparison module:
- Uses BFMatcher with Hamming distance
- Filters good matches
- Computes a similarity score: similarity = good_matches / total_matches

This enables future development of:
- Identity verification
- Fraud detection
- Signature matching systems

Tools Used
- Python
- OpenCV (cv2)
- Pillow
- NumPy
- Faker
- psycopg2
- PostgreSQL
- JSON for metadata
- Custom ETL pipeline

Skills Developed
- Synthetic data generation
- Image processing and computer vision
- ORB feature extraction
- Database schema design
- ETL development
- Binary data storage in PostgreSQL
- Signature comparison logic
- Modular Python project structure

Areas for Improvement
- Build a FastAPI endpoint for signature verification
- Add more advanced similarity metrics
- Train a machine learning classifier
- Create a dashboard for signature analytics
- Add real signature datasets for validation
- Implement hashing for fast descriptor lookup

How to Run the Project

Before running the project, create a .env file in the project root with your PostgreSQL credentials:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=signatures_db
DB_USER=your_user_here
DB_PASSWORD=your_password_here

Make sure the .env file is not committed to Git. Add it to .gitignore.

1. Clone the repository:
   git clone https://github.com/Faissen/Signatures_recognition
   cd Signatures_recognition
2. Install dependencies: pip install -r requirements.txt
3. Create the database table: python -m src.create_tables
4. Generate signatures: python src/create_signatures.py
5. Load signatures into PostgreSQL: python -m src.load_signatures
6. (Optional) Test signature comparison: python -m src.test_comparison

Future Visual Summary
- Signature quality distribution
- Descriptor density heatmaps
- Similarity score comparisons
- Dashboard for verification results
