#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0
__commit_date__ = "2025-06-07"
__last_commit__ = "v016 + use svc_acct :gcp-services.py"
__repository__ = "https://github.com/bomonike/google/blob/main/gcp-services.py"
__status__ = "WORKING: ruff check gcp-services.py => All checks passed!"

"""gcp-services.py

This script provides different ways to authenticate into the Google Cloud Platform (GCP)
using Google's official Python SDKs, known as client libraries. 

This script is being updated to use external workload-identity-federation to authenticate
using short-lived access tokens from trusted IdP Provider pools. See https://g.co/workloadidentityfederation and
https://www.youtube.com/watch?v=ZgVhU5qvK1M Jun 29, 2023 by Martin Omander 

Functions in this manages secrets and analyzes prices for Google Cloud.
and interact with services like Google Docs, Sheets, Drive, or 
Google Cloud Platform products (like Vertex AI, Storage, etc.) with less boilerplate and built-in authentication.

STATUS: Python 3.13.3 working on macOS Sequoia 15.3.1
ruff check gcp-services.py

#### Prerequisites:
# 1. Install external Python packages: Run: 
   gcp-setup.sh  # to install modules (gcloud, pip, etc.) such as:
        brew install google-cloud-sdk  # See https://cloud.google.com/sdk/docs/install-sdk

        deactivate       # out from within venv
        brew install uv  # new package manager
        # See all available versions for a minor release:
        uv python list 3.13   # list releases available
        uv python install 3.13.3   # --default

        uv --help
        uv init   # create pyproject.toml & .python-version files https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
        uv lock
        uv sync   # creates .venv folder & uv.lock file
        uv venv  # to create an environment,
        source .venv/bin/activate
        or: ./scripts/activate       # PowerShell only
        or: ./scripts/activate.bat   # Windows CMD only
        
        uv uv pip install -e .    # Editable Install (for development)
        uv uv pip install -r requirements.txt
        chmod +x ./gcp-services.py
        ./gcp-services.py

# 2. Run requirements.txt (instead of python -m uv pip install tzdata ...):
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

#### SECTION 02: Capture pgm start date/time from the earliest point:

# ruff: noqa: E402 Module level import not at top of file
# See https://bomonike.github.io/python-samples/#StartingTime
# Built-in libraries (no pip/conda install needed):
from datetime import datetime  # , timezone
import time  # for timestamp
#from time import perf_counter_ns
std_strt_timestamp = time.monotonic()
#from zoneinfo import ZoneInfo  # For Python 3.9+ https://docs.python.org/3/library/zoneinfo.html 

# To display wall clock date & time of program start:
# pgm_strt_datetimestamp = datetime.now() has been deprecated.
pgm_strt_timestamp = time.monotonic()

# TODO: Display Z (UTC/GMT) instead of local time
pgm_strt_epoch_timestamp = time.time()
pgm_strt_local_timestamp = time.localtime()
# NOTE: Can't display the dates until formatting code is run below


#### Built-in imports (alphabetically):

import argparse
# import base64       # UNUSED? from myutils
# import collections  # F401 not used
import configparser
#import datetime    # removed to avoid conflict with myutils import
import functools
#import importlib.util   # unused
#import inspect
#import itertools
import json
import logging
import os
from pathlib import Path   # for older Python 3.4+
import pickle         
# import pip
#import platform     # https://docs.python.org/3/library/platform.html
import random
import requests     # not module named requests
from requests.exceptions import RequestException
import string
import subprocess   # for CLI commands.
import sys
import traceback
import pip
#import webbrowser
std_stop_timestamp = time.monotonic()

#### External imports:

# Import datetime first to ensure it's properly initialized
# from datetime import datetime, timezone

xpt_strt_datetimestamp = time.monotonic()   # For wall time of xpt imports
try:
    # External: No known vulnerabilities were found by: pip-audit -r requirements.txt
    # See https://realpython.com/python39-new-features/#proper-time-zone-support
    import google.auth    # for google.auth.default()
    # UNUSED: from google.auth import identity_pool
    from google.auth import default, credentials
    from googleapiclient.discovery import build   # uv pip install google-api-python-client to authenticate_service_account()
        # service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)
        # See https://www.perplexity.ai/search/googleapiclient-discovery-cach-ll78_HWfRCm64biN3HJd_A#0
    #from google.cloud.iam_v1 import WorkloadIdentityPoolsClient  # uv pip install google-cloud-iam

    # Google reorganized their IAM client libraries, and Workload Identity Pool is now in the iam_v1 module rather than iam_admin_v1:
    # NOT: from google.cloud import iam_v1   # uv pip install google-cloud-iam
    #from google.cloud.iam_admin_v1 import IAMClient  # For general IAM operations
    # from google.cloud import iam_admin_v1 # NOT iam_v1  uv pip install google-cloud-iam
        # For client = iam_admin_v1.IAMClient()
        # See https://pypi.org/project/google-cloud-iam/
        # And https://cloud.google.com/python/docs/reference/iam/latest/google.cloud.iam_admin_v1.services.iam.IAMClient
                    # uv pip install google-api-python-client  # General Google APIs
                    # uv pip install googleapis-common-protos  # Common protocol buffers

    #from google.iam.v1 import iam_policy_pb2     # uv pip install grpc-google-iam-v1
    #from google.iam.v1 import iam_policy_pb2_grpc

    # For new releases: google.cloud has been deprecated:
    from google.cloud import resourcemanager_v3  # uv pip install google-cloud-resource-manager
    # from google.auth.exceptions import DefaultCredentialsError   # unused here?
    from google.auth.transport.requests import Request       # google-auth-httplib2
        # consider using `importlib.util.find_spec` to test for availability
    from google_auth_oauthlib.flow import InstalledAppFlow   # google-auth-oauthlib
    from google.auth.credentials import Credentials  # to automatically detect and use ADC credentials
    #from google.auth import identity_pool

    from google.oauth2 import service_account  # to check svc acct exists   # uv pip install google-auth
    from googleapiclient.errors import HttpError

    #from google.oauth2.credentials import Credentials   # used here?
    
    # UNUSED: from googleapiclient import discovery    # uv pip install google-api-python-client
        # for: service = discovery.build('iam', 'v1')

    # To enable the Cloud Resource Manager API for your project:
    # https://cloud.google.com/resource-manager/docs/quickstart
    from google.cloud import service_usage_v1    # uv pip install google-cloud-service-usage

    from google.cloud import bigquery       # uv pip install google-cloud-bigquery
    from google.cloud import compute_v1     # uv pip install google-cloud-compute
    #from google.cloud import core          # uv pip install google-cloud-core
    # google-cloud-firestore 
    from google.cloud import pubsub_v1      # uv pip install google-cloud-pubsub
    from google.cloud import secretmanager  # uv pip install google-cloud-secret-manager
    from google.cloud import storage        # uv pip install google-cloud-core

    # import matplotlib.pyplot as plt        # statsd
    #from numpy import numpy as np             # doesn't play well with others?
    #from cryptography.fernet import Fernet    # in myutils
    import statsd
    #from statsd import StatsClient    # uv pip install python-statsd or statsd
    import tabulate       # uv pip install tabulate
    from typing import Callable, Optional, Type, Union, List, Dict, Any
    import pandas as pd   # uv pip install pandas
    # from zoneinfo import ZoneInfo   # python -m uv pip install tzdata
        # ZoneInfo from IANA is now the most authoritative source for time zones.
    #import uuid
except ImportError as _:
    print(traceback.format_exc(), end='')
    sys.exit(4)
except Exception as e:
    print(f"import exception: {e}")
    #print("    sys.prefix      = ", sys.prefix)
    #print("    sys.base_prefix = ", sys.base_prefix)
    print("Please activate your virtual environment:\n  python3 -m venv venv && source .venv/bin/activate")
    print("  uv pip install --upgrade -r requirements.txt")
    exit(9)

# FIXME: ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
# google-cloud-aiplatform 1.92.0 requires google-cloud-storage<3.0.0,>=1.32.0, but you have 
# google-cloud-storage 3.1.0 which is incompatible.
# google-adk 0.5.0 requires google-cloud-storage<3.0.0,>=2.18.0, but you have 
# google-cloud-storage 3.1.0 which is incompatible.

# For wall time of xpt imports:
xpt_stop_datetimestamp = time.monotonic()


#### Local imports:

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

SHOW_QUIET = args.quiet
SHOW_DEBUG = args.debug
SHOW_VERBOSE = args.verbose
SHOW_FUNCTIONS = False
LIST_REGIONS = False
LIST_GCS = True

my_account = args.user
my_service_account = args.service_account

parent_org_id = None  # like "123456789"
parent_folder_id = None  # like "folders/123456789" 
my_project_id = args.project
my_project_number = None  # looked up from project ID

output_format = args.format

my_home_dir = str(Path.home())  # such as "/Users/johndoe"
# ADC first checks the environment variable GOOGLE_APPLICATION_CREDENTIALS, then:
my_adc_path = f"{str(Path.home())}/Users/johndoe/.google_credentials/credentials.json"
    # Windows	%APPDATA%\gcloud\application_default_credentials.json
    # json contains account, client_id, client_secret, quota_project_id, refresh_token, type, universe_domain.
# print(f"my_adc_path={my_adc_path}")


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

    dunder_items = myutils._extract_dunder_variables(THIS_PGM)
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


def get_provider_pool_id(project_id, location="global") -> (str, str):
    """
    Return created my_pool_id for use with Workload Identity Federation.
    The provider point to GitHub's OIDC issuer: and include the necessary attribute mapping.
    """
    if not project_id:
        return None
    if not location:
        location = "global"

    #yymmddhhmm = myutils.get_user_local_timestamp('yymmddhhmm')
    provider_id = "prov-{location}-{yymmddhhmm}"
    pool_id = f"pool-{location}-{yymmddhhmm}"
    # provider_ids are 1-32 characters, lowercase letters, numbers, and hyphens only:
    max_chars = 32
    if len(project_id) > max_chars:
        myutils.print_fail(f"{sys._getframe().f_code.co_name}(): pool_id: \"{pool_id}\" > {max_chars} chars!")
        exit()

    pool_display_name="GitHub Actions Pool",
    pool_description="Pool for GitHub Actions OIDC"

    try:
        # The provider point to GitHub's OIDC issuer at
        # https://token.actions.githubusercontent.com
        # and include the necessary attribute mapping.

        # Initialize the IAM client:
        from google.cloud import iam_admin_v1  # not iam_v1
        client = iam_admin_v1.IAMClient()
            # NOT client = iam_admin_v1.IAMClient()
            # NOT client = iam_v1.WorkloadIdentityPoolsClient()

    except Exception as e:
        myutils.print_error(f"get_provider_pool_id(): client: {e}")
            # FIXME: get_provider_pool_id(): name 'iam_v1' is not defined 
        #return None, None

    try:

        # Create workload identity pool
        request = iam_admin_v1.CreateWorkloadIdentityPoolRequest(
            parent=f"projects/{project_id}/locations/global",
            workload_identity_pool=iam_admin_v1.WorkloadIdentityPool(
                display_name="My Pool",
                description="Description of the pool",
                disabled=False
            ),
            workload_identity_pool_id="my-pool-id"
        )
    except Exception as e:
        myutils.print_error(f"get_provider_pool_id(): request: {e}")
            # FIXME: cannot access local variable 'client' where it is not associated with a value 
        # return None, None

    try:

        response = client.create_workload_identity_pool(request=request)
        myutils.print_verbose(f"{sys._getframe().f_code.co_name}(): response{response}")
    except Exception as e:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): {e}")
            # FIXME: cannot access local variable 'client' where it is not associated with a value 
        # return None, None

    try:
        #pool = iam_v1.WorkloadIdentityPool(
        pool = iam_admin_v1.IAMClient(
            display_name=pool_display_name,
            description=pool_description
        )
    except Exception as e:
        myutils.print_error(f"get_provider_pool_id(): response: {e}")
            # FIXME: cannot access local variable 'client' where it is not associated with a value 
        # return None, None

    try:
        myutils.print_verbose(f"pool: \"{pool}\" ")

        parent = f"projects/{project_id}/locations/{location}"
        myutils.print_verbose(f"parent: \"{parent}\" ")
        operation = client.create_workload_identity_pool(
            parent=parent,
            workload_identity_pool=pool,
            workload_identity_pool_id=pool_id
        )
    except Exception as e:
        myutils.print_error(f"get_provider_pool_id(): operation: {e}")
        # return None, None

    try:
        pool_result = operation.result()
        myutils.print_verbose(f"Created pool: \"{pool_result.name}\" ")
        # 2. Create the OIDC Provider for GitHub:
        provider_client = iam_admin_v1.IAMClient()
            # iam_v1.WorkloadIdentityPoolProvidersClient()
        provider_parent = f"{parent}/workloadIdentityPools/{pool_id}"
        provider = iam_admin_v1.IAMClient(
            # iam_v1.WorkloadIdentityPoolProvider(
            display_name="GitHub Provider",
            description="OIDC provider for GitHub Actions",
            oidc=iam_admin_v1.WorkloadIdentityPoolProvider.Oidc(
                issuer_uri="https://token.actions.githubusercontent.com"
            ),
            attribute_mapping={
                "google.subject": "assertion.sub",
                "attribute.actor": "assertion.actor",
                "attribute.repository": "assertion.repository",
                "attribute.repository_owner": "assertion.repository_owner"
            }
        )
        provider_op = provider_client.create_workload_identity_pool_provider(
            parent=provider_parent,
            workload_identity_pool_provider=provider,
            workload_identity_pool_provider_id=provider_id
        )
        provider_result = provider_op.result()
        myutils.print_info(f"Provider ID: \"{provider_result.name}\" ")
        myutils.print_info(f"Pool ID \"{pool_id}\" as \"{pool_result.name}\" from get_pool_id() ")
        return provider_id, pool_id
    except Exception as e:
        myutils.print_error(f"get_provider_pool_id(): last: {e}")
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
    myutils.print_verbose(f"my_google_config_filepath = \"{filepath}\" ")
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

        myutils.print_verbose(f"My current account: \"{config[section][key]}\" within get_account_id() ")
        return config[section][key]

        #with open(my_google_config_filepath, 'r') as f:
        #    account = f.read().strip()
        #    if account:
        #        return account
    except Exception as e:
        print(f"{sys._getframe().f_code.co_name}() {e}", file=sys.stderr)
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
        print(f"{sys._getframe().f_code.co_name}(): {e}")
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
        
        myutils.print_verbose(f"Project ID: \"{project_id}\" authenticated with Application Default Credentials")        
        return {
            "credentials": credentials,
            "client": client,
            "project_id": project_id
        }
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        raise


def get_adc_project_id(adc_path: str) -> str:
    """
    Returns the project ID string from the ADC file, or None if not found.
    """
    # if CLI: "gcloud auth application-default login" was run to setup file:

    if not os.path.exists(adc_path):
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): ADC project_id not found at \"{my_adc_path}\" ")
        rc = setup_local_adc()
        return rc
    
    myutils.print_verbose(f"{sys._getframe().f_code.co_name}(): ADC found at: {adc_path}")
    with open(adc_path, 'r') as file:
        json_str = file.read()
    # import json
    json_data = json.loads(json_str)
    project_id = json_data.get('quota_project_id')
    # TODO: Expose other contents: client_id, client_secret, refresh_token 
    myutils.print_trace(f"{sys._getframe().f_code.co_name}(): json_data: \"{json_data}\" ")

    max_chars = 21
    if len(project_id) > max_chars:
        myutils.print_fail(f"{sys._getframe().f_code.co_name}(): project_id: \"{project_id}\" > {max_chars} chars!")
        exit()    
    
    myutils.print_info(f"{sys._getframe().f_code.co_name}(): project_id: \"{project_id}\" within get_adc_project_id() ")
    return project_id


def generate_project_id(base_name, max_length=30):
    """
    Generate a valid GCP project ID.
    
    Args:
        base_name (str): Base name for the project
        max_length (int): Maximum length for project ID (default 30)
    
    Returns:
        str: Valid project ID
    """
    # Convert to lowercase and replace invalid characters
    clean_name = ''.join(c.lower() if c.isalnum() else '-' for c in base_name)
    
    # Remove consecutive dashes and leading/trailing dashes
    clean_name = '-'.join(filter(None, clean_name.split('-')))
    
    # Add random suffix to ensure uniqueness
    # import string
    suffix = ''.join(random.choices(string.digits, k=6))
    
    # Ensure it starts with a letter
    if clean_name and not clean_name[0].isalpha():
        clean_name = 'project-' + clean_name
    elif not clean_name:
        clean_name = 'project'
    
    project_id = f"{clean_name}-{suffix}"
    max_chars = 21
    if len(project_id) > max_chars:
        myutils.print_fail(f"{sys._getframe().f_code.co_name}(): project_id: \"{project_id}\" > {max_chars} chars!")
        exit()
    # Truncate if too long
    #if len(project_id) > max_length:
    #    available_length = max_length - len(suffix) - 1  # -1 for dash
    #    project_id = f"{clean_name[:available_length]}-{suffix}"
    
    return project_id


def get_project_number(project_id=None) -> tuple[str, str]:
    """Get 12-digit project number Google assigns for each user-defined alphanumeric project ID
    for use by some IAM policies, billing APIs.
    """
    #import google.auth
    credentials, default_project = google.auth.default()
    
    if not project_id:
        project_id = default_project
    
    #from google.cloud import resourcemanager_v3  (more recent than _v1)
    client = resourcemanager_v3.ProjectsClient(credentials=credentials)
    project_name = f"projects/{project_id}"  # example: 123456789012 (12 digits)
    
    try:
        project = client.get_project(name=project_name)
        project_number = project.name.split('/')[-1]
        myutils.print_info(f"{sys._getframe().f_code.co_name}(): project_number: {project_number} from project_id: {project_id} ")
        return project_number, project_id  # Returns project number
    except Exception as e:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): {e}")
        # FIXME: 403 Cloud Resource Manager API has not been used in project sdk83360 before or it is disabled.
        # Enable it by visiting https://console.developers.google.com/apis/api/cloudresourcemanager.googleapis.com/overview?project=sdk83360 
        # then retry. If you enabled this API recently, wait a few minutes fo
        return None, project_id


def create_gcp_project(project_name, project_id=None, parent_org_id=None, parent_folder_id=None):
    """
    Create a Google Cloud Resource structure under a company's organization resource id over 
    a folders hierarchy. Under a single folder, each individual project is allocated resources.
    See https://cloud.google.com/resource-manager/docs/cloud-platform-resource-hierarchy
    Diagram: https://res.cloudinary.com/dcajqrroq/image/upload/v1748376248/gcp-resc-arch-586x7782_fqmrun.jpg
    
    Args:
        project_name (str): Display name for the project
        project_id (str, optional): Project ID. If None, will be generated from project_name
        parent_org_id (str, optional): Organization ID to create project under
        parent_folder_id (str, optional): Folder ID to create project under

        # Hierarchy of parent_org_id, parent_folder_id, project_id:
        # Under an organization
        #create_gcp_project("My New Project", parent_org_id="123456789")

        # With custom project ID
        #create_gcp_project("My New Project", project_id="my-custom-project-123456")

        # Under a folder
        #create_gcp_project("My New Project", parent_folder_id="987654321")

    Returns:
        dict: Project details including project_id and project_number
    """
    
    # Initialize the client
    client = resourcemanager_v3.ProjectsClient()
    
    # Generate project ID if not provided
    if not project_id:
        project_id = generate_project_id(project_name)
    
    print(f"Creating project with ID: {project_id}")
    print(f"Project display name: {project_name}")
    
    # Create the project request
    project = resourcemanager_v3.Project(
        project_id=project_id,
        display_name=project_name
    )
    
    # Set parent (organization or folder)
    if parent_org_id:
        project.parent = f"organizations/{parent_org_id}"
        print(f"Parent organization: {parent_org_id}")
    elif parent_folder_id:
        project.parent = f"folders/{parent_folder_id}"
        print(f"Parent folder: {parent_folder_id}")
    else:
        print("No parent specified - project will be created at root level")
    
    try:
        # Create the project
        operation = client.create_project(project=project)
        myutils.print_info(f"{sys._getframe().f_code.co_name}(): Operation name: {operation.name}")
        
        # Wait for the operation to complete
        #print("Waiting for project creation to complete...")
        result = operation.result(timeout=300)  # 5 minute timeout
        
        myutils.print_info(f"{sys._getframe().f_code.co_name}(): Project created successfully!")
        print(f"Project ID: {result.project_id}")
        print(f"Project Number: {result.name.split('/')[-1]}")
        print(f"Display Name: {result.display_name}")
        print(f"State: {result.state.name}")
        
        return {
            'project_id': result.project_id,
            'project_number': result.name.split('/')[-1],
            'display_name': result.display_name,
            'state': result.state.name
        }        
    except Exception as e:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): {str(e)}")
        raise


def check_api_status(project_id,gcp_svc_id) -> str:
    """
    Check if an individual API is already enabled
    Args:
        project_id (str): The Google Cloud Project ID
        gcp_svc_id="cloudresourcemanager"
    Returns:
        bool: True if enabled, False otherwise
    """
    try:
        client = service_usage_v1.ServiceUsageClient()
        service_name = f"projects/{project_id}/services/{gcp_svc_id}.googleapis.com"
        
        request = service_usage_v1.GetServiceRequest(name=service_name)
        service = client.get_service(request=request)
        
        is_enabled = service.state == service_usage_v1.State.ENABLED
        status = "enabled" if is_enabled else "disabled"
        myutils.print_verbose(f"{sys._getframe().f_code.co_name} project_id: \"{project_id}\" {status} for {gcp_svc_id} ")
        return is_enabled
        
    except Exception as e:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): {gcp_svc_id}: {str(e)}")
        return None


def enable_cloud_resource_manager_api(project_id:str) -> bool:
    """
    Enable the Cloud Resource Manager API for a given project.
    This only needs to be done once when project is created.
    https://console.cloud.google.com/apis/library/cloudresourcemanager.googleapis.com
    Args:
        project_id (str): The Google Cloud Project ID
        # TODO: Convert to a dictionary of services and iterate:
        # https://www.googleapis.com/auth/spreadsheets - Google Sheets
        # https://www.googleapis.com/auth/drive - Google Drive
        # https://www.googleapis.com/auth/gmail.readonly - Gmail (read-only)
        # https://www.googleapis.com/auth/gmail.modify - Gmail (read/write)

            # IAM Service Account Credentials API					
            # Identity and Access Management (IAM) API					
            # Cloud Logging API
            # Cloud Monitoring API
        gcloud services enable iamcredentials.googleapis.com --project=$PROJECT_ID
        gcloud services enable sts.googleapis.com --project=$PROJECT_ID
            storage.googleapis.com  # Service Usage API  Cloud Storage API
            storage-component.googleapis.com  # Cloud Storage - a RESTful service for storing and accessing your data
               # Google Cloud Storage JSON API					
               Google Cloud APIs					

            # Cloud Resource Manager API	
            Analytics Hub API					
            BigQuery API					
            BigQuery Connection API					
            BigQuery Data Policy API					
            BigQuery Migration API					
            BigQuery Reservation API					
            BigQuery Storage API					
            Cloud Dataplex API					
            Cloud Datastore API					
            Cloud SQL
            Cloud Trace API					
            Dataform API					
            Security Token Service API					
            Service Management API					

    Returns:
        bool: True if successful, False otherwise
    CLI:
    """
    if not project_id:
        print("No project_id provided to enable_cloud_resource_manager_api() ")
        return False
    gcp_svc_id="cloudresourcemanager"
    if check_api_status(project_id, gcp_svc_id) == "enabled":
        myutils.print_verbose(f"{sys._getframe().f_code.co_name}(): project: \"{project_id}\" is enabled for \"{gcp_svc_id}\" ")
        return True

    try:
        # Initialize the Service Usage client
        client = service_usage_v1.ServiceUsageClient()
        
        # Define the service name for Cloud Resource Manager API
        service_name = f"projects/{project_id}/services/{gcp_svc_id}.googleapis.com"
        # Create the enable service request:
        request = service_usage_v1.EnableServiceRequest(name=service_name)
        # Enable the service (this returns a long-running operation):
        operation = client.enable_service(request=request)
        
        # print("Waiting for operation to complete...")
        
        # Wait for the operation to complete
        result = operation.result(timeout=300)  # 5 minute timeout
        myutils.print_verbose(f"{sys._getframe().f_code.co_name}(): result: \"{result}\" ")
        
        myutils.print_info(f"{sys._getframe().f_code.co_name}(): project_id: \"{project_id}\" enabled for Cloud Resource Manager API")
        return True
        
    except Exception as e:
        myutils.print_error(f"Error enabling Cloud Resource Manager API: {str(e)}")
        return False


# def add_tags_to_project(project_id:str, tags:dict) -> bool:


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
            myutils.print_fail(f"{sys._getframe().f_code.co_name}(): gcloud CLI is not installed. Please install it from: https://cloud.google.com/sdk/docs/install")
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
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): Error setting up ADC: {str(e)}")
        return False


### GCP Service account


# Service account keys access data that belongs to an application, which includes
# a Google Workspace or Cloud Identity users through domain-wide delegation.
# CAUTION: Service account keys are not the same as service account credentials?
# CAUTION: When an app authenticates as a service account, the app obtains
# access to ALL resources the service account has permission to access.
# https://developers.google.com/zero-touch/guides/customer/quickstart/python-service-account

def check_svc_acct_exists(project_id: str = None, svc_acct_email: str = None):
    """
    Returns True if the service account provided exists.
    """
    myutils.print_trace(f"{sys._getframe().f_code.co_name}(): project_id: \"{project_id}\" ")
    # Example usage:
    #project_id = 'your-gcp-project-id'
    #svc_acct_email = 'my-service-account@your-gcp-project-id.iam.gserviceaccount.com'
    if not svc_acct_email:
        svc_acct_email = f"svc-{my_project_id}-{yymmddhhmm}"  # length between 6 and 30.
        myutils.print_trace(f"svc_acct_email constructed: \"{svc_acct_email}\" ")
    max_chars = 30
    if len(svc_acct_email) > max_chars:
        myutils.print_fail(f"{sys._getframe().f_code.co_name}(): svc_acct_email: \"{svc_acct_email}\" > {max_chars} chars!")
        exit()

    if not project_id:
        # TODO: Retrieve current project_id between "svc-" and "-"
        myutils.print_trace(f"project_id constructed: \"{project_id}\" ")

    credentials_path = get_svc_credentials_path(svc_acct_email)

    # pip install google-api-python-client google-auth
    #from google.oauth2 import service_account
    #rom googleapiclient.errors import HttpError
    try:
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        #from googleapiclient.discovery import build
        service = build('iam', 'v1', credentials=credentials)
        name = f'projects/{project_id}/serviceAccounts/{svc_acct_email}'
        try:
            service.projects().serviceAccounts().get(name=name).execute()
            myutils.print_info(f"{sys._getframe().f_code.co_name}(): 404 to \"{name}\" ")
            return True  # Service account exists
        except HttpError as e:
            if e.resp.status == 404:
                return False  # Service account does not exist
            else:
                raise  # Other errors

        myutils.print_info(f"Service account: {svc_acct_email} exists!")
        return True
    except Exception as e:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): {str(e)}")
        # [Errno 2] No such file or directory: '/Users/.../.google_credentials/svc-....json' 
        return False


def create_svc_acct_email(project_id: str = None, svc_acct_email: str = None, display_name: str = None):
    """
    Returns my_svc_cred_path (path to JSON-formatted credentials file).
    This is done one time for each service account id.
    Usage: 
        my_svc_cred_path = (my_project_id, my_svc_acct_email, display_name)
    Args:
        project_id: GCP project ID
        svc_acct_email: Unique identifier like 'my-service-account@your-project-id.iam.gserviceaccount.com'
        display_name: Human-readable name for the service account
    CLI:
        gcloud iam service-accounts create $SA_NAME \
            --project=$PROJECT_ID \
            --display-name="$SA_DISPLAY_NAME" \
            --description="Service account for workload identity federation"    
    print(f"- Service Account: $SA_NAME@$PROJECT_ID.iam.gserviceaccount.com")
    """
    # TODO: If specified in CLI args, return
    # TODO: If GOOGLE_SVC_ACCT_EMAIL specified in .env, return 
    if not project_id:
        project_id = my_project_id
        myutils.print_trace(f"Global my_project_id: \"{project_id}\" ")
    if not svc_acct_email:
        svc_acct_email = f"svc-{my_project_id}-{yymmddhhmm}"  # length between 6 and 30.
        myutils.print_trace(f"svc_acct_email constructed: \"{svc_acct_email}\" ")
    max_chars = 30
    if len(svc_acct_email) > max_chars:
        myutils.print_fail(f"{sys._getframe().f_code.co_name}(): svc_acct_email: \"{svc_acct_email}\" > {max_chars} chars!")
        exit()    
    
    if not display_name:
        display_name = svc_acct_email + "-name"   #.iam.gserviceaccount.com"
        myutils.print_trace(f"display_name constructed: \"{display_name}\" ")
    
    exists = check_svc_acct_exists(project_id, svc_acct_email)
    if exists:
        myutils.print_verbose(f"Service account: \"{svc_acct_email}\" already created.")
        return True
        # Manually view Service Accounts using GUI Chrome browser at:
        # https://console.cloud.google.com/iam-admin/serviceaccounts

    try:
        #import requests
        #from google.auth import default
        # Get credentials and JWT access token:
        credentials, _ = default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
        #from google.auth.transport.requests import Request
        credentials.refresh(Request())
    except Exception as e:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): credentials: {str(e)}")
        return False

    try:
        access_token = credentials.token  # such as "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        myutils.print_trace(f"{sys._getframe().f_code.co_name}(): access_token: {len(access_token)} chars ")
        myutils.print_secret(f"{access_token}")
        url = f'https://iam.googleapis.com/v1/projects/{project_id}/serviceAccounts'
        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json'
        }
        data = {
            'accountId': svc_acct_email,
            'serviceAccount': {
                'displayName': display_name
            }
        }
        response = requests.post(url, headers=headers, json=data)
        key_data = response.json()
        # WARNING: Do not print out key_data which contains secret values!
        myutils.print_trace(f"{sys._getframe().f_code.co_name}(): {len(key_data)} chars")
            # The beginning of credential.json file for service account:
            # {'name': 'projects/sdk83360/serviceAccounts/svc-sdk83360-2506051513@sdk83360.iam.gserviceaccount.com', 
            # 'projectId': 'sdk83360', 
            # 'uniqueId': '123456749012345678901',  [21 chars]
            # 'email': 'svc-sdk83360-2506051513@sdk83360.iam.gserviceaccount.com', 
            # 'displayName': 'svc-sdk83360-2506051513-name', 
            # 'etag': 'MDEwMjE5MjA=', 
            # 'oauth2ClientId': '104640841729869098164'} 
        return key_data

    except Exception as e:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): {str(e)}")
        return None


def get_svc_credentials_path(svc_acct_email) -> str:
    """This utility function returns the full file path to a service account credentials file
    GCP uses to authenticate without human interaction.
    Use of this function standardizes the path so it would be easier to change system-wide.
    """
    # TODO: Retrieve from .env file variable GOOGLE_CREDENTIALS_PATH="~/.google_credentials"
    # if not GOOGLE_CREDENTIALS_PATH_PREFIX:
       #GOOGLE_CREDENTIALS_PATH_PREFIX = f"{str(Path.home())}/.google_credentials"

    credentials_path = f"{str(Path.home())}/.google_credentials"   # the private key never in GitHub
    myutils.print_trace(f"{sys._getframe().f_code.co_name}(): credentials_path: \"{credentials_path}\" ")
    if not svc_acct_email:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): svc_acct_email is required")
        return None
    else:
        svc_acct_credentials_path = f"{credentials_path}/{svc_acct_email}.json"  # the private key never in GitHub
        myutils.print_verbose(f"{sys._getframe().f_code.co_name}(): svc_acct_credentials_path: \"{svc_acct_credentials_path}\" ")
        # like "/Users/johndoe/.google_credentials/svc-sdk83360-2506050022@sdk83360.iam.gserviceaccount.com.json"
        return svc_acct_credentials_path


def get_svc_acct_key_path(svc_acct_email) -> str:
    """This utility function returns the full file path to the  
    private key .pem file needed to access the associated service account
    as global variable my_svc_acct_key_path.

    Args: The service account's long svc email address arg. 
    global my_svc_acct_email is used to create a folder
    like "/Users/johndoe/.google_credentials/svc-sdk83360.../private_key.pem"
    Use of this function standardizes the path so it would be easier to change system-wide:
    """
    if not svc_acct_email:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): svc_acct_email is required")
        return None
    else:
        key_path = f"{str(Path.home())}/.google_credentials/{svc_acct_email}"
           # WARNING: The private key is never exposed to GitHub
        myutils.print_verbose(f"{sys._getframe().f_code.co_name}(): \"{key_path}\" ")
        # like "/Users/johndoe/.google_credentials/svc-sdk83360-2506050022@sdk83360.iam.gserviceaccount.com/private_key.pem"
        return key_path


def save_svc_acct_credentials_path(credentials: str, filepath: str) -> bool:
    """
    Save credentials dictionary to a JSON file.
    Args:
        credentials: Dictionary of credentials
        filename: Name of the file to save the credentials to
    """
    if not credentials:
        myutils.print_fail(f"{sys._getframe().f_code.co_name}(): credentials is needed but not provided.")
        exit()
    if not filepath:
        myutils.print_fail(f"{sys._getframe().f_code.co_name}(): filepath is needed but not provided.")
        exit()

    try:
        with open(filepath, 'w') as f:
            json.dump(credentials, f, indent=2)
        myutils.print_info(f"{sys._getframe().f_code.co_name}(): saved to \"{filepath}\" ")
        return True
    except Exception as e:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): Error: {str(e)}")
        return False


def create_credentials_from_values(project_id, private_key_id, private_key, client_email, client_id):
    """
    Create credentials JSON Dictionary from individual values.
    """
    svc_cred_dict = {
        "type": "service_account",
        "project_id": project_id,
        "private_key_id": private_key_id,
        "private_key": private_key,
        "client_email": client_email,
        "client_id": client_id,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email.replace('@', '%40')}"
    }
    # etag?

    #svc_cred_json = base64.b64decode(credentials_dict).decode('utf-8')
    #svc_cred_dict = json.loads(svc_cred_str)  # Convert to dict

    # WARNING: Do not print secret value in private_key_id!
    myutils.print_verbose(f"{sys._getframe().f_code.co_name}(): {len(svc_cred_dict)} chars in {type(svc_cred_dict)}")
    return svc_cred_dict


def save_credentials_to_file(credentials, filename="service-account-credentials.json"):
    """
    Save credentials dictionary to a JSON file for access by GCP.
    """
    try:
        with open(filename, 'w') as f:
            json.dump(credentials, f, indent=2)
        myutils.print_verbose(f"{sys._getframe().f_code.co_name}(): Credentials template saved to \"{filename}\" ")
        return True
    except Exception as e:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): {str(e)}")
        return False


def validate_credentials_file(filename):
    """
    Validate that a credentials file has the required fields and type values.
    """
    required_fields = [
        "type", "project_id", "private_key_id", "private_key", 
        "client_email", "client_id", "auth_uri", "token_uri"
    ]
    
    try:
        with open(filename, 'r') as f:
            creds = json.load(f)
        
        missing_fields = [field for field in required_fields if field not in creds]
        
        if missing_fields:
            myutils.print_fail(f"{sys._getframe().f_code.co_name}(): Missing required fields: {missing_fields}")
            return False
        
        if creds["type"] != "service_account":
            myutils.print_fail(f"{sys._getframe().f_code.co_name}(): Invalid credential type. Must be 'service_account'")
            return False
            
        myutils.print_verbose(f"{sys._getframe().f_code.co_name}(): Credentials file is valid!")
        return True
        
    except FileNotFoundError:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): File {filename} not found")
        return False
    except json.JSONDecodeError:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): Invalid JSON in {filename}")
        return False
    except Exception as e:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): {str(e)}")
        return False


def auth_with_svc_acct_json(key_path: str) -> Dict[str, Any]:
    """
    Authenticate using a service account key file.
    Args:
        key_path: Path to the service account JSON key file
    Returns:
        Dict containing credentials info and authenticated client
    """
    try:
        #from google.cloud import storage
        
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
        # WARNING: Do not print key_data which contains secret values!
        myutils.print_verbose(f"{sys._getframe().f_code.co_name}(): key_data: {len(key_data)} chars ")
        
        svc_acct_dict = {
            "credentials": credentials,
            "client": client,
            "project_id": key_data.get('project_id'),
            "client_email": key_data.get('client_email')
        }
        myutils.print_verbose(f"{sys._getframe().f_code.co_name}(): svc_acct_dict: {svc_acct_dict}")
        return svc_acct_dict   # -> Dict[str, Any]:
        
    except Exception as e:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): {str(e)}")
        raise


#### Other Credential


def save_credential_config(config: Dict, filepath: str) -> None:
    """Save credential configuration to file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        myutils.print_info(f"{sys._getframe().f_code.co_name}(): to \"{filepath}\" ")
        return True
    except Exception as e:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): {str(e)}")
        return False


def get_project_info(credentials):
    """Get project information using the authenticated credentials"""

    # from google.cloud import resourcemanager_v3  # uv pip install google-cloud-resource-manager

    client = resourcemanager_v3.Client(credentials=credentials)
    projects = client.list_projects()
    
    myutils.print_heading(f"{sys._getframe().f_code.co_name}(): Accessible projects:")
    for project in projects:
        myutils.print_info(f"{sys._getframe().f_code.co_name}():  - {project.project_id}: {project.name}")



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
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): {e}")
        print("Please manually install the required packages:")
        print("uv pip install google-cloud-storage google-auth google-auth-oauthlib google-auth-httplib2")
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
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): {e}")
        # {file=sys.stderr} 
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


def list_regions(project_id=None):
    """List all available Google Cloud regions with their details."""
    #from google.cloud import compute_v1
    #import tabulate
    #import pandas as pd
    #import sys
    if not project_id:
        myutils.print_fail(f"{sys._getframe().f_code.co_name}(): project_id not provided")
        exit(9)
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
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): {e}")
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
        myutils.print_heading(f"{sys._getframe().f_code.co_name}(): service: \"{service}\" ")
        for key, value in pricing.items():
            print(f"    {key}: {value}")
        print()  # Extra line for readability


#### Google Workspaces Sheets, Documents zzz


def authenticate_service_account(credentials_file, scopes):
    """
    Authenticate using service account credentials
    
    Args:
        credentials_file (str): Path to the credentials.json file
        scopes (list): List of Google API scopes needed
    Returns:
        google.oauth2.service_account.Credentials: Authenticated credentials object
    """
    #from google.oauth2 import service_account
    #from googleapiclient.discovery import build
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file, 
            scopes=scopes
        )
        return credentials
    except Exception as e:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): {e}")
        return None

def create_service(credentials, service_name, version):
    """
    Create a Google API service object
    
    Args:
        credentials: Authenticated credentials object
        service_name (str): Name of the Google service (e.g., 'sheets', 'drive', 'gmail')
        version (str): API version (e.g., 'v4', 'v3', 'v1')
    
    Returns:
        Google API service object
    """
    try:
        service = build(service_name, version, credentials=credentials)
        myutils.print_verbose(f"{sys._getframe().f_code.co_name}(): service: \"{service}\" ")
        return service
    except Exception as e:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): {e}")
        return None


# Alternative: Direct authentication for specific services
def quick_sheets_auth(credentials_file):
    """Quick authentication specifically for Google Sheets"""
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = service_account.Credentials.from_service_account_file(
        credentials_file, scopes=scopes
    )
    service = build('sheets', 'v4', credentials=creds)
    myutils.print_verbose(f"{sys._getframe().f_code.co_name}(): service: \"{service}\" ")
    return service


def quick_drive_auth(credentials_file):
    """Quick authentication specifically for Google Drive"""
    scopes = ['https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_file(
        credentials_file, scopes=scopes
    )
    service = build('drive', 'v3', credentials=creds)
    myutils.print_verbose(f"{sys._getframe().f_code.co_name}(): service: \"{service}\" ")
    return service


# Example of reading a Google Sheet
def read_sheet_example(credentials_file, spreadsheet_id, range_name):
    """
    Example function to read data from a Google Sheet
    
    Args:
        credentials_file (str): Path to credentials.json
        spreadsheet_id (str): The ID of the Google Sheet
        range_name (str): Range to read (e.g., 'Sheet1!A1:C10')
    """
    try:
        service = quick_sheets_auth(credentials_file)
        
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print('No data found.')
            return None
        
        print(f'Retrieved {len(values)} rows of data:')
        for row in values:
            print(row)
        
        return values
        
    except Exception as e:
        myutils.print_verbose(f"{sys._getframe().f_code.co_name}(): service: \"{service}\" ")
        print(f'Error reading sheet: {e}')
        return None


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


def get_google_doc_title(doc_id=None):
    """
    See https://developers.google.com/workspace/sheets/api/quickstart/python
    import os.path
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    """
    if not doc_id:
        myutils.print_fail(f"{sys._getframe().f_code.co_name}(): doc_id not provided")
        exit(9)

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
        document = service.documents().get(documentId=doc_id).execute()
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
            myutils.print_fail(f"{sys._getframe().f_code.co_name}(): secret_id not provided")
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
            myutils.print_info(f"{sys._getframe().f_code.co_name}(): secret_id: {secret_id} v{version} added.")

        # Build the resource name of the secret version:
        if version_id == "latest":
            version_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        else:
            version_name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        
        # Access the secret version:
        response_obj = client.access_secret_version(request={"name": version_name})
        
        # WARNING: Do not print the secret in a production environment!
        myutils.print_verbose(f"{sys._getframe().f_code.co_name}(): Secret value not shown")
        return response_obj.payload.data.decode("UTF-8")
    
    except Exception as e:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): Error inget_secret_from_secret_manager(): {e}")
        return None    


### Backup


def start_backup(DRIVE_VOLUME=None) -> float:
    """On macOS, invoke macOS Time Machine drive to backup all files changed.
    USAGE: run_seconds = start_backup()
    :param VOLUME: The name of the external volume (e.g., 'T7') 
       We assume it's properly formatted.
    : Global flag DO_BACKUP to backup or not.
    : Global drive within /Volumes/DRIVE_VOLUME
    : returns func run time in seconds.
    """
    if not myutils.is_macos():
        myutils.print_fail(f"{sys._getframe().f_code.co_name}(): not macOS. No backup initiated.")
        return None
    if not DRIVE_VOLUME:        
        myutils.print_fail(f"{sys._getframe().f_code.co_name}(): DRIVE_VOLUME not specified.")
        return None

    # Verify that external USB drive is inserted:
    try:
        # import subprocess
        # Set the backup destination
        set_destination_command = ["tmutil", "setdestination", f"/Volumes/{DRIVE_VOLUME}"]

        func_start_timer = time.perf_counter()
        subprocess.run(set_destination_command, check=True)
        myutils.print_info(f"{sys._getframe().f_code.co_name}(): --volume {DRIVE_VOLUME} used by start_backup()")

        start_backup_command = ["tmutil", "startbackup", "--block"]
        subprocess.run(start_backup_command, check=True)

        func_duration = time.perf_counter() - func_start_timer
        myutils.print_info(f"{sys._getframe().f_code.co_name}(): completed in {func_duration:.5f} seconds")
    except subprocess.CalledProcessError as e:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): {e}")

    return func_duration


#### GCS Authenticated Bucket Storage



def list_gcs_buckets(client_obj):
    """
    List GCS (Google Cloud Storage) buckets (to verify authentication worked).
    Args:
        client: An authenticated storage client
    """
    try:
        myutils.print_trace(f"{sys._getframe().f_code.co_name}(): Listing storage buckets to verify authentication within list_gcs_buckets() ")
        buckets = list(client_obj.list_buckets())
        
        if not buckets:
            myutils.print_error(f"{sys._getframe().f_code.co_name}(): No buckets found in this project within list_gcs_buckets() ")
        else:
            for bucket in buckets:
                myutils.print_verbose(f"{sys._getframe().f_code.co_name}(): - {bucket.name}")
    except Exception as e:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): {e}")


# TODO: Google Key 


#### ADC 


def use_storage_with_adc():
    """Example of using Google Cloud Storage with ADC"""
    # Credentials are automatically loaded by the client
    storage_client = storage.Client()
    
    # List buckets
    buckets = storage_client.list_buckets()
    myutils.print_heading(f"{sys._getframe().f_code.co_name}(): Cloud Storage Buckets:")
    for bucket in buckets:
        myutils.print_info(f"{sys._getframe().f_code.co_name}(): {bucket.name}")
    else:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): No storage found.")


#### BigQuery


def use_bigquery_with_adc():
    """Example of using BigQuery with ADC"""
    # Credentials are automatically loaded by the client
    bigquery_client = bigquery.Client()
    
    # List datasets
    datasets = list(bigquery_client.list_datasets())
    myutils.print_heading(f"{sys._getframe().f_code.co_name}(): BigQuery Datasets:")
    if datasets:
        for dataset in datasets:
            print(f"- {dataset.dataset_id}")
    else:
        myutils.print_error(f"{sys._getframe().f_code.co_name}(): No datasets found.")


#### Pub/Sub


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
    print(f"{sys._getframe().f_code.co_name}(): subscriber: \"{subscriber}\" ")
    # Get authenticated project ID
    _, project_id = google.auth.default()
    
    # List topics (if project_id is available)
    if project_id:
        project_path = f"projects/{project_id}"
        topics = publisher.list_topics(request={"project": project_path})
        print("Pub/Sub Topics:")
        for topic in topics:
            print(f"- {topic.name}")


#### Send Gmail, Slack, Discord, SMS, etc.


def send_gmail():
    """
    Send an email using Gmail API.
    First, create a service account and grant it the "Gmail API User" role.
    Then, download the JSON key file and set the environment variable GOOGLE_APPLICATION_CREDENTIALS 
    to the path of the JSON key file.
    See https://levelup.gitconnected.com/how-to-send-emails-in-python-with-gcp-cloud-function-b5478e237b27
    """

    # Create a secure SSL/TLS connection with smtplib.SMTP_SSL() 
    # or smtplib.SMTP().starttls() to create an insecure connection with encrypted content.

    # Use MIMEText to send a MIME message in plain text.
    # Send MIMEMultipart HTML email with smtplib.SMTP.send_message().
    



####


if __name__ == "__main__":
    
    if SHOW_FUNCTIONS:
        myutils.list_pgm_functions(sys.argv[0])
    
    if args.install:   # --install:
        check_install_packages()

    my_account = get_account_id()  # client email address
    
    # Created by running CLI: gcloud auth application-default login
    my_adc_path = f"{my_home_dir}/.config/gcloud/application_default_credentials.json"
        # Windows	%APPDATA%\gcloud\application_default_credentials.json
    if args.setup_adc:   # if requested by --setup-adc:
        rc = setup_local_adc()  # which calls get_adc_project_id()
    else:   
        my_project_id = get_adc_project_id(my_adc_path)
    if not my_project_id:
        my_project_id = get_project_id()
    if my_project_id:
        enable_cloud_resource_manager_api(my_project_id)
    if not my_project_number:
        my_project_number, my_project_id = get_project_number(my_project_id)

    # Single global time for service account creation during this run:
    yymmddhhmm = myutils.get_user_local_timestamp('yymmddhhmm')

    pool_location = "global"
    # my_provider_id, my_pool_id = get_provider_pool_id(my_project_id)
    my_provider_id = "prov-{pool_location}-{yymmddhhmm}"
        # provider_ids are 1-32 characters, lowercase letters, numbers, and hyphens only

    my_pool_id = f"{pool_location}-{yymmddhhmm}"
    max_chars = 21
    if len(my_pool_id) > max_chars:
        myutils.print_fail(f"{sys._getframe().f_code.co_name}(): my_pool_id: \"{my_pool_id}\" > {max_chars} chars!")
        exit()

    my_pool_display_name="GitHub Actions Pool",
    my_pool_description="Pool for GitHub Actions OIDC"

    my_svc_acct_json = create_svc_acct_email(my_project_id)
          # The beginning of credential.json file for service account:
          # {'name': 'projects/sdk83360/serviceAccounts/svc-sdk83360-2506051513@sdk83360.iam.gserviceaccount.com', 
          # 'projectId': 'sdk83360', 
          # 'uniqueId': '123456749012345678901',  [21 chars]
          # 'email': 'svc-sdk83360-2506051513@sdk83360.iam.gserviceaccount.com', 
          # 'displayName': 'svc-sdk83360-2506051513-name', 
          # 'etag': 'MDEwMjE5MjA=', 
          # 'oauth2ClientId': '104640841729869098164'} 
    my_svc_acct_uniqueId = my_svc_acct_json['uniqueId']
    my_svc_acct_email = my_svc_acct_json['email']  # '???@?.iam.gserviceaccount.com
    my_svc_acct_etag = my_svc_acct_json['etag']
    my_svc_acct_oauth2ClientId = my_svc_acct_json['oauth2ClientId']

    my_svc_cred_path = get_svc_credentials_path(my_svc_acct_email)
    my_svc_acct_key_path = get_svc_acct_key_path(my_svc_acct_email)
    # svc_acct_key_path = get_svc_acct_key_path(svc_acct_credentials_path)
        # inside svc_acct_key_path=f"{svc_acct_key_path}/{svc_acct_email}"

    myutils.generate_rsa_keypair(key_size=4096, output_dir=my_svc_acct_key_path)
    # TODO: Retrieve from private key file:
    svc_acct_key_private_path = f"{my_svc_acct_key_path}/private_key.pem"
        # inside svc_acct_key_public_path=f"{svc_acct_key_path}/public_key.pem"
    private_key_text = myutils.read_file_to_string(svc_acct_key_private_path)
        # private_key_text="-----BEGIN PRIVATE KEY-----\...\n-----END PRIVATE KEY-----\n"
    #svc_acct_key_file = create_svc_acct_key_file(svc_acct_credentials_path, private_key_text)
    private_key_text = myutils.read_file_to_string(svc_acct_key_private_path)
    
    # WARNING: Do not expose secret value in private_key_id:
    my_private_key_id = myutils.gen_random_alphanumeric(12)  # like "abc123def456"  # 12 char.

    svc_cred_dict = create_credentials_from_values(
        project_id=my_project_id,
        private_key_id=my_private_key_id,
        private_key=private_key_text,
        client_email=my_svc_acct_email,
        client_id=my_svc_acct_oauth2ClientId,
    )
    # Add:
    #   unique_id=my_svc_acct_uniqueId
    #   etag=my_svc_acct_etag,

    my_svc_acct_json_path = f"{my_svc_acct_key_path}.json"
    result = save_credentials_to_file(svc_cred_dict, my_svc_acct_json_path)
    if result:  # True
        auth_result = auth_with_svc_acct_json(my_svc_acct_json_path)
    # TODO: Clean up unused service accounts!
    # Manually view Service Accounts using GUI Chrome browser at:
    # https://console.cloud.google.com/iam-admin/serviceaccounts


    SCOPES = ["https://www.googleapis.com/auth/documents.readonly",
                'https://www.googleapis.com/auth/spreadsheets', 
                'https://www.googleapis.com/auth/gmail.send']  # Adjust as needed

    #### Google Workspace Sheets, Documents, Gmail

    # def get_google_sheet_id():
    # TODO: Spreadsheet of Public file "Musicals" for View at Copy link: 
    # https://docs.google.com/spreadsheets/d/11CTYgW5TP9IzR8LR4NYWhxyanYp5XJypE4eMfnBIlhI/edit?usp=sharing

    # TODO: Login using Service Account or ADC or Workload Identity PoolPool


    exit()

    
    # Now, do something with GCP Secretes, Storage, BigQuery, etc.

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
        auth_result = auth_with_svc_acct_json(args.service_account)
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
        regions_data = list_regions(my_project_id)
        display_regions(regions_data, output_format)

        # print_svcs_price_list()
    
    # get_best_region() <- get_cheapest_region() <- get_region_to_sku() <- get_fastest_region() <- get_closest_region()

     #Utility test: my_encrypted_token = encrypt_secret(b"Hello world")
    # get_secret()
    # send_gmail() TODO: https://medium.com/gitconnected/how-to-send-emails-in-python-with-gcp-cloud-function-b5478e237b27
    # send_slack_msg()
    # send_discord_msg()


    # Create GCP VM using Python: https://www.youtube.com/watch?v=UWLBcuktb1U&list=PLLrA_pU9-Gz3zmg__9iK_nnfzYQAGwgH4
        # by https://www.linkedin.com/in/vishal-bulbule/">Vishal Bulbule</a> https://topmate.io/vishal_bulbule
        # from google.cloud import compute_v1

