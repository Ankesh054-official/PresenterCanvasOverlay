"""
    This module is to record specific window.
"""

# imports for multithreading and communication
import threading
import queue

# imports
import cv2
import numpy as np

import pyautogui
import pygetwindow as gw


class Window:
    """
    Class contains methods for window specific functionalities.
    """

    def __init__(self):
        """Method to initialize class object."""

        # Variables
        self.selected_window = object
        self.video_writer = object
        self.all_windows_title = []
        self.window_thread = threading
        self.video_recorder_thread = threading

        # flag for status
        self.is_running = False
        self.is_video_recording = False

        # Store frame in queue for communication b/w multiple threads
        self.window_frame_data = queue.Queue()

    def start(self):
        "Method will set a thread for recording and start process."

        self.is_running = True
        self.window_thread = threading.Thread(target=self.record)
        self.window_thread.start()

    def stop(self):
        """Metod will join threads."""

        self.is_running = False
        self.window_thread.join()

    def start_video_recording(self):
        """Method will set a thread for recording video of window and save into file."""

        self.is_video_recording = True
        self.video_recorder_thread = threading.Thread(target=self.record_video)
        self.video_recorder_thread.start()

    def stop_video_recording(self):
        """Method will join video recorder threads."""

        self.is_video_recording = False
        self.video_recorder_thread.join()

    def get_window_list(self):
        """Method Make a list of opened windows."""

        for window in gw.getAllWindows():
            if window.title:
                self.all_windows_title.append({window.title: {"OBJ": window}})

        return self.all_windows_title

    def show_window_list(self):
        """Method to show the list of opened windows."""

        for x in self.all_windows_title:
            for window in x.keys():
                print(f"{self.all_windows_title.index(x)}:{window}")

    def select_window(self):
        """Method to select a window."""

        window_index = int(input("Select window:\t"))
        window_title = list((self.all_windows_title[window_index]).keys())[0]
        obj = (self.all_windows_title[window_index])[window_title]["OBJ"]

        print(f"SELECTED WINDOW:\t {window_title}")

        self.selected_window = {"title": window_title, "OBJ": obj}
        return self.selected_window

    def get_selected_window(self):
        """Method returns window title and object."""

        return self.selected_window

    def record_video(self):
        """Method used to save recorded window into video."""

        # define the codec
        fourcc = cv2.VideoWriter_fourcc(*"XVID")

        # frame per second
        fps = 12.0

        window = self.get_selected_window()
        title = window.get("title")
        window_obj = window.get("OBJ")
        name = f"{title}.avi"

        # create the video write object
        self.video_writer = cv2.VideoWriter(name, fourcc, fps, tuple(window_obj.size))

        while self.is_running and self.is_video_recording:
            try:

                # Get the frame from the queue
                frame = self.window_frame_data.get(timeout=1)

                # Writting frames into video file
                self.video_writer.write(frame)
            except queue.Empty:
                continue

    def record(self):
        """Method used to record window of a application"""

        window = self.get_selected_window()
        window_obj = window.get("OBJ")
        window_obj.activate()

        while self.is_running:

            # make a screenshot
            image = pyautogui.screenshot(
                region=(
                    window_obj.left,
                    window_obj.top,
                    window_obj.width,
                    window_obj.height,
                )
            )

            # convert pixels to a proper numpy array to work with opencv.
            window_frame = np.array(image)

            # convert colors from BGR to RGB.
            window_frame = cv2.cvtColor(window_frame, cv2.COLOR_BGR2RGB)

            # Putting the frames into queue
            self.window_frame_data.put(window_frame)

    def show_preview(self):
        """Method for showing live recording voide from window object"""

        while self.is_running:
            try:

                # Get the frame from the queue
                frame = self.window_frame_data.get(timeout=1)

                # show the frame
                cv2.imshow("window preview", frame)

                # if the user clicks q, it exits
                if cv2.waitKey(1) == ord("q"):
                    self.is_running = False
                    break
            except queue.Empty:
                continue

    def __del__(self):
        """Deconstructor"""

        # Stoping the window recorder
        if self.is_running:
            self.is_running = False
            self.window_thread.join()

        # Stoping the video recorder thread
        if self.is_video_recording:
            self.video_writer.release()
            self.is_video_recording = False
            self.video_recorder_thread.join()

        # make sure everything is closed when exited
        cv2.destroyAllWindows()
