import os
from requests import adapters, exceptions, Response, Session


def request(url: str, retries: int = 60, timeout: int = 10) -> Response:
    session = Session()
    session.mount("http://", adapters.HTTPAdapter(max_retries=retries))
    if os.getenv("BACKEND") == "VM":
        timeout += 100

    while retries > 0:
        try:
            response = session.get(
                url,
                timeout=timeout,
            )
            return response
        except exceptions.ConnectionError:
            ...
        except exceptions.Timeout:
            timeout * 1.5
        finally:
            retries -= 1

    raise exceptions.ConnectionError()
