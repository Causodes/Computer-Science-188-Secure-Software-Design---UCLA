from flask import Flask, request, jsonify, abort
import sys
import os
import server
from base64 import *

app = Flask(__name__)
internal_server = server.Server(istest=True)

def check_if_valid_request(request, expected_fields):
    if (request.is_json is not True):
        raise ValueError('Request not json format')
    content = request.get_json()
    for field in expected_fields:
        if not field in content:
            return False
    return True

def error(code, error_info):
    response = jsonify({'status': code, 'error': error_info})
    response.status_code = code
    return response


@app.route('/', methods=['GET'])
def root_test():
    return "Hello, World!"

# Register implementation
# Register a new user into the database, given a username and password
# As it is a TLS connection that protects information coming into AWS,
# OK to send the derived password as well as encrypted master key
@app.route('/register', methods=['POST'])
def register():
    check_if_valid_request(request, ['username',
                                       'password',
                                       'encrypted_master',
                                       'recovery_key',
                                       'q1',
                                       'q2',
                                       'data1',
                                       'data2'])
    raise NotImplementedError

# Check implementation
# Validate login info passed along, and if valid then send back any new items
# Client will send username, password, and last updated time.
# Return value is a JSON with any updated information
# OK to send over the TLS connection
@app.route('/check', methods=['POST'])
def check():
    check_if_valid_request(request, ['username', 'password', 'last_update_time'])

    # Check user password

    # If failed, update next available time

    # Check last updated time of vault info

    # If the last_checked_time is before last_update_time, return

    # Get modified times, return encrypted blobs that have been updated
    raise NotImplementedError

@app.route('/salt', methods=['POST'])
def salt():
    if not check_if_valid_request(request, ['username']):
        return error(400, 'Incorrect fields given')
    content = request.get_json()
    server_resp = internal_server.get_salt(content['username'])
    if server_resp is None:
        return error(400, "No user")
    return jsonify({'status':200, 'salt': b64encode(server_resp)})


# Recovery Questions implementation
# Returns the recovery questions associated with a user
# OK to send over the TLS connection
@app.route('/recovery_questions', methods=['POST'])
def recovery_questions():
    if not check_if_valid_request(request, ['username']):
        return error(400, "Incorrect fields given")
    content = request.get_json()
    server_resp = internal_server.get_salt(content['username'])
    if server_resp is None:
        return error(400, "No user")
    return jsonify({'status':200,
                    'q1': server_resp[0],
                    'q2': server_resp[1],
                    'data_salt_11': b64encode(server_resp[2]),
                    'data_salt_12': b64encode(server_resp[3]),
                    'data_salt_21': b64encode(server_resp[4]),
                    'data_salt_22': b64encode(server_resp[5]),})


# Download implementation
# Validate login info passed along, and if valid then send back entire vault
# Client will send username and password.
# Return value is a JSON that contains vault information
# OK to send over the TLS connection
@app.route('/download', methods=['POST'])
def download():
    check_if_valid_request(request, ['username', 'password'])
    # Check user password

    # If failed, update next available time

    # If succeed, return header+encrypted blobs

    raise NotImplementedError

# Update implementation
# Validate login info passed along, and if valid then update cloud copy
# Client will send username and password along with updates.
# Return value is a JSON that contains vault information
# OK to send over the TLS connection
@app.route('/update', methods=['POST'])
def update():
    check_if_valid_request(request, ['username', 'password', 'last_updated_time', 'updates'])

    raise NotImplementedError

# Password Change implementation
# Validate current login info, and if valid update master and vault
# As the server cannot do any of the decoding, entire vault sent across
# Return if able to update the cloud
# OK to send over the TLS connection
@app.route('/password_change', methods=['POST'])
def password_change():
    check_if_valid_request(request, ['username', 'password', 'encrypted_master', 'last_updated_time'])
    # Check user password

    # Update header, each different device must update themselves

    raise NotImplementedError


if __name__ == '__main__':
    username = "aldenperrine"
    salt = b'thisissome128bitnumberthatsasalt'
    validation = b'anotherlongderivedkeythatshouldbe256bits'
    master_key = b'somelongencrypted256bitkeywitha192bitnonceand128bitmac'
    recovery_key = b'oneanotherencyrptionbutthistimewithtwoderiveedkeys'
    data1 = b'passwordhashtwiceofsomeanswertoahardquestion'
    data2 = b'anotherpasswordhashofadifferentquestionjustobesure'
    q1 = "Some string question"
    q2 = "Another string question"
    dbs11 = b'anothersalt'
    dbs12 = b'moreslats'
    dbs21 = b'sosaltynow'
    dbs22 = b'saltysalt'

    create_time = internal_server.register_user(username, validation, salt, master_key, recovery_key,
                                                q1, q2, data1, data2, dbs11, dbs12, dbs21, dbs22)


    app.run(host='0.0.0.0', port=5000)
