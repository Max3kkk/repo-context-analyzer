from pkgutil import extend_path
import subprocess
import re
import json

def get_base_image(image_name):
    try:
        # Execute the Docker Scout command
        result = subprocess.run(['docker', 'scout', 'quickview', image_name], capture_output=True, text=True, check=True)
        
        # Convert command output to string
        output = result.stdout
        
        # Search for the base image using a regular expression
        match = re.search(r'Base image\s+\│\s+(\S+)\s+\│', output)
        if match:
            return match.group(1)
        else:
            return None
    
    except subprocess.CalledProcessError as e:
        print(f"Failed to run Docker Scout for {image_name}: {str(e)}")
        return None
    except Exception as e:
        print(f"An error occurred for {image_name}: {str(e)}")
        return None

def find_image_hierarchy(image_name):
    current_image = image_name
    hierarchy = []

    # Trace back to the root base image
    while current_image:
        base_image = get_base_image(current_image)
        if base_image and base_image not in hierarchy:
            hierarchy.append(current_image)
            current_image = base_image
        else:
            hierarchy.append(current_image)
            break
    
    return hierarchy

def print_hierarchy(hierarchy):
    print("Image Hierarchy from Base to Top-Level:")
    for i, image in enumerate(hierarchy):
        indent = ' ' * (2 * i)
        print(f"{indent}- {image}")


def read_image_names_from_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def write_image_hierarchy_to_file(image_hierarchy):
    with open('data/docker_images.json', 'w') as f:
        json.dump(image_hierarchy, f, indent=4)

def main():
    image_name_list = read_image_names_from_file('data/docker_images.json')
    full_image_set = set(image_name_list)
    for image_name in image_name_list:
        hierarchy = find_image_hierarchy(image_name)
        full_image_set.update(hierarchy)
    write_image_hierarchy_to_file(list(full_image_set))
    
if __name__ == "__main__":
    main()