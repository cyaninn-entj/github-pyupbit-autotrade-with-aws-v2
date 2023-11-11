import pyupbit
import datetime
import upbit_defs as m_upbit
import log_defs as m_log
import time
import schedule
import boto3
import slack_sdk

def get_parameter_fromSSM() :
    ssm = boto3.client('ssm')

    parameters=['/ethauto/upbit-key/access-key',
                '/ethauto/upbit-key/secret-key',
                '/ethauto/slack-token']
    ssm_para=list()

    for i in parameters:
        response = ssm.get_parameter(
            Name=i,
            WithDecryption=True
        )
        ssm_para.append(response['Parameter']['Value'])
    
    return ssm_para[0],ssm_para[1], ssm_para[2]


global predicted_end_price
def read_dynamoDB_table() :
    global predicted_end_price
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



def main(coin):
    global predicted_end_price

    d = datetime.datetime.now()
    year=str(d.strftime("%Y"))
    month=str(d.strftime("%m"))
    day=str(d.strftime("%d"))

    log_file_name="output"+year+month+day+".log"
    log_file_path="output/"+log_file_name
    logger=m_log.open_logger(log_file_path)
    
    schedule.every(1).hours.do(read_dynamoDB_table)

    try : # read dynamoDB
        upbit_access_key, upbit_secret_key, slack_token = get_parameter_fromSSM()
        client=slack_sdk.WebClient(token=slack_token)
        best_k, predicted_end_price = read_dynamoDB_table()
        log_msg="success : get_parameter_fromSSM, read_dynamoDB_table"
        logger.debug(log_msg); 
        client.chat_postMessage(channel='#ethauto-step', text=log_msg)                     
    except Exception as e:
        log_msg="failure : get_parameter_fromSSM, read_dynamoDB_table"
        logger.error(log_msg); logger.error("Exception : "+str(e))
        client.chat_postMessage(channel='#ethauto-step', text=log_msg+' : Exception : '+str(e))

    try : # upbit api login
        upbit_login = pyupbit.Upbit(upbit_access_key, upbit_secret_key)
        log_msg="success : upbit login"
        logger.debug(log_msg)
        client.chat_postMessage(channel='#ethauto-step', text=log_msg)
    except Exception as e:
        log_msg="failure : upbit login"
        logger.error(log_msg)
        logger.error("Exception : "+str(e))
        client.chat_postMessage(channel='#ethauto-step', text=log_msg+' : Exception : '+str(e))
        
    
    try : # get target & current price
        target_price = m_upbit.get_target_price(coin, float(best_k))
        current_price = m_upbit.get_current_price(coin)
        log_msg="success : get trade indexes"
        logger.debug(log_msg)
        client.chat_postMessage(channel='#ethauto-step', text=log_msg+' : \n \
                            bestk:'+str(best_k)+' target:'+str(target_price)+' current:'+str(current_price)+' endprice:'+str(predicted_end_price))
    except Exception as e:
        log_msg="failure : get trade indexes"
        logger.error(log_msg)
        logger.error("Exception : "+str(e))
        client.chat_postMessage(channel='#ethauto-step', text=log_msg+' : Exception : '+str(e)) 

    # trading start
    log_cup=0; main_live_slack_cooltime=600
    while True:
        start_time = m_upbit.get_start_time(coin)
        end_time = start_time + datetime.timedelta(days=1)
        dt_now = datetime.datetime.now()

        schedule.run_pending()

        # trade time 9:00~8:53
        if start_time < dt_now < end_time - datetime.timedelta(minutes=7):
            # if bestk is less than 0, shutdown proccess
            if best_k<0 :
                log_msg="bestk value is not enough"
                logger.debug(log_msg)
                client.chat_postMessage(channel='#ethauto-step', text=log_msg+' :'+str(best_k))
                break

            # fit condition
            if target_price < current_price and current_price < predicted_end_price:
                krw = m_upbit.get_balance("KRW", upbit_login)
                if krw > 5000:
                    upbit_login.buy_market_order(coin, krw*0.9995)
                    logger.debug("buy_market_order : "+str(dt_now))
                    client.chat_postMessage(channel='#ethauto-step',
                        text='buy_market_order :'+str(current_price))
                    purchased_price=current_price
                else:
                    if main_live_slack_cooltime==600 :
                        log_msg='[purchased] purchased_price:'+str(purchased_price)+', current_price:'+str(current_price)+', end_price:'+str(predicted_end_price)
                        logger.info(log_msg)
                        client.chat_postMessage(channel='#ethauto-cluster-main', text=log_msg)
                        main_live_slack_cooltime=0

            # unfit condition
            else :
                log_msg="running :"+str(dt_now)+"  / target_price:"+str(target_price)+", current_price:"+str(current_price)+", end_price:"+str(predicted_end_price)
                if log_cup==10 :
                    logger.info(log_msg)
                    log_cup=0
                if main_live_slack_cooltime==600 :
                    client.chat_postMessage(channel='#ethauto-cluster-main', text=log_msg)
                    main_live_slack_cooltime=0
        
        #none trade time 8:53~9:00
        else:
            eth = m_upbit.get_balance("ETH", upbit_login)
            if eth > 0.00008:
                upbit_login.sell_market_order(coin, eth*0.9995)
                logger.debug("success: sell_market_order")
                client.chat_postMessage(channel='#ethauto-step', text='success: sell_market_order')
            break
        
        # log cooldown
        log_cup=log_cup+1; main_live_slack_cooltime=main_live_slack_cooltime+1
        time.sleep(1)

    logger.debug("success: shutdown daily autotrade")
    client.chat_postMessage(channel='#ethauto-step', text='success: shutdown daily autotrade')
        
    try:
        m_log.send_logs_to_s3(log_file_name, log_file_path)
        log_msg='success : send_logs_to_s3'
        logger.debug(log_msg)
        client.chat_postMessage(channel='#ethauto-step', text=log_msg)
    except Exception as e:
        log_msg='fail : send_logs_to_s3'
        logger.debug(log_msg)
        client.chat_postMessage(channel='#ethauto-step', text=log_msg+' : Exception : '+str(e))


coin="KRW-ETH"
main(coin)
