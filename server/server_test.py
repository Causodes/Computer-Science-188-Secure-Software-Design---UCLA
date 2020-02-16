import requests
from base64 import *

if __name__ == "__main__":
    salt_request = requests.post('https://noodlespasswordvault.com/salt', json={'username' : 'aldenperrine'}, verify=True)
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
    register_json = {"username" : username,
                     'pass_salt_1' : salt,
                     'pass_salt_2' : salt2,
                     'password' : b64encode(validation),
                     'encrypted_master' : master_key,
                     'recovery_key' : recovery_key,
                     'data1' : b64encode(data1),
                     'data2' : b64encode(data2),
                     'q1' : q1,
                     'q2' : q2,
                     'data_salt_11' : dbs11,
                     'data_salt_12' : dbs12,
                     'data_salt_21' : dbs21,
                     'data_salt_22' : dbs22}
    register_response = requests.post('https://noodlespasswordvault.com/register', json=register_json, verify=True)
    print(register_response.json())

    salt_request = requests.post('https://noodlespasswordvault.com/salt', json={'username' : 'aldenperrine'}, verify=True)
    print(salt_request.json())

    questions_response = requests.post('https://noodlespasswordvault.com/recovery_questions', json={'username' : 'aldenperrine'}, verify=True)
    print(questions_response.json())

    download_response = requests.post('https://noodlespasswordvault.com/download', json={'username' : 'aldenperrine', 'password' : b64encode(validation)}, verify=True)
    print(download_response.json())
