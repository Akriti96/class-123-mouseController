import cv2
import mediapipe as mp

import math
from pynput.mouse import Button,Controller
import pyautogui
# from pynput.keyboard import Key,Controller


state=None

mouse=Controller()

cap = cv2.VideoCapture(0)

drawing = mp.solutions.drawing_utils
hands = mp.solutions.hands

width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# print(width)
# print(height)
(screen_width,screen_height)=pyautogui.size()
# print(screen_width,screen_height)

hands_obj = hands.Hands(min_detection_confidence=0.75,
                        min_tracking_confidence=0.75,
                        max_num_hands=4)
pinch=False

def count_fingers(image,lst):
    global pinch
    cnt = 0

    thresh = (lst.landmark[0].y*100 - lst.landmark[9].y*100)/2

    if (lst.landmark[5].y*100 - lst.landmark[8].y*100) > thresh:
        cnt += 1

    if (lst.landmark[9].y*100 - lst.landmark[12].y*100) > thresh:
        cnt += 1

    if (lst.landmark[13].y*100 - lst.landmark[16].y*100) > thresh:
        cnt += 1

    if (lst.landmark[17].y*100 - lst.landmark[20].y*100) > thresh:
        cnt += 1

    if (lst.landmark[5].x*100 - lst.landmark[4].x*100) > 6:
        cnt += 1

    # line btw index and thumb line
    finger_tip_x=int(lst.landmark[8].x*width)
    finger_tip_y=int(lst.landmark[8].y*height)

    thumb_tip_x=int(lst.landmark[4].x*width)
    thumb_tip_y=int(lst.landmark[4].y*height)
    cv2.line(image, (finger_tip_x, finger_tip_y),(thumb_tip_x, thumb_tip_y),(255,0,0),2)

    # Draw a CIRCLE on CENTER of the LINE between FINGER TIP and THUMB TIP
    center_x = int((finger_tip_x + thumb_tip_x )/2)
    center_y = int((finger_tip_y + thumb_tip_y )/2)
    cv2.circle(image, (center_x, center_y), 2, (0,0,255), 2)

    # Calculate DISTANCE between FINGER TIP and THUMB TIP
    distance = math.sqrt(((finger_tip_x - thumb_tip_x)**2) + ((finger_tip_y - thumb_tip_y)**2))
    # print("Distance: ", distance)

    print("Computer Screen Size :",screen_width, screen_height, "Output Window size: ", width, height)
    print("Mouse Position: ", mouse.position, "Tips Line Centre Position: ", center_x, center_y)
    # Set Mouse Position on the Screen Relative to the Output Window Size	
    relative_mouse_x = (center_x/width)*screen_width
    relative_mouse_y = (center_y/height)*screen_height
    
    mouse.position = (relative_mouse_x, relative_mouse_y)

		# Check PINCH Formation Conditions
    if distance > 40:
        if pinch == True:
            pinch = False			
            mouse.release(Button.left)

    if distance <= 40 :
        if(pinch==False):
            pinch=True
            mouse.press(Button.left)

    
    

while True:
    success, image = cap.read()
    image = cv2.flip(image, 1)
    result = hands_obj.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if result.multi_hand_landmarks:

        hand_keyPoints = result.multi_hand_landmarks[0]

        c = count_fingers(image,hand_keyPoints)
        # print(c)
        cv2.putText(image, "pinch "+str(pinch), (200, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        drawing.draw_landmarks(image, hand_keyPoints, hands.HAND_CONNECTIONS)

    cv2.imshow("Media Controller", image)

    key = cv2.waitKey(1)
    if key == 27:
        break

cv2.destroyAllWindows()
