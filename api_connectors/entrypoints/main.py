# type: ignore[attr-defined]
from api_connectors import example


def main():
    greeting: str = example.hello("<author>")
    print(f"{greeting}")


if __name__ == "__main__":
    main()
