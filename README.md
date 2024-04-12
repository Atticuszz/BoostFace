# 🚀 BoostFace 🚀

Welcome to **BoostFace**! The cutting-edge, high-performance face recognition system designed to revolutionize the way we think about real-time identification and tracking. Built with a powerful stack of technologies, BoostFace is your go-to solution for handling high-load, high-concurrency scenarios with ease and efficiency. 🌟

## 🛠 Tech Stack

- **Frontend**: Leveraging [Streamlit](https://streamlit.io/) for an intuitive, user-friendly interface, combined with SCRFD for efficient and accurate face detection, and SORT for multi-object tracking. Real-time image transmission is facilitated through Websockets, ensuring a seamless and dynamic user experience. 🖥️

- **Backend**: Powered by [FastAPI](https://fastapi.tiangolo.com/) for lightning-fast backend operations, [ONNX Runtime](https://onnx.ai/onnx-runtime) for optimized machine learning model inference, and [CUDA](https://developer.nvidia.com/cuda-zone)/[cuDNN](https://developer.nvidia.com/cudnn) for leveraging NVIDIA's GPU acceleration. To round it all off, [Milvus](https://milvus.io/) is used to handle the heavy lifting of vector similarity search, making our system not only fast but also incredibly scalable. 🚀

## 🌈 Features

- **Real-Time Face Recognition**: Identify and track faces in real-time with unparalleled accuracy. 🤖

- **High Scalability**: Ready to handle an expansive number of concurrent requests without breaking a sweat. 📈

- **Low Latency**: Designed from the ground up to minimize response times, making it ideal for real-time applications. ⚡

- **Easy Integration**: With a well-documented API, integrating BoostFace into your existing infrastructure is a breeze. 🌐

## 📚 Getting Started

Dive into the world of high-performance face recognition by cloning this repo and following our detailed setup instructions. Whether you're a developer looking to integrate face recognition into your project, or you're simply curious about the technology, BoostFace has something for everyone.

```bash
git clone https://github.com/Atticuszz/boostface.git
cd boostface
```

- download arcface_onnx model
```bash
cd src/Demo/backend/services/inference/model_zoo
wget https://github.com/Atticuszz/BoostFace/releases/download/dataset/models.zip
unzip models.zip
rm -rf models.zip
```

- install env
```bash
cd src/Demo
conda env create -f environment.yml
```
