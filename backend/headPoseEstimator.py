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

#eye landmarks needed to calculate EAR
MODEL_PATH = "backend/face_landmarker.task"
# eye landmarks needed to calculate EAR
# Define eye landmarks
LEFT_EYE_LANDMARKS = {"top": 159, "bottom": 145, "outer": 133, "inner": 33}
RIGHT_EYE_LANDMARKS = {"top": 386, "bottom": 374, "outer": 362, "inner": 263}
NOSE_LANDMARKS = [168, 197, 2, 1, 0]
EAR_THRESHOLD = 0.25  # Adjust based on testing
EAR_THRESHOLD_GLASSES = 0.45

DEFAULT_SENSITIVITY = 1
DEFAULT_DEADZONE = 0.05
DEFAULT_CLICK_INTERVAL = 0.2

class HeadPoseEstimator:
    def __init__(self, sensitivity= DEFAULT_SENSITIVITY, deadzone = DEFAULT_DEADZONE, blinkInterval = DEFAULT_CLICK_INTERVAL):
        self.mouse = Mouse(click_interval= blinkInterval)
        self.sensitivity = SensitivityParams(sensitivity, deadzone) # set sensitivity and deadzone
        self.__init_model()

    def set_blink_interval(self, newInterval):
        self.mouse.setClickInterval(newInterval)

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
        display_img, glasses_detected = self.__detect_glasses(display_img, detection_result)
        if glasses_detected:
             ear_threshold = EAR_THRESHOLD_GLASSES
        else:
             ear_threshold = EAR_THRESHOLD
        display_img, blinked = self.__detect_blink(display_img, detection_result, blinkAnnot, ear_threshold)

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

	def detect_stick_through_nose_bridge(image, face_landmarks):
		h, w, _ = image.shape

		# Landmark 168 for nose bridge (upper part)
		nose_bridge_x = int(face_landmarks[168].x * w)
		nose_bridge_y = int(face_landmarks[168].y * h)

		# Define the region around landmark 168 (bounding box)
		region_top_left = (nose_bridge_x - 50, nose_bridge_y - 50)
		region_bottom_right = (nose_bridge_x + 50, nose_bridge_y + 50)
		cv2.rectangle(image, region_top_left, region_bottom_right, (0, 255, 0), 2)

		# Crop the region of interest around the nose bridge
		roi = image[region_top_left[1]:region_bottom_right[1], region_top_left[0]:region_bottom_right[0]]

		# Convert to grayscale and apply edge detection (Canny)
		gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
		edges = cv2.Canny(gray_roi, 50, 150)

		# Apply Hough Line Transform to detect lines
		lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=10)

		# Check if any vertical lines are detected
		if lines is not None:
			for line in lines:
				x1, y1, x2, y2 = line[0]
				# Calculate the angle of the line (vertical if angle is near 90 degrees)
				if abs(x1 - x2) < 10:  # Vertical line
					cv2.line(roi, (x1, y1), (x2, y2), (0, 0, 255), 3)
					cv2.putText(image, "Stick detected", (nose_bridge_x - 50, nose_bridge_y - 50),
								cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
					return True  # Stick detected in the region

		return False  # No stick detected

	# The main function for detecting glasses and stick detection
	def __detect_glasses(self, srgb_image, detection_result):
		face_landmarks_list = detection_result.face_landmarks
		annotated_image = np.copy(srgb_image)
		glasses_detected = False

		for face_landmarks in face_landmarks_list:
			h, w, _ = annotated_image.shape  # Image dimensions

			# Check for glasses based on eye and nose landmarks
			for idx in list(LEFT_EYE_LANDMARKS.values()) + list(RIGHT_EYE_LANDMARKS.values()) + NOSE_LANDMARKS:
				landmark = face_landmarks[idx]
				if landmark.x < 0.25 or landmark.x > 0.8:  # Example condition, adjust based on tests
					glasses_detected = True
					break

			# Stick detection (through nose bridge, landmark 168)
			if detect_stick_through_nose_bridge(annotated_image, face_landmarks.landmark) or glasses_detected:
				glasses_detected = True
                cv2.putText(annotated_image, "Glasses Detected", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

		return annotated_image, glasses_detected

    # Function to draw landmarks, lines, and EAR, detects blinks
    def __detect_blink(self, rgb_image, detection_result, draw_EAR, ear_threshold):
    def __detect_blink(self, rgb_image, detection_result, draw_EAR, ear_threshold):
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

            if draw_EAR:
                # Display EAR on the screen
                cv2.putText(annotated_image, f"EAR_LEFT: {left_ear:.2f}, EAR_RIGHT: {right_ear:.2f}", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

            left_blink = left_ear < ear_threshold
            right_blink = right_ear < ear_threshold
            left_blink = left_ear < ear_threshold
            right_blink = right_ear < ear_threshold

            if (left_blink and right_blink) and draw_EAR:
                # Blink detection message
                cv2.putText(annotated_image, "BLINKED BOTH EYES", (30, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            elif (right_blink) and draw_EAR:
                cv2.putText(annotated_image, "BLINKED RIGHT EYE", (annotated_image.shape[1] - 300, 90),
							cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            elif (left_blink) and draw_EAR:
                # Blink detection message
                cv2.putText(annotated_image, "BLINKED LEFT EYE", (30, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                blink = True

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

    def __detect_pupil(eye_image):
        gray_eye = cv2.cvtColor(eye_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray_eye, (5, 5), 0)
        circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=30,
                                   param1=50, param2=30, minRadius=10, maxRadius=50)

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            x, y, r = circles[0]
            return (x, y, r)
        return None

    def __extract_eye_region(face_landmarks, eye_landmarks, image):
        # Get bounding box coordinates for the eye region
        eye_coords = [face_landmarks[i] for i in eye_landmarks]
        x_coords = [coord[0] for coord in eye_coords]
        y_coords = [coord[1] for coord in eye_coords]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)

        # Crop the eye region
        eye_image = image[y_min:y_max, x_min:x_max]
        return eye_image

    def map_to_screen(x, y, eye_image, screen_width, screen_height):
        # Map coordinates from eye region to screen
        screen_x = np.interp(x, [0, eye_image.shape[1]], [0, screen_width])
        screen_y = np.interp(y, [0, eye_image.shape[0]], [0, screen_height])
        return screen_x, screen_y

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

    def __detect_glasses(self, srgb_image, detection_result):
        face_landmarks_list = detection_result.face_landmarks
        annotated_image = np.copy(srgb_image)
        glasses_detected = False

        for face_landmarks in face_landmarks_list:
            h, w, _ = annotated_image.shape  # Image dimensions
            for idx in list(LEFT_EYE_LANDMARKS.values()) + list(RIGHT_EYE_LANDMARKS.values()) + NOSE_LANDMARKS:
                landmark = face_landmarks[idx]
                if landmark.x < 0.25 or landmark.x > 0.8:  # Example condition, adjust based on tests
                    glasses_detected = True
                    break

            # Print result
            if glasses_detected:
                cv2.putText(annotated_image, "Glasses Detected", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        return annotated_image, glasses_detected

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
