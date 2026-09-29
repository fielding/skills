import urllib.request


def get(url: str, timeout: float = 10.0) -> bytes:
    """Fetch a URL once. No retries yet."""
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read()
