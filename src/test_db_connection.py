# Import the database connection utility
from src.db_utils import get_connection 

# Establishes a connection to PostgreSQL
conn = get_connection() 

# If the connection is successful, print a message
print("Connected successfully!") 

# Closes the connection
conn.close()