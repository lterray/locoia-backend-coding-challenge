# GistAPI

The app now contains one feature:
You can search among public gists of a GitHub user. Usage information below.

## Start with docker

1. Clone the project code
2. Run `docker build -t <your-docker-image-tag> .`
3. Run `docker run <your-docker-image-tag>`

## Start without docker

1. Clone the project code
2. Install [Poetry](https://python-poetry.org/docs/) package manager if you don't have it
3. Run `poetry install`
4. Run `poetry run python main.py`

## Use the gist search

Open the search on http://127.0.0.1:9876/api/v1/search with query parameters "username" and "pattern" for example:
http://127.0.0.1:9876/api/v1/search?username=justdionysus&pattern=import%20requests

## Run tests

1. First build the env like in section [Start without docker](#start-without-docker)
2. Run `poetry run pytest`

## Code quality checkers

I used [pep8](https://peps.python.org/pep-0008/) under pyCharm IDE to warn me if the code gets ugly.