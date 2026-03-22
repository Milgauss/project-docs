# Frameworks and tools

Sections are ordered from **highest-level** (whole user-facing stacks, platforms, and orchestration) down to **lowest-level** (small libraries and single-purpose utilities). **When adding a new tool**, insert it into the first section whose scope fits (roughly: end-user app → web/API framework → **database access** → data/ML stack → cross-cutting ops → project tooling → parsing/IO glue). If unsure, place it **below** things that *use* it and **above** things it *depends on*. Within a table, put broader or “default” choices first when it helps scanning.

The first column in each table is narrow—put ✅ when a tool is a default choice (leave blank otherwise). **Within each table, rows with ✅ appear first.** Other columns: name, short description, homepage, and documentation.

## Frontend (JavaScript / TypeScript)


|     | Name         | Description                                                                                          | Homepage                                    | Documentation                                     |
| :-: | ------------ | ---------------------------------------------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------- |
| ✅   | Tailwind CSS | Utility-first CSS framework for rapid UI layout and design tokens in HTML/JSX.                       | [tailwindcss.com](https://tailwindcss.com/) | [Tailwind CSS docs](https://tailwindcss.com/docs) |
|     | Next.js 15   | React framework with App Router, server components, and built-in routing and optimizations.          | [nextjs.org](https://nextjs.org/)           | [Next.js docs](https://nextjs.org/docs)           |
|     | React        | UI library for building component trees; hooks, concurrent features, and a vast ecosystem.           | [react.dev](https://react.dev/)             | [React documentation](https://react.dev/learn)    |
|     | Vue          | Progressive framework (templates, composition API, SFCs) for SPAs and full-stack stacks (e.g. Nuxt). | [vuejs.org](https://vuejs.org/)             | [Vue documentation](https://vuejs.org/guide/)     |
|     | Svelte       | Compile-time UI framework; less runtime overhead, stores, and SvelteKit for full-stack apps.         | [svelte.dev](https://svelte.dev/)           | [Svelte documentation](https://svelte.dev/docs)   |
|     | Vite         | Fast dev server and front-end build tool (ESM, HMR); common with React, Vue, and Svelte.             | [vitejs.dev](https://vitejs.dev/)           | [Vite documentation](https://vitejs.dev/guide/)   |


## Python web frameworks and HTTP servers


|     | Name                        | Description                                                                                                 | Homepage                                                            | Documentation                                                                       |
| --- | --------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
|     | Django                      | Batteries-included web framework: ORM, admin, auth, templates, and a huge ecosystem.                        | [djangoproject.com](https://www.djangoproject.com/)                 | [Django documentation](https://docs.djangoproject.com/)                             |
|     | FastAPI                     | Modern async API framework with automatic OpenAPI docs, Pydantic models, and Starlette/Uvicorn stack.       | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)               | [FastAPI documentation](https://fastapi.tiangolo.com/)                              |
|     | Flask                       | Lightweight WSGI microframework; extensions for DB, forms, auth, and APIs.                                  | [flask.palletsprojects.com](https://flask.palletsprojects.com/)     | [Flask documentation](https://flask.palletsprojects.com/)                           |
|     | Django REST framework (DRF) | Toolkit for building Web APIs on Django: serializers, viewsets, browsable API, and authentication.          | [django-rest-framework.org](https://www.django-rest-framework.org/) | [DRF documentation](https://www.django-rest-framework.org/)                         |
|     | Tornado                     | Async networking library and web framework; long-lived connections, WebSockets, and non-blocking I/O.       | [tornadoweb.org](https://www.tornadoweb.org/)                       | [Tornado documentation](https://www.tornadoweb.org/en/stable/)                      |
|     | Pyramid                     | Flexible “start small, finish big” web framework; URL dispatch, traversal, and pluggable auth.              | [trypyramid.com](https://trypyramid.com/)                           | [Pyramid documentation](https://docs.pylonsproject.org/projects/pyramid/en/latest/) |
|     | Sanic                       | Async-first HTTP server and framework built on uvloop for high throughput APIs.                             | [sanic.dev](https://sanic.dev/)                                     | [Sanic documentation](https://sanic.readthedocs.io/)                                |
|     | aiohttp                     | Async client and server for HTTP (and WebSockets); often used to build services without a full “framework.” | [docs.aiohttp.org](https://docs.aiohttp.org/)                       | [aiohttp documentation](https://docs.aiohttp.org/)                                  |
|     | Bottle                      | Single-file micro WSGI framework with routing, templates, and built-in development server.                  | [bottlepy.org](https://bottlepy.org/)                               | [Bottle documentation](https://bottlepy.org/docs/dev/)                              |
|     | CherryPy                    | Minimal object-oriented HTTP framework; multi-threaded server and WSGI hosting.                             | [cherrypy.dev](https://cherrypy.dev/)                               | [CherryPy documentation](https://docs.cherrypy.dev/)                                |
|     | Falcon                      | Lean WSGI/ASGI framework focused on fast HTTP APIs and minimal overhead.                                    | [falconframework.org](https://falconframework.org/)                 | [Falcon documentation](https://falcon.readthedocs.io/)                              |
|     | web2py                      | Full-stack framework with web IDE, ticketing, and a Python-based DSL; integrated stack and admin.           | [web2py.com](http://www.web2py.com/)                                | [web2py book](http://web2py.com/book)                                               |
|     | Reflex                      | Pure-Python full-stack framework compiling to React/Next-style frontends; state, routing, and deployment.   | [reflex.dev](https://reflex.dev/)                                   | [Reflex documentation](https://reflex.dev/docs/)                                    |
|     | Starlette                   | Lightweight ASGI framework and toolkit; routing, middleware, WebSockets—FastAPI builds on it.               | [starlette.io](https://www.starlette.io/)                           | [Starlette documentation](https://www.starlette.io/)                                |


## Database access and ORM (Python)


|     | Name       | Description                                                                                          | Homepage                                      | Documentation                                            |
| --- | ---------- | ---------------------------------------------------------------------------------------------------- | --------------------------------------------- | -------------------------------------------------------- |
|     | SQLAlchemy | SQL toolkit and ORM: Core expressions, `Session`, migrations (Alembic ecosystem), and async support. | [sqlalchemy.org](https://www.sqlalchemy.org/) | [SQLAlchemy documentation](https://docs.sqlalchemy.org/) |


## Interactive web UIs (Python)


|     | Name             | Description                                                                                        | Homepage                                    | Documentation                                         |
| --- | ---------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------- | ----------------------------------------------------- |
|     | Streamlit        | Script-to-app UI for data and ML: widgets, charts, caching, and sharing as a web app.              | [streamlit.io](https://streamlit.io/)       | [Streamlit documentation](https://docs.streamlit.io/) |
|     | Dash (by Plotly) | Analytical web apps in Python (and R/Julia); Plotly components, callbacks, and enterprise options. | [plotly.com/dash](https://plotly.com/dash/) | [Dash documentation](https://dash.plotly.com/)        |
|     | Gradio           | Quick demos and APIs for ML models: inputs/outputs, sharing links, and Hugging Face Spaces.        | [gradio.app](https://www.gradio.app/)       | [Gradio documentation](https://www.gradio.app/docs/)  |


## Desktop and mobile GUI (Python)


|     | Name          | Description                                                                                        | Homepage                                                                                                                                    | Documentation                                                                                                      |
| --- | ------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
|     | PyQt / PySide | Qt bindings for desktop GUIs: widgets, QML, multimedia; PySide is Qt’s official LGPL distribution. | [riverbankcomputing.com/software/pyqt](https://www.riverbankcomputing.com/software/pyqt/) / [Qt for Python](https://doc.qt.io/qtforpython/) | [PyQt docs](https://www.riverbankcomputing.com/static/Docs/PyQt6/) · [PySide docs](https://doc.qt.io/qtforpython/) |
|     | Tkinter       | Standard-library GUI toolkit; windows, widgets, and event loop (look and feel varies by platform). | [Python docs — tkinter](https://docs.python.org/3/library/tkinter.html)                                                                     | [tkinter documentation](https://docs.python.org/3/library/tkinter.html)                                            |
|     | Kivy          | Open-source framework for multitouch UIs; targets desktop, mobile (iOS/Android), and Raspberry Pi. | [kivy.org](https://kivy.org/)                                                                                                               | [Kivy documentation](https://kivy.org/doc/stable/)                                                                 |


## Workflow orchestration and data pipelines


|     | Name           | Description                                                                                    | Homepage                                          | Documentation                                               |
| --- | -------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------- | ----------------------------------------------------------- |
|     | Dagster        | Data orchestration focused on software-defined assets and local dev ergonomics.                | [dagster.io](https://dagster.io/)                 | [Dagster docs](https://docs.dagster.io/)                    |
|     | Apache Airflow | Platform to author, schedule, and monitor workflows as directed acyclic graphs (DAGs).         | [airflow.apache.org](https://airflow.apache.org/) | [Airflow documentation](https://airflow.apache.org/docs/)   |
|     | Prefect        | Python-native workflow orchestration with hybrid execution and a managed cloud option.         | [prefect.io](https://www.prefect.io/)             | [Prefect docs](https://docs.prefect.io/)                    |
|     | Celery         | Distributed task queue: async jobs, schedules, retries; common with Redis/RabbitMQ and Django. | [celeryproject.org](https://celeryproject.org/)   | [Celery documentation](https://docs.celeryq.dev/en/stable/) |


## Developer platforms and APIs


|     | Name                    | Description                                                                            | Homepage                                                      | Documentation                                                                |
| --- | ----------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------- |
|     | Google (for developers) | APIs and guides across Android, web, Workspace, Maps, AI, and related Google products. | [developers.google.com](https://developers.google.com/)       | [Developer products & documentation](https://developers.google.com/products) |
|     | AWS (for developers)    | Cloud APIs and SDKs: compute, storage, databases, AI/ML, and infrastructure as code.   | [aws.amazon.com/developer](https://aws.amazon.com/developer/) | [AWS documentation](https://docs.aws.amazon.com/)                            |
|     | Microsoft Azure         | Cloud services, AI, data, identity, and enterprise integrations on Azure.              | [azure.microsoft.com](https://azure.microsoft.com/)           | [Azure documentation](https://learn.microsoft.com/azure/)                    |
|     | Cloudflare              | Edge network: Workers, R2, DNS, security, and developer platform APIs.                 | [cloudflare.com](https://www.cloudflare.com/)                 | [Cloudflare Developers](https://developers.cloudflare.com/)                  |


## Web data and proxies


|     | Name        | Description                                                                            | Homepage                                  | Documentation                                    |
| :-: | ----------- | -------------------------------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------------ |
| ✅   | Bright Data | Web data collection platform: proxies, scraping browser, datasets, and unblocker APIs. | [brightdata.com](https://brightdata.com/) | [Bright Data docs](https://docs.brightdata.com/) |


## AI agents and messaging automation


|     | Name     | Description                                                                                | Homepage                            | Documentation                              |
| --- | -------- | ------------------------------------------------------------------------------------------ | ----------------------------------- | ------------------------------------------ |
|     | OpenClaw | Self-hosted gateway connecting chat apps (WhatsApp, Telegram, Discord, etc.) to AI agents. | [openclaw.ai](https://openclaw.ai/) | [OpenClaw docs](https://docs.openclaw.ai/) |


## LLM and NLP frameworks (Python)


|     | Name                      | Description                                                                                                   | Homepage                                    | Documentation                                                          |
| --- | ------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------- | ---------------------------------------------------------------------- |
|     | LangChain                 | Composition layer for LLM apps: chains, agents, tools, vector stores, and integrations with many model APIs.  | [langchain.com](https://www.langchain.com/) | [LangChain docs](https://docs.langchain.com/)                          |
|     | Hugging Face Transformers | Pretrained models and training APIs for NLP, vision, audio, and more; `pipeline`, `Trainer`, and Hub weights. | [huggingface.co](https://huggingface.co/)   | [Transformers documentation](https://huggingface.co/docs/transformers) |
|     | LlamaIndex                | Data framework for LLM apps: ingestion, indexes, query engines, and RAG over your sources.                    | [llamaindex.ai](https://www.llamaindex.ai/) | [LlamaIndex documentation](https://docs.llamaindex.ai/)                |


## Deep learning (Python)


|     | Name       | Description                                                                                                               | Homepage                                      | Documentation                                                       |
| --- | ---------- | ------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- | ------------------------------------------------------------------- |
|     | PyTorch    | Tensor computation and automatic differentiation for deep learning; dynamic graphs, GPU/CPU/MPS, `torch.nn`, and tooling. | [pytorch.org](https://pytorch.org/)           | [PyTorch documentation](https://pytorch.org/docs/stable/index.html) |
|     | TensorFlow | End-to-end platform for training and deploying models; graphs, `tf.keras`, TFX, and device acceleration.                  | [tensorflow.org](https://www.tensorflow.org/) | [TensorFlow guide](https://www.tensorflow.org/guide)                |
|     | Keras      | High-level neural-network API (multi-backend in Keras 3); composable layers, trainers, and Hugging Face integration.      | [keras.io](https://keras.io/)                 | [Keras guides](https://keras.io/guides/)                            |


## Machine learning (Python)


|     | Name         | Description                                                                                            | Homepage                                                               | Documentation                                                              |
| :-: | ------------ | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------- | -------------------------------------------------------------------------- |
|     | Scikit-learn | Classical ML: estimators, pipelines, preprocessing, model selection, and metrics in NumPy/SciPy.       | [scikit-learn.org](https://scikit-learn.org/)                          | [scikit-learn user guide](https://scikit-learn.org/stable/user_guide.html) |
|     | XGBoost      | Gradient-boosted trees for tabular data; fast training, distributed support, and multiple APIs.        | [xgboost.ai](https://xgboost.ai/)                                      | [XGBoost documentation](https://xgboost.readthedocs.io/)                   |
|     | LightGBM     | Gradient boosting from Microsoft; leaf-wise trees, speed on large tabular data, and sklearn-style API. | [github.com/microsoft/LightGBM](https://github.com/microsoft/LightGBM) | [LightGBM documentation](https://lightgbm.readthedocs.io/)                 |
|     | CatBoost     | Gradient boosting with strong categorical feature handling and GPU training from Yandex.               | [catboost.ai](https://catboost.ai/)                                    | [CatBoost documentation](https://catboost.ai/docs/)                        |


## Data analysis and interactive computing (Python)


|     | Name    | Description                                                                                               | Homepage                                        | Documentation                                                             |
| --- | ------- | --------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------- |
|     | Jupyter | Notebooks and interactive computing (JupyterLab, kernels); explore data and share reproducible workflows. | [jupyter.org](https://jupyter.org/)             | [Jupyter documentation](https://docs.jupyter.org/)                        |
|     | Pandas  | DataFrames and Series for labeled tabular data: alignment, groupby, time series, and I/O.                 | [pandas.pydata.org](https://pandas.pydata.org/) | [pandas user guide](https://pandas.pydata.org/docs/user_guide/index.html) |
|     | Polars  | Fast DataFrame library (Rust core); lazy queries, Arrow-friendly, Python-first API.                       | [pola.rs](https://pola.rs/)                     | [Polars documentation](https://docs.pola.rs/)                             |
|     | NumPy   | N-dimensional arrays, broadcasting, linear algebra, and RNG—the numeric base for SciPy/pandas.            | [numpy.org](https://numpy.org/)                 | [NumPy documentation](https://numpy.org/doc/stable/)                      |


## Observability and logging


|     | Name             | Description                                                                        | Homepage                                              | Documentation                                      |
| --- | ---------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------- | -------------------------------------------------- |
|     | Pydantic Logfire | Observability and structured logging from the Pydantic team (OpenTelemetry-based). | [logfire.pydantic.dev](https://logfire.pydantic.dev/) | [Logfire docs](https://logfire.pydantic.dev/docs/) |


## Testing and automation


|     | Name       | Description                                                                             | Homepage                                  | Documentation                                                     |
| :-: | ---------- | --------------------------------------------------------------------------------------- | ----------------------------------------- | ----------------------------------------------------------------- |
| ✅   | pytest     | Python testing framework with fixtures, parametrization, and a rich plugin ecosystem.   | [pytest.org](https://pytest.org/)         | [pytest documentation](https://docs.pytest.org/)                  |
|     | Playwright | End-to-end browser automation and testing across Chromium, Firefox, and WebKit.         | [playwright.dev](https://playwright.dev/) | [Playwright docs](https://playwright.dev/docs/intro)              |
|     | Selenium   | Browser automation and WebDriver ecosystem; cross-browser testing and grid deployments. | [selenium.dev](https://www.selenium.dev/) | [Selenium documentation](https://www.selenium.dev/documentation/) |


## Python packaging and environments


|     | Name        | Description                                                                                          | Homepage                                                   | Documentation                                  |
| --- | ----------- | ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------- |
|     | Poetry      | Dependency and packaging manager for Python projects; lockfiles, virtualenvs, and publishing.        | [python-poetry.org](https://python-poetry.org/)            | [Poetry docs](https://python-poetry.org/docs/) |
|     | uv (Astral) | Fast Python package and project manager (Rust); installs Python, manages envs, lockfiles, and tools. | [github.com/astral-sh/uv](https://github.com/astral-sh/uv) | [uv docs](https://docs.astral.sh/uv/)          |


## Command-line interfaces (Python)


|     | Name  | Description                                                     | Homepage                                          | Documentation                                      |
| :-: | ----- | --------------------------------------------------------------- | ------------------------------------------------- | -------------------------------------------------- |
| ✅   | Typer | Builds CLIs with type hints and automatic help, built on Click. | [typer.tiangolo.com](https://typer.tiangolo.com/) | [Typer documentation](https://typer.tiangolo.com/) |


## Data validation and settings


|     | Name     | Description                                                                                            | Homepage                              | Documentation                                        |
| :-: | -------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------- | ---------------------------------------------------- |
| ✅   | Pydantic | Data validation, serialization, and settings using type annotations (v2 is the current major release). | [pydantic.dev](https://pydantic.dev/) | [Pydantic documentation](https://docs.pydantic.dev/) |


## HTTP client (Python)


|     | Name     | Description                                                                      | Homepage                                                   | Documentation                                                        |
| :-: | -------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------- |
| ✅   | httpx    | Modern async-capable HTTP client for Python with HTTP/2 and a requests-like API. | [python-httpx.org](https://www.python-httpx.org/)          | [HTTPX documentation](https://www.python-httpx.org/)                 |
|     | Requests | De facto sync HTTP library for Python; sessions, auth hooks, and huge mindshare. | [github.com/psf/requests](https://github.com/psf/requests) | [Requests documentation](https://requests.readthedocs.io/en/latest/) |


## YouTube transcripts (Python)


|     | Name                   | Description                                                                     | Homepage                                                                                       | Documentation                                                                             |
| --- | ---------------------- | ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
|     | youtube-transcript-api | Retrieves transcripts / captions for YouTube videos without a headless browser. | [github.com/jdepoix/youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) | [youtube-transcript-api README](https://github.com/jdepoix/youtube-transcript-api#readme) |


## Content conversion (Python)


|     | Name        | Description                                                           | Homepage                                                                                             | Documentation                                                       |
| :-: | ----------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| ✅   | Markdownify | Converts HTML to Markdown, useful for scraping and cleanup pipelines. | [github.com/matthewwithanm/python-markdownify](https://github.com/matthewwithanm/python-markdownify) | [Markdownify on Read the Docs](https://markdownify.readthedocs.io/) |


## HTML and XML parsing (Python)


|     | Name             | Description                                                                        | Homepage                                                                            | Documentation                                                                 |
| :-: | ---------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| ✅   | Beautiful Soup 4 | Pulls data out of HTML and XML with forgiving parsers and a simple navigation API. | [crummy.com/software/BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) | [Beautiful Soup docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) |


## Serialization (Python)


|     | Name   | Description                                                               | Homepage                          | Documentation                                                       |
| :-: | ------ | ------------------------------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------- |
| ✅   | PyYAML | YAML parser and emitter for Python; load/dump config and structured data. | [pyyaml.org](https://pyyaml.org/) | [PyYAML documentation](https://pyyaml.org/wiki/PyYAMLDocumentation) |


## Environment and configuration (Python)


|     | Name          | Description                                                                           | Homepage                                                                         | Documentation                                                             |
| :-: | ------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| ✅   | python-dotenv | Reads key-value pairs from a `.env` file into the process environment (`os.environ`). | [github.com/theskumar/python-dotenv](https://github.com/theskumar/python-dotenv) | [python-dotenv README](https://github.com/theskumar/python-dotenv#readme) |


