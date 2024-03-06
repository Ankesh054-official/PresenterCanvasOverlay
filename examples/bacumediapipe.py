import cv2
import math
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasts.python import vision

BG_COLOR = (192, 192, 192) # grey
MASK_COLOR = (255, 255, 255) # white

# Height and width that will be used by the model
DESIRED_HEIGHT = 480
DESIRED_WIDTH = 480

print("segmenter init...")
# Create the options that will be used for ImageSegmenter
base_options = python.BaseOptions(model_asset_path='models/deeplabv3.tflite')
options = vision.ImageSegmenterOptions(base_options=base_options,
                                    output_category_mask=True)


# Performs resizing and showing the image
def resize_and_show(image):
    h, w = image.shape[:2]
    if h < w:
        img = cv2.resize(image, (DESIRED_WIDTH, math.floor(h/(w/DESIRED_WIDTH))))
    else:
        img = cv2.resize(image, (math.floor(w/(h/DESIRED_HEIGHT)), DESIRED_HEIGHT))
        cv2.imshow(img)


def remove_background(IMAGE):

    # Create the image segmenter
    with vision.ImageSegmenter.create_from_options(options) as segmenter:
        print("entring into segmenter")

        # Create the MediaPipe image file that will be segmented
        image = mp.Image.create_from_file(IMAGE)

        # Retrieve the masks for the segmented image
        segmentation_result = segmenter.segment(image)
        category_mask = segmentation_result.category_mask

        # Generate solid color images for showing the output segmentation mask.
        image_data = image.numpy_view()
        fg_image = np.zeros(image_data.shape, dtype=np.uint8)
        fg_image[:] = MASK_COLOR
        bg_image = np.zeros(image_data.shape, dtype=np.uint8)
        bg_image[:] = BG_COLOR

        condition = np.stack((category_mask.numpy_view(),) * 3, axis=-1) > 0.2
        output_image = np.where(condition, fg_image, bg_image)

        print(f'Segmentation mask of {name}:')
        resize_and_show(output_image)

def main():
    # Open camera
    print("--camera opening--")
    cap = cv2.VideoCapture(0)  # Change the index if you have multiple cameras

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        remove_background(frame_rgb)
        

        # Display the result
        cv2.imshow('Background Removed', result)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Release the camera and close windows                                                      
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("--Starting--")    
    main()
