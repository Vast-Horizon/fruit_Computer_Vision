import cv2

def find_cam_index():
    # ls /dev/video* shows all of the index, this function find the index for the webcam
    for i in range(40):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Device index {i} is available.")
            ret, frame = cap.read()
            if ret:
                cv2.imshow(f"Camera {i}", frame)
                cv2.waitKey(0)
                cap.release()
                cv2.destroyAllWindows()
            return i
        else:
            print(f"Device index {i} is not available.")
            

def streaming(index):
    cap = cv2.VideoCapture(index)
    cap.set(cv2.CAP_PROP_FPS,30)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 448)

    if not cap.isOpened():
        print("Error: Could not open video device.")
    else:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                break

            cv2.imshow("Webcam", frame)

            # Press 'q' to quit the video stream
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

def record_video(output_file, duration=10, device_index=0):
    # Open the webcam
    cap = cv2.VideoCapture(device_index)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Couldn't open the webcam.")
        return

    # Get the width and height of the video capture
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, 20.0, (width, height))

    # Record video for specified duration
    start_time = cv2.getTickCount()
    while (cv2.getTickCount() - start_time) / cv2.getTickFrequency() < duration:
        ret, frame = cap.read()
        if ret:
            # Write the frame into the file 'output.avi'
            out.write(frame)
            # Display the resulting frame
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    # Release everything when done
    cap.release()
    out.release()
    cv2.destroyAllWindows()

# Example usage: record video for 10 seconds and save it as 'output.avi'
#index = find_cam_index()
streaming(0)
#record_video('output1.avi', duration=10, device_index=index)

