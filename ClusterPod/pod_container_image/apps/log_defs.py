import boto3
import logging

def open_logger(log_file_path):
    # logger instance 생성
    logger = logging.getLogger(__name__)

    # handler 생성 (file type)
    fileHandler = logging.FileHandler(log_file_path)

    formatter = logging.Formatter('[%(asctime)s][%(levelname)s|%(filename)s:%(lineno)s] >> %(message)s')
    fileHandler.setFormatter(formatter)

    # logger instance에 handler 설정
    logger.addHandler(fileHandler)

    # set log level
    logger.setLevel(level=logging.DEBUG)

    return logger

def send_logs_to_s3(file_name,file_path):
    client = boto3.client('s3')
    response = client.put_object(
        Bucket='s3bucket-clusterlog-prod-ethauto',
        Key=file_name,
        Body=open(file_path, 'rb')
    )
    return response
