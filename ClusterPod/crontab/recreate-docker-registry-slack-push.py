import slack_sdk
import boto3

def get_parameter_fromSSM() :
    ssm = boto3.client('ssm')

    parameters=['/ethauto/slack-token']
    ssm_para=list()

    for i in parameters:
        response = ssm.get_parameter(
            Name=i,
            WithDecryption=True
        )
        ssm_para.append(response['Parameter']['Value'])
    
    return ssm_para[0]



my_token=get_parameter_fromSSM()
client=slack_sdk.WebClient(token=my_token)

# readline_all.py
f = open("/home/ubuntu/docker-reg-cred/output.log", 'r')
while True:
    line = f.readline()
    if not line: break
    client.chat_postMessage(channel='#ethauto-step',
                        text=line)
f.close()