import json
import pyupbit
from prophet import Prophet
import boto3
import slack_sdk


def predict_price(ticker):
    """Prophet으로 당일 종가 가격 예측"""

    #최근 200시간의 데이터 불러오기
    df = pyupbit.get_ohlcv(ticker, interval="minute60")

    #시간(ds) 과 종가(y) 만 남김
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]

    #학습
    model = Prophet()
    model.fit(data)

    #24시간 미래 예측
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)

    #예상 종가 도출
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue
    print("endprice-value : "+str(predicted_close_price)+" !!!")

    return predicted_close_price



def update_dynamodb_table(endprice):
    dynamodb = boto3.client('dynamodb')
    
    # define the table name and the key of the item to be updated
    table_name = 'Table-ForEthauto-PROD-ethauto'
    item_key = {'env': {'S': 'PROD'}}
    
    # define the attribute to be updated and its new value
    attribute_name = 'endprice'
    new_value = endprice
    
    # update the item with the new attribute value
    try:
        response = dynamodb.update_item(
            TableName=table_name,
            Key=item_key,
            UpdateExpression='SET #attr = :val',
            ExpressionAttributeNames={'#attr': attribute_name},
            ExpressionAttributeValues={':val': {'N': str(new_value)}}
        )
    except Exception as e:
        print("Exception : ", e)

    return response

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


def handler(event, context):
    slack_token=get_parameter_fromSSM()
    client=slack_sdk.WebClient(token=slack_token)

    try:
        endprice=predict_price("KRW-ETH")
        result=update_dynamodb_table(endprice)

        client.chat_postMessage(channel='#ethauto-step',
                                text='Lambda-Endprice: endprice-value : '+str(endprice))
    except Exception as e:
        client.chat_postMessage(channel='#ethauto-step',
                                text='Exception : '+str(e))

    return result