# Environment Configuration

This project uses a `.env` file to store environment variables for database connectivity. These variables are essential for configuring the application to connect to the database securely.

## `.env` File Structure

The `.env` file contains the following key-value pairs:

| Variable                 | Description                                                              | Example Value                                                      
|------------------|----------------------------------------------|---------------------------------------------
| `DB_USERNAME`  | The username used to access the database. | `username`                                                                    
| `DB_PASSWORD`  | The password for the database user.               | `password`    
| `DB_HOST`           | The host address of the database server.       | `host url`                           
| `DB_PORT`           | The port number for database connections. | `port`                                                                  
| `DB_NAME`           | The name of the database to connect to.      | `db name`                                                              

## Usage

1. **Setting Up the `.env` File**  
   Create a file named `.env` in the root directory of your project. Copy the structure above and replace the placeholder values with the appropriate credentials provided by your database provider.

2. **Loading Environment Variables**  
   Use a library like [`python-dotenv`](https://pypi.org/project/python-dotenv/) (for Python) or equivalent for your programming language to load the `.env` file. For example, in Python:

   ```python
   from dotenv import load_dotenv
   import os

   load_dotenv()

   db_username = os.getenv('DB_USERNAME')
   db_password = os.getenv('DB_PASSWORD')
   db_host = os.getenv('DB_HOST')
   db_port = os.getenv('DB_PORT')
   db_name = os.getenv('DB_NAME')