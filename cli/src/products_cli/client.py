import httpx

from .config import save_config

def login(base_url: str, username: str, password: str) -> dict:
    response = httpx.post(
        f"{base_url}/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )
    response.raise_for_status()
    return response.json()

def refresh_tokens(
    base_url: str,
    refresh_token: str,
) -> dict:
    response = httpx.post(
        f"{base_url}/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    response.raise_for_status()
    return response.json()

def authenticated_request(
    method: str,
    url: str,
    config: dict,
    **kwargs,
) -> httpx.Response:
    response = httpx.request(
        method,
        url,
        headers={
            "Authorization": f"Bearer {config['access_token']}",
        },
        **kwargs,
    )

    if response.status_code != 401:
        return response

    tokens = refresh_tokens(
        base_url=config["base_url"],
        refresh_token=config["refresh_token"],
    )

    config["access_token"] = tokens["access_token"]
    config["refresh_token"] = tokens["refresh_token"]

    save_config(
        base_url=config["base_url"],
        access_token=config["access_token"],
        refresh_token=config["refresh_token"],
    )

    return httpx.request(
        method,
        url,
        headers={
            "Authorization": f"Bearer {config['access_token']}",
        },
        **kwargs,
    )

def list_products(
    config: dict,
    section: str | None = None,
    name: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    has_discount: bool | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list:
    params = {}

    if section is not None:
        params["section"] = section

    if name is not None:
        params["name"] = name

    if min_price is not None:
        params["min_price"] = min_price

    if max_price is not None:
        params["max_price"] = max_price

    if has_discount is not None:
        params["has_discount"] = has_discount

    if limit is not None:
        params["limit"] = limit

    if offset is not None:
        params["offset"] = offset

    response = authenticated_request(
        "GET",
        f"{config['base_url']}/products",
        config,
        params=params,
    )

    response.raise_for_status()
    return response.json()["items"]

def get_product(
    config: dict,
    product_id: int,
) -> dict:
    response = authenticated_request(
        "GET",
        f"{config['base_url']}/products/{product_id}",
        config,
    )

    response.raise_for_status()
    return response.json()

def create_product(
    config: dict,
    name: str,
    section: str,
    description: str,
    price: float,
    discount: float,
) -> dict:
    response = authenticated_request(
        "POST",
        f"{config['base_url']}/products",
        config,
        json={
            "name": name,
            "section": section,
            "description": description,
            "price": price,
            "discount": discount,
        },
    )
    response.raise_for_status()
    return response.json()

def update_product(
    config: dict,
    product_id: int,
    name: str | None = None,
    section: str | None = None,
    description: str | None = None,
    price: float | None = None,
    discount: float | None = None,
) -> dict:
    payload = {}

    if name is not None:
        payload["name"] = name

    if section is not None:
        payload["section"] = section

    if description is not None:
        payload["description"] = description

    if price is not None:
        payload["price"] = price

    if discount is not None:
        payload["discount"] = discount

    response = authenticated_request(
        "PATCH",
        f"{config['base_url']}/products/{product_id}",
        config,
        json=payload,
    )

    response.raise_for_status()
    return response.json()

def delete_product(config: dict, product_id: int) -> None:
    response = authenticated_request(
        "DELETE",
        f"{config['base_url']}/products/{product_id}",
        config,
    )

    response.raise_for_status()

def batch_update_products(
    config: dict,
    section: str,
    discount: float,
) -> int:
    all_products = []
    offset = 0
    limit = 100

    while True:
        products = list_products(
            config=config,
            section=section,
            limit=limit,
            offset=offset,
        )

        if not products:
            break

        all_products.extend(products)

        if len(products) < limit:
            break

        offset += limit

    updated = 0

    for product in all_products:
        update_product(
            config=config,
            product_id=product["id"],
            discount=discount,
        )
        updated += 1

    return updated