from email.policy import default
import re
import json
from collections import defaultdict


def load_data_from_json(file_path):
    """ Load technology data from a JSON file. """
    with open(file_path, 'r') as file:
        return json.load(file)
    
def write_used_stigs_to_file(used_stigs):
    """Write the used STIGs to a file."""
    with open("data/used_stigs.json", "w") as file:
        json.dump(used_stigs, file, indent=2)   

def get_versions_from_stig_json():
    data = load_data_from_json('stig.json')
    versions = []
    for group in data['technology_groups']:
        for tech in group['technologies']:
            for version in tech['versions']:
                # Convert version to lower case
                versions.append(version['full_name'].lower())
    return versions

def main():
    versions = get_versions_from_stig_json()

    # Read the stig.txt file
    with open('stigs.txt', 'r') as file:
        lines = file.readlines()

    final_list = []
    for i in range(len(lines)):
        # Convert line to lower case and remove it if it's in versions
        if lines[i].strip().lower() not in versions:
            final_list.append(lines[i])

    # Write the modified content back to the stig.txt file
    with open('stigs.txt', 'w') as file:
        file.writelines(final_list)

    print(versions)



if __name__ == "__main__":
    main()
