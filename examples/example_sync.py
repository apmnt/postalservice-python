from postalservice import YJPService
from postalservice import MercariService
from postalservice import FrilService
from postalservice import SecondStreetService
from postalservice import KindalService
from postalservice import RagtagService
from postalservice import OkokuService
from postalservice import TrefacService

print("running")

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
        print(f"\n{service_name} res:")
        results = service.get_search_results(params=params)

        for res in results:
            if service_name == "YJP":
                print(res["title"], res["size"], res["url"])
            elif service_name == "Mercari":
                print(res["title"], res["url"])
                print(f"In total this many pictures: {len(res['img'])}")
            else:
                print(res["title"], res["size"], res["url"], len(res["img"]))

    except Exception as e:
        print(f"{service_name} failed: {e}")
