# Warbler

This is a simplified Twitter clone using Flask for the backend PostgreSQL for the database and HTML and CSS for the frontend by the jinja templating that is integrated in with Flask. The site allows users to login/register, make posts, like posts, follow people, and more.

## SetUp Instructions

```
python -m venv venv
```

```
source venv/bin/activate
```

```
pip install -r requirements.txt
```

```
createdb warbler
```

```
python seed.py
```

```
flask run --debug
```

## Testing

```
createdb warbler-test
```

#### Example run 

```
python -m unittest test_message_model.py
```