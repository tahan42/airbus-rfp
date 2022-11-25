# Airbus RFP demo


## Get up and running

 - Create a python virtual env
 - activate the virtual env
 - install dependencies
 ```sh
    pip install -r requirements.txt
 ```
 - run ingester server encrypted with self-signed certificates
 ```sh
    flask --app src run --cert='adhoc'
 ```