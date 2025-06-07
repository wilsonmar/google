README.md

This repository contains code to manage resources in the Google Cloud Platform (GCP).

First, the supporting files:
* README.md is this file.
* <strong>pyproject.toml</strong> defines settings for several tools rather than individual files, such as the Black code formatter, Ruff code style checker, etc. See https://www.youtube.com/watch?v=tqrsTtbJ0L4 and https://packaging.python.org/en/latest/flow/
* .flake8.txt to control the Flake8 Python code style checker preferences.
* .vscode/extensions.json contains recommended extensions for use of VSCode IDE for this project.
* .gitignore contains the names of files and folders to ignore for this project, such as venv, etc.
* LICENSE
* CONTRIBUTING.md
* requirements.txt
* .vscode/settings.json
* __pycache__ folder contains cached Python files.

Each .py (Python) script file is store within its own folder:
* folder gcp-setup contains gcp-setup.sh
* folder gcp-services contains gcp-services.py

Within each source folder are dunder names:
* <strong>__main__.py</strong> which contains the main function so that each script can be run from the root folder like this:
   ```
   python gcp-services
   ```

### Environment variables

Note that program gpc-services.py by default looks for a file named <strong>python-samples.env</strong> in the current user's home folder (e.g. /Users/johndoe/python-samples.env).

<a target="_blank" href="https://cloud.google.com/resource-manager/docs/cloud-platform-resource-hierarchy">
<img alt="gcp-resc-arch-586x7782.jpg" src="https://res.cloudinary.com/dcajqrroq/image/upload/v1748376248/gcp-resc-arch-586x7782_fqmrun.jpg" ></a>

    Organization Administrators at the top company organization level
    ensure that there are no shadow projects or rogue admins.
    So they have central control of all resources (view and manage all of a company's project resources).
    
    Project resources belong to the organization instead of the employee who created the project. 
    This is why project resources are not deleted when an employee leaves the company.
    instead they will follow the organization resource's lifecycle on Google Cloud.

    The initial IAM policy for a newly created organization resource grants the 
    Project Creator and Billing Account Creator roles to the entire Google Workspace domain. 
    This means users will be able to continue creating project resources and billing accounts 
    as they did before the organization resource existed. 
    No other resources are created when an organization resource is created.

### Setup

1. Create a Workload Identity Pool in GCP
   
   https://cloud.google.com/iam/docs/manage-workload-identity-pools-providers

2. Create a Workload Identity Provider - Adds OIDC providers (like GitHub Actions) to the pool

   https://cloud.google.com/iam/docs/workload-identity-federation-with-other-providers

3. Configure attribute mappings and conditions

4. Grant IAM permissions to the external identity

5. Use the generated configuration in your workload
  
Your account or service account needs these permissions:

iam.workloadIdentityPools.create
iam.workloadIdentityPoolProviders.create
iam.workloadIdentityPools.list

The script is configured for GitHub Actions by default but can be easily adapted for other OIDC providers like AWS, Azure, or custom identity providers by modifying the issuer URI and attribute mappings.


## Chaos Engineering

https://github.com/GoogleCloudPlatform/chaos-engineering/blob/main/Chaos-Engineering-Recipes-Book.md

