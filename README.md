ElephantChat
=============

A small Django project that simulates restaurant conversations between a waiter and a customer using OpenAI chat models. The project includes a simple app `RestaurantSimulator` with models to store simulated chat threads and messages, a simulator that drives two stateful bots, and a Tailwind/DaisyUI theme for the UI.

Quick overview
--------------
- Framework: Django >= 6.0.2
- Python: >= 3.14
- Styling: Tailwind (integrated via the `theme` app)
- AI: OpenAI Python client (OpenAI API key required)
- Static serving: Whitenoise

Contents
--------
- `ElephantChat/` — Django project settings and WSGI/ASGI entrypoints
- `RestaurantSimulator/` — main app: models, simulator logic, management commands
- `theme/` — Tailwind/DaisyUI theme app with `static_src`
- `manage.py` — Django management wrapper
- `Dockerfile`, `docker-compose.yml` — containerized development setup

Requirements
------------
The project dependencies are declared in `pyproject.toml`.
Minimum requirements:
- Python 3.14+
- Node.js (for Tailwind build) — Node 25 used in the Docker image

Environment variables
---------------------
The app uses `environs` to load environment variables. Common variables used by the project:

- SECRET_KEY (string) — Django secret key
- DEBUG (bool) — set to `True` or `False`
- OPENAI_KEY (string) — OpenAI API key used by the simulator
- WEBSITE_HOSTNAME (comma-separated list) — optional, used for `ALLOWED_HOSTS` in production

Development setup
-------------------------------
Run `docker compose up`


Simulator
------------------
The simulator uses the OpenAI client. Make sure `OPENAI_KEY` is set. The simulation code lives in `RestaurantSimulator/simulator/` and includes:

- `chatbot.py` — small wrapper around the OpenAI
- `tasks.py` — tasked give given in the assigment

open terminal in the django-web-server docker container and run python manage.py simulate_chats
