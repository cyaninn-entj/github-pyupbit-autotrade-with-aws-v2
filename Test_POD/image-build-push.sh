#!/bin/bash

# 버전 변수 설정
VERSION="ethauto.v.1.1"

# 이미지 태그에 버전 변수를 사용하여 Docker 이미지 빌드
docker build -t test-image:$VERSION .

# AWS ECR 로그인 및 이미지 푸시
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 553149402753.dkr.ecr.ap-northeast-2.amazonaws.com

docker tag test-image:$VERSION 553149402753.dkr.ecr.ap-northeast-2.amazonaws.com/test-image:$VERSION

docker push 553149402753.dkr.ecr.ap-northeast-2.amazonaws.com/test-image:$VERSION
