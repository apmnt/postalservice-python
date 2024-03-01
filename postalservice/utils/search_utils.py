class SearchParams:
    def __init__(self, search_params: dict):
        self.search_params = search_params

    def get_size(self):
        return self.search_params.get('size')

    def get_dict(self):
        return self.search_params
    
class SearchResults:
    def __init__(self, results: str):
        self.results = results

    def get(self, index: int):
        return self.results[index]

    def get_all(self):
        return self.results