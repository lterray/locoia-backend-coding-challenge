FROM python:3.9-alpine

ARG YOUR_ENV

RUN apk update && apk add python3-dev \
                        gcc \
                        libc-dev \
                        libffi-dev

ENV YOUR_ENV=${YOUR_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.3.2

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project initialization:
# RUN poetry config virtualenvs.in-project true
RUN poetry config virtualenvs.create false --local
RUN poetry install --no-root $(test  "$YOUR_ENV" == production && echo "--no-dev") --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY . /code

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN chown -R appuser /code
USER appuser

# Run Application
EXPOSE 9876
CMD [ "poetry", "run", "python", "main.py"]