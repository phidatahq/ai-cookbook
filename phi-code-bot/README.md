### 1. Create a virtual environment

```shell
python3 -m venv ~/.venvs/discord-env
source ~/.venvs/discord-env/bin/activate
```

### 2. Export `OPENAI_API_KEY` and `DISCORD_BOT_TOKEN`

```shell
export OPENAI_API_KEY=***
export DISCORD_BOT_TOKEN=***
```

### 3. Run redis and PGvector docker containers

```shell
docker run --name redis -p 6379:6379 -d redis

docker run -d \
  -e POSTGRES_DB=ai \
  -e POSTGRES_USER=ai \
  -e POSTGRES_PASSWORD=ai \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v pgvolume:/var/lib/postgresql/data \
  -p 5532:5432 \
  --name pgvector \
  phidata/pgvector:16
```

### 3. Install libraries

```shell
pip install -r requirements.txt
```

### 4. Run the bot

```shell
python main.py
```
