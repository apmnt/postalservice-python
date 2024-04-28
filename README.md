# Postal Service Python Library
[![Mercari](https://github.com/apmnt/postalservice_python/actions/workflows/mercari_tests.yml/badge.svg)](https://github.com/apmnt/postalservice_python/actions/workflows/mercari_tests.yml)
[![Fril](https://github.com/apmnt/postalservice_python/actions/workflows/fril_tests.yml/badge.svg)](https://github.com/apmnt/postalservice_python/actions/workflows/fril_tests.yml)
[![YJP](https://github.com/apmnt/postalservice_python/actions/workflows/yjp_tests.yml/badge.svg)](https://github.com/apmnt/postalservice_python/actions/workflows/yjp_tests.yml)
[![PyPI version](https://badge.fury.io/py/postalservice.svg)](https://badge.fury.io/py/postalservice)

Python library for scraping second hand Japanese websites for easier access to the search results. Useful for creating datasets, notification systems, or web APIs. Targets the website API if available, or parses the HTML response.

## Features

- Mercari, Fril scraping
- Filter by keyword and size
- Built in asynchronous requests for fast html scraping
- Unit tested locally and with Github Actions workflow

## Installation
postalservice is available on PyPI as `postalservice`
```
pip install postalservice
```

## One shot example

```python
from postalservice import MercariService

mercari = MercariService()

# The `get_search_results` method returns a `SearchResults` object
searchresults = mercari.get_search_results({'keyword':'comme des garcons', 'size':'XL'})

# When you print the `SearchResults` object, it outputs a well-formatted JSON string
print(searchresults)
```
Output:
```json
[
    {
        "id": "m65906652855",
        "title": "ルイスレザー ジュンヤワタナベ JUNYA WATANABE MAN ライダース",
        "price": 120000.0,
        "size": "L",
        "url": "https://jp.mercari.com/item/m65906652855",
        "img": [
            "https://static.mercdn.net/c!/w=240,f=webp/thumb/photos/m65906652855_1.jpg?1705291813"
        ]
    },
    # ... more items
]
```

## Main methods of all service classes

`BaseService` is an abstract base class that defines the interface for a service. All services implement this and therefore have all these class methods:

- `get_search_results(params: dict) -> SearchResults`: Fetches data synchronously using the provided parameters, parses the response, and returns the results as SearchResults object.

- `get_search_results_async(params: dict) -> SearchResults`: Fetches data asynchronously using the provided parameters, parses the response (asynchronously, if needed), and returns the results as SearchResults object. 

## todo
- Rakuten support
- General improvements to structure of the library
- Support for multiple sizes for sites where only one size is possible to select at a time