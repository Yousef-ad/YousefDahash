from Congestion_Estimation import*
from Ramp_Regulater import*
import cv2
import pandas as pd
from ultralytics import YOLO
import time
import math


class Tracker:
    def __init__(self):
        # Store the center positions of the objects
        self.center_points = {}
        # Keep the count of the IDs
        # each time a new object id detected, the count will increase by one
        self.id_count = 0


    def update(self, objects_rect):
        # Objects boxes and ids
        objects_bbs_ids = []

        # Get center point of new object
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2

            # Find out if that object was detected already
            same_object_detected = False
            for id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])
                if dist < 90: #110
                    self.center_points[id] = (cx, cy)
                    objects_bbs_ids.append([x, y, w, h, id])
                    same_object_detected = True
                    break

            # New object is detected we assign the ID to that object
            if same_object_detected is False:
                self.center_points[self.id_count] = (cx, cy)
                objects_bbs_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1

        # Clean the dictionary by center points to remove IDS not used anymore
        new_center_points = {}
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center

        # Update dictionary with IDs not used removed
        self.center_points = new_center_points.copy()
        return objects_bbs_ids


model = YOLO('yolov8n.pt' , verbose=False)

def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE :  
        colorsBGR = [x, y]
        print(colorsBGR)
        

cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', RGB)

cap=cv2.VideoCapture("Green3.mp4")

my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n") 

def video_processing(video_path):
    cap = cv2.VideoCapture(video_path)
    count = 0
    tracker = Tracker()
    cy1 = 347
    cy2 = 645
    offset = 35
    Vh_D = {}
    counter = []
    speeds = {}
    counts = {}
    last_reset_time = time.time()
    total_speed = 0.0
    total_count = 0
    average_speed = 0.0
    congestion_state="Null"
    interval_start_time = time.time()  # Timer for tracking 10-second intervals
    
    fps_start_time = 0
    fps = 0

    with open("speed_data.txt", "w") as speed_file:
        while True:
            
            ret, frame = cap.read()
            
            if not ret:
                break
            count += 1
            if count % 3 != 0:
                continue
            frame = cv2.resize(frame, (1080, 1300))  # Smaller resolution
            
            # Pre-Processing 
            normalized_frame = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX) 
            gray_frame = cv2.cvtColor(normalized_frame, cv2.COLOR_BGR2GRAY)
            equalized_frame = cv2.equalizeHist(gray_frame)  # Consider using equalizeHist
            preprocessed_frame = cv2.cvtColor(equalized_frame, cv2.COLOR_GRAY2BGR) 

            results = model.predict(preprocessed_frame,verbose=False, device='cpu')
            
            fps_end_time = time.time() 
            time_diff= fps_end_time - fps_start_time
            fps= 1/(time_diff)
            fps_start_time = fps_end_time
            fps_text = "FPS {:.2f}" .format(fps)
            cv2.putText(preprocessed_frame, fps_text, (5, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 1)
            
            a = results[0].boxes.data.cpu()  
            px = pd.DataFrame(a.numpy()).astype("float")  
            list = []
                         
            for index, row in px.iterrows():
                x1 = int(row[0])
                y1 = int(row[1])
                x2 = int(row[2])
                y2 = int(row[3])
                d = int(row[5])
                c = class_list[d]
                if 'car' in c:
                    list.append([x1, y1, x2, y2])
            bbox_id = tracker.update(list)
            for bbox in bbox_id:
                x3, y3, x4, y4, id = bbox
                cx = int(x3 + x4) // 2
                cy = int(y3 + y4) // 2
                
                cv2.circle(preprocessed_frame, (cx, cy), 4, (0, 0, 255), -1)
                cv2.putText(preprocessed_frame, str(id), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
                if cy2 < (cy + offset) and cy2 > (cy - offset):
                    cv2.circle(preprocessed_frame, (cx, cy), 8, (0, 0, 255), -1)
    
                if cy1 < (cy + offset) and cy1 > (cy - offset) and cx > 342:
                    cv2.circle(preprocessed_frame, (cx, cy), 8, (0, 0, 255), -1)
                    Vh_D[id] = time.time()
                if id in Vh_D:
                    if cy2 < (cy + offset) and cy2 > (cy - offset):
                        elapsed_time = time.time() - Vh_D[id]
                        if counter.count(id) == 0:
                            counter.append(id)
                            if elapsed_time != 0:  # Check if elapsed_time is not zero
                                distance = 25
                                speed_ms = distance / elapsed_time
                                speed_km = speed_ms * 3.6
                                # Write speed to file
                                speed_file.write(f"{speed_km}\n")
                                
                                cv2.circle(preprocessed_frame, (cx, cy), 4, (0, 0, 255), -1)
                                cv2.putText(preprocessed_frame, str(id), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
                                cv2.putText(preprocessed_frame, str(int(speed_km))+"speed", (x4, y4), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
                                
                                if id not in speeds:
                                    speeds[id] = 0
                                    counts[id] = 0
    
                                speeds[id] += speed_km
                                counts[id] += 1
                                total_speed += speed_km
                                total_count += 1
                                
            # Reset the speeds and counts dictionaries
            current_time = time.time()
            if current_time - last_reset_time >= 30:  
                break

                
            # Calculate average speed for all vehicles combined
            total_speed = sum(speeds.values())
            total_count = sum(counts.values())
            average_speed = total_speed / total_count if total_count > 0 else 0.0
            
            formatted_average = f"Avg: {average_speed:.2f}"     
            cv2.putText(preprocessed_frame, formatted_average, (180,30), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
            
            #Show the state on screen
            if congestion_state == "State 1":
                cv2.putText(preprocessed_frame, ('Congestion State: ')+(congestion_state), (5,60), cv2.FONT_HERSHEY_COMPLEX, 0.8, (6, 6, 145), 2)
            elif congestion_state == "State 2":
                cv2.putText(preprocessed_frame, ('Congestion State: ')+(congestion_state), (5,60), cv2.FONT_HERSHEY_COMPLEX, 0.8, (9, 66, 181), 2)
            elif congestion_state == "State 3":
                cv2.putText(preprocessed_frame, ('Congestion State: ')+(congestion_state), (5,60), cv2.FONT_HERSHEY_COMPLEX, 0.8, (9, 106, 181), 2)
            elif congestion_state == "State 4":
                cv2.putText(preprocessed_frame, ('Congestion State: ')+(congestion_state), (5,60), cv2.FONT_HERSHEY_COMPLEX, 0.8, (86, 255, 255), 2)
            elif congestion_state == "State 5":
                cv2.putText(preprocessed_frame, ('Congestion State: ')+(congestion_state), (5,60), cv2.FONT_HERSHEY_COMPLEX, 0.8, (12, 235, 16), 2)

            #cv2.putText(frame, ('Time is:')+str(interval_start_time), (60,99), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
            cv2.line(preprocessed_frame,(820,cy1),(128,cy1),(255,255,255),1)
            cv2.line(preprocessed_frame,(987,cy2),(33,cy2),(255,255,255),1)
            cv2.imshow("RGB", preprocessed_frame)
            
            
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            if key == ord('p'):  # Update remaining time
                cv2.waitKey(-1) #wait until any key is pressed


    cap.release()
    cv2.destroyAllWindows()
    return speeds
