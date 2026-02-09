#!/usr/bin/env python3
import os
import shutil
import argparse
import sys

def add_model(model_name, template_dir="templates/whisper_template"):
    """
    Creates a new model directory by copying the template and updating the config.pbtxt.
    """
    
    # Get the absolute path of the script directory to locate models relative to it
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Define paths
    template_path = os.path.join(project_root, template_dir)
    new_model_path = os.path.join(project_root, "models", model_name)
    config_path = os.path.join(new_model_path, "config.pbtxt")

    # Check if template exists
    if not os.path.exists(template_path):
        print(f"Error: Template directory not found at {template_path}")
        return False

    # Check if model already exists
    if os.path.exists(new_model_path):
        print(f"Error: Model '{model_name}' already exists at {new_model_path}")
        return False

    try:
        # Copy template directory
        print(f"Copying template from {template_path} to {new_model_path}...")
        shutil.copytree(template_path, new_model_path)
        
        # Update config.pbtxt
        print(f"Updating configuration at {config_path}...")
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Replace the model name in the config file
        # The template has 'name: "whisper_template"'
        new_content = content.replace('name: "whisper_template"', f'name: "{model_name}"')
        
        # If the direct string replacement didn't work (maybe different spacing), 
        # let's try a regex or just force it if it's the first line. 
        # But simple replace should work if the template is consistent.
        # Fallback: if not replaced, warn the user.
        if 'name: "whisper_template"' not in content and f'name: "{model_name}"' not in new_content:
             print("Warning: Could not automatically update model name in config.pbtxt. Please check the file manually.")
        else:
             # Actually perform the replacement
             new_content = content.replace('name: "whisper_template"', f'name: "{model_name}"')

        with open(config_path, 'w') as f:
            f.write(new_content)

        print(f"Successfully created model '{model_name}'.")
        print(f"Next steps:")
        print(f"1. Place your model weights in: {new_model_path}/1/faster-whisper-model/")
        print(f"2. Restart the Triton server to load the new model.")
        
        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        # Cleanup if partial creation happened
        if os.path.exists(new_model_path):
             shutil.rmtree(new_model_path)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a new model from the whisper template.")
    parser.add_argument("--name", required=True, help="Name of the new model")
    
    args = parser.parse_args()
    
    if add_model(args.name):
        sys.exit(0)
    else:
        sys.exit(1)
