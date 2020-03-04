from flask import Flask, request, jsonify, abort
import sys
import os
import server
from base64 import *

application = Flask(__name__)
internal_server = server.Server()


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


@application.route('/', methods=['GET'])
def root_test():
    return "I'm a teapot\n"


@application.route('/time', methods=['GET', 'POST'])
def get_time():
    return jsonify({'status': 200, 'time': internal_server.time()})


# Register implementation
# Register a new user into the database, given a username and password
# As it is a TLS connection that protects information coming into AWS,
# OK to send the derived password as well as encrypted master key
# Master key, recovery key, data1 and 2, password, and salts should all be in b64
@application.route('/register', methods=['POST'])
def register():
    if not check_if_valid_request(request, [
            'username', 'password', 'pass_salt_1', 'pass_salt_2',
            'encrypted_master', 'recovery_key', 'q1', 'q2', 'data1', 'data2',
            'data_salt_11', 'data_salt_12', 'data_salt_21', 'data_salt_22'
    ]):
        return error(400, 'Incorrect fields given')
    content = request.get_json()
    server_resp = internal_server.register_user(
        content['username'], b64decode(content['password']),
        content['pass_salt_1'], content['pass_salt_2'],
        content['encrypted_master'], content['recovery_key'],
        content['q1'], content['q2'], b64decode(content['data1']),
        b64decode(content['data2']), content['data_salt_11'],
        content['data_salt_12'], content['data_salt_21'],
        content['data_salt_22'])
    if server_resp is None:
        return error(400, 'User already exists')
    if server_resp < 10:
        return error(500, "Internal server error")
    return jsonify({'status': 200, 'time': server_resp})


# Check implementation
# Validate login info passed along, and if valid then send back any new items
# Client will send username, password, and last updated time.
# Return value is a JSON with any updated information
# OK to send over the TLS connection
@application.route('/check', methods=['POST'])
def check():
    if not check_if_valid_request(request,
                                  ['username', 'password', 'last_update_time']):
        return error(400, "Incorrect fields given")
    content = request.get_json()
    server_resp = internal_server.check_for_updates(
        content['username'], b64decode(content['password']),
        content['last_update_time'])
    if server_resp is None:
        return error(400, 'User does not exist')
    c_time = server_resp[0]
    updates = server_resp[1]
    if c_time == 0:
        return error(400, 'Last failed login too soon')
    if c_time == 1:
        return error(400, 'Wrong password given')
    if c_time == 2:
        return error(500, 'Internal server error')
    return jsonify({'status': 200, 'updates': updates, 'time': c_time})


@application.route('/salt', methods=['POST'])
def salt():
    if not check_if_valid_request(request, ['username']):
        return error(400, 'Incorrect fields given')
    content = request.get_json()
    server_resp = internal_server.get_salt(content['username'])
    if server_resp is None:
        return error(400, "No user")
    pass_salt_1, pass_salt_2 = server_resp
    return jsonify({
        'status': 200,
        'pass_salt_1': pass_salt_1,
        'pass_salt_2': pass_salt_2
    })


# Recovery Questions implementation
# Returns the recovery questions associated with a user
# OK to send over the TLS connection
@application.route('/recovery_questions', methods=['POST'])
def recovery_questions():
    if not check_if_valid_request(request, ['username']):
        return error(400, "Incorrect fields given")
    content = request.get_json()
    server_resp = internal_server.recovery_questions(content['username'])
    if server_resp is None:
        return error(400, "No user")
    return jsonify({
        'status': 200,
        'q1': server_resp[0],
        'q2': server_resp[1],
        'data_salt_11': server_resp[2],
        'data_salt_12': server_resp[3],
        'data_salt_21': server_resp[4],
        'data_salt_22': server_resp[5],
    })


# Download implementation
# Validate login info passed along, and if valid then send back entire vault
# Client will send username and password.
# Return value is a JSON that contains vault information
# OK to send over the TLS connection
@application.route('/download', methods=['POST'])
def download():
    if not check_if_valid_request(request, ['username', 'password']):
        return error(400, "Incorrect fields given")
    content = request.get_json()
    server_resp = internal_server.download_vault(content['username'],
                                                 b64decode(content['password']))
    if server_resp is None:
        return error(400, "No user")
    c_time, header, keys = server_resp
    if c_time == 0:
        return error(400, 'Last failed login too recent')
    if c_time == 1:
        return error(400, 'Wrong password given')
    if c_time == 2:
        return error(500, 'Internal server error')
    return jsonify({
        'status': 200,
        'header': header,
        'pairs': keys,
        'time': c_time
    })


# Update implementation
# Validate login info passed along, and if valid then update cloud copy
# Client will send username and password along with updates.
# Return value is a JSON that contains vault information
# OK to send over the TLS connection
@application.route('/update', methods=['POST'])
def update():
    if not check_if_valid_request(request, ['username', 'password', 'updates']):
        return error(400, "Incorrect fields given")
    content = request.get_json()
    server_resp = internal_server.update_server(content['username'],
                                                b64decode(content['password']),
                                                content['updates'])
    if server_resp is None:
        return error(400, "No user")
    c_time = server_resp
    if c_time == 0:
        return error(400, 'Last failed login too recent')
    if c_time == 1:
        return error(400, 'Wrong password given')
    if c_time == 2:
        return error(500, 'Internal server error')
    return jsonify({'status': 200, 'time': c_time})


# Password Change implementation
# Validate current login info, and if valid update master and vault
# As the server cannot do any of the decoding, entire vault sent across
# Return if able to update the cloud
# OK to send over the TLS connection
@application.route('/password_change', methods=['POST'])
def password_change():
    if not check_if_valid_request(request, [
            'username', 'password', 'new_password', 'new_salt_1', 'new_salt_2',
            'new_master', 'last_updated_time'
    ]):
        return error(400, "Incorrect fields given")
    content = request.get_json()
    server_resp = internal_server.password_change_pass(
        content['username'], b64decode(content['password']),
        b64decode(content['new_password']), content['new_salt_1'],
        content['new_salt_2'], content['new_master'])
    if server_resp is None:
        return error(400, "No user")
    c_time = server_resp
    if c_time == 0:
        return error(400, 'Last failed login too recent')
    if c_time == 1:
        return error(400, 'Wrong responses given')
    if c_time == 2:
        return error(500, 'Internal server error')
    return jsonify({'status': 200, 'time': c_time})


@application.route('/recovery_change', methods=['POST'])
def recovery_change():
    if not check_if_valid_request(request, [
            'username', 'recovery_1', 'recovery_2', 'new_password',
            'new_salt_1', 'new_salt_2', 'new_master'
    ]):
        return error(400, "Incorrect fields given")
    content = request.get_json()
    server_resp = internal_server.password_change_recover(
        content['username'], b64decode(content['recovery_1']),
        b64decode(content['recovery_2']), b64decode(content['new_password']),
        content['new_salt_1'], content['new_salt_2'], content['new_master'])
    if server_resp is None:
        return error(400, "No user")
    c_time = server_resp
    if c_time == 0:
        return error(400, 'Last failed login too recent')
    if c_time == 1:
        return error(400, 'Wrong responses given')
    if c_time == 2:
        return error(500, 'Internal server error')
    return jsonify({'status': 200, 'time': c_time})


@application.route('/recover', methods=['POST'])
def get_recovery():
    if not check_if_valid_request(request, ['username', 'r1', 'r2']):
        return error(400, "Incorrect fields given")
    content = request.get_json()
    server_resp = internal_server.check_recovery(content['username'],
                                                 b64decode(content['r1']),
                                                 b64decode(content['r2']))
    if server_resp is None:
        return error(400, "No user")
    c_time, recovery_key = server_resp
    if c_time == 0:
        return error(400, 'Last failed login too recent')
    if c_time == 1:
        return error(400, 'Wrong responses given')
    if c_time == 2:
        return error(500, 'Internal server error')
    return jsonify({
        'status': 200,
        'time': c_time,
        'recovery_key': recovery_key
    })


@application.route('/delete', methods=['POST'])
def delete_user():
    if not check_if_valid_request(request,
                                  ['username', 'password', 'r1', 'r2']):
        return error(400, "Incorrect fields given")

    content = request.get_json()
    server_resp = internal_server.delete_user(content['username'],
                                              b64decode(content['password']),
                                              b64decode(content['r1']),
                                              b64decode(content['r2']))
    if server_resp is None:
        return error(400, "No user")
    c_time = server_resp
    if c_time == 0:
        return error(400, 'Last failed login too recent')
    if c_time == 1:
        return error(400, 'Wrong responses given')
    if c_time == 2:
        return error(500, 'Internal server error')
    return jsonify({'status': 200, 'time': c_time, 'message': 'Goodbye'})


if __name__ == '__main__':
    username = "aldenperrine"
    salt = 'thisissome128bitnumberthatsasalt'
    salt2 = 'another128bitnumbertoactassalt'
    validation = b'anotherlongderivedkeythatshouldbe256bits'
    master_key = 'somelongencrypted256bitkeywitha192bitnonceand128bitmac'
    recovery_key = 'oneanotherencyrptionbutthistimewithtwoderiveedkeys'
    data1 = b'passwordhashtwiceofsomeanswertoahardquestion'
    data2 = b'anotherpasswordhashofadifferentquestionjustobesure'
    q1 = "Some string question"
    q2 = "Another string question"
    dbs11 = 'anothersalt'
    dbs12 = 'moreslats'
    dbs21 = 'sosaltynow'
    dbs22 = 'saltysalt'

    create_time = internal_server.register_user(username, validation, salt,
                                                salt2, master_key, recovery_key,
                                                q1, q2, data1, data2, dbs11,
                                                dbs12, dbs21, dbs22)

    application.run(host='0.0.0.0', port=5000)
