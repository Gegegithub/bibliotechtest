import requests

def get_wikipedia_description(author_name, lang='fr'):
    """
    Récupère la description courte d'un auteur depuis l'API Wikipédia.
    """
    # On remplace les espaces par des underscores pour l'URL
    formatted_name = author_name.replace(" ", "_")
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{formatted_name}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("extract")  # description courte
    return None
