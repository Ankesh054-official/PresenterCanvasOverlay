"""
    Module for camera related functionalities.
"""

# imports for multithreading and communication
import threading
import queue

# Import
import cv2

class Camera:
    """Class is a prtotype for camera related functions."""

    def __init__(self, camera_index: int = 0, height: int = 480, width: int = 640):
        """Constructor"""

        # Variables
        self.desired_height = height
        self.desired_width = width
        self.camera_index = camera_index
        self.thread = threading

        # Queue for communication between multiple threads
        self.frame_data = queue.Queue()

        # Camera object
        self.camera = cv2.VideoCapture(self.camera_index)

        # `ret` flag
        self.ret = False

        # flag for thread control
        self.is_running = False

        # set video output dimensions.
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.desired_height)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.desired_width)

    def start(self):
        """Method will set a thread for recording and start process."""
        self.is_running = True
        self.thread = threading.Thread(target=self.record)
        self.thread.start()

    def stop(self):
        """Method will join threads."""
        self.is_running = False

    def record(self):
        """Method for recording video from camera frame by frame."""

        while self.is_running:

            # Capture the video frame by frame
            self.ret, frame = self.camera.read()

            if not self.ret:
                print("Error: Failed to capture frame")
                break

            # Putting the frames into queue
            self.frame_data.put(frame)

    def show_preview(self):
        """Method for showing live recording video from camera."""

        while self.is_running:

            try:

                # Get the frame from the queue
                frame = self.frame_data.get(timeout=1)

                #  Show the frame
                cv2.imshow("Camera preview", frame)

                # if the user clicks q, it exits
                if cv2.waitKey(1) == ord("q"):
                    self.is_running = False
                    break

            except queue.Empty:
                continue

    def __del__(self):
        """Deconstructor"""

        # updating flag
        self.is_running = False

        # Join the thread
        self.thread.join()
        # release the camera object
        self.camera.release()

        # Destroy all the windows
        cv2.destroyAllWindows()

