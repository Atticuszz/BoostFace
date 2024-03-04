import cv2
import numpy as np
import streamlit as st
from pygizmokit.rich_logger import set_up_logging
from setttings import ModelsConfig, SourceConfig
from web.inference import onnx_runner
from web.inference.utils.decorator import calm_down

set_up_logging()


def init_ui():
    # 设置页面布局
    st.set_page_config(
        page_title="BoostFace: Real-Time Multi-Face Detection and Recognition System",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 主页标题
    st.title("Real-Time Multi-Face Recognition")

    # 侧边栏配置
    st.sidebar.header("Model Config")

    model_type = st.sidebar.radio("Select Task", ["Detection", "Identification"])
    confidence = (
        float(st.sidebar.slider("Select Detection Threshold", 25, 100, 40)) / 100
    )

    # 根据模型类型选择模型路径
    model_path = (
        ModelsConfig.detect_model.path()
        if model_type == "Detection"
        else ModelsConfig.extract_model.path()
    )


# 加载预训练ML模型
# try:
#     model = helper.load_model(model_path)
# except Exception as ex:
#     st.error(f"Unable to load model. Check the specified path: {model_path}")
#     st.error(ex)


def run_app():
    # 图像/视频配置
    st.sidebar.header("Image/Video Config")
    source_type = st.sidebar.radio(
        "Select Source", [source.value for source in SourceConfig]
    )

    # 图像源处理
    if source_type == SourceConfig.Image.value:
        source_img = st.sidebar.file_uploader(
            "Choose an image...", type=("jpg", "jpeg", "png", "bmp", "webp")
        )
        col1, col2 = st.columns(2)

        with col1:
            if source_img is not None:
                # 使用OpenCV加载和显示图像
                file_bytes = np.asarray(bytearray(source_img.read()), dtype=np.uint8)
                uploaded_image = cv2.imdecode(file_bytes, 1)
                st.image(
                    uploaded_image,
                    caption="Uploaded Image",
                    channels="BGR",
                    use_column_width=True,
                )

        # 其他源类型（视频、Webcam、RTSP、YouTube）的处理可以类似地进行调整

    elif source_type == SourceConfig.video.value:
        st.info("Video source is not yet supported!")
        st_frame = st.empty()
        while True:
            with calm_down(1 / 30):
                img = onnx_runner.get_result()
                st_frame.image(
                    img.nd_arr,
                    caption="Detected Video",
                    channels="BGR",
                    use_column_width=True,
                )

    else:
        st.error("Please select a valid source type!")


if __name__ == "__main__":
    init_ui()
    run_app()
