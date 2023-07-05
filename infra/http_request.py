import os
from requests import adapters, exceptions, Response, Session


def request(
    url: str,
    retries: int = 60,
    timeout: int = 10,
    method="get",
    data=None,
    headers=None,
) -> Response:
    session = Session()
    session.mount("http://", adapters.HTTPAdapter(max_retries=retries))
    if os.getenv("BACKEND") == "VM":
        timeout += 100

    method = {
        "get": session.get,
        "post": session.post,
    }[method.lower()]

    while retries > 0:
        try:
            response = method(
                url,
                data=data,
                headers=headers,
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
