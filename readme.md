# Environment Configuration

This project uses a `.env` file to store environment variables for database connectivity. These variables are essential for configuring the application to connect to the database securely.

## `.env` File Structure

The `.env` file contains the following key-value pairs:


```
USE_SQLITE=true

APP_SECRET=example_secret

DB_USERNAME=username
DB_PASSWORD=password
DB_HOST=host
DB_PORT=port
DB_NAME=db_name
```

## Usage

1. **Setting Up the `.env` File**  
   Create a file named `.env` in the root directory of your project. Copy the structure above and replace the placeholder values with the appropriate credentials provided by your database provider if you are not using sqlite.

2. **Loading Environment Variables**  
   Use a library like [`python-dotenv`](https://pypi.org/project/python-dotenv/) (for Python) or equivalent for your programming language to load the `.env` file. For example, in Python:

   ```python
   from dotenv import load_dotenv
   import os

   load_dotenv()

   app_secret = os.getenv('APP_SECRET')

   sqlite_bool = os.getenv('USE_SQLITE')

   if sqlite_bool == 'true':
      db_uri_string = 'sqlite:///auth.sqlite'
   else:
      db_username = os.getenv("DB_USERNAME")
      db_password = os.getenv("DB_PASSWORD")
      db_host = os.getenv("DB_HOST")
      db_port = os.getenv("DB_PORT")
      db_name = os.getenv("DB_NAME")
      db_uri_string = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
   ```