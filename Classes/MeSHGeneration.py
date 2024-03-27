import requests

class MeSHGeneration:
    def get_descriptor(self, text):
        query = text.replace(" ", "%20")
        url = f"https://id.nlm.nih.gov/mesh/lookup/descriptor?match=startswith&label={query}&limit=20"

        response = requests.get(url)
        response_json = response.json()
        return response_json
    
    def get_details(self, resource_url):
        resource_url = resource_url.replace(":", "%3A").replace("/", "%2F")
        url = f"https://id.nlm.nih.gov/mesh/lookup/details?descriptor={resource_url}"

        response = requests.get(url)
        response_json = response.json()
        return response_json