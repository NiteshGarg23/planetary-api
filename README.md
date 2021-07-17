#create virtual environment

##python -m venv venv


###activate virtual environment

####for windows
.\venv\Scripts\activate.bat

for linux
source ./venv/bin/activate


install dependencies

pip install -r requirements.txt


create database file

flask db_create


seed database

flask db_seed


to drop database use 

flask db_drop


run

flask run
