# 조코딩 채널 프로젝트 + AWS + K3S + ArgoCD
## 유튜버 '조코딩' 의 비트코인 자동매매 Open Source Project에 CNCF project 적용해보기

### 프로젝트 블로그
- <https://yeonwoo97.tistory.com/503>

- 패치노트, 설계, 구축, 관리 문서 포스팅

### 프로젝트 개요

<p align="center">
  <img src="file:///home/cyaninn/Pictures/ethauto/1-architecture.drawio%20(1).png">
</p>

- CNCF sandbox project인 k3s cluster 로 컨테이너 관리

- CNCF graduate project인 argoCD 를 사용해 프로젝트 배포 및 간단한 모니터링

- AWS Pipeline 을 사용해 ci/cd 를 구현

- 노션을 사용해 프로젝트 문서를 관리하며 여러 프로젝트 문서를 작성함으로써 프로젝트 완성도를 높힘