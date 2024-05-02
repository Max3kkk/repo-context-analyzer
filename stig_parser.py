from email.policy import default
import re
import json
from collections import defaultdict


def load_data_from_json(file_path):
    """ Load technology data from a JSON file. """
    with open(file_path, 'r') as file:
        return json.load(file)
    
def determine_type(text:str, tecs):
    # Determine the specific technology within the group
    # If any of type_names list a present in the text, return the technology, else return 1st technology
    for tech in tecs:
        if any(re.search(r'\b' + re.escape(name) + r'\b', text) for name in tech['type_names']):
            return tech
    return tecs[0]
    

def determine_version(text, versions):
    """ Find and return the matching version details if available. """
    for version in versions:
        if re.search(r'\b' + re.escape(version['number']) + r'\b', text):
            return version['full_name']
    return versions[0]['full_name']

def find_technology_in_text(text, data):
    matched_groups = []
    for group in data['technology_groups']:
        usage_names = [name.lower() for name in group['usage_names']]
        if any(re.search(r'\b' + re.escape(name) + r'\b', text) for name in usage_names):
            matched_groups.append(group)
    return matched_groups if matched_groups else None


def parse_text(text:str, data):
    """ Determine the technology used in the given text based on the loaded data. """
    text = text.lower()  # Case insensitive matching
    tech_groups = find_technology_in_text(text, data)
    matched_versions = []
    if tech_groups:
        for tech_group in tech_groups:
            type_tech = determine_type(text, tech_group['technologies'])
            version = determine_version(text, type_tech['versions'])
            matched_versions.append(version)
            # return f"{tech_group['usage_names'][0]}->{type_tech['type_names'][0]}->{version}"
        return matched_versions

def read_dependency_descriptions(file_path):
    """Read the JSON file containing dependency descriptions."""
    with open(file_path, "r") as file:
        data = json.load(file)
        for language, packages in data.items():
            if not packages:
                yield None, None, language
            for package in packages:
                name, description = package
                yield name, description, language

def process_dependency_descriptions(file_path, stig_schema):
    """Process the JSON file containing dependency descriptions."""
    used_stigs = defaultdict(list)
    for name, description, language in read_dependency_descriptions(file_path):
        text = f"{name}.  {description}"
        result = parse_text(text, stig_schema)
        if result:
            print(f"{name} ({language}): {result}")
            used_stigs[language].append(result)
    return used_stigs

def process_image_descriptions(file_path, stig_schema):
    """Process the JSON file containing image descriptions."""
    used_stigs = defaultdict(list)
    with open(file_path, "r") as file:
        data = json.load(file)
        for image, image_details in data.items():
            text = image_details['name'] + ". " + image_details['description'] + ". " + image_details['full_description']
            result = parse_text(text, stig_schema)
            if result:
                print(f"{image}: {result}")
                used_stigs[image].append(result)
    return used_stigs 

def process_project_languages(stig_schema):
    language_file = "data/dependency_descriptions.json"
    used_stigs = defaultdict(list)
    with open(language_file, "r") as file:
        data = json.load(file)
        for language, _ in data.items():
            result = parse_text(language, stig_schema)
            if result:
                print(f"{language}: {result}")
                used_stigs[language].append(result)
    return used_stigs


    
       
def write_used_stigs_to_file(used_stigs):
    """Write the used STIGs to a file."""
    with open("data/used_stigs.json", "w") as file:
        json.dump(used_stigs, file, indent=2)           

def main():
    file_path = 'stig.json'
    stig_schema = load_data_from_json(file_path)
    used_stigs = process_dependency_descriptions("data/dependency_descriptions.json", stig_schema)
    used_stigs.update(process_image_descriptions("data/image_details.json", stig_schema))
    used_stigs.update(process_project_languages(stig_schema))
    write_used_stigs_to_file(used_stigs)



if __name__ == "__main__":
    main()
