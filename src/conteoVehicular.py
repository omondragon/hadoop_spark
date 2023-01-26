import cv2
import numpy as np

import time
import uuid
import math
import os

import hdfs
from hdfs.client import InsecureClient
import pyspark
from pyspark import SparkContext
conf = pyspark.SparkConf()

master_url = 'http://192.168.200.3:9870'

min_contour_width = 40
min_contour_height = 40
offset = 2
line_height = 240
matches = []


def remove_files():
	dir_name= "/tmp/"
	extensions = [".mov", ".avi"]

	test = os.listdir(dir_name)

	for e in extensions:
		for item in test:
			if item.endswith(e):
				os.remove(os.path.join(dir_name,item))

def get_centrolid(x, y, w, h):
   x1 = int(w / 2)
   y1 = int(h / 2)

   cx = x + x1
   cy = y + y1
   return cx, cy

# process_image function based on code available at:
# https://python.plainenglish.io/vehicle-detection-and-counting-project-opencv-python-4f8a17f1aa30
def process_image(path):

    cars = 0

    print("Process image")
    client = InsecureClient(master_url, user='hadoop')
    random_ = str(uuid.uuid1())
    random = '/tmp/ori-{}.mov'.format(random_)
    client.download(path, random)

    save = '/tmp/rs-{}.avi'.format(random_)

    print("****** PRINTING RANDOM ******")
    print(random)
    print(save)	


    # Set up image source
    cap = cv2.VideoCapture(random)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(save, fourcc, 30.0, (640,480))

    cap.set(3, 1920)
    cap.set(4, 1080)

    if cap.isOpened():
        ret, frame1 = cap.read()
    else:
        ret = False
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()

    while ret:
        d = cv2.absdiff(frame1, frame2)
        grey = cv2.cvtColor(d, cv2.COLOR_BGR2GRAY)

        blur = cv2.GaussianBlur(grey, (5, 5), 0)

        ret, th = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(th, np.ones((3, 3)))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))


        closing = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)
        contours, h = cv2.findContours(
        closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for(i, c) in enumerate(contours):
            (x, y, w, h) = cv2.boundingRect(c)
            contour_valid = (w >= min_contour_width) and (
                h >= min_contour_height)

            if not contour_valid:
                continue
            cv2.rectangle(frame1, (x-10, y-10), (x+w+10, y+h+10), (255, 0, 0), 2)

            cv2.line(frame1, (0, line_height), (1200, line_height), (0, 255, 0), 2)
            centrolid = get_centrolid(x, y, w, h)
            matches.append(centrolid)
            cv2.circle(frame1, centrolid, 5, (0, 255, 0), -1)
            cx, cy = get_centrolid(x, y, w, h)
            for (x, y) in matches:
                if y < (line_height+offset) and y > (line_height-offset):
                    cars = cars+1
                    matches.remove((x, y))
                    print(cars)

        cv2.putText(frame1, "Total Cars Detected: " + str(cars), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1,
               (0, 170, 0), 2)


        out.write(frame1)
        out.write(th)
        if cv2.waitKey(1) == 27:
            break
        frame1 = frame2
        ret, frame2 = cap.read()

    cv2.destroyAllWindows()
    cap.release()

    #Remove video files from /tmp
    #remove_files()

    return cars

def main():

    # To run local on one of the working nodes: (spark-submit in client mode)
    #sc = SparkContext('local', appName="hadoop")

    sc = SparkContext(appName="hadoop")
    client = InsecureClient(master_url, user='hadoop')
    paths = client.list('vids')
    filepaths = ['vids/{}'.format(x) for x in paths]

    print("filepaths", filepaths)
    results = sc.parallelize(filepaths, 2).map(process_image).sum()

    print(results, type(results))

if __name__ == "__main__":
    main()