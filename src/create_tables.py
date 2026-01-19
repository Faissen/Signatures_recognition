from src.db_utils import get_connection

def create_tables():
    """
    Creates the required PostgreSQL tables for the signature recognition system.
    """
    # Establishes a connection to PostgreSQL
    connection = get_connection()
    # Creates a cursor object to interact with the database 
    cursor = connection.cursor()
    # SQL command to create the signatures table
    # IF NOT EXISTS prevents errors if the table already exists
    # BYTEA is used to store binary data such as image descriptors.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signatures (
            id SERIAL PRIMARY KEY,
            person_name VARCHAR(255) NOT NULL,
            image_path TEXT NOT NULL,
            descriptors BYTEA NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
            quality BOOLEAN DEFAULT TRUE
        );
    """)

    connection.commit() # Saves the changes to the database
    # Closes the cursor and connection
    cursor.close()
    connection.close()
    # Prints a success message
    print("Table 'signatures' created successfully.")

# Run the table creation when this script is executed directly
if __name__ == "__main__":
    create_tables()

