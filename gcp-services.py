#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0
__commit_date__ = "2025-05-27"
__last_commit__ = "v011 + proj number :gcp-services.py"
__repository__ = "https://github.com/bomonike/agentic/blob/main/gcp-services.py"

"""gcp-services.py

This script provides different ways to authenticate into the Google Cloud Platform (GCP)
using Google's official Python SDKs, known as client libraries. 

This script is being updated to use workload-identity-federation to authenticate.

Functions in this manages secrets and analyzes prices for Google Cloud.
and interact with services like Google Docs, Sheets, Drive, or 
Google Cloud Platform products (like Vertex AI, Storage, etc.) with less boilerplate and built-in authentication.

STATUS: Python 3.13.3 working on macOS Sequoia 15.3.1
ruff check gcp-services.py

#### Prerequisites:
# 1. Install external Python packages: Run: 
   gcp-setup.sh  # to install modules (gcloud, pip, etc.) such as:
        brew install google-cloud-sdk  # See https://cloud.google.com/sdk/docs/install-sdk

        # Set permissions:            
        chmod +x ./gcp-services.py

        deactivate       # out from within venv
        brew install uv  # new package manager
        # See all available versions for a minor release:
        uv python list 3.12   # list releases available
        uv python install 3.12.10 --default
        uv --help
        uv init   # for pyproject.toml & .python-version files https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
        uv lock
        uv sync
        uv venv  # to create an environment,
        source .venv/bin/activate
        ./scripts/activate       # PowerShell only
        ./scripts/activate.bat   # Windows CMD only

# 2. Run requirements.txt (instead of python -m pip install tzdata ...):
    # Python Cloud Client Libraries: https://cloud.google.com/python/docs/reference    

# 3. Update Google Cloud CLI components:
    yes | gcloud components update

# 4. Confirm library install (pip):
   ./gcp-services.py --install

# 5. Run functions which do not require a login, such as List Google Cloud Services:
   ./gcp-services.py --project "weather-454da" -v

# 6. Store the default user and project using Google CLI:
    gcloud init  

    # WARNING: pip is being invoked by an old script wrapper. This will fail in a future version of pip.
    # Please see https://github.com/pypa/pip/issues/5599 for advice on fixing the underlying issue.
    # To avoid this problem you can invoke Python with '-m pip' instead of running pip directly.

    To update your Application Default Credentials quota project, use the command
    gcloud auth application-default set-quota-project weather-454da

# 7. Set up credentials:

    a. OAuth client ID: For applications that need to access user data
    b. Service Account: For server-to-server interactions
    c. API Key: For simple API access without user data


    Go to the Google Cloud Console (https://console.cloud.google.com/)
    Create a new project or select an existing project.
    Click "APIs & Services", then "Enable APIs services".
    Click each service to click "Enable" for it.
    Click the "Credentials" drop-down for the service.
    Copy and paste the Service account ID and password.

    Step 4: Download Credentials

    For OAuth client ID:

    Configure the OAuth consent screen
    Choose application type (Web, Desktop, etc.)
    Add authorized redirect URIs if needed
    Click "Create"
    Click the download icon (JSON) to download your credentials.json file

    For Service Account:

    Enter a name and description
    Grant roles if needed
    Click "Create"
    Click "Create Key", select JSON format
    The credentials.json file will download automatically

# 7a. Application Default Credentials (ADC) is Google's recommended approach for most scenarios
   to authenticate calls to Google Cloud APIs by client libraries.
   See https://cloud.google.com/secret-manager/docs/reference/libraries#client-libraries-install-python

   python gcp-services.py --setup-adc

   gcloud config set

   ✅ Application Default Credentials are set up at: /Users/johndoe/.config/gcloud/application_default_credentials.json

   python gcp-services.py --adc
   RESPONSE: ⚠️ This will open a browser window for you to log in to Google Cloud.

   RESPONSE: https://cloud.google.com/docs/authentication/adc-troubleshooting/user-creds.

# 7b. Run using default OAuth User Account Authentication - Interactive authentication for personal use:
    ./gcp-services.py --setup-adc   # Set up Application Default Credentials
    ./gcp-services.py --user

    Do not overrride -u "johndoe@gmail.com" -v

# 7c. --service-account [KEY_PATH]: Authenticate with a service account key
    For simple API access without user data:

    Enter a name and description
    Grant roles if needed
    Click "Create"
    Click "Create Key", select JSON format
    Specify the folder to store the json credentials file downloaded automatically.

    python gcp-services.py --service-account path/to/your-service-account-key.json

# 8. Hit Ctrl-C to exit CLI session.
"""

#### Built-in imports (alphabetically):

# ruff: noqa: E402 Module level import not at top of file
import time
std_strt_timestamp = time.monotonic()
import argparse
# import collections  # F401 not used
import configparser
# import datetime - removed to avoid conflict with myutils import
import functools
import importlib.util
# import inspect
# import itertools
import json
import logging
import os
from pathlib import Path
import pickle         
import pip
#import platform     # https://docs.python.org/3/library/platform.html
import random
import requests
from requests.exceptions import RequestException
import subprocess
import sys
#import webbrowser
std_stop_timestamp = time.monotonic()

#### External imports:

# Enable import of local module (myutils)
sys.path.append(os.getcwd())  # Returns None
    # Example: /Users/johndoe/github-wilsonmar/python-samples
#sys.path.insert(0, '.')
# Now import myutils with a forced reload

# import importlib
import myutils
# from myutils import *   # import all objects into the symbol table
# importlib.reload(myutils)
# print(f"sys.path={sys.path}")

# Clear any cached modules to ensure fresh imports
for module in ['myutils', 'datetime']:
    if module in sys.modules:
        del sys.modules[module]

# Import datetime first to ensure it's properly initialized
# from datetime import datetime, timezone

xpt_strt_datetimestamp = time.monotonic()   # For wall time of xpt imports
try:
    # External: No known vulnerabilities were found by: pip-audit -r requirements.txt
    # See https://realpython.com/python39-new-features/#proper-time-zone-support
    import google.auth
    from google.auth import default
    from google.auth.exceptions import DefaultCredentialsError
    from google.auth.transport.requests import Request       # google-auth-httplib2
    from google_auth_oauthlib.flow import InstalledAppFlow   # google-auth-oauthlib
    from google.auth.credentials import Credentials  # to automatically detect and use ADC credentials
    from google.auth import identity_pool
    from google.oauth2 import service_account                # pip install google-auth
    from google.oauth2.credentials import Credentials

    from googleapiclient.discovery import build              # pip install google-api-python-client
    from googleapiclient.errors import HttpError

    # To enable the Cloud Resource Manager API for your project:
    # https://cloud.google.com/resource-manager/docs/quickstart
    from google.cloud import service_usage_v1    # pip install google-cloud-service-usage
    #from google.cloud import service_usage_v1     # pip install google-cloud-service-usage

    from google.cloud import bigquery       # pip install google-cloud-bigquery
    from google.cloud import compute_v1     # pip install google-cloud-compute
    #from google.cloud import core          # pip install google-cloud-core
    # google-cloud-firestore 
    from google.cloud import pubsub_v1      # pip install google-cloud-pubsub
    from google.cloud import secretmanager  # pip install google-cloud-secret-manager
    from google.cloud import storage        # pip install google-cloud-core

    #from google.cloud import iam_v1              # pip install google-cloud-iam
    from google.cloud import iam                 # pip install google-cloud-iam
    from google.cloud import resourcemanager_v3  # pip install google-cloud-resource-manager 
    #from google.cloud.iam_v1 import IAMClient
                            # pip install google-api-python-client  # General Google APIs
                            # pip install googleapis-common-protos  # Common protocol buffers
    # import matplotlib.pyplot as plt        # statsd
    # from numpy import numpy as np
    import statsd
    #from statsd import StatsClient    # pip install python-statsd or statsd
    import tabulate       # pip install tabulate
    from typing import Callable, Optional, Type, Union, List, Dict, Any
    import pandas as pd   # pip install pandas
    # from zoneinfo import ZoneInfo   # python -m pip install tzdata
        # ZoneInfo from IANA is now the most authoritative source for time zones.
    #import uuid
except Exception as e:
    print(f"Python module import failed: {e}")
    #print("    sys.prefix      = ", sys.prefix)
    #print("    sys.base_prefix = ", sys.base_prefix)
    print("Please activate your virtual environment:\n  python3 -m venv venv && source venv/bin/activate")
    print("  pip install --upgrade -r requirements.txt")
    exit(9)

# FIXME: ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
# google-cloud-aiplatform 1.92.0 requires google-cloud-storage<3.0.0,>=1.32.0, but you have 
# google-cloud-storage 3.1.0 which is incompatible.
# google-adk 0.5.0 requires google-cloud-storage<3.0.0,>=2.18.0, but you have 
# google-cloud-storage 3.1.0 which is incompatible.

# For wall time of xpt imports:
xpt_stop_datetimestamp = time.monotonic()

#### Global CLI parameters:

parser = argparse.ArgumentParser(description='gcp-services.py for Google Cloud Authentication')
parser.add_argument("-q", "--quiet", action="store_true", help="Quiet")
parser.add_argument("-v", "--verbose", action="store_true", help="Show each download")
parser.add_argument("-vv", "--debug", action="store_true", help="Show debug")
parser.add_argument("-l", "--log", help="Log to external file")
parser.add_argument("--project", "-p", help="Google Cloud project ID")
parser.add_argument("--service-account", "-acct", type=str, help='Path to service account key file')
parser.add_argument('--setup-adc', action='store_true', help='Set up Application Default Credentials')
parser.add_argument('--adc', action='store_true', help='Use Application Default Credentials (ADC)')
parser.add_argument('--user', action='store_true', help='Use interactive user authentication (email)')
parser.add_argument('--install', action='store_true', help='Install required packages')
parser.add_argument("--format", "-fmt", choices=["table", "csv", "json"], 
                    default="table", help="Output format (default: table)")

# Load arguments from CLI:
args = parser.parse_args()

SHOW_DEBUG = args.debug
SHOW_VERBOSE = args.verbose
SHOW_FUNCTIONS = False
LIST_REGIONS = False
LIST_GCS = True

#### Global variables:

my_service_account = args.service_account
my_project_id = args.project
my_project_number = None
my_account = args.user
output_format = args.format

#### DEBUG:

if SHOW_DEBUG:
    myutils.show_print_samples()

    THIS_PGM = os.path.basename(__file__)  # "gcp-services.py"
             # os.path.splitext(os.path.basename(__file__))[0]
    myutils.print_trace(f"Filename without extension: {THIS_PGM}")
    myutils.print_trace(f"fuid (F User ID): {myutils.get_fuid(THIS_PGM)})")
    myutils.print_trace(f"realpath={os.path.realpath(__file__)} ")
    # Get file timestamp using myutils.filetimestamp
    try:
        file_path = THIS_PGM
        # First attempt to use myutils.filetimestamp
        timestamp = myutils.filetimestamp(file_path)
        myutils.print_trace(f"File last modified: {timestamp} ")
    except Exception as e:
        myutils.print_trace(f"Warning: Could not get timestamp using myutils: {e}")
        # Fallback to direct datetime usage if myutils fails
        t = os.path.getmtime(file_path)
        timestamp = datetime.fromtimestamp(t).strftime("%Y-%m-%d-%H:%M")
        myutils.print_trace(f"File last modified: {timestamp} ")

    dunder_items = myutils.extract_dunder_variables(THIS_PGM)
    for i, (key, value) in enumerate(dunder_items.items(), 1):
        myutils.print_trace(f"{key}: {value}")   # without {i}. 

    myutils.print_heading("sys.path to import external modules:")
    syspaths = sys.path
    for i, path in enumerate(syspaths, 1):
        myutils.print_trace(f"{i}. {path}")

    # FIXME: myutils.print_trace(myutils.list_pgm_functions(THIS_PGM))
    # FIXME: myutils.print_trace(myutils.list_files())


### Logging and Monitoring utilities:


# Example prep for backoff:
#import requests
#from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def send_retry_to_metrics(info):
    """ Send retry metrics to your monitoring system:
    """
    # FIXME: F821 Undefined name `statsd`
    statsd.increment(f"retries.{info['func_name']}")
    
# Example callback function:
def log_retry_to_metrics(info):
    """Example callback that sends retry metrics to a monitoring system
    """
    print(f"METRIC: function={info['func_name']}, retry={info['retry_number']}, "
            f"exception={info['exception'].__class__.__name__}")
    
def backoff(
    max_retries: int = 5,
    exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception,
    base_delay: float = 0.5,
    max_delay: float = 60.0,
    factor: float = 2.0,
    jitter: bool = True,
    on_backoff: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Callable:
    """
    A @decorator added to function definitions to automatically retry function calls that fail
    with exponential backoff, jitter, etc.
    Rather than use 3rd-party tenacity or backoff lib at https://pypi.org/project/backoff/
        or https://github.com/alexferl/justbackoff
    See https://medium.com/@suryasekhar/exponential-backoff-decorator-in-python-26ddf783aea0
    and https://medium.com/@oggy/retry-mechanisms-in-python-practical-guide-with-real-life-examples-ed323e7a8871
    Args:
        max_retries: Maximum number of retries before giving up
        exceptions: Exception or tuple of exceptions to catch and retry on
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        factor: Multiplication factor for exponential backoff
        jitter: Whether to add randomness to the delay
        on_backoff: Optional callback function that will be called with info about each retry
                   The callback receives a dict with: retry_number, delay, exception, func_name    
    Returns:
        Decorated function
    Example:
        @backoff(max_retries=3, exceptions=(ConnectionError, TimeoutError))
        def fetch_data_from_api(url):
            return requests.get(url)
    """
    #import functools   # built-in
    #import logging     # built-in
    #import random      # built-in
    #import time        # built-in
    # Third-party install necessary:
    #from typing import Callable, Optional, Type, Union, List, Dict, Any

    if isinstance(exceptions, list):
        exceptions = tuple(exceptions)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = base_delay
            
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries. "
                            f"Final exception: {e}"
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    actual_delay = min(delay, max_delay)
                    if jitter:
                        # Add randomness to avoid thundering herd problem
                        actual_delay = actual_delay * (0.5 + random.random())
                    
                    # Log the retry
                    logger.warning(
                        f"Retry {retries}/{max_retries} for function {func.__name__} "
                        f"after error: {e}. Waiting {actual_delay:.2f}s before next attempt."
                    )
                    
                    # Call the on_backoff callback if provided
                    if on_backoff is not None:
                        info = {
                            "retry_number": retries,
                            "delay": actual_delay,
                            "exception": e,
                            "func_name": func.__name__
                        }
                        try:
                            on_backoff(info)
                        except Exception as callback_error:
                            logger.error(f"Error in backoff callback: {callback_error}")
                    
                    # Sleep before retry
                    time.sleep(actual_delay)
                    
                    # Increase delay for next potential retry
                    delay = min(delay * factor, max_delay)
        
        return wrapper
    
    return decorator


@backoff(
    max_retries=3,
    exceptions=(RequestException, ConnectionError),
    base_delay=1.0,
    on_backoff=log_retry_to_metrics
)
def fetch_data(url):
    """Example function that might fail and need retries"""
    response = requests.get(url, timeout=2)
    response.raise_for_status()
    return response.json()


### Authenticate GCP Account


# Set up Workload Identity Federation in Google Cloud:
# 1. Create a Workload Identity Pool
# 2.Create a Provider within the pool
# 3. Configure attribute mappings and conditions
# 4. Grant necessary IAM roles

# Placeholders in the configuration and .ENV file:
# PROJECT_NUMBER: Your Google Cloud project number
# POOL_ID: Your Workload Identity Pool ID
# PROVIDER_ID: Your Provider ID
# Token source paths/URLs specific to your environment


def authenticate_with_adc():
    """
    Authenticate using Application Default Credentials (ADC)
    Returns the credentials and project ID
    """
    try:
        # Get credentials and project ID using ADC
        #import google.auth
        credentials, project_id = google.auth.default()
        print(f"✅ Project ID \"{project_id}\" authenticated with ADC.")
        return credentials, project_id
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None, None


def get_account_id() -> str:
    """Obtain account_id 3 different ways based on overrides:
    1) command line argument parm, 2) from gcloud cli, 3) .env file GOOGLE_account_id, 4) prompt for it
    """

    # WAY 1: global parm from CLI: --account or -p:
    if args.user:
        print(f"--account \"{args.user}\" within get_account_id() ")
        return args.user

    # WAY 2: Read from Google local INI-format config file set by gcloud init CLI command:
    # On macOS:
    filepath = os.path.expanduser('~/.config/gcloud/configurations/config_default')
    print(f"my_google_config_filepath = \"{filepath}\" ")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Config file at \"{filepath}\" not found within get_account_id()")
    try:
        # import configparser
        config = configparser.ConfigParser()
        config.read(filepath)
            # [core]
            # account = johndoe@gmail.com
            # project = something
        section="core"
        if section not in config:
            raise KeyError(f"Section '[{section}]' not found in config file within get_account_id() ")
        #key="account"
        #if key not in config[section]:
        #    raise KeyError(f"Key '{key}' not found in section '{section}'")
        key="account"  # static assigned by Google.
        if key not in config[section]:
            raise KeyError(f"Key '{key}' not found in section '{section}'")

        print(f"My current account: \"{config[section][key]}\" within get_account_id() ")
        return config[section][key]

        #with open(my_google_config_filepath, 'r') as f:
        #    account = f.read().strip()
        #    if account:
        #        return account
    except Exception as e:
        print(f"get_account_id() {e}", file=sys.stderr)
        exit(9)
    
    # WAY 3: Read from .env file:
    # Add optional default account configuration file

    # WAY 4: Prompt for manual entry:
    while True:
        try:
            account_id = input("Enter account_id: ")
            print(f"Hello, {account_id}!")
        except ValueError:
            print("Please enter a value for account_id.")
    return account_id


def authenticate_with_user_account(account_in) -> Dict[str, Any]:
    """
    Authenticate using a user account interactively.
    
    Returns:
        Dict containing credentials info and authenticated client
    """
    try:
        #from google.auth.credentials import Credentials
        #from google.cloud import storage
        #from google_auth_oauthlib.flow import InstalledAppFlow
        #from google.auth.transport.requests import Request
        #import google.oauth2.credentials
        #import pickle
        
        # Define the scopes
        SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
        
        # Where to save the token
        token_path = os.path.join(os.path.expanduser('~'), '.google_cloud_token.pickle')
        
        credentials = None
        
        # Check if token file exists
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                credentials = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                #print("⚠️ Pleas provide OAuth client ID credentials.")
                client_id = account_in  # input("Enter your OAuth client ID: ")
                client_secret = input("Enter your OAuth client secret: ")
                
                # Create a simple OAuth config
                oauth_config = {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
                    }
                }
                
                # Create a temporary client secrets file
                temp_secrets_path = "temp_client_secrets.json"
                with open(temp_secrets_path, 'w') as f:
                    json.dump(oauth_config, f)
                
                # Start the OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    temp_secrets_path, SCOPES)
                credentials = flow.run_local_server(port=0)
                
                # Remove temporary file
                os.remove(temp_secrets_path)
                
                # Save credentials for future use
                with open(token_path, 'wb') as token:
                    pickle.dump(credentials, token)
        
        # Create an authenticated client
        client = storage.Client(credentials=credentials)
        
        print("✅ Successfully authenticated with user account")
        
        return {
            "credentials": credentials,
            "client": client
        }
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        raise


def authenticate_with_service_account(key_path: str) -> Dict[str, Any]:
    """
    Authenticate using a service account key file.
    Args:
        key_path: Path to the service account JSON key file
    Returns:
        Dict containing credentials info and authenticated client
    """
    try:
        #from google.cloud import storage
        # Set environment variable for other libraries to use
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
           # such as GOOGLE_APPLICATION_CREDENTIALS="/Users/johndoe/.google_credentials/credentials.json"
        
        # Create credentials object:
        #from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_file(
            filename=key_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        
        # Create an authenticated client (using storage as an example)
        client = storage.Client(credentials=credentials)
        
        # Get service account details
        with open(key_path, 'r') as key_file:
            key_data = json.load(key_file)
        
        print(f"✅ Successfully authenticated as: {key_data.get('client_email', 'Unknown')}")
        
        return {
            "credentials": credentials,
            "client": client,
            "project_id": key_data.get('project_id'),
            "client_email": key_data.get('client_email')
        }
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        raise


def authenticate_with_application_default() -> Dict[str, Any]:
    """
    Authenticate using Application Default Credentials.
    This looks for credentials in environment variables and local ADC file.
    
    Returns:
        Dict containing credentials info and authenticated client
    """
    try:
        #from google.auth.credentials import Credentials
        #from google.auth import default
        #from google.cloud import storage
        
        # Get default credentials
        credentials, project_id = authenticate_with_adc()
        
        # Create an authenticated client (using storage as an example)
        client = storage.Client(credentials=credentials, project=project_id)
        
        print("✅ Successfully authenticated with Application Default Credentials")
        print(f"   Project ID: {project_id}")
        
        return {
            "credentials": credentials,
            "client": client,
            "project_id": project_id
        }
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        raise


def get_adc_project_id() -> str:
    """
    Returns the project ID string from the ADC file, or None if not found.
    """
    # if CLI: "gcloud auth application-default login" was run to setup file:
    home_dir = str(Path.home())
    my_adc_path = f"{home_dir}/.config/gcloud/application_default_credentials.json"
    if os.path.exists(my_adc_path):
        print(f"ADC (Application Default Credentials) found at: {my_adc_path} within get_adc_project_id() ")
        # TODO: read the file and print the contents: project_id, client_id, client_secret, refresh_token 
        # {
        #   "account": "",
        #   "client_id": "...",
        #   "client_secret": "...",
        #   "quota_project_id": "weather-454da",
        #   "refresh_token": "...M",
        #   "type": "authorized_user",
        #   "universe_domain": "googleapis.com"
        # }
        with open(my_adc_path, 'r') as file:
            json_str = file.read()
        # import json
        json_data = json.loads(json_str)
        project_id = json_data.get('quota_project_id')
        print(f"project_id: \"{project_id}\" within get_adc_project_id() ")
        return project_id
    else:
        print(f"❌ ADC project_id not found at path: {my_adc_path} within get_adc_project_id() ")
        rc = setup_local_adc()
        return rc


def get_project_number(project_id=None) -> tuple[str, str]:
    """Get 12-digit project number Google assigns for each user-defined alphanumeric project ID
    for use by some IAM policies, billing APIs.
    """
    credentials, default_project = google.auth.default()
    
    if not project_id:
        project_id = default_project
    
    #from google.cloud import resourcemanager_v3
    client = resourcemanager_v3.ProjectsClient(credentials=credentials)
    project_name = f"projects/{project_id}"  # example: 123456789012 (12 digits)
    
    try:
        project = client.get_project(name=project_name)
        project_number = project.name.split('/')[-1]
        print(f"✅ project_number: {project_number} from project_id: {project_id} ")
        return project_number, project_id  # Returns project number
    except Exception as e:
        print(f"get_project_number(): {e}")
        # FIXME: 403 Cloud Resource Manager API has not been used in project sdk83360 before or it is disabled.
        # Enable it by visiting https://console.developers.google.com/apis/api/cloudresourcemanager.googleapis.com/overview?project=sdk83360 
        # then retry. If you enabled this API recently, wait a few minutes fo
        return None, project_id


def enable_cloud_resource_manager_api(project_id) -> bool:
    """
    Enable the Cloud Resource Manager API for a given project.
    This only needs to be done once when project is created.
    
    Args:
        project_id (str): The Google Cloud Project ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not project_id:
        print("No project_id provided to enable_cloud_resource_manager_api() ")
        return False
    if check_api_status(project_id) == "enabled":
        print(f"Cloud Resource Manager API is already enabled for project {project_id}")
        return True

    try:
        # Initialize the Service Usage client
        client = service_usage_v1.ServiceUsageClient()
        
        # Define the service name for Cloud Resource Manager API
        service_name = f"projects/{project_id}/services/cloudresourcemanager.googleapis.com"
        
        #print(f"Enabling Cloud Resource Manager API for project: {project_id}")
        
        # Create the enable service request
        request = service_usage_v1.EnableServiceRequest(name=service_name)
        
        # Enable the service (this returns a long-running operation)
        operation = client.enable_service(request=request)
        
        print("Waiting for operation to complete...")
        
        # Wait for the operation to complete
        result = operation.result(timeout=300)  # 5 minute timeout
        
        print(f"✅ project_id \"{project_id}\" enabled for Cloud Resource Manager API ")
        return True
        
    except Exception as e:
        print(f"❌ Error enabling Cloud Resource Manager API: {str(e)}")
        return False


def check_api_status(project_id) -> str:
    """
    Check if the Cloud Resource Manager API is already enabled.
    
    Args:
        project_id (str): The Google Cloud Project ID
        
    Returns:
        bool: True if enabled, False otherwise
    """
    try:
        client = service_usage_v1.ServiceUsageClient()
        service_name = f"projects/{project_id}/services/cloudresourcemanager.googleapis.com"
        
        request = service_usage_v1.GetServiceRequest(name=service_name)
        service = client.get_service(request=request)
        
        is_enabled = service.state == service_usage_v1.State.ENABLED
        status = "enabled" if is_enabled else "disabled"
        print(f"project_id: \"{project_id}\" Cloud Resource Manager API is: {status}")
        return is_enabled
        
    except Exception as e:
        print(f"Error checking API status: {str(e)}")
        return None


def setup_local_adc() -> bool:
    """
    Set up local Application Default Credentials via the gcloud CLI.
    This is an interactive process.
    Returns:
        Boolean indicating success
    """
    try:       
        # Check if gcloud is installed:
        try:
            subprocess.run(["gcloud", "--version"], 
                          check=True, 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
        except (subprocess.SubprocessError, FileNotFoundError):
            print("❌ gcloud CLI is not installed. Please install it from: https://cloud.google.com/sdk/docs/install")
            return None
        
        # Run the gcloud auth login command:
        print("\n⚠️ This will open a browser window for you to log in to Google Cloud.")
        input("Press Enter to continue...")
        
        # Set up application default credentials:
        subprocess.run(["gcloud", "auth", "login"], check=True)
        print("\nNow setting up application default credentials...")
        subprocess.run(["gcloud", "auth", "application-default", "login"], check=True)
        
        # Check if credentials file now exists:
        project_id = get_adc_project_id()
        if project_id:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error setting up ADC: {e}")
        return False


def authenticate_with_workload_identity_federation():
    """
    Authenticate using Workload Identity Federation with external credentials.
    This example shows multiple approaches.
    """
    
    # Method 1: Using credential configuration file
    def auth_with_config_file():
        """Authenticate using a credential configuration JSON file"""
        
        # Path to your credential configuration file
        credential_source_file = "path/to/your/credential-config.json"
        
        # Load credentials from the configuration file
        credentials = identity_pool.Credentials.from_file(credential_source_file)
        
        # Refresh credentials if needed
        if not credentials.valid:
            credentials.refresh(google.auth.transport.requests.Request())
        
        return credentials
    
    # Method 2: Using environment variables
    def auth_with_env_vars():
        """Authenticate using environment variables"""
        
        # Set these environment variables in your environment
        # GOOGLE_APPLICATION_CREDENTIALS should point to your config file
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/credential-config.json"
        
        # Use default credentials (will automatically use WIF if configured)
        credentials, project = google.auth.default()
        
        return credentials
    
    # Method 3: Programmatic configuration
    def auth_programmatic():
        """Create credentials programmatically"""
        
        # Audience string for your Workload Identity Pool contains PROJECT_NUMBER, POOL_ID, PROVIDER_ID:
        audience = "//iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID"
        subject_token_type = "urn:ietf:params:oauth:token-type:id_token"  # or jwt
        token_url = "https://sts.googleapis.com/v1/token"
        
        # External credential source (example for file-based)
        credential_source = {
            "file": "path/to/external/token/file",
            "format": {
                "type": "text"  # or "json" with subject_token_field_name
            }
        }
        
        # Create credentials
        credentials = identity_pool.Credentials(
            audience=audience,
            subject_token_type=subject_token_type,
            token_url=token_url,
            credential_source=credential_source,
        )
        
        return credentials


def create_credential_config_example():
    """
    Example of what your credential configuration file should look like.
    Save this as a JSON file and reference it in your authentication.
    """
    
    config = {
        "type": "external_account",
        "audience": "//iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID",
        "subject_token_type": "urn:ietf:params:oauth:token-type:id_token",
        "token_url": "https://sts.googleapis.com/v1/token",
        "credential_source": {
            # For file-based source
            "file": "/path/to/token/file",
            "format": {
                "type": "text"
            }
        },
        # Optional: Service account impersonation
        "service_account_impersonation_url": "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/SERVICE_ACCOUNT_EMAIL:generateAccessToken"
    }
    
    return config


def authenticate_from_aws():
    """
    Example for authenticating from AWS using Workload Identity Federation
    """
    
    config = {
        "type": "external_account",
        "audience": "//iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "token_url": "https://sts.googleapis.com/v1/token",
        "credential_source": {
            "environment_id": "aws1",
            "regional_cred_verification_url": "https://sts.{region}.amazonaws.com?Action=GetCallerIdentity&Version=2011-06-15",
            "url": "http://169.254.169.254/latest/meta-data/iam/security-credentials",
            "format": {
                "type": "json",
                "subject_token_field_name": "access_token"
            }
        }
    }
    
    # Save config to file and use it
    with open("aws-wif-config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    credentials = identity_pool.Credentials.from_file("aws-wif-config.json")
    return credentials


def authenticate_from_azure():
    """
    Example for authenticating from Azure using Workload Identity Federation
    """
    
    config = {
        "type": "external_account",
        "audience": "//iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID",
        "subject_token_type": "urn:ietf:params:oauth:token-type:id_token",
        "token_url": "https://sts.googleapis.com/v1/token",
        "credential_source": {
            "url": "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/",
            "headers": {
                "Metadata": "True"
            },
            "format": {
                "type": "json",
                "subject_token_field_name": "access_token"
            }
        }
    }
    
    # Save config to file and use it
    with open("azure-wif-config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    credentials = identity_pool.Credentials.from_file("azure-wif-config.json")
    return credentials


def use_authenticated_client():
    """
    Example of using the authenticated credentials with Google Cloud services
    """
    
    # Get credentials using any of the above methods
    credentials = authenticate_with_workload_identity_federation()
    
    # Use with Google Cloud Storage
    storage_client = storage.Client(credentials=credentials)
    
    # List buckets to test the authentication
    buckets = storage_client.list_buckets()
    print("Accessible buckets:")
    for bucket in buckets:
        print(f"  - {bucket.name}")


def refresh_credentials(credentials):
    """Helper function to refresh expired credentials"""
    from google.auth.transport.requests import Request
    
    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            raise Exception("Unable to refresh credentials")
    
    return credentials


def get_project_info(credentials):
    """Get project information using the authenticated credentials"""
    from google.cloud import resourcemanager
    
    client = resourcemanager.Client(credentials=credentials)
    projects = client.list_projects()
    
    print("Accessible projects:")
    for project in projects:
        print(f"  - {project.project_id}: {project.name}")


# Example credential configuration templates

def save_config_template(filename="wif-config-template.json"):
    """Save a template configuration file"""
    
    template = {
        "type": "external_account",
        "audience": "//iam.googleapis.com/projects/YOUR_PROJECT_NUMBER/locations/global/workloadIdentityPools/YOUR_POOL_ID/providers/YOUR_PROVIDER_ID",
        "subject_token_type": "urn:ietf:params:oauth:token-type:id_token",
        "token_url": "https://sts.googleapis.com/v1/token",
        "credential_source": {
            "file": "/path/to/your/external/token",
            "format": {
                "type": "text"
            }
        },
        # Optional: For service account impersonation
        # "service_account_impersonation_url": "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com:generateAccessToken"
    }
    
    with open(filename, "w") as f:
        json.dump(template, f, indent=2)


def auth_using_workload_identity_federation():
    """
    Main function demonstrating usage
    """
    
    try:
        # print("Authenticating with Workload Identity Federation...")
        
        # Method 1: Using config file
        credentials = identity_pool.Credentials.from_file("your-config.json")
        
        # Test the credentials
        if not credentials.valid:
            credentials.refresh(google.auth.transport.requests.Request())
        
        print("Authentication successful! Token expires at: {credentials.expiry}")
        
        # Use the credentials with a Google Cloud service:
        storage_client = storage.Client(credentials=credentials)
        print("Successfully created authenticated Storage client")
        
    except Exception as e:
        print(f"Authentication failed: {e}")


#### Check install packages

def check_install_packages():
    """Check and install required packages"""
    required_packages = [
        "google-cloud-storage",
        "google-auth",
        "google-auth-oauthlib",
        "google-auth-httplib2"
    ]
    
    try:
        #import pip
        for package in required_packages:
            try:
                __import__(package.replace('-', '_').split('[')[0])
            except ImportError:
                print(f"📦 Installing {package}...")
                pip.main(['install', package])
        return True
    except Exception as e:
        print(f"❌ Error installing packages: {e}")
        print("Please manually install the required packages:")
        print("pip install google-cloud-storage google-auth google-auth-oauthlib google-auth-httplib2")
        return False


def get_google_billing_id():
    """
    Intro to Google Billing: https://youtu.be/raEbnlIohLE
    Prerequisite: Link Billing account to your project at https://cloud.google.com/products/calculator?hl=en
    Add entry ~/.env GOOGLE_BILLING_ACCT="123456-789012-345678"
    See https://console.cloud.google.com/billing
    """


### Projects


def get_project_id() -> str:
    """Obtain project_id 3 different ways based on overrides:
    1) command line argument parm, 2) from gcloud cli, 3) .env file GOOGLE_PROJECT_ID, 4) prompt for it
    """

    # WAY 1: global parm from CLI: --project or -p:
    if my_project_id:  # global from --project to args.project:
        print(f"--project \"{args.project}\" within get_project_id() ")
        return args.project
    # else if args.project is blank.

    # WAY 2: Read from Google local INI-format config file set by gcloud init CLI command:
    # On macOS:
    filepath = os.path.expanduser('~/.config/gcloud/configurations/config_default')
    print(f"my_google_config_filepath = \"{filepath}\" ")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Config file at \"{filepath}\" not found within get_project_id()")
    try:
        # import configparser
        config = configparser.ConfigParser()
        config.read(filepath)
            # [core]
            # account = johndoe@gmail.com
            # project = something
        section="core"
        if section not in config:
            raise KeyError(f"Section '[{section}]' not found in config file within get_project_id() ")
        #key="account"
        #if key not in config[section]:
        #    raise KeyError(f"Key '{key}' not found in section '{section}'")
        key="project"  # static assigned by Google.
        if key not in config[section]:
            raise KeyError(f"Key '{key}' not found in section '{section}'")

        print(f"My current project: \"{config[section][key]}\" within get_project_id() ")
        return config[section][key]

        #with open(my_google_config_filepath, 'r') as f:
        #    project = f.read().strip()
        #    if project:
        #        return project
    except Exception as e:
        print(f"get_project_id() {e}", file=sys.stderr)
        exit(9)
    
    # WAY 3: Read from .env file:
    # Add optional default project configuration file

    # WAY 4: Prompt for manual entry:
    while True:
        try:
            project_id = input("Enter project_id: ")
            print(f"Hello, {project_id}!")
        except ValueError:
            print("Please enter a value for project_id.")
    return project_id


#### Google Region


def list_regions():
    """List all available Google Cloud regions with their details."""
    #from google.cloud import compute_v1
    #import tabulate
    #import pandas as pd
    #import sys

    try:
        # Create a client
        client = compute_v1.RegionsClient()
        
        # Initialize request and make API call
        request = compute_v1.ListRegionsRequest(project=project_id)
        regions_list = client.list(request=request)
        
        # Extract region information
        regions_data = []
        for region in regions_list:
            status = "UP" if region.status == "UP" else region.status
            regions_data.append({
                "Name": region.name,
                "Description": region.description,
                "Status": status,
                "Zones": len(region.zones) if hasattr(region, "zones") else 0
            })
        
        return regions_data
    
    except Exception as e:
        print(f"Error listing regions: {e}")
        return []

def display_regions(regions_data, output_format="table"):
    """Display the regions in the specified format."""
    if not regions_data:
        print("No regions found or unable to retrieve regions.")
        return
    
    if output_format == "table":
        print(tabulate.tabulate(regions_data, headers="keys", tablefmt="grid"))
    elif output_format == "csv":
        df = pd.DataFrame(regions_data)
        print(df.to_csv(index=False))
    elif output_format == "json":
        df = pd.DataFrame(regions_data)
        print(df.to_json(orient="records"))
    else:
        print("Unsupported output format. Using default table format.")
        print(tabulate.tabulate(regions_data, headers="keys", tablefmt="grid"))
    


# For list of Google Services, see https://cloud.google.com/python/docs/reference
# Google Cloud Services Pricing Overview (as of mid-2024) 
# Prices are approximate and may vary based on usage, region, and specific configurations
GCP_SVCS_PRICING = {
    "google-cloud-aiplatform": {
        "name": "AI Platform",
        "url": "https://cloud.google.com/aiplatform/pricing",
        "free_tier": "$0/month for basic usage",
        "paid_tier": "$0.017 per service call",
        "monthly_estimate": "$50-$500+ depending on usage"
    },
    "google-cloud-bigquery": {
        "name": "Big Query",
        "url": "https://cloud.google.com/bigquery/pricing",
        "free_tier": "1 TB of query processing per month free",
        "storage_pricing": "$0.02 per GB per month",
        "query_pricing": "$5 per TB of query processed after free tier"
    },
    "google-cloud-bigtable": {
        "name": "Big Table",
        "url": "https://cloud.google.com/bigtable/pricing",
        "storage_pricing": "$0.17 per GB per month",
        "node_pricing": "$0.65 per node per hour"
    },
    "google-cloud-compute": {
        "name": "Compute",
        "url": "https://cloud.google.com/compute/pricing",
        "free_tier": "$300 credit for new users",
        "vm_pricing": {
            "e2-micro": "$0.010 per hour",
            "n2-standard-2": "$0.125 per hour"
        }
    },
    "google-cloud-dataflow": {
        "name": "Dataflow",
        "url": "https://cloud.google.com/dataflow/pricing",
        "processing_pricing": "$0.056 per vCPU per hour",
        "memory_pricing": "$0.004 per GB per hour"
    },
    "google-cloud-dataproc": {
        "name": "Data proc",
        "url": "https://cloud.google.com/dataproc/pricing",
        "cluster_pricing": "$0.048 per vCPU per hour",
        "preemptible_instances": "$0.013 per vCPU per hour"
    },
    "google-cloud-datastore": {
        "name": "Data Store",
        "url": "https://cloud.google.com/datastore/pricing",
        "free_tier": "1 GB storage free",
        "storage_pricing": "$0.18 per GB per month",
        "operations_pricing": "$0.06 per 100,000 operations"
    },
    "google-cloud-dlp": {
        "name": "Data Loss Prevention",
        "url": "https://cloud.google.com/dlp/pricing",
        "info_type_detection": "$0.01 per 100 characters",
        "sensitive_data_scanning": "$0.045 per 100 characters"
    },
    "google-cloud-firestore": {
        "name": "Firestore",
        "url": "https://cloud.google.com/firestore/pricing",
        "free_tier": "1 GB storage, 50,000 document reads/day",
        "storage_pricing": "$0.18 per GB per month",
        "operations_pricing": {
            "document_writes": "$0.18 per 100,000 writes",
            "document_deletes": "$0.02 per 100,000 deletes"
        }
    },
    "google-cloud-functions": {
        "name": "Functions",
        "url": "https://cloud.google.com/functions/pricing",
        "free_tier": "2 million invocations per month free",
        "beyond_free_tier": "$0.40 per million invocations"
    },
    "google-cloud-kms": {
        "name": "KMS (Key Management System)",
        "url": "https://cloud.google.com/kms/pricing",
        "encryption_pricing": "$0.03 per 10,000 cryptographic operations"
    },
    "google-cloud-logging": {
        "name": "Logging",
        "url": "https://cloud.google.com/stackdriver/pricing",
        "free_tier": "50 GB of logs ingestion per project per month",
        "beyond_free_tier": "$0.50 per GB of logs ingested"
    },
    "google-cloud-monitoring": {
        "name": "Monitoring",
        "url": "https://cloud.google.com/stackdriver/pricing",
        "basic_monitoring": "Free",
        "advanced_monitoring": "$8 per monitored resource per month"
    },
    "google-cloud-pubsub": {
        "name": "PubSub",
        "url": "https://cloud.google.com/pubsub/pricing",
        "free_tier": "10 GB of messages per month",
        "beyond_free_tier": "$0.40 per GB of messages"
    },
    "google-cloud-redis": {
        "name": "Redis",
        "url": "https://cloud.google.com/memorystore/docs/redis/pricing",
        "standard_tier": "$0.054 per GB per hour"
    },
    "google-cloud-spanner": {
        "name": "Spanner",
        "url": "https://cloud.google.com/spanner/pricing",
        "compute_pricing": "$0.90 per hour per processing unit",
        "storage_pricing": "$0.30 per GB per month"
    },
    "google-cloud-speech": {
        "name": "Speech",
        "url": "https://cloud.google.com/speech/pricing",
        "standard_recognition": "$0.006 per 15 seconds",
        "video_recognition": "$0.009 per 15 seconds"
    },
    "google-cloud-storage": {
        "name": "Storage",
        "url": "https://cloud.google.com/storage/pricing",
        "standard_storage": "$0.020 per GB per month",
        "standard_operations": "$0.05 per 10,000 write operations"
    },
    "google-cloud-translate": {
        "name": "Translate",
        "url": "https://cloud.google.com/translate/pricing",
        "basic_translation": "$20 per million characters",
        "advanced_translation": "$45 per million characters"
    },
    "google-cloud-vision": {
        "name": "Vision",
        "url": "https://cloud.google.com/vision/pricing",
        "feature_detection": "$1.50 per 1000 images",
        "ocr_pricing": "$0.60 per 1000 pages"
    }
}  # count: 20

def print_svcs_price_list() -> None:
    """
    Print Google Cloud Services pricing information
    """
    for service, pricing in GCP_SVCS_PRICING.items():
        print(f"{service}:")
        for key, value in pricing.items():
            print(f"    {key}: {value}")
        print()  # Extra line for readability


### GCS


def list_gcs_buckets(client_obj):
    """
    List GCS (Google Cloud Storage) buckets (to verify authentication worked).
    Args:
        client: An authenticated storage client
    """
    try:
        print("\n📋 Listing storage buckets to verify authentication within list_gcs_buckets() ")
        buckets = list(client_obj.list_buckets())
        
        if not buckets:
            print("No buckets found in this project within list_gcs_buckets() ")
        else:
            for bucket in buckets:
                print(f" - {bucket.name}")
    except Exception as e:
        print(f"❌ Error listing buckets in list_gcs_buckets(): {e}")


# TODO: Google Key 


#### Google Workspaces Sheets, Documents, Gmail


# def get_google_sheet_id():
# TODO: Spreadsheet of Public file "Musicals" for View at Copy link: https://docs.google.com/spreadsheets/d/11CTYgW5TP9IzR8LR4NYWhxyanYp5XJypE4eMfnBIlhI/edit?usp=sharing


def list_google_sheet(sheet_id, range_in):
    """
    See https://developers.google.com/workspace/sheets/api/quickstart/python
    """
    # range_in="Sheet1!A1:D5"
    # from googleapiclient.discovery import build
    # ... (authentication code is nearly identical to the Docs example above)
    # TODO: define creds.
    service = build("sheets", "v4", credentials="creds")
        # FIXME: Undefined name `creds`
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId="sheet_id", range=range_in).execute()
    values = result.get("values", [])
    print(values)


SCOPES = ["https://www.googleapis.com/auth/documents.readonly",
            'https://www.googleapis.com/auth/spreadsheets', 
            'https://www.googleapis.com/auth/gmail.send']  # Adjust as needed

def gcp_token_refresh():
    """
    x
    """
    # import os.path
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If credentials don't exist or are invalid, run the auth flow:
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())


def get_gcp_document_id() -> str:
    """
    Return doc (document) ID within Google Workspaces.
    """
    # TODO: from .env, then remove plug value here Copy Link of "NV86_RP2_v1_mobile.png" with public anyone access:
    GOOGLE_DOCUMENT_ID = "https://drive.google.com/file/d/0BwxFrV4vHhBGdUV3azBMYzR0OW8/view?usp=sharing&resourcekey=0-4kDrfMO3Kp_4Obp9wwEixg"
    return GOOGLE_DOCUMENT_ID


def get_google_doc_title(doc_id):
    """
    See https://developers.google.com/workspace/sheets/api/quickstart/python
    import os.path
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    """
    creds = None
    # Load credentials if they exist:
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If not, go through the OAuth flow:
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials for next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        service = build("docs", "v1", credentials=creds)
        document = service.documents().get(documentId=DOCUMENT_ID).execute()
            # FIXME: F821 Undefined name `DOCUMENT_ID`
        print(f"The title of the document is: {document.get('title')}")
    except HttpError as err:
        print(err)


def get_secret_from_secret_manager(project_id, secret_id, version_id="latest", secret_in=""):
    """ Retrieve (access)the secret value from Google Secret Manager
    Args:
        project_id (str): Google Cloud project ID
        secret_id (str): ID of the secret to access
        version_id (str): Version of the secret to access, defaults to "latest"    
    Returns:
        str: The secret value
    See https://cloud.google.com/secret-manager/docs/reference/libraries#client-libraries-install-python
    """
    #from google.cloud import secretmanager  # google-cloud-secret-manager
    try:
        client = secretmanager.SecretManagerServiceClient()
        if not secret_id:
            print("secret_id not provided within get_secret_from_secret_manager() ")
            return None

        if secret_in:
            # Create the parent secret:
            secret = client.create_secret(
                request={
                    "parent": f"projects/{project_id}",
                    "secret_id": secret_id,
                    "secret": {"replication": {"automatic": {}}},
                }
            )
            # Add the secret version:
            version = client.add_secret_version(
                request={"parent": secret.name, "payload": {"data": b"{secret_in}"}}
            )
            print(f"secret_id: {secret_id} v{version} added.")

        # Build the resource name of the secret version:
        if version_id == "latest":
            version_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        else:
            version_name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        
        # Access the secret version:
        response_obj = client.access_secret_version(request={"name": version_name})
        
        # WARNING: Do not print the secret in a production environment!
        print("Secret value not shown by get_secret_from_secret_manager() ")
        return response_obj.payload.data.decode("UTF-8")
    
    except Exception as e:
        print(f"❌ Error inget_secret_from_secret_manager(): {e}")
        return None    



def use_storage_with_adc():
    """Example of using Google Cloud Storage with ADC"""
    # Credentials are automatically loaded by the client
    storage_client = storage.Client()
    
    # List buckets
    buckets = storage_client.list_buckets()
    myutils.print_heading("Cloud Storage Buckets:")
    for bucket in buckets:
        print(f"- {bucket.name}")
    else:
        print("No storage found.")

def use_bigquery_with_adc():
    """Example of using BigQuery with ADC"""
    # Credentials are automatically loaded by the client
    bigquery_client = bigquery.Client()
    
    # List datasets
    datasets = list(bigquery_client.list_datasets())
    myutils.print_heading("BigQuery Datasets:")
    if datasets:
        for dataset in datasets:
            print(f"- {dataset.dataset_id}")
    else:
        print("No datasets found.")

def use_pubsub_with_adc():
    """Example of using Pub/Sub with ADC
    """
    # Credentials are automatically loaded by the client
    #from google.cloud import storage
    #from google.cloud import bigquery
    #from google.cloud import pubsub_v1
    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()
        # FIXME: F841 Local variable `subscriber` is assigned to but never used

    # Get authenticated project ID
    _, project_id = google.auth.default()
    
    # List topics (if project_id is available)
    if project_id:
        project_path = f"projects/{project_id}"
        topics = publisher.list_topics(request={"project": project_path})
        print("Pub/Sub Topics:")
        for topic in topics:
            print(f"- {topic.name}")


####


if __name__ == "__main__":

    if SHOW_FUNCTIONS:
        myutils.list_pgm_functions(sys.argv[0])
    
    if args.install:   # --install:
        check_install_packages()

    my_account = get_account_id()  # client email address
    if args.setup_adc:   # if requested by --setup-adc:
        rc = setup_local_adc()  # which calls get_adc_project_id()
    else:   
        my_project_id = get_adc_project_id()
    if not my_project_id:
        my_project_id = get_project_id()
    if my_project_id:
        enable_cloud_resource_manager_api(my_project_id)
    if not my_project_number:
        my_project_number, my_project_id = get_project_number(my_project_id)

    credentials, my_project_id = authenticate_with_adc()
        # Successfully authenticated with ADC. Project ID: weather-454da
    if credentials:
        # Step 2: Use the credentials with various Google Cloud services
        myutils.print_verbose("Accessing Google Cloud services with ADC...\n")
        use_storage_with_adc()
        print()
        use_bigquery_with_adc()
        print()
        #use_pubsub_with_adc()
    else:
        print("\nFailed to authenticate with ADC. Please ensure ADC is properly set up.")
        print("You can set up ADC in one of the following ways:")
        print("1. Run 'gcloud auth application-default login' if developing locally")
        print("2. Use a service account key with GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("3. Deploy to a GCP environment with appropriate service account attached")
    exit()
    #gcp_token_refresh()

    # Try using the decorated function:
    try:
        # This URL is designed to return failed 500 requested to trigger retries:
        data = fetch_data("https://httpbin.org/status/500")
        print(data)
    except Exception as e:
        print(f"Failed after all retries: {e}")
    exit()
    my_secret_id = "your-secret-id"
    # secret_value = get_secret_from_secret_manager(project_id, secret_id, secret_in="my secret")

    my_doc_id = get_gcp_document_id()
    if my_doc_id:
        get_google_doc_title(my_doc_id)
        # Define the scope and document ID:
        GOOGLE_DOCUMENT_ID = "your-doc-id-here"

    # Choose authentication method:
    auth_result = None
    if args.service_account:
        print(f"🔑 Authenticating with service account key: {args.service_account}")
        auth_result = authenticate_with_service_account(args.service_account)
    elif args.adc:
        print("🔑 Authenticating with Application Default Credentials")
        auth_result = authenticate_with_application_default()
    elif my_account:
        print("🔑 Authenticating with user account")
        # FIXME: gcp-services.py: error: unrecognized arguments: johndoe@gmail.com
        auth_result = authenticate_with_user_account(my_account)
    #else:
    #    print("⚠️ No authentication method specified. Please use one of the following:")
    #    print("   --service-account [KEY_PATH]: Authenticate with a service account key")
    #    print("   --adc: Authenticate with Application Default Credentials")
    #    print("   --setup-adc: Set up Application Default Credentials")
    #    print("   --user: Authenticate interactively with a user account")
    #    print("   --install: Install required packages")

    if LIST_GCS:
        # List buckets using the client object "auth_result":
        if auth_result and "client" in auth_result:
            list_gcs_buckets(auth_result["client"])

    if LIST_REGIONS:
        regions_data = list_regions()
        display_regions(regions_data, output_format)

        # print_svcs_price_list()
    
    # get_best_region() <- get_cheapest_region() <- get_region_to_sku() <- get_fastest_region() <- get_closest_region()

 
    # get_secret()
    # send_gmail() TODO: https://medium.com/gitconnected/how-to-send-emails-in-python-with-gcp-cloud-function-b5478e237b27
    # send_slack_msg()
    # send_discord_msg()
