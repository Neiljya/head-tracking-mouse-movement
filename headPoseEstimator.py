import cv2
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import numpy as np
import matplotlib.pyplot as plt

from Rotation2Vector import RotationVector, SensitivityParams, rot2MouseVector
from MouseAction import Mouse

MODEL_PATH = "face_landmarker.task"
LEFT_EYE_LANDMARKS = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_LANDMARKS = [263, 387, 385, 362, 380, 373]
MAX_EYE_LANDMARK = max(max(LEFT_EYE_LANDMARKS), max(RIGHT_EYE_LANDMARKS)) + 1
EAR_THRESHOLD = 0.2  # Adjust based on testing

# Helper functions
#-------------------------------------------------------------------------------
def draw_landmarks_on_image(rgb_image, detection_result):
  face_landmarks_list = detection_result.face_landmarks
  annotated_image = np.copy(rgb_image)

  # Loop through the detected faces to visualize.
  for idx in range(len(face_landmarks_list)):
    face_landmarks = face_landmarks_list[idx]

    # Draw the face landmarks.
    face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    face_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in face_landmarks
    ])

    solutions.drawing_utils.draw_landmarks(
        image=annotated_image,
        landmark_list=face_landmarks_proto,
        connections=solutions.face_mesh.FACEMESH_TESSELATION,
        landmark_drawing_spec=None,
        connection_drawing_spec=solutions.drawing_styles
        .get_default_face_mesh_tesselation_style())
    solutions.drawing_utils.draw_landmarks(
        image=annotated_image,
        landmark_list=face_landmarks_proto,
        connections=solutions.face_mesh.FACEMESH_CONTOURS,
        landmark_drawing_spec=None,
        connection_drawing_spec=solutions.drawing_styles
        .get_default_face_mesh_contours_style())
    solutions.drawing_utils.draw_landmarks(
        image=annotated_image,
        landmark_list=face_landmarks_proto,
        connections=solutions.face_mesh.FACEMESH_IRISES,
          landmark_drawing_spec=None,
          connection_drawing_spec=solutions.drawing_styles
          .get_default_face_mesh_iris_connections_style())

  return annotated_image

def get_euler_angles(detection_result):
    matrices = detection_result.facial_transformation_matrixes
    if (matrices == None or len(matrices) == 0):
       return 0,0,0
    facial_transformation_matrix = detection_result.facial_transformation_matrixes[0]
    # Convert the 4x4 transformation matrix to a 3x3 rotation matrix
    rotation_matrix = np.array((facial_transformation_matrix).reshape(4, 4))[:3, :3]

    # Decompose the rotation matrix into Euler angles (roll, pitch, yaw)
    pitch, yaw, roll = cv2.RQDecomp3x3(rotation_matrix)[0]
    return roll, -pitch, yaw

def calculate_EAR(landmarks, eye_indices):
    """Compute the Eye Aspect Ratio (EAR) to detect blinking."""
    left_eye = np.array([[landmarks[i].x, landmarks[i].y] for i in eye_indices])

    # Vertical distances
    v1 = np.linalg.norm(left_eye[1] - left_eye[5])
    v2 = np.linalg.norm(left_eye[2] - left_eye[4])
    
    # Horizontal distance
    h = np.linalg.norm(left_eye[0] - left_eye[3])
    
    ear = (v1 + v2) / (2.0 * h)
    return ear

def avg_EAR(detection_result):
    landmarks = detection_result.face_landmarks
    if (landmarks == None or len(landmarks) < MAX_EYE_LANDMARK):
       return 10
    left_EAR = calculate_EAR(landmarks, LEFT_EYE_LANDMARKS)
    right_EAR = calculate_EAR(landmarks, RIGHT_EYE_LANDMARKS)
    return np.average(left_EAR, right_EAR)

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    print("Initialized camera")

    # Creating Face Landmarker Object
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.FaceLandmarkerOptions(base_options=base_options,
                                        output_face_blendshapes=True,
                                        output_facial_transformation_matrixes=True,
                                        num_faces=1)
    detector = vision.FaceLandmarker.create_from_options(options)
    print("Created Face landmarker")

    sensitivity = SensitivityParams(1, .05) # set sensitivity and deadzone
    mouse = Mouse()

    while cap.isOpened():
        success, img = cap.read()

        if not success:
           break
        mp_image = mp.Image(image_format= mp.ImageFormat.SRGB, data=cv2.flip(img, 1))

        start = time.time()

        detection_result = detector.detect(mp_image)
        roll, pitch, yaw = get_euler_angles(detection_result)
        rotation = RotationVector(roll, pitch, yaw)
        mouseVector = rot2MouseVector(rotation, sensitivity)
        mouse.moveCursor(mouseVector)
        # print(len(detection_result.face_landmarks))
        annotated_image = draw_landmarks_on_image(mp_image.numpy_view(), detection_result)
        cv2.imshow("test", annotated_image)
        if cv2.waitKey(1) == ord('q'):
            break
        
    cap.release()
    cv2.destroyAllWindows()