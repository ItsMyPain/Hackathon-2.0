# Hackathon-2.0

## Install requirements

```
pip install -r .\requirements.txt
```

## Start server

[Development](http://127.0.0.1:5000)

```
flask --app server:app run --debug
```

[Production](http://127.0.0.1:8080)

```
waitress-serve --host 127.0.0.1 server:app
```

For start server you need to specify `config.py` file.

## Pages

One page - `/`
