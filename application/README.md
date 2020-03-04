# Password Vault Application

The password vault application is the main entrypoint for users into the system, as it handles the encryption of their passwords, communication with the server and the Chrome extension, and logging in the user.

## Installation Instructions

Installing the application mainly involves setting up the environement for the application to be run in. This consists of two parts; compiling the C code into a shared library, and setting up the environment that Python will run in.

### Building the C Library

The C library consists of two C files, vault_map.c and vault.c, that are compiled together to implement the functionality of the lower level vault. 

- vault_map.c is a hash table from key strings to meta information about they keys.
- vault.c handles the file I/O for a vault and maintaining meta information about the vault itself.

The following instructions should specify the necessary steps to build the C library.

1. Install libsodium from [here](https://libsodium.gitbook.io/doc/installation), following the instructions on the page. This will allow the -lsodium flag that links in libsodium to the shared library.
2. Run `make` from the application directory (this directory). This will allow the Makefile to run, which will compile vault_map.c and vault.c into *.o files, and then combine them into a .so file.
3. To test, running `python3 vault.py` should not throw any exceptions. This will run a smoke test that ensures that the shared library can be loaded by python, and that the functions can be called without issue.

### Running the Python Application

The Python application can be run with the following steps, with step 0 optional. All of these commands should be run from the *base* directory, **NOT** the *application* directory. If not, there may be issues such as "Module application.utils not found". Also note that the application runs on **PYTHON 3**.

0. Setup a python virtual envrionement with virtualenv, which can be installed with `pip install virtualenv`. Running `virtualenv -p python3 .` from the **base** directory will set up a virtualenv, which can then be started with `source ./bin/activate`.
1. Run `pip install -r application/requirements.txt`. This will install all the python libraries required to run the application.
2. Run `python application/ui.py` to start the application without connection to the Chrome Extension. Note that internet connection is required to communicate with the server.
