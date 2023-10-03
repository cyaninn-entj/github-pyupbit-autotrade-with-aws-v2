import pyupbit
import numpy as np
import boto3
import slack_sdk

'''
def get_ror(k):
    df = pyupbit.get_ohlcv("KRW-ETH", count=14)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'],
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror'''
    
def get_ror(k):
    try:
        df = pyupbit.get_ohlcv("KRW-ETH", count=14)
        #print(df)
    except Exception as e:
        print("Exception1 : ", e)
        
    try:
        df['range'] = (df['high'] - df['low']) * k
        #print(df)
    except Exception as e:
        print("Exception2 : ", e)
        
    try:
        df['target'] = df['open'] + df['range'].shift(1)
        #print(df)
    except Exception as e:
        print("Exception3 : ", e)
    try:
        df['ror'] = np.where(df['high'] > df['target'],
                            df['close'] / df['target'],
                            1)
        #print(df)
    except Exception as e:
        print("Exception4 : ", e)
        
    ror = df['ror'].cumprod().iloc[-2]
    return ror



def update_dynamodb_table(bestk):
    print("start function : updating dynamoDB talbe")
    dynamodb = boto3.client('dynamodb')
    
    # define the table name and the key of the item to be updated
    table_name = 'Table-ForEthauto-PROD-ethauto'
    item_key = {'env': {'S': 'PROD'}}
    
    # define the attribute to be updated and its new value
    attribute_name = 'k-value'
    new_value = bestk
    
    # update the item with the new attribute value
    try:
        response = dynamodb.update_item(
            TableName=table_name,
            Key=item_key,
            UpdateExpression='SET #attr = :val',
            ExpressionAttributeNames={'#attr': attribute_name},
            ExpressionAttributeValues={':val': {'N': str(new_value)}}
        )
        print("success : updating dynamoDB talbe")
    except Exception as e:
        print("Exception : ", e)

    return response

def get_parameter_fromSSM() :
    print("start function : get_parameter_fromSSM")
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


def handler(event, context):
    slack_token=get_parameter_fromSSM()
    client=slack_sdk.WebClient(token=slack_token)
    
    try:
        dict={}
        try:
            for k in np.arange(0.05, 1.0, 0.05):
                ror = get_ror(k)
                print("%.2f %f" % (k, ror))
                if ror<1 :
                    k=k*(-1)
                dict[k]=ror
        except :
            pass
        bestk=max(dict, key=dict.get)
        bestk=round(bestk, 2)
        
        
        result=update_dynamodb_table(bestk)

        client.chat_postMessage(channel='#ethauto-step',
                                text='Lambda-Bestk: k-value: '+str(bestk))
    except Exception as e:
        client.chat_postMessage(channel='#ethauto-step',
                                text='Lambda-Bestk: Exception : '+str(e))

    return result