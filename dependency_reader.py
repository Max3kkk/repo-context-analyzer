import json
import glob
from collections import defaultdict
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

OUTPUT_FILE_PATH = "data/dependency_descriptions.json"
PROJ_DEP_FILE_PATH = "data/project_dependencies.json"
IMAG_DEP_FILE_PATH = "data/docker_dependency_*.json"
LANG_FILE_PATH = "data/project_languages.json"


def fetch_description_pypi(package_name):
    """Fetches the package description from PyPI (Python Package Index)."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["info"]["summary"] or "-"


def fetch_description_npm(package_name):
    """Fetches the package description from npm (package manager for JavaScript)."""
    url = f"https://registry.npmjs.org/{package_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        latest_version = data["dist-tags"]["latest"]
        return data["versions"][latest_version]["description"] or "-"


def fetch_description_rubygems(gem_name):
    """Fetches the gem description from RubyGems (package manager for Ruby)."""
    url = f"https://rubygems.org/api/v1/gems/{gem_name}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["info"] or "-"


def fetch_description_maven(group_id, artifact_id):
    """Fetches package description from Maven Central (Java packages)."""
    url = f'https://search.maven.org/solrsearch/select?q=g:"{group_id}"+AND+a:"{artifact_id}"&rows=1&wt=json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        docs = data["response"]["docs"]
        return docs[0]["p"] or "-"


def fetch_description_nuget(package_name):
    """Fetches package description from NuGet (package manager for .NET)."""
    url = f"https://api.nuget.org/v3/registration5-semver1/{package_name}/index.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        latest_version = data["items"][0]["upper"]
        url_version = f"https://api.nuget.org/v3/registration5-semver1/{package_name}/{latest_version}.json"
        response_version = requests.get(url_version)
        if response_version.status_code == 200:
            data_version = response_version.json()
            return data_version["items"][0]["catalogEntry"]["description"] or "-"

def fetch_description_go(package_name):
    """Fetches package description from the Go module proxy."""
    url = f"https://proxy.golang.org/{package_name}/@latest"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("Description", "-")
    


def fetch_description_crates(package_name):
    """Fetches package description from crates.io (Rust packages)."""
    url = f"https://crates.io/api/v1/crates/{package_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["crate"]["description"] or "-"

def fetch_description_packagist(package_name):
    """Fetches package description from Packagist (PHP packages)."""
    url = f"https://repo.packagist.org/p2/{package_name}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        latest_version = list(data["packages"][package_name].keys())[0]
        return data["packages"][package_name][latest_version]["description"] or "-"



def fetch_description_debian(package_name):
    url = f"https://packages.debian.org/sid/{package_name}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        description_div = soup.find('div', id='pdesc')
        if description_div:
            # Extract the header within the description div to get the summary line.
            header = description_div.find('h2')
            summary = header.text.strip() if header else 'No summary available.'
            # Extract paragraphs in the description div for detailed description.
            paragraphs = description_div.find_all('p', recursive=False)
            description = ' '.join([p.text for p in paragraphs])
            return f"{summary}\n\n{description}"
        else:
            return "-"


def get_package_description(artifact):
    """Determines the language and fetches the description accordingly."""
    language = artifact["language"]
    if not language:
        language = artifact["type"]
    package_name = artifact["name"]
    description = None
    if language == "python":
        description = fetch_description_pypi(package_name)
    elif language == "javascript":
        description = fetch_description_npm(package_name)
    elif language == "ruby":
        description = fetch_description_rubygems(package_name)
    elif language == "java":
        # For Java, Maven Central requires group and artifact IDs
        group_id, artifact_id = package_name.split(":")
        description = fetch_description_maven(group_id, artifact_id)
    elif language == ".net":
        description = fetch_description_nuget(package_name)
    elif language == "go":
        description = fetch_description_go(package_name)
    elif language == "rust":
        description = fetch_description_crates(package_name)
    elif language == "php":
        description = fetch_description_packagist(package_name)
    elif language == "deb":
        description = fetch_description_debian(package_name)
    return language, description, package_name


def process_syft_output(file_path):
    """Processes the Syft output JSON file to extract package names and fetch their descriptions."""
    package_descriptions = defaultdict(set)
    with open(file_path, "r") as file:
        data = json.load(file)
        artifacts = data["artifacts"]
        for artifact in tqdm(artifacts, desc="Processing dependencies", unit="dependency"):
            language, description, package_name = get_package_description(artifact)
            if description:
                package_descriptions[language].add((package_name, description))
    return package_descriptions

def write_descriptions_to_file(file_path, package_descriptions):
    """Writes the package descriptions to a file."""
    formatted_descriptions = {language: [{"name": name, "description": description} for name, description in descriptions] for language, descriptions in package_descriptions.items()}
    with open(file_path, "w") as file:
        json.dump(formatted_descriptions, file, indent=2)

def process_project_dependencies():
    syft_file = f"data/project_dependencies.json"
    package_descriptions = process_syft_output(syft_file)
    write_descriptions_to_file("data/dependency_descriptions.json", package_descriptions)

def append_descriptions_to_file(package_descriptions):
    output_file = "data/dependency_descriptions.json"
    with open(output_file, "r") as file:
        data = json.load(file)
        # package_descriptions[language].add((package_name, description))
        for language, descriptions in package_descriptions.items():
            if language in data:
                data[language].extend(list(descriptions))
            else:
                data[language] = list(descriptions)
    with open(output_file, "w") as file:
        json.dump(data, file, indent=2)


def process_docker_dependencies():
    files = glob.glob('data/docker_dependency_*.json')
    docker_images = [file.split('_')[-1].split('.')[0] for file in files]

    for docker_image in docker_images:
        syft_file = f"data/docker_dependency_{docker_image}.json"
        package_descriptions = process_syft_output(syft_file)
        append_descriptions_to_file(package_descriptions)

def process_project_languages():
    language_file = "data/project_languages.json"
    with open(language_file, "r") as file:
        data = json.load(file)
        for language, _ in data.items():
            with open("data/dependency_descriptions.json", "r") as file:
                descriptions = json.load(file)
                if language not in descriptions:
                    descriptions[language] = []
            with open("data/dependency_descriptions.json", "w") as file:
                json.dump(descriptions, file, indent=2)
        
    

def main():
    process_project_dependencies()
    process_docker_dependencies()
    process_project_languages()

if __name__ == "__main__":
    main()
