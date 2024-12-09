#!/usr/bin/env python3
import secrets
import string
from django.core.management.utils import get_random_secret_key
import sys
import os

def generate_strong_password(length=32):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    # Create secrets directory if it doesn't exist
    os.makedirs('secrets', exist_ok=True)

    # Known values
    known_values = {
        'DB_HOST': 'db',
        'DB_NAME': 'movie_rating_db',
        'DB_PORT': '5432',
        'DB_USER': 'movie_rating_user',
        'DJANGO_SUPERUSER_EMAIL': 'admin@paragoni.space',
        'DJANGO_SUPERUSER_USERNAME': 'admin',
        'SERVER_HOST': 'paragoni.space',
        'SERVER_USERNAME': 'alien'
    }

    # Generate secrets
    generated_secrets = {
        'DB_PASSWORD': generate_strong_password(),
        'DJANGO_SUPERUSER_PASSWORD': generate_strong_password(),
        'GRAFANA_ADMIN_PASSWORD': generate_strong_password(),
        'SECRET_KEY': get_random_secret_key(),
    }

    # Values from previous project
    previous_project_values = {
        'DOCKERHUB_TOKEN': '<copy-from-previous-project>',
        'DOCKERHUB_USERNAME': '<copy-from-previous-project>'
    }

    # Values that need to be generated
    needed_values = {
        'SERVER_SSH_KEY': '<generate-new-ssh-key>'
    }

    # Save to file
    with open('secrets/generated_secrets.txt', 'w') as f:
        f.write("# Generated secrets - KEEP SECURE AND NEVER COMMIT\n\n")
        
        f.write("# Known values:\n")
        for key, value in known_values.items():
            f.write(f"{key}={value}\n")
        
        f.write("\n# Generated secrets:\n")
        for key, value in generated_secrets.items():
            f.write(f"{key}={value}\n")
        
        f.write("\n# Values from previous project:\n")
        for key, value in previous_project_values.items():
            f.write(f"# {key}={value}\n")
        
        f.write("\n# Values you need to generate:\n")
        for key, value in needed_values.items():
            f.write(f"# {key}={value}\n")
        
        f.write("\n# Instructions:\n")
        f.write("# 1. Copy Docker Hub credentials from previous project's GitHub secrets\n")
        f.write("# 2. Generate SSH key pair using:\n")
        f.write("#    ssh-keygen -t rsa -b 4096 -C 'your_email@paragoni.space' -f ~/.ssh/paragoni_deploy\n")
        f.write("# 3. Add public key to server:\n")
        f.write("#    cat ~/.ssh/paragoni_deploy.pub >> ~/.ssh/authorized_keys\n")
        f.write("# 4. Add private key content as SERVER_SSH_KEY\n")

    print("Secrets generated and saved to secrets/generated_secrets.txt")
    print("\nNext steps:")
    print("1. Copy Docker Hub credentials from previous project")
    print("2. Generate SSH key pair for deployment")
    print("3. Add all secrets to GitHub Actions")
    print("4. Never commit the generated secrets file")

if __name__ == "__main__":
    main() 