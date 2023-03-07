import json
from valrpy.client import ValrClient


def main() -> None:
    client = ValrClient()

    response = client.get_order_types("BTCZAR")

    print(json.dumps(response, indent=4))


if __name__ == "__main__":
    main()
