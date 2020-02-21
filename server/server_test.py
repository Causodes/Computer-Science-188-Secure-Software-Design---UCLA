import requests
from base64 import *
import time

if __name__ == "__main__":
    salt_request = requests.post('https://noodlespasswordvault.com/salt',
                                 json={'username': 'aldenperrine'},
                                 verify=True)
    print(salt_request.json())
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
    register_json = {
        "username": username,
        'pass_salt_1': salt,
        'pass_salt_2': salt2,
        'password': b64encode(validation).decode('ascii'),
        'encrypted_master': master_key,
        'recovery_key': recovery_key,
        'data1': b64encode(data1).decode('ascii'),
        'data2': b64encode(data2).decode('ascii'),
        'q1': q1,
        'q2': q2,
        'data_salt_11': dbs11,
        'data_salt_12': dbs12,
        'data_salt_21': dbs21,
        'data_salt_22': dbs22
    }
    register_response = requests.post(
        'https://noodlespasswordvault.com/register',
        json=register_json,
        verify=True)
    print(register_response.json())
    if 'time' in register_response.json().keys():
        r_time = register_response.json()['time']
    else:
        r_time = 0

    salt_request = requests.post('https://noodlespasswordvault.com/salt',
                                 json={'username': 'aldenperrine'},
                                 verify=True)
    print(salt_request.json())

    questions_response = requests.post(
        'https://noodlespasswordvault.com/recovery_questions',
        json={'username': 'aldenperrine'},
        verify=True)
    print(questions_response.json())

    update_response = requests.post('https://noodlespasswordvault.com/update',
                                    json={
                                        'username': 'aldenperrine',
                                        'password': b64encode(validation).decode('ascii'),
                                        'last_updated_time': 0,
                                        'updates': [('google', 'pass')]
                                    },
                                    verify=True)
    print(update_response.json())

    download_response = requests.post(
        'https://noodlespasswordvault.com/download',
        json={
            'username': 'aldenperrine',
            'password': b64encode(validation).decode('ascii')
        },
        verify=True)
    print(download_response.json())

    check_response = requests.post('https://noodlespasswordvault.com/check',
                                   json={
                                       'username': 'aldenperrine',
                                       'password': b64encode(validation).decode('ascii'),
                                       'last_update_time': r_time
                                   },
                                   verify=True)
    print(f'check {check_response.json()}')

    new_pass = b'Thisissomenewpassword'
    new_salt_1 = 'somenewsalt'
    new_salt_2 = 'devenissaltyaf'
    new_master = "Devenisalwayssaltydealwithit"
    pass_change_response = requests.post('https://noodlespasswordvault.com/password_change',
                                         json={
                                             'username': 'aldenperrine',
                                             'password': b64encode(validation).decode('ascii'),
                                             'new_password': b64encode(new_pass).decode('ascii'),
                                             'new_salt_1': new_salt_1,
                                             "new_salt_2": new_salt_2,
                                             'new_master': new_master,
                                             'last_updated_time': r_time
                                         },
                                         verify=True)
    print(pass_change_response.json())


    recovery_response = requests.post('https://noodlespasswordvault.com/recover',
                                    json={
                                        'username': 'aldenperrine',
                                        'r1': b64encode(data1).decode('ascii'),
                                        'r2': b64encode(data2).decode('ascii')
                                    },
                                    verify=True)

    print(recovery_response.json())

    recover_change = requests.post('https://noodlespasswordvault.com/recovery_change',
                                    json={
                                        'username': 'aldenperrine',
                                        'recovery_1': b64encode(data1).decode('ascii'),
                                        'recovery_2': b64encode(data2).decode('ascii'),
                                        'new_password': b64encode(validation).decode('ascii'),
                                        'new_salt_1': salt,
                                        'new_salt_2': salt2,
                                        'new_master': master_key
                                    },
                                    verify=True)

    print(recover_change.json())

    delete_response = requests.post('https://noodlespasswordvault.com/delete',
                                    json={
                                        'username': 'aldenperrine',
                                        'password': b64encode(new_pass).decode('ascii'),
                                        'r1': b64encode(data1).decode('ascii'),
                                        'r2': b64encode(data2).decode('ascii')
                                    },
                                    verify=True)
    print(delete_response.json())
