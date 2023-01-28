[![Python package test](https://github.com/jayhere1/Kraken_api/actions/workflows/test.yml/badge.svg)](https://github.com/jayhere1/Kraken_api/actions/workflows/test.yml)
# Solution:

A webapp built using FastAPI and aiohttp for async requests.
Needs a .env file with the api key in format:

```
api_key = <key>
```

Can be installed and run with 

```
pip install -r requirements.txt
python main.py
```

Alternatively (If poetry installed):

```
poetry run python main.py
```

Or:
```
docker-compose up  
```

- Outages endpoint:  http://127.0.0.1:8000/outages
- Site-info: http://127.0.0.1:8000/site/{site_id}

## For testing:

 ```
pip install -r requirements.txt
pytest
 ```

 - With poetry: 

```
poetry run pytest
```

- In docker container:
```
docker-compose up -d  
docker exec -it kf_backend_test-web-1 bash

pytest
```