import cv2
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import numpy as np

from backend.Rotation2Vector import RotationVector, SensitivityParams, rot2MouseVector
from backend.MouseAction import Mouse

MODEL_PATH = "face_landmarker.task"
# eye landmarks needed to calculate EAR
# Define eye landmarks
LEFT_EYE_LANDMARKS = {"top": 159, "bottom": 145, "outer": 133, "inner": 33}
RIGHT_EYE_LANDMARKS = {"top": 386, "bottom": 374, "outer": 362, "inner": 263}
EAR_THRESHOLD = 0.2  # Adjust based on testing

DEFAULT_SENSITIVITY = 1
DEFAULT_DEADZONE = 0.05

class HeadPoseEstimator:
    def __init__(self, sensitivity= DEFAULT_SENSITIVITY, deadzone = DEFAULT_DEADZONE):
        self.mouse = Mouse()
        self.sensitivity = SensitivityParams(sensitivity, deadzone) # set sensitivity and deadzone
        self.__init_model()

    def process_img(self, img, moveMouse= True, drawMask= True, blinkAnnot= True, displayAngle= True, verbose= False):
        mp_image = mp.Image(image_format= mp.ImageFormat.SRGB, data=cv2.flip(img, 1))
        detection_result = self.detector.detect(mp_image)
        roll, pitch, yaw = self.__get_euler_angles(detection_result)
        rotation = RotationVector(roll, pitch, yaw)
        if moveMouse:
            mouseVector = rot2MouseVector(rotation, self.sensitivity)
            self.mouse.moveCursor(mouseVector)
        display_img = mp_image.numpy_view()
        if drawMask:
            display_img = self.__draw_landmarks_on_image(display_img, detection_result)
        display_img, blinked = self.__detect_blink(display_img, detection_result, blinkAnnot)
        if blinked:
            self.mouse.registerClick()
        self.mouse.checkClick(verbose)
        return display_img

    def set_sensitivity_params(self, sensitivity, deadzone):
        self.sensitivity.sensitivity = sensitivity
        self.sensitivity.deadzone = min(1, deadzone)

    def __init_model(self):
        # Creating Face Landmarker Object
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.FaceLandmarkerOptions(base_options=base_options,
                                            output_face_blendshapes=True,
                                            output_facial_transformation_matrixes=True,
                                            num_faces=1)
        self.detector = vision.FaceLandmarker.create_from_options(options)

    def __draw_landmarks_on_image(self, rgb_image, detection_result):
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

    # Function to draw landmarks, lines, and EAR, detects blinks
    def __detect_blink(self, rgb_image, detection_result, draw_EAR):
        face_landmarks_list = detection_result.face_landmarks
        annotated_image = np.copy(rgb_image)
        blink = False

        for face_landmarks in face_landmarks_list:
            h, w, _ = annotated_image.shape  # Image dimensions

            if draw_EAR:
                for eye in [LEFT_EYE_LANDMARKS, RIGHT_EYE_LANDMARKS]:
                    # Get landmark coordinates
                    top = (int(face_landmarks[eye["top"]].x * w), int(face_landmarks[eye["top"]].y * h))
                    bottom = (int(face_landmarks[eye["bottom"]].x * w), int(face_landmarks[eye["bottom"]].y * h))
                    outer = (int(face_landmarks[eye["outer"]].x * w), int(face_landmarks[eye["outer"]].y * h))
                    inner = (int(face_landmarks[eye["inner"]].x * w), int(face_landmarks[eye["inner"]].y * h))

                    # Draw vertical line (green) - between top and bottom eyelid
                    cv2.line(annotated_image, top, bottom, (0, 255, 0), 2)

                    # Draw horizontal line (blue) - between inner and outer eye corners
                    cv2.line(annotated_image, inner, outer, (255, 0, 0), 2)

                    # Draw eye landmarks as yellow dots
                    for point in [top, bottom, outer, inner]:
                        cv2.circle(annotated_image, point, 4, (0, 255, 255), -1)

            # Compute and display EAR
            left_ear = self.__calculate_EAR(face_landmarks, LEFT_EYE_LANDMARKS)
            right_ear = self.__calculate_EAR(face_landmarks, RIGHT_EYE_LANDMARKS)
            avg_ear = (left_ear + right_ear) / 2

            if draw_EAR:
                # Display EAR on the screen
                cv2.putText(annotated_image, f"EAR: {avg_ear:.2f}", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

            blink = avg_ear < EAR_THRESHOLD

            if blink and draw_EAR:
                # Blink detection message
                cv2.putText(annotated_image, "BLINK DETECTED", (30, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        return annotated_image, blink

    def __get_euler_angles(self, detection_result):
        matrices = detection_result.facial_transformation_matrixes
        if (matrices == None or len(matrices) == 0):
            return 0,0,0
        facial_transformation_matrix = detection_result.facial_transformation_matrixes[0]
        # Convert the 4x4 transformation matrix to a 3x3 rotation matrix
        rotation_matrix = np.array((facial_transformation_matrix).reshape(4, 4))[:3, :3]

        # Decompose the rotation matrix into Euler angles (roll, pitch, yaw)
        pitch, yaw, roll = cv2.RQDecomp3x3(rotation_matrix)[0]
        return roll, -pitch, yaw

    # Function to compute EAR
    def __calculate_EAR(self, landmarks, eye):
        """Computes Eye Aspect Ratio (EAR)"""
        top = np.array([landmarks[eye["top"]].x, landmarks[eye["top"]].y])
        bottom = np.array([landmarks[eye["bottom"]].x, landmarks[eye["bottom"]].y])
        outer = np.array([landmarks[eye["outer"]].x, landmarks[eye["outer"]].y])
        inner = np.array([landmarks[eye["inner"]].x, landmarks[eye["inner"]].y])

        vertical_dist = np.linalg.norm(top - bottom)
        horizontal_dist = np.linalg.norm(outer - inner)

        ear = vertical_dist / horizontal_dist
        return ear

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    print("Initialized camera")

    tracker = HeadPoseEstimator()

    while cap.isOpened():
        success, img = cap.read()

        if not success:
           break
        
        img = tracker.process_img(img, verbose= True)

        cv2.imshow("test", img)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
