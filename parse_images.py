import glob
from dockerfile_parse import DockerfileParser
import yaml
import re
import json

def find_dockerfiles():
    """Finds Dockerfiles in the current directory and subdirectories."""
    return glob.glob('**/Dockerfile', recursive=True)

def find_docker_compose_files():
    """Finds Docker Compose files in the current directory and subdirectories."""
    return glob.glob('**/docker-compose*.yml', recursive=True)

def parse_dockerfile_images(dockerfiles):
    """Parses Dockerfiles to extract image names."""
    images = []
    for dockerfile in dockerfiles:
        dfp = DockerfileParser(path=dockerfile)
        for instruction in dfp.structure:
            if instruction['instruction'] == 'FROM':
                # Use a regular expression to extract the image name
                instruction_text = instruction['value']
                # Skip dynamic image names, e.g. $IMAGE_NAME or ${IMAGE_NAME}
                if '$' in instruction_text or '{' in instruction_text or '}' in instruction_text:
                        print("--Skip dynamic image: ", instruction_text)
                        continue
                match = re.search(r'([a-zA-Z0-9/_-]+)(:[a-zA-Z0-9._-]+)?(\s+as\s+[a-zA-Z0-9_]+)?$', instruction_text)
                if match:
                    image_name = match.group(1)
                    # Include the tag if it's present
                    if match.group(2): 
                        image_name += match.group(2)
                    images.append(image_name)
    return images

def parse_docker_compose_images(docker_compose_files):
    """Parses Docker Compose files to extract image names."""
    images = []
    for file in docker_compose_files:
        with open(file, 'r') as f:
            compose_dict = yaml.safe_load(f)
            for service in compose_dict.get('services', {}):
                if 'image' in compose_dict['services'][service]:
                    image_name = compose_dict['services'][service]['image']
                    if '$' in image_name or '{' in image_name or '}' in image_name:
                        print("--Skip dynamic image: ", image_name)
                        continue
                    images.append(compose_dict['services'][service]['image'])
    return images


def parse_image_names():
    """Fetches and displays information for images found in Docker and Docker Compose files."""
    dockerfiles = find_dockerfiles()
    docker_compose_files = find_docker_compose_files()

    dockerfile_images = parse_dockerfile_images(dockerfiles)
    docker_compose_images = parse_docker_compose_images(docker_compose_files)

    return list(set(dockerfile_images + docker_compose_images))

def write_image_info_to_file(image_details):
    with open('data/initial_docker_images.json', 'w') as f:
        json.dump(image_details, f, indent=4)

if __name__ == "__main__":
    image_names = parse_image_names()
    print("images: ", image_names)
    write_image_info_to_file(image_names)

