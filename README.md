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

### roadmap
1. scrfd
2. sort
3. tracker
   1. [mobiface-toolkit](src%2Fmobiface-toolkit) update to 3.11
4. arcface+cuda
5. milvus + gpu
6. fastapi



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
# draft
我们个项目的主要使用场景研究，是针对于多人脸的实时的人脸识别情况，这个多人的实时你人脸识别的情况，他的研究的主题是前端使用更优化的人脸检测算法，以及选择了一个比较合适的追踪方法，多目标追踪算法。他们分别在现有的数据集上面表现的非常的优秀，以及我人脸检测算法，他在现有的数据集上面表现仅仅只是针对于多人脸检测的效果非常好。然后是多目标追踪，我们选由于我们的上下文是人脸识别，因此不太可能出现人脸被遮挡的情况，因为人们会刻意的在识别的场景下露出人脸，即使是多人同时识别的环境下。因此我们在这种非遮蔽的情况下，选择了一个性能比较优异的，清亮的，以及能很好的和人脸追踪算法，和人脸检测算法结合在一起的多目标追踪算法。以及我们给他取了个新的名字，并且我们在人脸追踪数据集上面表现性，表现准确率，儿子追踪性能，追踪的性能优异，这是人脸追踪的部分。之所以使用这种方式是为了他可以大大的减少后端的负载，因为我们对人脸进行赋予语义进行追踪，判断前后针之间的人脸的关系，我们可以在此基础上加一些额外的可以选择的条件，比如说人脸满足什么大小，以及后端的准确率是多少。如果检测精度识别的精度较低，我们可以对对这个结果进行再次检测，错误的结果进行再次检测等，这种就是说我们可以加入额外的人为的选择性条件来时，检测识别更加的灵活，以及可以减少后端的负载。这是前端人脸追踪算法部分相关的研究

对于后端，我们主要采用异步网络框架发API，在异步网络框架中使用web sock的socket技术进行双向通讯，双向异步通讯来实时的与前端传输图像流。因此相比较传统的同步框架，我们做了对图像传输性能相关的测试。在高负荷的情况下，异步框架具有极高的性能，就是在后端网络框架上的研究。在选定了后端网络框架这个接口网关的接口之后，我们涉及到了人脸识别的问题。人脸识别我们采用最新的人脸特征提取器，我们从前端接触到从前端接收到人脸检测的图片，我们在后端进行拉伸，并且进行特征提取，这个特征提取由于它是非常计算密集型的，耗时较长，因此我们在后端可以采用cud深度学习加速推理。这是前后端分离项目的优势，以及提取完特征线上之后，我们需要拿到特征数据库中去比对。我们在此之前，我们也对人脸特征TSHE模型的精度与速度做了相关的测试。然后我们也对车上搜索特征向量数据库的搜索做了相关测试。线上数据库对大量线上数据中，进行线上搜索的性能以及准确度做了相关测试，并且尝试使用GPU进行加速搜索。以及涉及到后端服务器负载的问题，我们可以使用K8S进行自动扩容等相关的操作，从而使得后端的服务可以弄纳高并发的性能以及高负荷的情况。这是后端相关的研究