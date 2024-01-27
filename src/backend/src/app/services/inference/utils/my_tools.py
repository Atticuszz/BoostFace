import cv2

# from ..app.common import Face

__all__ = ['flatten_list', 'get_digits', 'get_nodigits']


# # 展开嵌套列表,最底层元素是Face或者Image对象
# def flatten_list(nested_list):
#     from ..data.image import Image
#     try:
#         assert not isinstance(nested_list, Face) or isinstance(nested_list, Image)
#         for sublist in nested_list:
#             for element in flatten_list(sublist):
#                 yield element
#     except (TypeError, AssertionError):
#         yield nested_list


def get_digits(s: str) -> str:
    return ''.join(c for c in s if c.isdigit())


def get_nodigits(s: str) -> str:
    return ''.join(c for c in s if not c.isdigit())


def detect_cameras():
    import cv2
    max_to_check = 10
    available_cameras = []

    for i in range(max_to_check):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            print(f"Camera index {i} is available.")
            available_cameras.append(i)
            cap.release()
        else:
            print(f"Camera index {i} is not available.")
    print("Available cameras are:", available_cameras)
    return available_cameras


def get_codec_format(cap: cv2.VideoCapture):
    # 获取当前的视频编解码器
    fourcc = cap.get(cv2.CAP_PROP_FOURCC)

    # 因为FOURCC编码是一个32位的值，我们需要将它转换为字符来理解它
    # 将整数编码值转换为FOURCC编码的字符串表示形式
    codec_format = "".join([chr((int(fourcc) >> 8 * i) & 0xFF) for i in range(4)])
    print(f"The video  codec  is {codec_format}")
    return codec_format
