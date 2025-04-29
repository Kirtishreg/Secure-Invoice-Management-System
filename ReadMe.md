### Setup the application
set FLASK_APP=app.py

flask db init
flask db migrate -m ""
flask db upgrade


### Run the Application

```bash
flask run
```
# Capstone
