import requests

def get_wikipedia_description(author_name, lang='fr'):
    """
    Récupère la description courte d'un auteur depuis l'API Wikipédia.
    """
    # On remplace les espaces par des underscores pour l'URL
    formatted_name = author_name.replace(" ", "_")
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{formatted_name}"

    # Headers avec User-Agent pour respecter la politique de Wikipédia
    headers = {
        'User-Agent': 'Bibliotech/1.0 (https://bibliotech.example.com; contact@example.com)'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("extract")  # description courte
        else:
            print(f"Erreur API Wikipédia: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erreur lors de la récupération Wikipédia: {e}")
        return None
