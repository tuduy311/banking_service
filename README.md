# Banking AI Agent (submission package)

This folder contains the packaged project ready for submission. It follows the assignment structure and includes the backend API Gateway, intent gRPC service, Streamlit frontend, and an Ollama service via Docker Compose.

Contents
- `backend/` — FastAPI application (code under `backend/app/`), `Dockerfile`, and `requirements.txt`.
- `intent_service/` — gRPC intent service, `intent_service.proto`, generated stubs, `server.py`, `Dockerfile`, and `requirements.txt`.
- `frontend/` — Streamlit UI, `Dockerfile`, and `requirements.txt`.
- `docker-compose.yml` — Compose file to run all services together.
- `examples/sample_requests.json` — example inputs for demo and testing.
- `run.py` — convenience entrypoint to run the backend locally.
- `requirements.txt` — top-level pointer to service-specific requirements.

Quick checklist (matches `input.md` requirements):
- Project README with architecture, run/build instructions, and container roles: this file.
- Instructions to generate gRPC code from `.proto`: included below.
- Instructions to build Docker images and run with Docker Compose: included below.
- Example requests for demonstration: `examples/sample_requests.json`.

Video demo URL: <https://drive.google.com/drive/folders/15V56y_cG-nsURJvH1JeZLGVOvRzfPpvo?usp=sharing>

-----

## Architecture overview

The system is split into microservices:
- **API Gateway / Backend (FastAPI)**: exposes REST endpoints (`/run-agent`) and orchestrates nodes (intent → priority → policy → draft → validation → routing). Port: `8000`.
- **Intent Service (gRPC)**: serves the intent classifier as a gRPC server (`50051`), loads the fine-tuned Lab2 checkpoint from `/models/final_model` (mounted). Port: `50051`.
- **Frontend (Streamlit)**: simple UI to enter messages and call backend. Port: `8501`.
- **Ollama (LLM server)**: provides the response-generation model via HTTP API (default `11434`). Used by `DraftNode` when `ENABLE_LLM_DRAFTING=true`.

## Generate gRPC code (when `.proto` changes)

Run from the `banking-service/` folder (where `intent_service/` is located):

```bash
python -m pip install grpcio grpcio-tools protobuf
python -m grpc_tools.protoc -I intent_service --python_out=intent_service --grpc_python_out=intent_service intent_service/intent_service.proto
```

This regenerates `intent_service/intent_service_pb2.py` and `intent_service/intent_service_pb2_grpc.py`.

## Build Docker images

Build individual images (optional):

```bash
docker build -f backend/Dockerfile -t banking-backend .
docker build -f intent_service/Dockerfile -t intent-service .
docker build -f frontend/Dockerfile -t banking-frontend .
```

Or build all via Compose:

```bash
docker compose build
```

## Run the system with Docker Compose

From the `banking-service/` folder:

```bash
docker compose up --build
```

To run detached:

```bash
docker compose up -d --build
```

Notes:
- Ensure Docker Desktop (or Docker Engine) is running.
- The compose file mounts the intent model from `./checkpoints/final_model` into the intent-service container at `/models/final_model`. Provide the checkpoint locally or adjust the volume.
- To enable LLM drafting via Ollama, set `ENABLE_LLM_DRAFTING=true` and ensure `OLLAMA_BASE_URL` points to a reachable Ollama instance (default in compose is `http://ollama:11434`).

## Roles of containers (ports)

- `banking-backend` (FastAPI) — port `8000`: REST API, orchestration.
- `intent-service` (gRPC) — port `50051`: intent classification (loads checkpoint).
- `banking-frontend` (Streamlit) — port `8501`: UI.
- `banking-ollama` (Ollama) — port `11434`: LLM HTTP API.

## Example requests

See `examples/sample_requests.json` for demo messages used in the video.

## Run locally without Docker (development)

Install dependencies for backend and run the backend directly (development only):

```bash
python -m pip install -r backend/requirements.txt
python run.py
```

To run the frontend locally:

```bash
python -m pip install -r frontend/requirements.txt
streamlit run frontend/main.py --server.address=localhost --server.port=8501
```

To run intent service locally (requires heavy ML deps):

```bash
python -m pip install -r intent_service/requirements.txt
python -m intent_service.server
```

## Notes on submission

- The model checkpoint (`checkpoints/final_model`) is not included by default due to size. You can:
  - Provide the checkpoint folder when pushing, or
  - Host it externally and update `docker-compose.yml` to mount or download at container start.
- Replace `Video demo URL: <PASTE_YOUR_DEMO_VIDEO_LINK_HERE>` with your actual demo link before submitting.
- If you use a public GitHub repository for grading, make sure the files under `banking-service/` are pushed together with this README.

-----

If you want, I can also:
- Add `checkpoints/final_model` into this package (large files), or
- Create a zip archive of `banking-service/` ready for upload.
