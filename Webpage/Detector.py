import numpy as np
import time
import sys
import cv2
from pygame import mixer 
from math import pow, sqrt

path_model = './../SSD_MobileNet.caffemodel'
path_prototxt = './../SSD_MobileNet_prototxt.txt'
path_label = './../class_labels.txt'
################################################################################################################################
confidence_req = 0.8      ##### Minimum confidence for human detection #####
h_source = 11             #####      Acutal length of reference        #####
h_target = 28             #####      Acutal length of Target           #####
F = 800                   #####      Focal length of camera            #####
################################################################################################################################

# Reading Labels for network
labels = [line.strip() for line in open(path_label)]
bounding_box_color = np.random.uniform(0, 255, size=(len(labels), 3))

# Loading Netowork
network = cv2.dnn.readNetFromCaffe(path_prototxt, path_model)

def alert():
    # Starting the mixer 
    mixer.init() 

    # Loading the song 
    mixer.music.load('./../Alarm.mp3') 

    # Setting the volume 
    mixer.music.set_volume(0.7) 

    # Start playing the song 
    mixer.music.play() 
    
    # Sleep for 5 second
    time.sleep(5)
    
    #Pause the sound and close the mixer
    mixer.music.pause()
    mixer.music.stop()
    return

def detect(pri = False,dis = True):
    cap = cv2.VideoCapture(0)

    frame_no = 0
    first = True
    source = 0

    while cap.isOpened():

        frame_no = frame_no+1

        # Capture one frame after another
        ret, frame = cap.read()

        frame = cv2.flip(frame, 1)

        if not ret:
            break

        (h, w) = frame.shape[:2]

        # Resize the frame to suite the model requirements. Resize the frame to 300X300 pixels
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

        network.setInput(blob)
        detections = network.forward()

        pos_dict = dict()
        coordinates = dict()

        for i in range(detections.shape[2]):

            confidence = detections[0, 0, i, 2]

            if confidence > confidence_req:

                class_id = int(detections[0, 0, i, 1])

                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype('int')

                # Filtering only persons detected in the frame. Class Id of 'person' is 15
                if class_id == 15.00:
                    
                    if dis:
                        # Draw bounding box for the object
                        cv2.rectangle(frame, (startX, startY), (endX, endY), bounding_box_color[class_id], 2)
                    
                    label = "{}: {:.2f}%".format(labels[class_id], confidence * 100)
                    if pri:
                        print("{}".format(label))


                    coordinates[i] = (startX, startY, endX, endY)

                    # Mid point of bounding box
                    x_mid = round((startX+endX)/2,4)
                    y_mid = round((startY+endY)/2,4)

                    height = round(endY-startY,4)
                    # Distance from camera based on triangle similarity
                    
                    # For Source
                    if first:
                        distance = (h_source * F)/height
                        first = False
                        if pri:
                            print("Distance from camera(cm):{dist}\n".format(dist=distance))

                        # Mid-point of bounding boxes (in cm) based on triangle similarity technique
                        x_mid_cm = (x_mid * distance) / F
                        y_mid_cm = (y_mid * distance) / F
                        source = (x_mid_cm,y_mid_cm,distance)
                        
                    # For Targets
                    else:
                        distance = (h_target * F)/height
                        if pri:
                            print("Distance from camera(cm):{dist}\n".format(dist=distance))

                        # Mid-point of bounding boxes (in cm) based on triangle similarity technique
                        x_mid_cm = (x_mid * distance) / F
                        y_mid_cm = (y_mid * distance) / F
                        pos_dict[i] = (x_mid_cm,y_mid_cm,distance)

        # Distance between Source and every Target detected in a frame
        close_objects = set()
        for i in pos_dict.keys():
            
            dist = sqrt(pow(abs(pos_dict[i][0]-source[0]),2) + pow(abs(pos_dict[i][1]-source[1]),2) + pow(abs(pos_dict[i][2]-source[2]),2))
            
            COLOR = (0,255,0)
            if pri:
                print(dist)
            if dist <= 50:
                close_objects.add(i)
                COLOR = (0,0,255)
            if dis:
                cv2.putText(frame, 'Distance from source: {i} cm'.format(i=round(dist,4)), (startX, startY+200),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR, 2)
                
        # Check if any Target is too close to the Source
        if len(close_objects) > 1:
            alert()
        if dis:
            for i in pos_dict.keys():

                if i in close_objects:
                    COLOR = (0,0,255)
                else:
                    COLOR = (0,255,0)
                (startX, startY, endX, endY) = coordinates[i]

                cv2.rectangle(frame, (startX, startY), (endX, endY), COLOR, 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                # Convert cms to feet
                cv2.putText(frame, 'Distance from camera: {i} cm'.format(i=round(pos_dict[i][2],4)), (startX, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR, 2)

            cv2.namedWindow('Frame',cv2.WINDOW_NORMAL)

            # Show frame
            cv2.imshow('Frame', frame)
            cv2.resizeWindow('Frame',800,600)

            key = cv2.waitKey(1) & 0xFF

            # Press `q` to exit
            if key == ord("q"):
                break
    if dis:
        # Clean
        cap.release()
        cv2.destroyAllWindows()