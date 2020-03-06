# Password Vault Server

The password vault server acts as cloud storage for a user, allowing them to back up their encrypted passwords on the cloud and update multiple devices.

## Running Locally

As the server is implemented as a Flask server, it can be run remotely. There are a few changes which need to be made to run locally, and these will run without a database.

1. Set `isTest=True` in the construction of `internal_server` within `applicaiton.py`
2. Run `pip install -r requirements.txt` to install all necessary files
3. Run `python application.py` to run the Flask server

To have a locally running vault use this, change all calls to `https:noodlespasswordvault.com` to `localhost:5000` within `application/bank.py`. Also notice that while this uses HTTP, the actual server does not as Flask sits behind a load balancer
