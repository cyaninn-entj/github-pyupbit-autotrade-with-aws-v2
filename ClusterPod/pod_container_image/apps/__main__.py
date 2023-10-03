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

global best_k
global predicted_end_price
def read_dynamoDB_table() :
    global best_k
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



def main():
    global best_k
    global predicted_end_price

    d = datetime.datetime.now()
    year=str(d.strftime("%Y"))
    month=str(d.strftime("%m"))
    day=str(d.strftime("%d"))
    log_file_name="output/output"+year+month+day+".log"
    logger=m_log.open_logger(log_file_name)
    

    schedule.every(1).hours.do(read_dynamoDB_table)

    try :
        upbit_access_key, upbit_secret_key, slack_token = get_parameter_fromSSM()
        client=slack_sdk.WebClient(token=slack_token)
        best_k,predicted_end_price= read_dynamoDB_table()
        logger.debug("success : get_parameter_fromSSM, read_dynamoDB_table")
        client.chat_postMessage(channel='#ethauto-step',
                                text='success : get_parameter_fromSSM, read_dynamoDB_table')
                            
    except Exception as e:
        logger.error("failure : get_parameter_fromSSM, read_dynamoDB_table")
        logger.error("Exception : "+str(e))
        client.chat_postMessage(channel='#ethauto-step',
                                text='failure : get_parameter_fromSSM, read_dynamoDB_table : Exception : '+str(e))

    try :
        upbit_login = pyupbit.Upbit(upbit_access_key, upbit_secret_key)
        logger.debug("success : upbit login")
        client.chat_postMessage(channel='#ethauto-step',
                                text='success : upbit login')
    except Exception as e:
        logger.error("failure : upbit login")
        logger.error("Exception : "+str(e))
        client.chat_postMessage(channel='#ethauto-step',
                                text='failure : upbit login : Exception : '+str(e))
        
    
    try :
        '''자동매매'''
        logger.debug("success : start daily autotrade")
        target_price = m_upbit.get_target_price("KRW-ETH", float(best_k))
        current_price = m_upbit.get_current_price("KRW-ETH")
        client.chat_postMessage(channel='#ethauto-step',
                                text='success : start daily trading : \n \
                                bestk:'+str(best_k)+' target:'+str(target_price)+' current:'+str(current_price)+' endprice:'+str(predicted_end_price))
        

        # trading start
        log_cup=0
        main_live_slack_cooltime=600
        while True:
            try:
                now = datetime.datetime.now()
                start_time = m_upbit.get_start_time("KRW-ETH")
                end_time = start_time + datetime.timedelta(days=1)
                dt_now = datetime.datetime.now()
                
                schedule.run_pending()

                if start_time < now < end_time - datetime.timedelta(minutes=7):
                    if best_k<0 :
                        client.chat_postMessage(channel='#ethauto-step',
                                text='bestk value is not enough :'+str(best_k))
                        break
                    target_price = m_upbit.get_target_price("KRW-ETH", float(best_k))
                    current_price = m_upbit.get_current_price("KRW-ETH")
                    if target_price < current_price and current_price < predicted_end_price:
                        krw = m_upbit.get_balance("KRW", upbit_login)
                        if krw > 5000:
                            upbit_login.buy_market_order("KRW-ETH", krw*0.9995)
                            client.chat_postMessage(channel='#ethauto-step',
                                text='buy_market_order :'+str(current_price))
                            logger.debug("buy_market_order : "+str(dt_now))
                            purchased_price=current_price
                        else:
                            if main_live_slack_cooltime==600 :
                                client.chat_postMessage(channel='#ethauto-cluster-main',
                                    text='[purchased] purchased_price:'+str(purchased_price)+', current_price:'+str(current_price)+', end_price:'+str(predicted_end_price))
                                logger.info('[purchased] purchased_price:'+str(purchased_price)+', current_price:'+str(current_price)+', end_price:'+str(predicted_end_price))
                                main_live_slack_cooltime=0
                    else :
                        if log_cup==10 :
                            logger.info("running :"+str(dt_now)+"  / target_price:"+str(target_price)+", current_price:"+str(current_price)+", end_price:"+str(predicted_end_price))
                            log_cup=0
                        if main_live_slack_cooltime==600 :
                            client.chat_postMessage(channel='#ethauto-cluster-main',
                                text='[running]'+str(dt_now)+' target_price:'+str(target_price)+', current_price:'+str(current_price)+', end_price:'+str(predicted_end_price))
                            main_live_slack_cooltime=0
                else:
                    eth = m_upbit.get_balance("ETH", upbit_login)
                    if eth > 0.00008:
                        upbit_login.sell_market_order("KRW-ETH", eth*0.9995)
                    break
                log_cup=log_cup+1; main_live_slack_cooltime=main_live_slack_cooltime+1 # log cup
                time.sleep(1)
            except Exception as e:
                logger.error("Exception : "+str(e))
                time.sleep(1)

        logger.debug("success: shutdown daily autotrade")
        client.chat_postMessage(channel='#ethauto-cluster-main',
                                text='success: shutdown daily autotrade')
        
        try:
            m_log.send_logs_to_s3(log_file_name)
            client.chat_postMessage(channel='#ethauto-step',
                                text='success : send_logs_to_s3')
        except Exception as e:
            client.chat_postMessage(channel='#ethauto-step',
                                text='fail : send_logs_to_s3 : Exception : '+str(e))
            

    except Exception as e:
        logger.error("failure : trading __main__")
        logger.error("Exception : "+str(e))
        client.chat_postMessage(channel='#ethauto-step',
                                text='failure : trading __main__ : Exception : '+str(e))
        

main()
