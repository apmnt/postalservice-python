import asyncio
from postalservice import YJPService
from postalservice import MercariService
from postalservice import FrilService
from postalservice import SecondStreetService
from postalservice import KindalService
from postalservice import RagtagService
from postalservice import OkokuService
from postalservice import TrefacService

print("running async tests")


async def main():
    params = {"keyword": "junya", "item_count": 3}

    services = [
        ("SecondStreet", SecondStreetService),
        # ("Trefac", TrefacService),
        # ("Okoku", OkokuService),
        # ("Ragtag", RagtagService),
        # ("YJP", YJPService),
        # ("Mercari", MercariService),
        # ("Kindal", KindalService),
        # ("Fril", FrilService),
    ]

    for service_name, service in services:
        try:
            print(f"\nTesting {service_name} async...")
            print(f"{service_name} async res:")
            results = await service.get_search_results_async(params=params)

            for res in results:
                print("\t", res["title"])
                print("\t", res["size"])
                print("\t", res["url"])
                print("\t", f"Found {len(res['img'])} images")
                print("\t", res["img"][0] if res["img"] else "No images found")

        except Exception as e:
            print(f"{service_name} async failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
