# AI Cookbook

This repo contains a collection of AI recipes/patterns built using [phidata](https://github.com/phidatahq/phidata)

- [Full documentation](https://docs.phidata.com/ai-cookbook)

## Live Demos

The AI cookbook apps are live and can be accessed at:

- <a href="https://hn.aidev.run/" target="_blank" rel="noopener noreferrer">HackerNews AI</a> that interacts with the HN API to summarize stories, users, find out what's trending, summarize topics.
- <a href="https://demo.aidev.run/" target="_blank" rel="noopener noreferrer">Streamlit App</a> serving a PDF, Image and Website Assistant (password: admin)
- <a href="https://api.aidev.run/docs" target="_blank" rel="noopener noreferrer">FastApi </a> serving a PDF Assistant.

## Setup

1. Clone the git repo

> from the `ai-cookbook` dir:

2. Create + activate a virtual env:

```sh
python3 -m venv aienv
source aienv/bin/activate
```

3. Install `phidata`:

```sh
pip install phidata
```

4. Setup workspace:

```sh
phi ws setup
```

5. Copy `workspace/example_secrets` to `workspace/secrets`:

```sh
cp -r workspace/example_secrets workspace/secrets
```

6. Copy `.env` file:

```sh
cp example.env .env
```

7. Update `.env` file:

- Set the AI apps like `HACKERNEWS_AI` you'd like to enable as True
- Set your `OPENAI_API_KEY`

```sh
HACKERNEWS_AI=True
# OPENAI_API_KEY=sk-***
```

- You can also export these as environment variable like:

```sh
export OPENAI_API_KEY=sk-***
```

## Run AI Cookbook locally

1. Install [docker desktop](https://www.docker.com/products/docker-desktop)

2. Start the workspace using:

```sh
phi ws up
```

- Open [localhost:8501](http://localhost:8501) to view the Streamlit App.
- Open [localhost:8000/docs](http://localhost:8000/docs) to view the FastApi docs.
- If HackerNews AI is enabled, open [localhost:8502](http://localhost:8502) to view HackerNews AI.
- If Jupyter is enabled, open [localhost:8888](http://localhost:8888) to view JupyterLab UI.

3. Stop the workspace using:

```sh
phi ws down
```
