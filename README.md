# Project Noodles Password Vault

This is the main repository for the password vault, written by the Noodles team in CS 188 Winter '20.

## Structure

The repository is broken down into three main components:
1. A directory containing python code for the HTTP server that sits behind an HSTS Elastic Beanstalk setup, along with its database access.
2. A directory containing the python and c code for the client application.
3. A directory containing the javascript code for the Chrome extension.
    
Each repository contains instructions for running those specific components. The application and extension will connect to the running server, and the Flask server can be run on a localhost for testing without HTTPS.
