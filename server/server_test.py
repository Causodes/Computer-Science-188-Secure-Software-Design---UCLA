import requests
from base64 import *
import time

if __name__ == "__main__":
    salt_request = requests.post('http://127.0.0.1:5000/salt',
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
        'password': b64encode(validation),
        'encrypted_master': master_key,
        'recovery_key': recovery_key,
        'data1': b64encode(data1),
        'data2': b64encode(data2),
        'q1': q1,
        'q2': q2,
        'data_salt_11': dbs11,
        'data_salt_12': dbs12,
        'data_salt_21': dbs21,
        'data_salt_22': dbs22
    }
    register_response = requests.post(
        'http://127.0.0.1:5000/register',
        json=register_json,
        verify=True)
    print(register_response.json())
    if 'time' in register_response.json().keys():
        r_time = register_response.json()['time']
    else:
        r_time = 0

    salt_request = requests.post('http://127.0.0.1:5000/salt',
                                 json={'username': 'aldenperrine'},
                                 verify=True)
    print(salt_request.json())

    questions_response = requests.post(
        'http://127.0.0.1:5000/recovery_questions',
        json={'username': 'aldenperrine'},
        verify=True)
    print(questions_response.json())

    update_response = requests.post('http://127.0.0.1:5000/update',
                                    json={
                                        'username': 'aldenperrine',
                                        'password': b64encode(validation),
                                        'last_updated_time': 0,
                                        'updates': {'google' : ('pass', 1029239)}
                                    },
                                    verify=True)
    print(update_response.json())

    download_response = requests.post(
        'http://127.0.0.1:5000/download',
        json={
            'username': 'aldenperrine',
            'password': b64encode(validation)
        },
        verify=True)
    print(download_response.json())

    check_response = requests.post('http://127.0.0.1:5000/check',
                                   json={
                                       'username': 'aldenperrine',
                                       'password': b64encode(validation),
                                       'last_update_time': r_time
                                   },
                                   verify=True)
    print(check_response.json())

    new_pass = b'Thisissomenewpassword'
    new_salt_1 = 'somenewsalt'
    new_salt_2 = 'devenissaltyaf'
    new_master = "Devenisalwayssaltydealwithit"
    pass_change_response = requests.post('http://127.0.0.1:5000/password_change',
                                         json={
                                             'username': 'aldenperrine',
                                             'password': b64encode(validation),
                                             'new_password': b64encode(new_pass),
                                             'new_salt_1': new_salt_1,
                                             "new_salt_2": new_salt_2,
                                             'new_master': new_master,
                                             'last_updated_time': r_time
                                         },
                                         verify=True)
    print(pass_change_response.json())


    recovery_response = requests.post('http://127.0.0.1:5000/recover',
                                    json={
                                        'username': 'aldenperrine',
                                        'r1': b64encode(data1),
                                        'r2': b64encode(data2)
                                    },
                                    verify=True)

    print(recovery_response.json())

    recover_change = requests.post('http://127.0.0.1:5000/recovery_change',
                                    json={
                                        'username': 'aldenperrine',
                                        'recovery_1': b64encode(data1),
                                        'recovery_2': b64encode(data2),
                                        'new_password': b64encode(validation),
                                        'new_salt_1': salt,
                                        'new_salt_2': salt2,
                                        'new_master': master_key
                                    },
                                    verify=True)

    print(recover_change.json())

    delete_response = requests.post('http://127.0.0.1:5000/delete',
                                    json={
                                        'username': 'aldenperrine',
                                        'password': b64encode(new_pass),
                                        'r1': b64encode(data1),
                                        'r2': b64encode(data2)
                                    },
                                    verify=True)
    print(delete_response.json())
