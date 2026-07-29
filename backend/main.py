"""Local dev entrypoint: `python main.py` or `uvicorn main:app --reload`."""

from jewelmind.api.app import app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
