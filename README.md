## AI Cookbook

This repo contains a collection of AI recipes/patterns built using [phidata](https://github.com/phidatahq/phidata)

- [Full documentation](https://docs.phidata.com/ai-cookbook)

## Run locally using docker

### Setup

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

6. Optional: Create `.env` file:

```sh
cp example.env .env
```

### Run Cookbook locally

1. Install [docker desktop](https://www.docker.com/products/docker-desktop)

2. Set OpenAI Key

Set the `OPENAI_API_KEY` environment variable using

```sh
export OPENAI_API_KEY=sk-***
```

**OR** set in the `.env` file

3. Start the workspace using:

```sh
phi ws up
```

- Open [localhost:8501](http://localhost:8501) to view the Streamlit App.
- Open [localhost:8000/docs](http://localhost:8000/docs) to view the FastApi docs.
- If Jupyter is enabled, open [localhost:8888](http://localhost:8888) to view JupyterLab UI.

4. Stop the workspace using:

```sh
phi ws down
```
