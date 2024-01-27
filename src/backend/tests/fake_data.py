import itertools

import numpy as np

# from boostface.types import MatchInfo
# from app.services.inference.common import Face2Search, FaceNew, Image2Detect


def generate_normalized_embeddings(n, dim=512):
    embeddings = np.random.randn(n, dim)  # 生成正态分布的随机向量
    embeddings /= np.linalg.norm(embeddings, axis=1)[:, np.newaxis]  # 规范化向量
    return embeddings


def data_generator(num_items, dim=512):
    # 使用 itertools.count 可以无限生成连续的整数
    for i in itertools.count(start=1):
        if i > num_items:
            break
        embedding = np.random.randn(dim)
        embedding /= np.linalg.norm(embedding)
        id = f"id_{i}"
        name = f"name_{i}"
        yield embedding, id, name
# def generate_face2search(pixels=None, size=None) -> Face2Search:
#     """
#     Generate a LightImage object with either the specified number of pixels or the specified size.
#     Include face data with five keypoints as NumPy arrays based on the image size
#     or a random rectangle if only pixels are specified.
#     """
#     det_score = 0.8  # Fixed detection score
#
#     if size:
#         # If size is specified, create an image with the given size
#         height, width = size
#         # The entire image is considered a face
#         bbox = np.array([[0, 0], [width - 1, 0], [width - 1,
#                                                   height - 1], [0, height - 1]], dtype=np.int32)
#         # Approximate positions for the five keypoints
#         kps = np.array([
#             [width // 2, height // 4],  # Nose
#             [width // 3, height // 3],  # Left eye
#             [2 * width // 3, height // 3],  # Right eye
#             [width // 3, 2 * height // 3],  # Left mouth corner
#             [2 * width // 3, 2 * height // 3]  # Right mouth corner
#         ], dtype=np.int32)
#     else:
#         # If size is not specified, calculate the size based on the number of
#         # pixels
#         if pixels is None:
#             pixels = 5000000  # Default to 5 million pixels if neither size nor pixels are provided
#         side_length = int(np.sqrt(pixels / 3))
#         height, width = side_length, side_length
#         # Create a random face rectangle in the image
#         x1, y1 = np.random.randint(0, width // 2, size=2)
#         x2, y2 = np.random.randint(width // 2, width, size=2)
#         bbox = np.array([[x1, y1], [x2, y1], [x2, y2],
#                          [x1, y2]], dtype=np.int32)
#         # Approximate positions for the five keypoints within the bbox
#         kps = np.array([
#             [(x1 + x2) // 2, (y1 + 3 * y2) // 4],  # Nose
#             [x1 + (x2 - x1) // 3, y1 + (y2 - y1) // 3],  # Left eye
#             [x1 + 2 * (x2 - x1) // 3, y1 + (y2 - y1) // 3],  # Right eye
#             [x1 + (x2 - x1) // 3,
#              y1 + 2 * (y2 - y1) // 3],
#             # Left mouth corner
#             # Right mouth corner
#             [x1 + 2 * (x2 - x1) // 3, y1 + 2 * (y2 - y1) // 3]
#         ], dtype=np.int32)
#
#     image_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
#     return Face2Search(
#         face_img=image_array,
#         bbox=bbox,
#         kps=kps,
#         det_score=det_score
#     )
#
#
# def generate_image2detect(pixels=None, size=None, num_faces=3) -> Image2Detect:
#     """
#     Generate an Image2Detect object with a specified number of pixels or size,
#     containing a number of detected faces.
#
#     :param pixels: Total number of pixels in the image (if size is not given).
#     :param size: Tuple of (width, height) for the image.
#     :param num_faces: Number of face objects to generate in the image.
#     :return: An Image2Detect object.
#     """
#     # Generate the main image
#     if size:
#         # Use specified size
#         height, width = size
#     else:
#         # Calculate size based on pixels
#         if pixels is None:
#             pixels = 5000000  # Default to 5 million pixels
#         side_length = int(np.sqrt(pixels / 3))
#         height, width = side_length, side_length
#
#     image_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
#
#     # Generate faces
#     faces = []
#     for _ in range(num_faces):
#         face2search = generate_face2search(size=(height, width))
#         # Create a FaceNew object
#         face = FaceNew(
#             bbox=face2search.bbox,
#             kps=face2search.kps,
#             det_score=face2search.det_score,
#             scene_scale=(0, 0, width, height),
#             color=(50, 205, 255),
#             match_info=MatchInfo(0.0, '')
#         )
#         faces.append(face)
#
#     return Image2Detect(image=image_array, faces=faces)


if __name__ == "__main__":
    img = generate_face2search(size=(640, 640))
    print(img)
