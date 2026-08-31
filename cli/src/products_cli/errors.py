import json
import sys
import httpx


def handle_error(error: Exception) -> None:
    if isinstance(error, FileNotFoundError):
        message = str(error)

    elif isinstance(error, httpx.HTTPStatusError):
        try:
            data = error.response.json()
            message = data.get("detail", str(data))
        except ValueError:
            message = error.response.text or str(error)

    elif isinstance(error, httpx.RequestError):
        message = f"Unable to connect to API: {error}"

    else:
        message = str(error)

    print(
        json.dumps({"error": message}),
        file=sys.stderr,
    )

    raise SystemExit(1)