sudo k3s kubectl delete secret regcred -n prod-ethauto
sudo k3s kubectl create secret docker-registry regcred \
  --docker-server=553149402753.dkr.ecr.ap-northeast-2.amazonaws.com \
  --docker-username=AWS \
  --docker-password=$(aws ecr get-login-password) \
  --namespace=prod-ethauto

python3 /home/ubuntu/docker-reg-cred/recreate-docker-registry-slack-push.py

rm /home/ubuntu/docker-reg-cred/output.log