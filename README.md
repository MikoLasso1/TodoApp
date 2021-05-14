# TodoApp
Open project directory

Create Python virtualenv, 
    virtualenv venv/
    
Activate the virtual environment
    source venv/bin/activate

Install all packages by
    pip install -r requirements.txt

then migrate the databse by
    python3 migrate.py

start the flask server
    export FLASK_APP=todos
    flask run

register a new account and use it
