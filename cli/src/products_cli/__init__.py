"""Products CLI — starter package.

Implement the commands described in README.md. Entry point: `main()`.
Run with: `uv run products-cli ...`
"""

import argparse
import json

from .client import (
    login,
    list_products,
    get_product,
    create_product,
    update_product,
    delete_product,
    batch_update_products,
)

from .errors import handle_error
from .config import load_config, save_config

def main() -> None:
    parser = argparse.ArgumentParser(description="Product management CLI")

    subparsers = parser.add_subparsers(dest="command")

    # Login parser
    login_parser = subparsers.add_parser("login", help="Log in to the API")
    login_parser.add_argument('--base-url', required=True, help="Base url of Products API")
    login_parser.add_argument('--username', required=True, help="Username for login")
    login_parser.add_argument('--password', required=True, help="Password for login")

    # Products parser
    products_parser = subparsers.add_parser("products", help="Manage Products")
    products_subparsers = products_parser.add_subparsers(dest="products_command")

    # Products list subparser
    list_parser = products_subparsers.add_parser("list", help="List products")
    list_parser.add_argument("--section", help="Filter by section")
    list_parser.add_argument("--name", help="Filter by product name")
    list_parser.add_argument("--min-price", type=float, help="Minimum price")
    list_parser.add_argument("--max-price", type=float, help="Maximum price")
    
    discount_group = list_parser.add_mutually_exclusive_group()
    discount_group.add_argument("--has-discount", dest="has_discount", action="store_true")
    discount_group.add_argument("--no-discount", dest="has_discount", action="store_false")
    
    list_parser.add_argument("--limit", type=int)
    list_parser.add_argument("--offset", type=int)

    list_parser.set_defaults(has_discount=None)

    # Products get subparser
    get_parser = products_subparsers.add_parser("get", help="Get a product by ID")
    get_parser.add_argument("--id", type=int, required=True, help="Product ID")

    # Products create subparser
    create_parser = products_subparsers.add_parser("create", help="Create a product")
    create_parser.add_argument("--name", required=True)
    create_parser.add_argument("--section", required=True)
    create_parser.add_argument("--description", default="")   
    create_parser.add_argument("--price", type=float, required=True)
    create_parser.add_argument("--discount", type=float, default=0.0)
    
    # Products update subparser
    update_parser = products_subparsers.add_parser("update", help="Update a product")
    update_parser.add_argument("--id", type=int, required=True, help="Product ID")
    update_parser.add_argument("--name")
    update_parser.add_argument("--section")
    update_parser.add_argument("--description")
    update_parser.add_argument("--price", type=float)
    update_parser.add_argument("--discount", type=float)

    # Products delete subparser
    delete_parser = products_subparsers.add_parser("delete", help="Delete a product")
    delete_parser.add_argument("--id", type=int, required=True, help="Product ID")
    
    # Products batch update subparser
    batch_update_parser = products_subparsers.add_parser("batch-update", help="Update multiple products")
    batch_update_parser.add_argument("--section", required=True, help="Section to update",)
    batch_update_parser.add_argument("--discount", type=float, required=True, help="Discount to apply")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return
    try:
        if args.command == "login":
            tokens = login(
                base_url=args.base_url,
                username=args.username,
                password=args.password,
            )
            save_config(
                base_url=args.base_url,
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
            )
            print('{"status": "ok"}')
        
        elif args.command == "products":
            if args.products_command is None:
                products_parser.print_help()

            elif args.products_command == "list":
                config = load_config()
                products = list_products(
                    config=config,
                    section=args.section,
                    name=args.name,
                    min_price=args.min_price,
                    max_price=args.max_price,
                    has_discount=args.has_discount,
                    limit=args.limit,
                    offset=args.offset,
                )
                print(json.dumps(products))
            
            elif args.products_command == "get":
                config = load_config()
                product = get_product(
                    config=config,
                    product_id=args.id,
                )
                print(json.dumps(product))

            elif args.products_command == "create":
                config = load_config()

                product = create_product(
                    config=config,
                    name=args.name,
                    section=args.section,
                    description=args.description,
                    price=args.price,
                    discount=args.discount,
                )
                print(json.dumps(product))

            elif args.products_command == "update":
                config = load_config()
                product = update_product(
                    config=config,
                    product_id=args.id,
                    name=args.name,
                    section=args.section,
                    description=args.description,
                    price=args.price,
                    discount=args.discount,
                )
                print(json.dumps(product))

            elif args.products_command == "delete":
                config = load_config()
                delete_product(
                    config=config,
                    product_id=args.id,
                )
                print('{"status": "ok"}')

            elif args.products_command == "batch-update":
                config = load_config()
                updated = batch_update_products(
                    config=config,
                    section=args.section,
                    discount=args.discount,
                )
                print(json.dumps({"updated": updated}))
    except Exception as error:
        handle_error(error)
