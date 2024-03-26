import requests
import json
import csv
import os


def scrape(query="machine learning", path='/home/tyler/PPA_ws/scrape'):

    # URLs of the APIs
    arxiv_url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=10"
    crossref_url = f"https://api.crossref.org/works?query={query}&rows=10"
    semantic_scholar_url = f"https://api.semanticscholar.org/v1/paper/{query}"
    plos_url = f"http://api.plos.org/search?q=title:{query}&rows=10"
    doaj_url = f"https://doaj.org/api/v2/search/articles/{query}"

    # List of the URLs
    urls = [arxiv_url, crossref_url, semantic_scholar_url, plos_url, doaj_url]

    # For each URL
    for i, url in enumerate(urls):

        # Make a GET request
        response = requests.get(url)

        # Print the status code and the response text
        print("Status code:", response.status_code)
        print("Response text:", response.text)

        # Try to parse the response as JSON
        try:
            # Create the file path
            file_path = os.path.join(path, f'response_{i}.json')
            
            # Open a file in write mode
            with open(file_path, 'w') as f:
                # Write the response text to the file
                json.dump(response.json(), f, indent=2)
        except requests.exceptions.JSONDecodeError:
            print("Could not decode response as JSON")

def save_csv(path='/home/tyler/PPA_ws/scrape', fieldnames = ['title', 'URL']):
    # Create a CSV file
    with open(path + 'output.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # Write the header
        writer.writeheader()

        # For each file in the directory
        for filename in os.listdir(path):
            # If the file is a JSON file
            if filename.endswith('.json'):
                # Create the file path
                file_path = os.path.join(path, filename)

                # Open the JSON file
                with open(file_path, 'r') as f:
                    data = json.load(f)

                    # Extract the title and url
                    # Please replace 'title' and 'url' with the actual keys in your JSON data
                    title = data.get(fieldnames[0])
                    url = data.get(fieldnames[1])

                    # Write the title and url to the CSV file
                    writer.writerow({fieldnames[0]: title, fieldnames[1]: url})
                    
if __name__ == '__main__':
    path='/home/tyler/PPA_ws/scrape'
    # scrape(path=path)
    save_csv(path=path)
    
    # debug saving the desired json output to a csv