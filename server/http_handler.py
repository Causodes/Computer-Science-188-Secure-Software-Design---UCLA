from flask import Flask, request, jsonify, abort
import sys
import os

app = Flask(__name__)

def throw_if_invalid_request(request, expected_fields):
    if (request.is_json is not True):
        raise ValueError('Request not json format')
    content = request.get_json()
    for field in expected_fields:
        if not field in content:
            raise ValueError('Field '+str(field)+' expected but not found')

# Register implementation
# Register a new user into the database, given a username and password
# As it is a TLS connection that protects information coming into AWS,
# OK to send the derived password as well as encrypted master key
@app.route('/register', methods=['POST'])
def register():
    throw_if_invalid_request(request, ['username', 'password', 'encrypted_master'])
    raise NotImplementedError

# Check implementation
# Validate login info passed along, and if valid then send back any new items
# Client will send username, password, and last updated time.
# Return value is a JSON with any updated information
# OK to send over the TLS connection
@app.route('/check', methods=['POST'])
def check():
    throw_if_invalid_request(request, ['username', 'password', 'last_update_time'])
    raise NotImplementedError

# Download implementation
# Validate login info passed along, and if valid then send back entire vault
# Client will send username and password.
# Return value is a JSON that contains vault information
# OK to send over the TLS connection
@app.route('/download', methods=['POST'])
def download():
    throw_if_invalid_request(request, ['username', 'password'])
    raise NotImplementedError

# Update implementation
# Validate login info passed along, and if valid then update cloud copy
# Client will send username and password along with updates.
# Return value is a JSON that contains vault information
# OK to send over the TLS connection
@app.route('/update', methods=['POST'])
def update():
    throw_if_invalid_request(request, ['username', 'password', 'updates'])
    raise NotImplementedError

# Password Change implementation
# Validate current login info, and if valid update master and vault
# As the server cannot do any of the decoding, entire vault sent across
# Return if able to update the cloud
# OK to send over the TLS connection
@app.route('/password_change', methods=['POST'])
def password_change():
    throw_if_invalid_request(request, ['username', 'password', 'encrypted_master', 'vault'])
    raise NotImplementedError


