# BoostFace_fastapi

## Introduction📃

- cloud compute for extract and search face embedding
- db backend for desktop and mobile app

## deployment ☁️

- docker compose
  - fastapi cloud compute
  - milvus-standalone

- cloud service
  - digital ocean
    - vps

## architecture🌈

- fastapi container
  - main process
    - fastapi
      - basic apis
    - IdentifyWorker sub process
      - identify-worker sub process
        - extract
          - arcface onnx
        - register or search
          - milvus
- milvus container
  - milvus-standalone
    - milvus
    - minio
    - milvus-etcd

## Road map🚀
1. for demo ✅ 
2. for paper 🥵
   -
3. for real world 🥵
   










