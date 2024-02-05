## 结构

### 论文名称

### 主要切入点

1. 系统架构
   1. 前端
      1. 人脸追踪算法
         1. scrfd + 卡尔曼滤波+匈牙利匹配
         2. pyqt跨平台框架
      2. 人脸活体检测
         1. expo face detector
         2. expo前端框架
   2. 后端
      1. 人脸特征提取
         1. arcface
            1. onnxruntime cuda加速推理
            2. 与其他常见相比的精确度
      2. 人脸特征比对
         1. milvus
            1. 矢量搜索，Nvidia加速
            2. 矢量搜索精度
            3. 速度
      3. 高并发网络框架
         1. fastapi
            1. 异步框架 io吞吐性能与其他同步框架相比
            2. websocket 双向通讯支持高并发
      4. 容器化+自动扩容部署+负载均衡
         1. docker
            1. 容器化管理避免系统之间不兼容的问题
         2. kubernetes
            1. 根据负载自动扩容
         3. nginx

### 结构


### 人脸追踪数据集
MobiFace Benchmark Request Form
Hi, 
Please find the MobiFace dataset on https://drive.google.com/open?id=1LrVrx_InOo3og9RfCynQkMkfaVydn7ra 

Please note due to regulations in Europe, we are not allowed to distribute videos directly. Please find the original videos with the provided IDs on YouTube. If some videos have been taken down, we are unfortunately unable to provide the videos.

Please consider citing the following papers if you find the dataset useful:

@inproceedings{FT-RCNN,
    author = {Yiming Lin and Jie Shen and Shiyang Cheng and Maja Pantic},
    booktitle = {The IEEE International Conference on Automatic Face and Gesture Recognition (FG)},
    title = {FT-RCNN: Real-time Visual Face Tracking with Region-based Convolutional Neural Networks},
    year = {2020},
}

@inproceedings{mobiface_fg2019,
    author={Yiming Lin and Shiyang Cheng and Jie Shen and Maja Pantic},
    booktitle = {The IEEE International Conference on Automatic Face and Gesture Recognition (FG)},
    title={MobiFace: A Novel Dataset for Mobile Face Tracking in the Wild},
    year={2019},
    url={https://arxiv.org/abs/1805.09749v2}
}

Best,
MobiFace Team
Edit your response
