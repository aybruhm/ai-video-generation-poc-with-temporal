# Video Generation Pipeline with Temporal

Proof of concept for orchestrating an AI video generation pipeline (AI Provider → S3 → token deduction → DB) using Temporal workflows and activities with FastAPI.

## Author's Note

At my last role, I led the migration of an AI film production platform — where thousands of generations were being processed every day — from Streamlit to React/TypeScript and FastAPI/Python.

The generation pipeline I settled on at the time looked like this:

```
AI Provider completes generation → deduct tokens → offload to Celery → upload to S3 → save to DB
```

As you can already imagine, this pipeline had a structural reliability problem: failure modes that Celery couldn't protect against. Some examples:

- AI Provider succeeds, token deduction crashes → tokens never deducted, but the Celery task starts anyway
- Celery task starts, S3 upload succeeds, DB write crashes → result lost, no way to retry just the DB step
- Worker process dies mid-task → job silently disappears unless you've manually wired dead-letter queues
- No introspection — you can't see what stage a generation is in without querying multiple systems

These were problems I had to work around for longer than I should have. Before my contract ended, I proposed a solution that was accepted, but in hindsight — if I had remembered that Temporal already solved this problem — I wouldn't have needed to reinvent it.

This POC is my redemption: what I would have built instead. It was designed with production-readiness in mind, though I intentionally left out some improvements to avoid over-engineering. At its core, it uses hexagonal architecture and the repository pattern for the data layer.

## Project Structure

```
.
├── Dockerfile
├── LICENSE
├── README.md
├── alembic.ini
├── apis
│   └── fastapi
│       └── routes
│           ├── auth.py
│           ├── dtos.py
│           └── video.py
├── compose.yml
├── core
│   ├── generations
│   │   ├── __init__.py
│   │   ├── dtos.py
│   │   └── service.py
│   ├── temporal
│   │   ├── __init__.py
│   │   ├── activities
│   │   │   ├── __init__.py
│   │   │   ├── falai.py
│   │   │   ├── storage.py
│   │   │   └── tokens.py
│   │   ├── types.py
│   │   ├── worker.py
│   │   └── workflows
│   │       ├── __init__.py
│   │       └── video_generation.py
│   ├── tokens
│   │   ├── __init__.py
│   │   ├── dtos.py
│   │   └── service.py
│   └── users
│       ├── __init__.py
│       ├── auth.py
│       ├── dtos.py
│       └── service.py
├── dbs
│   └── inmemory
│       ├── __init__.py
│       ├── base.py
│       ├── engine.py
│       ├── generations
│       │   ├── __init__.py
│       │   ├── dao.py
│       │   ├── dbes.py
│       │   └── interfaces.py
│       ├── tokens
│       │   ├── __init__.py
│       │   ├── dao.py
│       │   ├── dbes.py
│       │   └── interfaces.py
│       └── users
│           ├── __init__.py
│           ├── dao.py
│           ├── dbes.py
│           └── interfaces.py
├── main.py
├── makefile
├── middlewares
│   ├── __init__.py
│   └── jwt_bearer.py
├── migrations
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   └── versions
│       └── 0ef757c71b03_initial_migrations.py
├── pyproject.toml
├── services
│   ├── __init__.py
│   ├── dependencies
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── temporal.py
│   │   └── types.py
│   └── exceptions.py
├── tests
│   ├── __init__.py
│   └── manual
│       ├── create_account.py
│       └── run_generations.py
├── utils
│   ├── env_utils.py
│   ├── jwt.py
│   └── password.py
└── uv.lock
```

## Installation

After cloning the repository, install dependencies using uv:

```bash
uv sync
```

## Usage

### 1. Configure environment

Copy the template and fill in your values — the application will not start without them:

```bash
cp .env.template .env
```

### 2. Run the application

```bash
make run
```

> **Note:** Every `make run` resets the SQLite database. You must re-run migrations after each restart.

### 3. Apply schema migrations

```bash
make run_migrations
```

### 4. Run the video generation workflow

The generation workflow is exposed via `/api/generations/`. You can inspect the workflow definition [here](https://github.com/aybruhm/ai-video-generation-poc-with-temporal/blob/main/core/temporal/workflows/video_generation.py).

To trigger it end-to-end using the included test script:

```bash
uv run -m tests.manual.run_generations
```

#### Expected output

```
============================================================================
Testing server connection...
Server is up and running.
============================================================================
Account created for 05430c
Logging in as 05430c...
============================================================================
Logged in as 05430c
Access token: eyJhbGciOiJIUzI1NiIsI...
============================================================================
Generation created: 8798d9cb-1f82-4aef-a770-20200587a57e - Status: queued - Workflow ID: video-gen-8798d9cb-1f82-4aef-a770-20200587a57e
============================================================================
Polling status for generation: 8798d9cb-1f82-4aef-a770-20200587a57e
Status: RUNNING
...
Status: COMPLETED
```

You should also see the workflow execution traced in your worker container logs:

```
INFO:temporalio.workflow:Starting VideoGenerationWorkflow for generation 8798d9cb-1f82-4aef-a770-20200587a57e
INFO:temporalio.activity:Starting FAL.AI generation for 8798d9cb-1f82-4aef-a770-20200587a57e
INFO:httpx:HTTP Request: POST https://fal.run/fal-ai/veo3.1/fast "HTTP/1.1 200 OK"
INFO:temporalio.activity:FAL.AI returned URL for 8798d9cb-1f82-4aef-a770-20200587a57e: https://v3b.fal.media/files/b/xxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxx.mp4
INFO:httpx:HTTP Request: GET https://v3b.fal.media/files/b/xxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxx.mp4 "HTTP/1.1 200 OK"
INFO:temporalio.activity:Uploaded 8798d9cb-1f82-4aef-a770-20200587a57e to https://generations.s3.amazonaws.com/videos/45dd048f-71d3-4433-ae29-e0664c90e82b/8798d9cb-1f82-4aef-a770-20200587a57e.mp4
INFO:temporalio.activity:Deducted 20 tokens from user 45dd048f-71d3-4433-ae29-e0664c90e82b
INFO:temporalio.activity:Saved result for 8798d9cb-1f82-4aef-a770-20200587a57e
INFO:temporalio.workflow:VideoGenerationWorkflow completed for 8798d9cb-1f82-4aef-a770-20200587a57e
```


### 5. Stop the application

```bash
make stop
```