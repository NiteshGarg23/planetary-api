# Create virtual environment
python -m venv venv

# Activate virtual environment
## For windows
.\venv\Scripts\activate.bat

## For ubuntu
source ./venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Create database file
flask db_create

# Seed database
flask db_seed

# To drop the database, use 
flask db_drop

# Run
flask run
