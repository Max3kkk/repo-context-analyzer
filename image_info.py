from email.mime import image
import os
import glob
import requests
import json
from collections import defaultdict


def get_image_info(image_name):
    """Fetches information about a Docker image from Docker Hub."""
    # Split image name and tag, if present
    tag = "latest"
    if ':' in image_name:
        image_name, tag = image_name.split(':')
    
    # Handle Docker Hub library images and others
    if '/' not in image_name:
        url = f'https://hub.docker.com/v2/repositories/library/{image_name}/'
    else:
        # This is a non-library image hosted on Docker Hub
        url = f'https://hub.docker.com/v2/repositories/{image_name}/'
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()
        category_names = [category['name'] for category in data.get('categories', [])]
        
        # Return relevant information
        return {
            'name': image_name,
            'tag': tag,
            'description': data.get('description', 'No description available.'),
            'full_description': data.get('full_description', 'No full description available.'),
            'categories': ', '.join(category_names) if category_names else 'N/A'
        }
    except requests.RequestException as e:
        print(f"Error fetching data for image {image_name}: {e}")
        return None


def fetch_image_info(docker_image_names):
    """Fetches and displays information for images found in Docker and Docker Compose files."""
    image_details = defaultdict(dict)

    for image in docker_image_names:
        info = get_image_info(image)
        if info:
            image_details[image] = info

    return image_details

def write_image_info_to_file(image_details):
    with open('data/image_details.json', 'w') as f:
        json.dump(image_details, f, indent=4)

def read_image_names_from_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

if __name__ == "__main__":
    docker_image_names = read_image_names_from_file('data/docker_images.json')
    image_details = fetch_image_info(docker_image_names)
    write_image_info_to_file(image_details)
