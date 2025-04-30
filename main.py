import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.server.fast_server:app", host="0.0.0.0", port=10264, reload=True)
