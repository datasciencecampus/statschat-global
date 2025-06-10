# Server deployment

**In case of issues with server deployment try these steps below:**

```
nano .env
```
- Opens the `.env` file in the Nano text editor to edit the HF_TOKEN = ""
- HF_TOKEN is huggingface API token

```
sudo lsof -i :8000
```
- Lists all processes using port 8000.
- Checks if uvicorn is running on port 8000.
- Finds and kills conflicting processes if the port is "already in use".

```
ps aux | grep uvicorn
```
- Searches all running processes for uvicorn.
- Helps confirm that the FastAPI server is currently running.
- Can find the PID (process ID) to stop it manually if needed (kill).

```
uvicorn fast-api.main_api_local:app --host 0.0.0.0 --port 8000
```

- Starts the FastAPI server using uvicorn.

```
curl http://102.220.23.39:8000/search?q=what+was+inflation
```
Sends a test HTTP GET request to the FastAPI /search endpoint. Tests if the deployed server is: 
- running and reachable
- accepting and responding to queries (like a question about inflation)
