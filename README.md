# 조코딩 채널 프로젝트 + AWS + K3S + ArgoCD
## 유튜버 '조코딩' 의 비트코인 자동매매 Project에 CNCF project 적용해보기

### 프로젝트 블로그
- <https://yeonwoo97.tistory.com/503>

- 패치노트, 설계, 구축, 관리 문서 포스팅

### 프로젝트 개요
- architecture diagram
![1-architecture drawio (1)](https://github.com/cyaninn-entj/github-pyupbit-autotrade-with-aws-v2/assets/83701837/57811db6-f644-4243-89e5-0db43dab13e4)

- proccess diagram
![process-general](https://github.com/cyaninn-entj/github-pyupbit-autotrade-with-aws-v2/assets/83701837/3e0207fc-55e6-4b03-9a5d-e45850524703)

- CNCF sandbox project인 k3s cluster 로 컨테이너 관리

- CNCF graduate project인 argoCD 를 사용해 프로젝트 배포 및 간단한 모니터링

- AWS Pipeline 을 사용해 ci/cd 를 구현

- 노션을 사용해 프로젝트 문서를 관리하며 여러 프로젝트 문서를 작성함으로써 프로젝트 완성도를 높힘