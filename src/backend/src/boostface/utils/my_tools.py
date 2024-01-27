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

