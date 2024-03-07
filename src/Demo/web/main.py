import logging
from pathlib import Path

import streamlit as st
from pygizmokit.rich_logger import set_up_logging
from setttings import (
    CameraConfig,
    DetectorConfig,
    InferenceProvider,
    SourceConfig,
    TrackerConfig,
)
from web.inference import BoostFace
from web.inference.utils.decorator import calm_down

set_up_logging()
logger = logging.getLogger(__file__)


# @profile
def run_app():
    # init ui
    st.set_page_config(
        page_title="BoostFace: Real-Time Multi-Face Detection and Recognition System",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("Real-Time Multi-Face Recognition")

    st.sidebar.header("Model Config")
    st.sidebar.header("Image/Video Config")

    with st.sidebar:
        # source config
        source_type = st.sidebar.radio(
            "Select Source", [source for source in SourceConfig]
        )
        st.toast(f"Selected source: {source_type}", icon="📡")
        # source file
        file_path: dict[str, str] = {
            file.name: file.as_posix()
            for file in source_type.files()
            if isinstance(file, Path) and file.is_file()
        }
        # camera config
        source_file_name = st.sidebar.selectbox("Select File", list(file_path.keys()))
        source_file = (
            file_path[source_file_name] if source_file_name else 0
        )  # 0 for webcam
        st.toast(f"Selected file: {source_file}", icon="📁")

        # detector config
        threshold = st.sidebar.slider("Select Detection Threshold", 10, 100, 70) / 100
        provider = st.sidebar.radio(
            "Select Detection Provider", [prov for prov in InferenceProvider]
        )
        st.toast(f"Selected provider: {provider}", icon="🔍")
        # tracker config
        iou_threshold = st.sidebar.slider("Select IOU Threshold", 10, 100, 40) / 100
        max_age = st.sidebar.slider("Select Max Age", 1, 100, 40)
        scale_threshold = st.sidebar.slider("Select Scale Threshold", 5, 30, 15) / 1000
        frames_threshold = st.sidebar.slider("Select Frames Threshold", 100, 400, 200)
        min_hits = st.sidebar.slider("Select Min Hits", 1, 10, 10)

    with st.spinner(text="Loading models...", cache=True):
        # config inference runner
        inference_runner = BoostFace(
            CameraConfig(url=source_file, url_type=source_type),
            DetectorConfig(threshold=threshold, provider=provider),
            TrackerConfig(
                iou_threshold=iou_threshold,
                max_age=max_age,
                scale_threshold=scale_threshold,
                frames_threshold=frames_threshold,
                min_hits=min_hits,
            ),
        )
    st.toast("Hooray! Models is ready!", icon="🎉")
    with st.container():
        run = st.toggle("Run", value=False)
        FRAME_WINDOW = st.image([])
        if run:
            st.info("Running...")
        while run:

            with calm_down(1 / 30):
                result = inference_runner.get_result()
                FRAME_WINDOW.image(result, channels="BGR", use_column_width=True)
        else:
            st.error("Stopped!")


if __name__ == "__main__":
    run_app()
