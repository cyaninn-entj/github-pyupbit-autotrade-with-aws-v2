# Cluster Pod

![proccess-main](https://github.com/cyaninn-entj/github-pyupbit-autotrade-with-aws-v2/assets/83701837/a6cd9b86-6b0e-4a49-bcaf-f89b72e50d8c)

### 프로젝트 블로그
- <https://yeonwoo97.tistory.com/503>

### 파일 구성

```
.
├── buildspec.yml
├── create-secret-for-docker-credential.sh
├── crontab
│   ├── crontab
│   ├── recreate-docker-registry.sh
│   └── recreate-docker-registry-slack-push.py
├── manifests
│   ├── kustomization.yaml
│   ├── pod-cronjob.yaml
│   ├── pv-pvc.yaml
│   └── test-pod-230927.yaml
└── pod_container_image
    ├── apps
    │   ├── log_defs.py
    │   ├── __main__.py
    │   └── upbit_defs.py
    ├── Dockerfile
    ├── requirements.txt
    └── run.sh
```

