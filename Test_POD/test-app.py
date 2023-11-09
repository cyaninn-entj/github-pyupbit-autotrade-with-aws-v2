import pyupbit
import upbit_defs as m_upbit
import boto3
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

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

def read_dynamoDB_table():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Table-ForEthauto-PROD-ethauto')

    response = table.get_item(
        Key={
            'env': 'PROD'
        }
    )

    item = response['Item']
    best_k = item['k-value']
    predicted_end_price = item['endprice']

    return best_k, predicted_end_price

def send_slack_message(channel, text):
    try:
        ssm = boto3.client('ssm')
        slack_token = ssm.get_parameter(Name='/ethauto/slack-token', WithDecryption=True)['Parameter']['Value']
        client = WebClient(token=slack_token)
        client.chat_postMessage(channel=channel, text=text)
    except SlackApiError as e:
        print(f"Error sending Slack message: {e.response['error']}")

def test_get_parameter_fromSSM():
    try:
        upbit_access_key, upbit_secret_key, slack_token = get_parameter_fromSSM()
        send_slack_message("#test", f"Success: get_parameter_fromSSM")
    except Exception as e:
        send_slack_message("#test", f"Failure: get_parameter_fromSSM - Exception: {str(e)}")

def test_read_dynamoDB():
    try:
        best_k, predicted_end_price = read_dynamoDB_table()
        send_slack_message("#test", f"Success: read_dynamoDB")
    except Exception as e:
        send_slack_message("#test", f"Failure: read_dynamoDB - Exception: {str(e)}")

def test_pyupbit_api():
    try:
        coin = "KRW-ETH"
        upbit_access_key, upbit_secret_key, _ = get_parameter_fromSSM()
        upbit_login = pyupbit.Upbit(upbit_access_key, upbit_secret_key)

        target_price = m_upbit.get_target_price(coin, 0.5)  # Replace 0.5 with your desired 'k' value
        current_price = m_upbit.get_current_price(coin)
        balance = m_upbit.get_balance("KRW", upbit_login)

        message = f"Success: pyupbit API tests\n"
        message += f"Target Price(k=0.5): {target_price}\nCurrent Price: {current_price}\nBalance: {balance} KRW\n"

        send_slack_message("#test", message)
    except Exception as e:
        send_slack_message("#test", f"Failure: pyupbit API tests - Exception: {str(e)}")

# 독립적으로 호출되는 메시지 추가
def send_test_start_message():
    send_slack_message("#test", "-----------------start test-------------------\n")

def send_test_end_message():
    send_slack_message("#test", "-----------------end-----------------")

if __name__ == "__main__":
    coin = "KRW-ETH"
    send_test_start_message()
    test_get_parameter_fromSSM()
    test_read_dynamoDB()
    test_pyupbit_api()
    send_test_end_message()