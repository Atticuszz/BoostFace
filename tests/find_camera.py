import cv2

# define a video capture object
camera = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L2)
# camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
# camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
# camera.set(cv2.CAP_PROP_FPS, 30)
print(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
print(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(camera.get(cv2.CAP_PROP_FPS))
# print(cv2.getBuildInformation())
camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))

while True:

    # Capture the video frame
    # by frame
    ret, frame = camera.read()
    if ret:
        # Display the resulting frame
        cv2.imshow("frame", frame)

        # the 'q' button is set as the
        # quitting button you may use any
        # desired button of your choice
    else:
        print("Error reading frame")
        break
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# After the loop release the cap object
camera.release()
# Destroy all the windows
cv2.destroyAllWindows()
