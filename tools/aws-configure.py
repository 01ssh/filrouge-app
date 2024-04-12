#!/usr/bin/python3

import hvac
import os
import getopt,sys

from hvac.api.vault_api_base import VaultApiBase

rootnamespace="admin"

def get_aws_credentials(addr:str, token:str, secret_path:str, envstream:str):
    if addr is not None and token is not None:
       hvac_secrets_data = None
       vault_client = hvac.Client(addr, token, namespace=rootnamespace+"/"+envstream)
       vault_client.is_authenticated()
       hvac_secrets_data = vault_client.secrets.kv.v2.read_secret_version(secret_path)
       return (hvac_secrets_data["data"]["data"])
       
def aws_configure(path, creds, region, envstream, prefix):
    account = prefix + "_admin_" + envstream
    aws_account_access_key = "AWS_ACCESS_KEY_" + account + ""
    aws_account_secret_key = "AWS_SECRET_KEY_" + account + ""
    
    with open(path+"/config", 'w') as awsconfigfile:
         configoutput = '''[default]
region = {region}
output = json
'''.format(region=region)
         awsconfigfile.write(configoutput)
         
    with open(path+"/credentials", 'w') as awscredentialsfile:
         awscredsoutput = '''[default]
aws_access_key_id = {access_key_id}
aws_secret_access_key = {aws_secret_access_key}
'''.format(access_key_id=creds[0][aws_account_access_key],
           aws_secret_access_key=creds[0][aws_account_secret_key])
         awscredentialsfile.write(awscredsoutput)
         
    with open(os.getenv("HOME")+"/.bashrc", 'a') as awsbashfile:
         account = prefix + "_admin_" + envstream
         awsenvsoutput = '''
export AWS_ACCESS_KEY_ID={access_key_id}
export AWS_SECRET_ACCESS_KEY="{aws_secret_access_key}"
export AWS_DB_AURORA_USER={db_aurora_user}
export AWS_DB_AURORA_NAME={db_aurora_name}
export AWS_DB_AURORA_PASSWORD="{db_aurora_password}"
'''.format(access_key_id=creds[0][aws_account_access_key],
           aws_secret_access_key=creds[0][aws_account_secret_key],
           db_aurora_user=creds[1]["AWS_DB_AURORA_USER_" + account],
           db_aurora_name=creds[1]["AWS_DB_AURORA_NAME_" + account],
           db_aurora_password=creds[1]["AWS_DB_AURORA_PASSWORD_" + account])
         awsbashfile.write(awsenvsoutput)

def main():
    options = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:p:r:e:v:u:", ["help", "output="])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
    for o, a in opts:
        if o == "-a":
            options['VAULT_ADDR']  = a
        elif o in ("-p", "--path"):
            options['VAULT_PATH']  = a
        elif o in ("-v", "--token"):
            options['VAULT_TOKEN'] = a
        elif o in ("-r", "--region"):
            options['AWS_REGION']  = a
        elif o in ("-e", "--env"):
            options['AWS_ENVIRONNMENT']= a
        elif o in ("-u", "--profile"):
            options['PROFILE']= a
        else:
            assert False, "unhandled option"

    os.mkdir(os.getenv("HOME")+"/.aws")
    aws_configure(os.getenv("HOME")+"/.aws",
            [get_aws_credentials(options['VAULT_ADDR'],
                                options['VAULT_TOKEN'],
                                options['VAULT_PATH'],
                                options['AWS_ENVIRONNMENT']),
             get_aws_credentials(options['VAULT_ADDR'], 
                                options['VAULT_TOKEN'], 
                                options['VAULT_PATH'] + "_db", 
                                options['AWS_ENVIRONNMENT'])],
                                options['AWS_REGION'],
                                options['AWS_ENVIRONNMENT'],
                                options['PROFILE'])
if __name__ == "__main__":
   main()