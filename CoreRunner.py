from core.pyimagesearch.centroidtracker import CentroidTracker
from core.pyimagesearch.trackableobject import TrackableObject
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
from core import config
import datetime
from sklearn.linear_model import LinearRegression
import requests
import os

class CoreRunner(object):

    def __init__(self, user_id, line_id, rtsp_url, x1, y1, x2, y2):
        ## line id is enough to be unique so just edit by line id if the url and position change in pickle file
        self.user_id = user_id
        self.line_id = line_id
        self.rtsp_url = rtsp_url
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.still_continue = None

    def __str__(self):
        string = u'[<CoreRunner> user_id:%s line_id:%s rtsp_url:%s x1:%s]' %(self.user_id, self.line_id, self.rtsp_url, self.x1)
        return string

    def _url(self,path):
        return 'http://0.0.0.0:5000' + path

    def postEvent(self, in_out, dateandtime):
        data = {'time_stamp': dateandtime, 'event': in_out}
        r = requests.get(url=self._url('/get_event/' + self.line_id + '/' + in_out + '/' + dateandtime))
        return r.status_code, r.text

    def start(self):
        self.still_continue = True
        # num = 0

        with open("app/main/status_line/" + self.line_id + ".txt", "w") as file:
            file.write("1")
        file.close()

        CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                   "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                   "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                   "sofa", "train", "tvmonitor"]

        # load our serialized model from disk
        print("[INFO] loading model...")
        net = cv2.dnn.readNetFromCaffe('core/mobilenet_ssd/MobileNetSSD_deploy.prototxt',
                                       'core/mobilenet_ssd/MobileNetSSD_deploy.caffemodel')

        vs = cv2.VideoCapture()
        vs.open(self.rtsp_url)

        fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # codec for video
        out1 = cv2.VideoWriter('output1.avi', fourcc, 20, (300, 300))  # Output object
        out2 = cv2.VideoWriter('output2.avi', fourcc, 20, (300, 300))  # Output object

        W = None
        H = None

        ct = CentroidTracker(maxDisappeared=100, maxDistance=100)
        trackers = []
        trackableObjects = {}

        totalFrames = 0
        totalDown = 0
        totalUp = 0

        rtsp_split = self.rtsp_url.split("/")
        channel = rtsp_split[len(rtsp_split)-1]

        while self.still_continue:
            with open("app/main/status_line/" + self.line_id + ".txt", "r") as mytxt:
                for line in mytxt:
                    status_line = int(line)
            mytxt.close()
            if status_line == 0:
                break
            # if num % 20000 == 0:
            #     print(self.__str__() + " still continue ")
            # num = num + 1

            ret, frame = vs.read()

            if frame is None:
                # print("frame is none")
                continue

            if(channel == '201'):
                position = config.detection_area['201-half']
                x = position['x']
                y = position['y']
                w = position['w']
                h = position['h']

                frame = frame[y:y + h, x:x + w]
                frame = cv2.resize(frame, (300, 300))
                # out1.write(frame)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                if W is None or H is None:
                    (H, W) = frame.shape[:2]
                    detection_line_height = 210

            else:
                frame = cv2.resize(frame, (300, 300))
                # out1.write(frame)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                if W is None or H is None:
                    (H, W) = frame.shape[:2]
                    detection_line_height = int((int(self.y1) + int(self.y2)) / 2)  # 210

            status = "Waiting"
            rects = []

            if totalFrames % 10 == 0:
                # set the status and initialize our new set of object trackers
                status = "Detecting"
                trackers = []

                # convert the frame to a blob and pass the blob through the
                # network and obtain the detections
                blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
                net.setInput(blob)
                detections = net.forward()

                # loop over the detections
                for i in np.arange(0, detections.shape[2]):
                    # extract the confidence (i.e., probability) associated
                    # with the prediction
                    confidence = detections[0, 0, i, 2]

                    # filter out weak detections by requiring a minimum
                    # confidence
                    if confidence > 0.4:
                        # extract the index of the class label from the
                        # detections list
                        idx = int(detections[0, 0, i, 1])

                        # if the class label is not a person, ignore it
                        if CLASSES[idx] != "person":
                            continue

                        # compute the (x, y)-coordinates of the bounding box
                        # for the object
                        box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                        (startX, startY, endX, endY) = box.astype("int")

                        # construct a dlib rectangle object from the bounding
                        # box coordinates and then start the dlib correlation
                        # tracker
                        tracker = dlib.correlation_tracker()
                        rect = dlib.rectangle(startX, startY, endX, endY)
                        tracker.start_track(rgb, rect)

                        # add the tracker to our list of trackers so we can
                        # utilize it during skip frames
                        trackers.append(tracker)

            # otherwise, we should utilize our object *trackers* rather than
            # object *detectors* to obtain a higher frame processing throughput
            else:
                # print('trackers', trackers)
                # loop over the trackers
                for tracker in trackers:
                    # set the status of our system to be 'tracking' rather
                    # than 'waiting' or 'detecting'
                    status = "Tracking"

                    # update the tracker and grab the updated position
                    tracker.update(rgb)
                    pos = tracker.get_position()

                    # unpack the position object
                    startX = int(pos.left())
                    startY = int(pos.top())
                    endX = int(pos.right())
                    endY = int(pos.bottom())
                    cv2.rectangle(frame, (startX, startY), (endX, endY), (255, 0, 0), 3)
                    # add the bounding box coordinates to the rectangles list
                    rects.append((startX, startY, endX, endY))

            # draw a horizontal line in the center of the frame -- once an
            # object crosses this line we will determine whether they were
            # moving 'up' or 'down'
            cv2.line(frame, (0, detection_line_height), (W, detection_line_height), (0, 255, 255), 2)

            # use the centroid tracker to associate the (1) old object
            # centroids with (2) the newly computed object centroids
            objects = ct.update(rects)
            # loop over the tracked objects
            for (objectID, centroid) in objects.items():
                # check to see if a trackable object exists for the current
                # object ID
                to = trackableObjects.get(objectID, None)

                # if there is no existing trackable object, create one
                if to is None:
                    to = TrackableObject(objectID, centroid)

                # otherwise, there is a trackable object so we can utilize it
                # to determine direction
                else:
                    # the difference between the y-coordinate of the *current*
                    # centroid and the mean of *previous* centroids will tell
                    # us in which direction the object is moving (negative for
                    # 'up' and positive for 'down')
                    y = [c[1] for c in to.centroids]
                    direction = float(centroid[1] - np.mean(y))
                    to.centroids.append(centroid)

                    # check to see if the object has been counted or not
                    if not to.counted and len(y) > 19:
                        # if the direction is negative (indicating the object
                        # is moving up) AND the centroid is above the center
                        # line, count the object
                        x_train = np.array([i + 1 for i in range(len(y))]).reshape(-1, 1)
                        y_train = np.array(y).reshape(-1, 1)
                        reg = LinearRegression().fit(x_train, y_train)

                        # isUp = ((direction < 0) and (centroid[1] < detection_line_height))
                        # isDown = ((direction > 0) and (centroid[1] > detection_line_height))
                        pred_first_y = reg.predict(np.array([0]).reshape(-1, 1))
                        pred_last_y = reg.predict(np.array([len(y) - 1]).reshape(-1, 1))
                        isUp = reg.coef_ < 0 and pred_first_y > detection_line_height and pred_last_y < detection_line_height
                        isDown = reg.coef_ >= 0 and pred_first_y < detection_line_height and pred_last_y > detection_line_height

                        # print('isDown', isDown)

                        if isUp:
                            totalUp += 1
                            datetimeString = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            dateString = datetime.datetime.now().strftime("%Y-%m-%d")
                            self.postEvent('out',datetimeString)
                            cv2.imwrite('FirstAndLastPersonOut/' + datetimeString + '.png', frame)
                            print(dateString)
                            to.counted = True

                        # if the direction is positive (indicating the object
                        # is moving down) AND the centroid is below the
                        # center line, cout the object
                        elif isDown:
                            totalDown += 1
                            datetimeString = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            dateString = datetime.datetime.now().strftime("%Y-%m-%d")
                            self.postEvent('in', datetimeString)
                            cv2.imwrite('FirstAndLastPersonIn/'  + datetimeString + '.png', frame)
                            print(dateString)
                            to.counted = True

                # store the trackable object in our dictionary
                trackableObjects[objectID] = to

                # draw both the ID of the object and the centroid of the object on the output frame
                # text = "ID {}".format(objectID)
                # cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                # cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

            # construct a tuple of information we will be displaying on the
            # frame
            info = [
                ("Up", totalUp),
                ("Down", totalDown),
                ("Status", status),
            ]

            # loop over the info tuples and draw them on our frame
            # for (i, (k, v)) in enumerate(info):
            #     text = "{}: {}".format(k, v)
            #     cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
            #                 cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # show the output frame
            # cv2.imshow("Frame", frame)
            # key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            # if key == ord("q"):
            #     break

            # out2.write(frame)
            # increment the total number of frames processed thus far and
            # then update the FPS counter
            totalFrames += 1

        print("stop")
        print(totalUp, totalDown, totalFrames)

        cv2.destroyAllWindows()

        if out1 is not None:
            out1.release()
        #
        if out2 is not None:
            out2.release()

        self.still_continue = False
        with open("app/main/status_line/" + self.line_id + ".txt", "w") as file:
            file.write("0")

    def stop(self):
        print("stop")
        self.still_continue = False
        with open("app/main/status_line/" + self.line_id + ".txt", "w") as file:
            file.write("0")
        file.close()