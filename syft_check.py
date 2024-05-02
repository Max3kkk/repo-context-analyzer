import json
import subprocess

def load_images(image_file):
    with open(image_file, 'r') as file:
        return json.load(file)

def run_syft(image):
    result = subprocess.run(['syft', image, '-o', 'json'], capture_output=True, text=True, check=True)
    return result.stdout.strip()

def run_syft_on_directory():
    result = subprocess.run(['syft', 'dir:.', '-o', 'json'], capture_output=True, text=True, check=True)
    return result.stdout.strip()

def write_output(output, output_file):
    with open(output_file, 'w') as file:
        file.write(output)

def run_syft_on_images(image_file):
    images = load_images(image_file)

    for index, image in enumerate(images):
        output_file = f'data/docker_dependency_{image}.json'
        try:
            output = run_syft(image)
            if output:
                write_output(output, output_file)
                print(f"Syft analysis complete for {image}, results saved to {output_file}")
            else:
                print(f"No output from Syft for {image}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to run Syft on {image}: {str(e)}")

def run_syft_on_project():
    output_file = 'data/project_dependencies.json'
    try:
        output = run_syft_on_directory()
        if output:
            write_output(output, output_file)
            print(f"Syft analysis complete for current directory, results saved to {output_file}")
        else:
            print(f"No output from Syft for current directory")
    except subprocess.CalledProcessError as e:
        print(f"Failed to run Syft on current directory: {str(e)}")

if __name__ == "__main__":
    run_syft_on_images('data/docker_images.json')
    run_syft_on_project()