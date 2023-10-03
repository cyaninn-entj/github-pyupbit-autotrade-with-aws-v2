import boto3
import datetime

def send_logs_to_s3(file):
    bucket_name="s3bucket-cloudformationstack-prod-ethauto"
    session = boto3.Session(profile_name='default')

    s3=session.client('s3')
    opened_file=open(file, 'rb')
    
    # 파일 이름을 추출하여 객체 키로 사용
    object_key = file

    s3.upload_fileobj(opened_file, bucket_name, object_key)

files=list()
files.append('ethauto-main-template.yaml') #main_template_file
files.append('cluster-stack.yaml') #cluster_stack_file
files.append('serverless-stack.yaml') #serverless_stack_file

now = datetime.datetime.now()
try:
    for i in files:
        send_logs_to_s3(i)
    print("success pusing files to s3 : "+str(now))
except Exception as e:
    print("Exception : "+str(e))