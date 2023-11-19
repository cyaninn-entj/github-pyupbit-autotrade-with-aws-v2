import boto3

def get_parameter_fromSSM():
    ssm = boto3.client('ssm')

    parameters=['/ethauto/upbit-key/access-key',
                '/ethauto/upbit-key/secret-key',
                '/ethauto/slack-token']
    ssm_para = list()

    for i in parameters:
        response = ssm.get_parameter(
            Name=i,
            WithDecryption=True
        )
        ssm_para.append(response['Parameter']['Value'])

    return ssm_para[0], ssm_para[1], ssm_para[2]

try:
    a,b,c=get_parameter_fromSSM()
    print(a,b,c)
except Exception as e:
    print("Exception: {str(e)}")