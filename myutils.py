#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0

#### SECTION 01: Dunder (double-underline) variables accessible from CLI outside Python:

__commit_date__ = "2025-05-30"
__commit_msg__ = "v005 + print emojis :myutils.py"
__repository__ = "https://github.com/bomonike/google/blob/main/myutils.py"

"""myutils.py

This Python module provides utility functions called by my other custom programs running on macOS:
gcp-services.py, etc.

Functions provided show OS properties, process directories, files, strings, etc.

USAGE on CLI: 
    pip install myutils
    import myutils

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
"""

# from https://github.com/trkonduri/myutils/blob/master/myutils.py

#### SECTION 02: Built-in Python libraries:

import argparse
import ast
import base64
# import boto3  # for aws python
from collections import OrderedDict, defaultdict
from datetime import datetime, timezone  # ensure this is the only datetime import
import gc
import http.client
import importlib.util
import inspect
import json
import logging   # see https://realpython.com/python-logging/
import math
import os
#import pathlib
from pathlib import Path
import platform # https://docs.python.org/3/library/platform.html
import pwd                # https://www.geeksforgeeks.org/pwd-module-in-python/
import random
import resource
import site
import shutil     # for disk space calcs
import socket
import subprocess
import sys
import time
from typing import Dict, Any
import urllib.request
from urllib import request, parse, error
import uuid


#### SECTION 03: Third-party Python libraries (requiring pip install):

try:
    # pylint: disable=wrong-import-position
    from contextlib import redirect_stdout
    from dotenv import load_dotenv   # install python-dotenv
    import pandas as pd
    from pathlib import Path
    import psutil      #  psutil-5.9.5
    from pythonping import ping
    import pytz   # time zones
    import requests
    import statsd
    from tabulate import tabulate
    import tracemalloc
except Exception as e:
    print(f"Python module import failed: {e}")
    # pyproject.toml file exists
    print(f"Please activate your virtual environment:\n  python3 -m venv venv && source venv/bin/activate")
    #print("    sys.prefix      = ", sys.prefix)
    #print("    sys.base_prefix = ", sys.base_prefix)
    exit(9)


#### SECTION 03: Print utility globals and functions:


## Global variables: Colors Styles:
class bcolors:  # ANSI escape sequences: https://gist.github.com/JBlond/2fea43a3049b38287e5e9cefc87b2124
    BOLD = '\033[1m'       # Begin bold text
    UNDERLINE = '\033[4m'  # Begin underlined text

    INFO = '\033[92m'      # [92 green
    HEADING = '\033[37m'   # [37 white
    VERBOSE = '\033[91m'   # [91 beige
    WARNING = '\033[93m'   # [93 yellow
    ERROR = '\033[95m'     # [95 purple
    TRACE = '\033[35m'     # CVIOLET
    TODO = '\033[96m'      # [96 blue/green
    FAIL = '\033[31m'      # [31 red
                           # [94 blue (bad on black background)
    STATS = '\033[36m'     # [36 cyan
    CVIOLET = '\033[35m'
    CBEIGE = '\033[36m'
    CWHITE = '\033[37m'
    GRAY = '\033[90m'

    RESET = '\033[0m'   # switch back to default color

# Starting settings:
show_secrets = False   # Always False to not show
show_heading = True    # -q  Don't display step headings before attempting actions
show_fail = True       # Always show
show_error = True      # Always show
show_warning = True    # Always show
show_trace = True      # -vv Display responses from API calls for debugging code
show_verbose = True    # -v  Display technical program run conditions
show_sys_info = True
show_todo = True
show_info = True
SHOW_DEBUG = True
show_dates_in_logs = False
print_prefix = "***"

SHOW_SUMMARY_COUNTS = True

def no_newlines(in_string):
    """Strip new line from in_string
    """
    return ''.join(in_string.splitlines())

def print_separator():
    """A function to put a blank line in CLI output. Used in case the technique changes throughout this code.
    """
    print(" ")

def print_heading(text_in):
    if show_heading:
        # Backhand Index Pointing Down Emoji highlights content below was approved as part of Unicode 6.0 in 2010 under the name "White Down Pointing Backhand Index" and added to Emoji 1.0 in 2015.
        print("👇", end="")
        if show_dates_in_logs:
            print(get_log_datetime(), end="")
        print(bcolors.HEADING+bcolors.UNDERLINE,f'{text_in}', bcolors.RESET)

def print_fail(text_in):  # when program should stop
    if show_fail:
        # The ⛔ No Entry (Stop sign) Emoji indicates forbidden. approved as part of Unicode 5.2 in 2009 and added to Emoji 1.0 in 2015.
        print("❌", end="")
        if show_dates_in_logs:
            print(get_log_datetime(), end="")
        print(bcolors.FAIL, f'{text_in}', bcolors.RESET)

def print_error(text_in):  # when a programming error is evident
    if show_fail:
        print("⭕", end="")
        if show_dates_in_logs:
            print(get_log_datetime(), end="")
        print(bcolors.ERROR, f'{text_in}', bcolors.RESET)

def print_warning(text_in):
    if show_warning:
        print("⚠️", end="")
        if show_dates_in_logs:
            print(get_log_datetime(), end="")
        print(bcolors.WARNING, f'{text_in}', bcolors.RESET)

def print_todo(text_in):
    if show_todo:
        # The 🛠️ hammer and wrench emoji is commonly used for various content concerning tools, building, construction, and work, both manual and digital
        print("💡", end="")
        if show_dates_in_logs:
            print(get_log_datetime(),  end="")
        print(bcolors.TODO, f'{text_in}', bcolors.RESET)

def print_info(text_in):
    if show_info:
        # Alternately: print("👍", end="")
        print("✅", end="")
        if show_dates_in_logs:
            print(get_log_datetime(), end="")
        print(bcolors.INFO+bcolors.BOLD, f'{text_in}', bcolors.RESET)

def print_verbose(text_in):
    if show_verbose:
        # The 📣 speaker emoji is used to represent sound, noise, or speech.
        print("📢", end="")
        if show_dates_in_logs:
            print(get_log_datetime(), end="")
        print(bcolors.VERBOSE, f'{text_in}', bcolors.RESET)

def print_trace(text_in):  # displayed as each object is created in pgm:
    if show_trace:
        # The 🔍 magnifying glass is a classic for searching, looking, inspecting, approved as part of Unicode 6.0 in 2010 under the name "Left-Pointing Magnifying Glass" and added to Emoji 1.0 in 2015.
        print("⚙️", end="")
        if show_dates_in_logs:
            print(get_log_datetime(), end="")
        # The fingerprint emoji was approved as part of Unicode 16.0 in 2024 and added to Emoji 16.0 in 2024.
        print(bcolors.TRACE, f'{text_in}', bcolors.RESET)

def print_secret(secret_in: str) -> None:
    """ Outputs secrets discreetly - display only the first few characters (like Git) with dots replacing the rest.
    """
    # See https://stackoverflow.com/questions/3503879/assign-output-of-os-system-to-a-variable-and-prevent-it-from-being-displayed-on
    if show_secrets:  # program parameter 
        # The triangular red flag on post emoji signals a problem or issue. Approved as part of Unicode 6.0 in 2010  added to Emoji 1.0 in 2015.
        print("🚩", end="")
        if show_dates_in_logs:
            print(get_log_datetime(), end="")

        secret_len = 3
        if len(secret_in) <= 10:  # slice
            # Regardless of secret length, to reduce hacker ability to guess:
            print(bcolors.GRAY,"secret too small to print.", bcolors.RESET)
            #print(bcolors.GRAY,"\"",secret_in,"\"", bcolors.RESET)
        else:
            print(bcolors.WARNING, "WARNING: Secret specified to be shown. POLICY VIOLATION: ", bcolors.RESET)
            # WARNING NOTE: secrets should not be printed to logs.
            secret_out = secret_in[0:4] + "."*(secret_len-1)
            print(bcolors.GRAY,"\"",secret_out,"...\"", bcolors.RESET)
    return None


def show_print_samples() -> None:
    """Display what different type of output look like.
    """
    # See https://wilsonmar.github.io/python-samples/#PrintColors
    print_heading("print_heading( show_print_samples():")
    print_fail("print_fail() -> sample fail")
    print_error("print_error() -> sample error")
    print_warning("print_warning() -> sample warning")
    print_todo("print_todo() -> sample task to do")
    print_info("print_info() -> sample info")
    print_verbose("print_verbose() -> sample verbose")
    print_trace("print_trace() -> sample trace")
    print_secret("123456")
    return None


def current_function_name(method="A") -> str:
    """Return the name of the current function
    using match-case (Python 3.10+).
    """
    match method:
        case "A":
            # import sys
            current_function = sys._getframe().f_code.co_name
        case "B":
            # import inspect
            current_function = inspect.currentframe().f_code.co_name
        case "C":
            current_function = inspect.stack()[0][3]
        case "D":
            current_function = inspect.currentframe().f_back.f_code.co_name
        case _:  # default case
            print_error("Invalid (method)")
            return None

    return current_function


def do_clear_cli() -> None:
    """Clear the CLI screen."""
    print_trace(f"At {sys._getframe().f_code.co_name}()")
    # import os
    # QUESTION: What's the output variable?
    lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')
    return None


#### SECTION 09: File timestamps and lists:


def filetimestamp(fileName):
    """
    USAGE: print(f"File last modified: {myutils.filetimestamp("myutils.py")} ")
    # TODO: Add time zone info. 📢
    """
    created = os.path.getmtime(fileName)
    modified = os.path.getctime(fileName)
    if created == modified:
        return f"{ctimestamp(fileName)}"
    else:
        return f"{mtimestamp(fileName)}"

def mtimestamp(fileName):
    """
    USAGE: print(f"File last modified: {myutils.mtimestamp("myutils.py")} ")
    """
    t = os.path.getmtime(fileName)
    return datetime.fromtimestamp(t).strftime("%Y-%m-%d-%H:%M")

def ctimestamp(fileName):
    """
    USAGE: print(f"File created: {myutils.ctimestamp("myutils.py")}")
    Fixed datetime import issue
    """
    t = os.path.getctime(fileName)
    # Use the imported datetime class correctly
    return datetime.fromtimestamp(t).strftime("%Y-%m-%d-%H:%M")

def list_files(basePath,validExts=None,contains=None):
    """
    USAGE: print(myutils.list_files("./"))
    List files in a directory with optional filters.
    Args:
        basePath: Base directory to search for files
        validExts: Optional tuple of valid file extensions
        contains: Optional string to filter file names
    Yields:
        File paths that match the filters
    """
    for rootDir, dirNames, fileNames in os.walk(basePath):
        for fileName in fileNames:
            if contains is not None and fileName.find(contains) == -1:
                continue
            # reverse find the "." from back wards
            ext = fileName[fileName.rfind("."):]
            if validExts is None or ext.endswith(validExts):
                file = os.path.realpath(os.path.join(rootDir,fileName))
                yield file


#### SECTION 04: Python program name:

def print_module_filenames() -> None:
    """
    USAGE: print_filename()
    """
    print_trace(f"At {sys._getframe().f_code.co_name}()")

    #import inspect
    current_frame = inspect.currentframe()
    filename = inspect.getfile(current_frame)
    print(f"inspect.getfile(currentframe()): {os.path.basename(filename)}")

    filename_no_ext = os.path.splitext(os.path.basename(__file__))[0]
    print(f"__file__ without extension:      {filename_no_ext}     created:  {ctimestamp(__file__)} " )

    #import sys
    current_module = sys.modules[__name__]
    print(f"Filename only:      {os.path.basename(__file__):>23}  modified: {mtimestamp(__file__)}")

    if hasattr(current_module, '__file__'):
        print(f"os.path.basename():              {os.path.basename(current_module.__file__)} ")
        print(f"current_module.__file__:    {current_module.__file__}")

    print(f"os.path.abspath(__file__):  {os.path.abspath(__file__)} ")


    return None



#### SECTION 05: Python environment variables:


# See https://bomonike.github.io/python-samples/#ParseArguments

def set_cli_parms(count):
    """Present menu and parameters to control program
    """
    # import click
    @click.command()
    @click.option('--count', default=1, help='Number of greetings.')
    #@click.option('--name', prompt='Your name',
    #              help='The person to greet.')
    def set_cli_parms(count):
        for x in range(count):
            click.echo("Hello!")
    # Test by running: ./python-examples.py --help


def open_env_file() -> bool:
    """Update global variables obtained from .env file based on key provided.
    """
    global global_env_path
    global user_home_dir_path
    global ENV_FILE
    if not global_env_path:
        # from pathlib import Path
        # See https://wilsonmar.github.io/python-samples#run_env
        if not user_home_dir_path:  # example: /users/john_doe
            user_home_dir_path = str(Path.home())
            if not ENV_FILE:
                ENV_FILE="python-samples.env"  # the hard-coded default
            global_env_path = user_home_dir_path + "/" + ENV_FILE  # concatenate path

    # PROTIP: Check if .env file on global_env_path is readable:
    if not os.path.isfile(global_env_path):
        print_error(global_env_path+" (global_env_path) not found!")
        return None
    else:
        path = pathlib.Path(global_env_path)
        # Based on: pip3 install python-dotenv
        # from dotenv import load_dotenv
        # See https://www.python-engineer.com/posts/dotenv-python/
        # See https://pypi.org/project/python-dotenv/
        load_dotenv(global_env_path)  # using load_dotenv
        # Wait until variables for print_trace are retrieved:
        print_info(f"open_env_file() to \"{global_env_path}\" ")

    return True

def get_str_from_env_file(key_in) -> str:
    """Return a value of string data type from OS environment or .env file
    (using pip python-dotenv)
    """
    # TODO: Default ENV_FILE name:
    ENV_FILE="python-samples.env"

    env_var = os.environ.get(key_in)
    if not env_var:  # yes, defined=True, use it:
        print_trace(f"get_str_from_env_file(\"{key_in}\") not found in .env file.")
        return None
    else:
        # PROTIP: Display only first characters of a potentially secret long string:
        if len(env_var) > 5:
            print_trace(key_in + "=\"" + str(env_var[:5]) +" (remainder removed)")
        else:
            print_trace(key_in + "=\"" + str(env_var) + "\" from .env")
        return str(env_var)


def print_env_vars():
    """List all environment variables, one line each using pretty print (pprint)
    """
    # import os
    # import pprint
    environ_vars = os.environ
    print_heading("User's Environment variable:")
    pprint.pprint(dict(environ_vars), width = 1)


#### SECTION 05: Time utility functions:


def test_datetime():
    """Test function to verify datetime functionality"""
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d-%H:%M")
    return formatted_time


def get_user_local_time() -> str:
    """ 
    Returns a string formatted with datetime stamp in local timezone.
    Example: "07:17 AM (07:17:54) 2025-04-21 MDT"
    """
    now: datetime = datetime.now()
    local_tz = datetime.now(timezone.utc).astimezone().tzinfo
    return f'{now:%I:%M %p (%H:%M:%S) %Y-%m-%d} {local_tz}'


#### SECTION 06: Logging utility functions:


def get_log_datetime() -> str:
    """
    Returns a formatted datetime string in UTC (GMT) timezone so all logs are aligned.
    Example: 2504210416UTC for a minimal with year, month, day, hour, minute, second and timezone code.
    """
    #from datetime import datetime
    # importing timezone from pytz module
    #from pytz import timezone

    # To get current time in (non-naive) UTC timezone
    # instead of: now_utc = datetime.now(timezone('UTC'))
    # Based on https://docs.python.org/3/library/datetime.html#datetime.datetime.utcnow
    fts = datetime.fromtimestamp(time.time(), tz=timezone.utc)
    time_str = fts.strftime("%y%m%d%H%M%Z")  # EX: "...-250419" UTC %H%M%Z https://strftime.org

    # See https://stackoverflow.com/questions/7588511/format-a-datetime-into-a-string-with-milliseconds
    # time_str=datetime.utcnow().strftime('%F %T.%f')
        # for ISO 8601-1:2019 like 2023-06-26 04:55:37.123456 https://www.iso.org/news/2017/02/Ref2164.html
    # time_str=now_utc.strftime(MY_DATE_FORMAT)

    # Alternative: Converting to Asia/Kolkata time zone using the .astimezone method:
    # now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
    # Format the above datetime using the strftime()
    # print('Current Time in Asia/Kolkata TimeZone:',now_asia.strftime(format))
    # if show_dates:  https://medium.com/tech-iiitg/zulu-module-in-python-8840f0447801

    return time_str


# TODO: OpTel (OpenTelemetry) spans and logging:

def export_optel():
    """ Create and export a trace to your console:
    https://www.perplexity.ai/search/python-code-to-use-opentelemet-bGjntbF4Sk6I6z3l5HBBSg#0
    """
    #from opentelemetry import trace
    #from opentelemetry.sdk.trace import TracerProvider
    #from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

    # Set up the tracer provider and exporter
    trace.set_tracer_provider(TracerProvider())
    span_processor = SimpleSpanProcessor(ConsoleSpanExporter())
    trace.get_tracer_provider().add_span_processor(span_processor)

    # Get a tracer:
    tracer = trace.get_tracer(__name__)

    # Create spans:
    with tracer.start_as_current_span("parent-span"):
        print_verbose("Doing some work in the parent span")
        with tracer.start_as_current_span("child-span"):
            print_verbose("Doing some work in the child span")


#### SECTION 07: Operating System properties


def mem_usage(tag):
    """
    USAGE: print(f"Memory used: {myutils.mem_usage("myutils.py")}")
    """
    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    denom = 1024
    if sys.platform == "darwin":
        denom = denom**2
    print(f'INFO: memory used is at {tag} : {round(mem/denom,2)} MB')

def beautify_json(file,outfile=None):
    """
    USAGE: myutils.beautify_json("myutils.py"))
    """
    js = json.loads(open(file).read())
    if outfile is None:
        outfile=file
    with open(outfile, 'w') as outfilep:
        json.dump(js,outfilep,sort_keys=True,indent=4)

def get_fuid(fileName):
    """ Returns user id (such as "johndoe")
    USAGE: print(f"FUID: {myutils.get_fuid("myutils.py")}")
    """
    return(pwd.getpwuid(os.stat(fileName).st_uid).pw_name)

def execsh(command):
    """
    USAGE: myutils.execsh("echo")
    """
    result = subprocess.run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    return result.stdout

def force_link(src,linkName):
    """
    USAGE: myutils.force_link(???)
    """
    try:
        os.symlink(src,linkName)
    except:
        if os.path.islink(linkName):
            os.remove(linkName)
            os.symlink(src,linkName)



#### SECTION 08. Environment information metadata:


def show_summary() -> bool:
    """Prints summary of timings together at end of run.
    """
    if not SHOW_SUMMARY_COUNTS:
        return None

    pgm_stop_mem_diff = get_process_memory() - float(pgm_strt_mem_used)
    print_info(f"{pgm_stop_mem_diff:.2f} MB memory consumed during run {RUNID}.")

    pgm_stop_disk_free, pct_disk_free_now = get_disk_free()
    pgm_stop_disk_diff = pgm_strt_disk_free - pgm_stop_disk_free
    print_info(f"{pgm_stop_disk_diff:.2f} GB disk space consumed during run {RUNID}. {pct_disk_free_now} remaining.")

    print_separator()
    print_heading("Monotonic wall timings (seconds):")
    # TODO: Write to log for longer-term analytics

    # For wall time of std imports:
    std_elapsed_wall_time = std_stop_timestamp -  std_strt_timestamp
    print_verbose("for import of Python standard libraries: "+ \
        f"{std_elapsed_wall_time:.4f}")

    # For wall time of xpt imports:
    xpt_elapsed_wall_time = xpt_stop_timestamp -  xpt_strt_timestamp
    print_verbose("for import of Python extra    libraries: "+ \
        f"{xpt_elapsed_wall_time:.4f}")

    pgm_stop_timestamp =  time.monotonic()
    pgm_elapsed_wall_time = pgm_stop_timestamp -  pgm_strt_timestamp
    # pgm_stop_perftimestamp = time.perf_counter()
    print_verbose("for whole program run:                   "+ \
        f"{pgm_elapsed_wall_time:.4f}")

    # TODO: Write wall times to log for longer-term analytics
    return True


# See https://bomonike.github.io/python-samples/#run_env

def os_platform():
    """Return a friendly name for the operating system
    """
    #import platform # https://docs.python.org/3/library/platform.html
    platform_system = str(platform.system())
       # 'Linux', 'Darwin', 'Java', 'Windows'
    print_trace("platform_system="+str(platform_system))
    if platform_system == "Darwin":
        my_platform = "macOS"
    elif platform_system == "linux" or platform_system == "linux2":
        my_platform = "Linux"
    elif platform_system == "win32":  # includes 64-bit
        my_platform = "Windows"
    else:
        print_fail("platform_system="+platform_system+" is unknown!")
        exit(1)  # entire program
    return my_platform

def macos_version_name(release_in):
    """Returns the marketing name of macOS versions which are not available
    from the running macOS operating system.
    """
    # NOTE: Return value is a list!
    # This has to be updated every year, so perhaps put this in an external library so updated
    # gets loaded during each run.
    # Apple has a way of forcing users to upgrade, so this is used as an
    # example of coding.
    # FIXME: https://github.com/nexB/scancode-plugins/blob/main/etc/scripts/homebrew.py
    # See https://support.apple.com/en-us/HT201260 and https://www.wikiwand.com/en/MacOS_version_history
    MACOS_VERSIONS = {
        '22.7': ['Next2024', 2024, '24'],
        '22.6': ['macOS Sonoma', 2023, '23'],
        '22.5': ['macOS Ventura', 2022, '13'],
        '12.1': ['macOS Monterey', 2021, '21'],
        '11.1': ['macOS Big Sur', 2020, '20'],
        '10.15': ['macOS Catalina', 2019, '19'],
        '10.14': ['macOS Mojave', 2018, '18'],
        '10.13': ['macOS High Sierra', 2017, '17'],
        '10.12': ['macOS Sierra', 2016, '16'],
        '10.11': ['OS X El Capitan', 2015, '15'],
        '10.10': ['OS X Yosemite', 2014, '14'],
        '10.9': ['OS X Mavericks', 2013, '10.9'],
        '10.8': ['OS X Mountain Lion', 2012, '10.8'],
        '10.7': ['OS X Lion', 2011, '10.7'],
        '10.6': ['Mac OS X Snow Leopard', 2008, '10.6'],
        '10.5': ['Mac OS X Leopard', 2007, '10.5'],
        '10.4': ['Mac OS X Tiger', 2005, '10.4'],
        '10.3': ['Mac OS X Panther', 2004, '10.3'],
        '10.2': ['Mac OS X Jaguar', 2003, '10.2'],
        '10.1': ['Mac OS X Puma', 2002, '10.1'],
        '10.0': ['Mac OS X Cheetah', 2001, '10.0'],
    }
    # WRONG: On macOS Monterey, platform.mac_ver()[0]) returns "10.16", which is Big Sur and thus wrong.
    # See https://eclecticlight.co/2020/08/13/macos-version-numbering-isnt-so-simple/
    # and https://stackoverflow.com/questions/65290242/pythons-platform-mac-ver-reports-incorrect-macos-version/65402241
    # and https://docs.python.org/3/library/platform.html
    # So that is not a reliable way, especialy for Big Sur
       # https://bandit.readthedocs.io/en/latest/blacklists/blacklist_imports.html#b404-import-subprocess
    # import subprocess  # built-in
    # from subprocess import PIPE, run
    # p = subprocess.Popen("sw_vers", stdout=subprocess.PIPE)
    # result = p.communicate()[0]
    macos_platform_release = platform.release()
    # Alternately:
    release = '.'.join(release_in.split(".")[:2])  # ['10', '15', '7']
    macos_info = MACOS_VERSIONS[release]  # lookup for ['Monterey', 2021]
    print_trace("macos_info="+str(macos_info))
    print_trace("macos_platform_release="+macos_platform_release)
    return macos_platform_release


def macos_sys_info():

    if not show_sys_info:   # defined among CLI arguments
        return None

    print_heading("macos_sys_info():")

        # or socket.gethostname()
    my_platform_node = platform.node()
    print_trace("my_platform_node = "+my_platform_node + " (machine name)")

    # print_trace("env_file = "+env_file)
    print_trace("user_home_dir_path = "+user_home_dir_path)
    # the . in .secrets tells Linux that it should be a hidden file.

    # import platform # https://docs.python.org/3/library/platform.html
    platform_system = platform.system()
       # 'Linux', 'Darwin', 'Java', 'Win32'
    print_trace("platform_system = "+str(platform_system))

    # my_os_platform=localize_blob("version")
    print_trace("my_os_version = "+str(platform.release()))
    #           " = "+str(macos_version_name(my_os_version)))

    my_os_process = str(os.getpid())
    print_trace("my_os_process = "+my_os_process)

    my_os_uname = str(os.uname())
    print_trace("my_os_uname = "+my_os_uname)
        # MacOS version=%s 10.14.6 # posix.uname_result(sysname='Darwin',
        # nodename='NYC-192850-C02Z70CMLVDT', release='18.7.0', version='Darwin
        # Kernel Version 18.7.0: Thu Jan 23 06:52:12 PST 2020;
        # root:xnu-4903.278.25~1/RELEASE_X86_64', machine='x86_64')

    # import pwd   #  https://zetcode.com/python/os-getuid/
    pwuid_shell = pwd.getpwuid(os.getuid()).pw_shell     # like "/bin/zsh" on MacOS
        # preferred over os.getuid())[0]

    # machine_uid_pw_name = psutil.Process().username()
    print_trace("pwuid_shell = "+pwuid_shell)

    # Obtain machine login name:
    # This handles situation when user is in su mode.
    # See https://docs.python.org/3/library/pwd.html
    pwuid_gid = pwd.getpwuid(os.getuid()).pw_gid         # Group number datatype
    print_trace("pwuid_gid = "+str(pwuid_gid)+" (process group ID number)")

    pwuid_uid = pwd.getpwuid(os.getuid()).pw_uid
    print_trace("pwuid_uid = "+str(pwuid_uid)+" (process user ID number)")

    pwuid_name = pwd.getpwuid(os.getuid()).pw_name
    print_trace("pwuid_name = "+pwuid_name)

    pwuid_dir = pwd.getpwuid(os.getuid()).pw_dir         # like "/Users/johndoe"
    print_trace("pwuid_dir = "+pwuid_dir)

    # Several ways to obtain:
    # See https://stackoverflow.com/questions/4152963/get-name-of-current-script-in-python
    # this_pgm_name = sys.argv[0]                     # = ./python-samples.py
    # this_pgm_name = os.path.basename(sys.argv[0])   # = python-samples.py
    # this_pgm_name = os.path.basename(__file__)      # = python-samples.py
    # this_pgm_path = os.path.realpath(sys.argv[0])   # = python-samples.py
    # Used by display_run_stats() at bottom:
    this_pgm_name = os.path.basename(os.path.normpath(sys.argv[0]))
    print_trace("this_pgm_name = "+this_pgm_name)

    #this_pgm_last_commit = __last_commit__
    #    # Adapted from https://www.python-course.eu/python3_formatted_output.php
    #print_trace("this_pgm_last_commit = "+this_pgm_last_commit)

    this_pgm_os_path = os.path.realpath(sys.argv[0])
    print_trace("this_pgm_os_path = "+this_pgm_os_path)
    # Example: this_pgm_os_path=/Users/wilsonmar/github-wilsonmar/python-samples/python-samples.py

    # import site
    site_packages_path = site.getsitepackages()[0]
    print_trace("site_packages_path = "+site_packages_path)

    this_pgm_last_modified_epoch = os.path.getmtime(this_pgm_os_path)
    print_trace("this_pgm_last_modified_epoch = "+str(this_pgm_last_modified_epoch))

    #this_pgm_last_modified_datetime = datetime.fromtimestamp(
    #    this_pgm_last_modified_epoch)
    #print_trace("this_pgm_last_modified_datetime=" +
    #            str(this_pgm_last_modified_datetime)+" (local time)")
        # Default like: 2021-11-20 07:59:44.412845  (with space between date & time)

    # Obtain to know whether to use new interpreter features:
    python_ver = platform.python_version()
        # 3.8.12, 3.9.16, etc.
    print_trace("python_ver = "+python_ver)

    # python_info():
    python_version = no_newlines(sys.version)
        # 3.9.16 (main, Dec  7 2022, 10:16:11) [Clang 14.0.0 (clang-1400.0.29.202)]
        # 3.8.3 (default, Jul 2 2020, 17:30:36) [MSC v.1916 64 bit (AMD64)]
    print_trace("python_version = "+python_version)

    print_trace("python_version_info = "+str(sys.version_info))
        # Same as on command line: python -c "print_trace(__import__('sys').version)"
        # 2.7.16 (default, Mar 25 2021, 03:11:28)
        # [GCC 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.29.20) (-macos10.15-objc-

    if sys.version_info.major == 3 and sys.version_info.minor <= 6:
            # major, minor, micro, release level, and serial: for sys.version_info.major, etc.
            # Version info sys.version_info(major=3, minor=7, micro=6,
            # releaselevel='final', serial=0)
        print_fail("Python 3.6 or higher is required for this program. Please upgrade.")
        sys.exit(1)

    # TODO: Make this function for call before & after run:
    #    disk_list = get_disk_free()
    #    disk_space_free = disk_list[1]:,.1f / disk_list[0]:,.1f
    #    print_info(localize_blob("Disk space free")+"="+disk_space_free+" GB")
        # left-to-right order of fields are re-arranged from the function's output.

    is_uv_venv_activated()  # both True:


def is_running_locally() -> bool:
    """
    Returns True if the program is running in a local development environment.
    Returns False if in production/remote environment (within a server/VM).
    """    
    # Method 1: Check for common local development indicators:
    local_indicators = [
        # Development environment variables
        os.getenv('DEVELOPMENT') == 'true',
        os.getenv('DEBUG') == 'true',
        os.getenv('ENV') == 'development',
        os.getenv('ENVIRONMENT') == 'local',
        
        # Common local hostnames/IPs:
        socket.gethostname().lower() in ['localhost', '127.0.0.1'],
        
        # Check if running on local IP ranges
        _is_local_ip(),
        
        # Development tools/paths present
        Path('.git').exists(),  # Git repository
        Path('requirements.txt').exists() or Path('pyproject.toml').exists(),
        
        # Interactive terminal (likely local development)
        sys.stdin.isatty() and sys.stdout.isatty(),
    ]
    
    return any(local_indicators)

def _is_local_ip():
    """Check if running on a local IP address."""
    try:
        # Get local IP by connecting to external address
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            
        # Check if IP is in private ranges
        ip_parts = local_ip.split('.')
        if len(ip_parts) == 4:
            first_octet = int(ip_parts[0])
            second_octet = int(ip_parts[1])
            
            # Private IP ranges: 10.x.x.x, 172.16-31.x.x, 192.168.x.x
            return (first_octet == 10 or 
                   (first_octet == 172 and 16 <= second_octet <= 31) or
                   (first_octet == 192 and second_octet == 168) or
                   local_ip == '127.0.0.1')
    except:
        return False

def get_environment_info():
    """Returns a dictionary of detailed information about the current environment.
    """
    return {
        'hostname': socket.gethostname(),
        'platform': sys.platform,
        'python_version': sys.version,
        'working_directory': os.getcwd(),
        'environment_vars': {
            'PATH': os.getenv('PATH', ''),
            'HOME': os.getenv('HOME', ''),
            'USER': os.getenv('USER', ''),
            'SHELL': os.getenv('SHELL', ''),
        },
        'is_interactive': sys.stdin.isatty(),
        'has_git': Path('.git').exists(),
        'local_ip': _get_local_ip(),
    }

def _get_local_ip():
    """Returns the local IP address such as 192.168.1.23. 
    By "connecting" to an external UDP address such as 8.8.8.8 (Google's DNS), 
    the operating system's routing table determines which 
    local network interface (and its associated IP address) 
    is used to reach the internet rather than localhost (127.0.0.1).
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception as e:
        print(f"{sys._getframe().f_code.co_name}(): {e}")
        return "Unknown"


# Alternative approach using specific environment checks:
def is_local_development():
    """
    Alternative method focusing on common deployment patterns.
    """
    # Check for containerized environments (usually not local)
    if os.path.exists('/.dockerenv') or os.getenv('KUBERNETES_SERVICE_HOST'):
        return False
    
    # Check for cloud platform environment variables
    cloud_indicators = [
        'HEROKU_APP_NAME',
        'AWS_EXECUTION_ENV',
        'GOOGLE_CLOUD_PROJECT',
        'AZURE_FUNCTIONS_ENVIRONMENT',
        'VERCEL',
        'NETLIFY',
    ]
    
    if any(os.getenv(var) for var in cloud_indicators):
        return False
    
    # If none of the above, likely local
    return True


def get_disk_free() -> (float, str):
    """
    Returns float GB of disk space free and text of percentage free.
    References global GB_BYTES.
    """
    GB_BYTES = 1073741824  # = 1024 * 1024 * 1024 = Terrabyte
    # import shutil
    # Replace '/' with your target path (e.g., 'C:\\' on Windows)
    usage = shutil.disk_usage('/')
    pct_free = ( float(usage.free) / float(usage.total) ) * 100
    disk_gb_free = float(usage.free) / GB_BYTES
    disk_pct_free = f"{pct_free:.2f}%"
    # print_verbose(f"get_disk_free(): {disk_gb_free:.2f} ({pct_free:.2f}%) disk free")
    return disk_gb_free, disk_pct_free


def get_process_memory() -> float:
    """
    Returns MiB of memory used by the current process.
    """
    # import os, psutil  #  psutil-5.9.5
    process = psutil.Process(os.getpid())
    # Divide by (1024 * 1024) to convert bytes to MB:
    mem=process.memory_info().rss / 1048576
    print_trace(f"{str(process)} MiB from get_process_memory()")
    return float(mem)

def get_all_objects_by_type():
    """Get memory usage by object type."""
    type_sizes = defaultdict(int)
    type_counts = defaultdict(int)
    
    # Force garbage collection to get more accurate results:
    # import gc
    gc.collect()
    
    # Get all objects tracked by the garbage collector
    for obj in gc.get_objects():
        try:
            obj_type = type(obj).__name__
            # import sys
            obj_size = sys.getsizeof(obj)
            type_sizes[obj_type] += obj_size
            type_counts[obj_type] += 1
        except:
            pass  # Skip objects that can't be processed
    
    return type_sizes, type_counts

def trace_memory_usage(func):
    """Decorator @trace_memory_usage to trace memory usage before and after 
    calling a function that uses a dubiously large amount of memory.
    """
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        start_memory = get_process_memory()
        print_verbose(f"{'Memory before:':<43} {start_memory:.2f} MB")
        
        result = func(*args, **kwargs)
        
        current, peak = tracemalloc.get_traced_memory()
        print_verbose(f"    {'tracemalloc current:':<43} {current / (1024 * 1024):.2f} MB")
        print_verbose(f"    {'tracemalloc peak:':<43} {peak / (1024 * 1024):.2f} MB")
        end_memory = get_process_memory()
        print_verbose(f"    {'Memory after:':<43} {end_memory:.2f} MB")
        print_verbose(f"    {'Memory used:':<43} {end_memory - start_memory:.2f} MB")
        
        # import tracemalloc
        tracemalloc.stop()
        return result
    
    return wrapper

def show_memory_profile():
    """Print detailed memory usage information.
    """
    GB_BYTES = 1073741824  # = 1024 * 1024 * 1024 = Terrabyte

    print_verbose("show_memory_profile():")

    system_memory = psutil.virtual_memory()
    print_verbose(f"psutil.virtual_memory(): {system_memory.percent}% "
        f"(Available: {system_memory.available / GB_BYTES:.2f} GB"
        f", System: {system_memory.total / GB_BYTES:.2f} GB)")

    print_verbose(f"{'    Total process memory: ':<43} {get_process_memory():.2f} MB")
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    print_verbose(f"{'    RSS (Resident Set Size):':<43} {memory_info.rss / (1024 * 1024):.2f} MB")
    print_verbose(f"{'    VMS (Virtual Memory Size):':<43} {memory_info.vms / (1024 * 1024):.2f} MB")
    
    # Get memory usage by type
    type_sizes, type_counts = get_all_objects_by_type()
    
    # Show top 10 memory consumers by type
    print_verbose("Top 10 memory consumers by type:")
    top_types = sorted(type_sizes.items(), key=lambda x: x[1], reverse=True)[:10]
    for obj_type, size in top_types:
        count = type_counts[obj_type]
        print_verbose(f"    {obj_type:<43} {size / (1024 * 1024):.2f} MB ({count} objects)")
    
    # Show other system information
    # print(f"\nPython version: {sys.version}")
    

def stats_to_file(filepath) -> bool:
    """
    Redirects system info stdout to a file using contextlib, 
    which is the cleanest and most pythonic way.
    """
    if not filepath:  # if filepath is empty
       filepath = f"{os.getcwd()}/stats_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    elif os.path.isfile(filepath):  # if file exists, so append:
        try:
            with open('append_output.txt', 'a') as f:
                original_stdout = sys.stdout
                sys.stdout = f
                
                macos_sys_info()  # appended to existing file.
                
                sys.stdout = original_stdout
        except Exception as e:
            print(f"{sys._getframe().f_code.co_name}(\"{filepath}\") append: {e}")
    else:  # not exist:
        try:
            # from contextlib import redirect_stdout
            with open(filepath, 'w') as f:
                with redirect_stdout(f):
                    macos_sys_info()
            # print("Back to console")
            return True
        except Exception as e:
            print(f"{sys._getframe().f_code.co_name}(\"{filepath}\") add: {e}")
    return False


#### SECTION 08: Python code utilities:


def handle_fatal_exit():
    """
    Handle fatal exit with a message first.
    """
    print_trace("handle_fatal_exit() called.")
    sys.exit(9)


def list_pgm_functions(filename):
    """
    USAGE: print(myutils.list_pgm_functions("myutils.py"))
    """
    #import importlib.util
    spec = importlib.util.spec_from_file_location("module", filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Get all functions:
    # import inspect
    functions = inspect.getmembers(module, inspect.isfunction)
    
    # Print function names:
    print(f"myutils.list_pgm_functions(\"{sys.argv[0]}\") alphabetically: ")
    for name, func in functions:
        print("    "+name)


def _extract_dunder_variables(filename: str) -> Dict[str, Any]:
    """
    USAGE: 
        dunder_items = myutils.extract_dunder_variables("myutils.py")
        for i, (key, value) in enumerate(dunder_items.items(), 1):
            print(f"{i}. {key}: {value}")
        for key, value in dunder.items():
            print(f"{key}: {value}")

    Extract dunder variables from a Python source file.
    Args:
        filename: Path to the Python source file
    Returns:
        Dictionary of dunder variable names and their values
    """
    #import ast
    #import sys
    #from typing import Dict, Any
    with open(filename, 'r', encoding='utf-8') as file:
        source = file.read()
    
    # Parse the source code into an AST:
    tree = ast.parse(source)
    
    dunder_vars = {}  # Dictionary to store dunder variables
    # Find all assignments at the module level
    for node in tree.body:
        # Look for assignment statements
        if isinstance(node, ast.Assign):
            for target in node.targets:
                # Check if the target is a name (variable)
                if isinstance(target, ast.Name):
                    var_name = target.id
                    # Check if it's a dunder (starts and ends with double underscores)
                    if var_name.startswith('__') and var_name.endswith('__'):
                        # Try to evaluate the value
                        try:
                            value = ast.literal_eval(node.value)
                            dunder_vars[var_name] = value
                        except (ValueError, SyntaxError):
                            # If we can't evaluate it, store it as a string representation
                            dunder_vars[var_name] = f"<non-literal value: {ast.dump(node.value)}>"
    return dunder_vars

def print_dunder_vars(filename) -> str:
    print_trace(f"At {sys._getframe().f_code.co_name}() within {filename}:")
    try:
        dunder_vars = _extract_dunder_variables(filename)
        if not dunder_vars:
            print(f"No dunder variables found in {filename}")
        else:
            for name, value in dunder_vars.items():
                print(f"{name} = {repr(value)}")
    
    except FileNotFoundError:
        print(f"{sys._getframe().f_code.co_name}() Error: File '{filename}' not found!")
        sys.exit(1)
    except SyntaxError as e:
        print(f"{sys._getframe().f_code.co_name}()Error: Invalid Python syntax in '{filename}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"{sys._getframe().f_code.co_name}() Error: {e}! ")
        sys.exit(1)


#### Strings of words


def reverse_words(input_str: str) -> str:
    """
    USAGE: print(myutils.reverse_words("The dog jumped"))
    Reverses words in a given string
    >>> sentence = "I love Python"
    >>> reverse_words(sentence) == " ".join(sentence.split()[::-1])
    True
    >>> reverse_words(sentence)
    'Python love I'
    """
    return " ".join(reversed(input_str.split(" ")))


#### Numeric utilities


def is_number(s) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def main():

    do_clear_cli()
    show_print_samples()
    print_module_filenames()
    get_environment_info()    
    #mem_usage("start")
    #for a in list_files("./",(".py"), ("__init__")):
    #    print(a)
    #    print(get_fuid(a))
    #my_file="myutils.py"

    print(f"is_running_locally()? {is_running_locally()} ")
    print(f"is_local_development()? {is_local_development()} ")
    #print(f"get_environment_info(): {get_environment_info()} ")

    list_pgm_functions(__file__)
    print_dunder_vars(__file__)  # __file__ = current module name (like "myutils.py")

    get_disk_free()
    get_process_memory()
    #trace_memory_usage(func)
    show_memory_profile()
    get_all_objects_by_type()

    reverse_words("A string of words")

if __name__ == "__main__":
    main()

