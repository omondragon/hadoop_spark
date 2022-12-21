#!/usr/bin/python3

"""
Distributed System for Vehicular Traffic Analysis (2018)
Authors:
Kevin Sebastián Arce Millán
Ian Steban Vasco Alzate
Oscar Hernán Mondragón Martínez
Juan Carlos Perafán Villota
"""

import numpy.core.multiarray

import cv2
import time
import uuid
import math

import numpy as np

import os
import sys

os.environ["PYSPARK_PYTHON"] = "python3"
os.environ['PYTHONPATH'] = ':'.join(sys.path)

print("Python Version: ", sys.version)

#import hdfs
#from hdfs.client import InsecureClient
import pyspark
from pyspark import SparkContext
conf = pyspark.SparkConf()


WAIT_TIME = 1

#master_url = 'http://192.168.200.3:9870'

DIVIDER = (255, 255, 0)
BOX_COLOR = (255, 0, 0)
CENTRO_COLOR = (0, 0, 255)


COLOURS = [(0, 0, 255), (0, 106, 255), (0, 216, 255), (0, 255, 182),
           (0, 255, 76), (144, 255, 0), (255, 255, 0), (255, 148, 0),
           (255, 0, 178), (220, 0, 255)]


def main():
    
    path="../media/corto30s3.mov" 
    process_image(path)


class Vehicle(object):
    def __init__(self, id, position, first_frame):
        self.id = id
        self.positions = [position]
        self.first_frame = first_frame
        self.frames_since_seen = 0
        self.counted = False

    @property
    def last_position(self):
        return self.positions[-1]

    def add_position(self, new_position):
        self.positions.append(new_position)
        self.frames_since_seen = 0

    def draw(self, output_image):
        car_colour = COLOURS[self.id % len(COLOURS)]
        for point in self.positions:
            cv2.circle(output_image, point, 2, car_colour, -1)
            cv2.polylines(output_image, [np.int32(self.positions)],
                          False, car_colour, 1)


class VehicleCounter(object):
    def __init__(self, shape, divider, starter, vertical):

        self.height, self.width = shape
        self.divider = divider
        self.starter = starter
        self.vertical_div = vertical
        self.vehicles = []
        self.next_vehicle_id = 0
        self.vehicle_count = 0
        self.max_unseen_frames = 7
        self.delta = 12.0/(divider - starter)


    @staticmethod
    def get_vector(a, b):
        """Calculate vector (distance, angle in degrees) from point a to point b.

        Angle ranges from -180 to 180 degrees.
        Vector with angle 0 points straight down on the image.
        Values increase in clockwise direction.
        """
        dx = float(b[0] - a[0])
        dy = float(b[1] - a[1])

        distance = math.sqrt(dx**2 + dy**2)

        if dy > 0:
            angle = math.degrees(math.atan(-dx/dy))
        elif dy == 0:
            if dx < 0:
                angle = 90.0
            elif dx > 0:
                angle = -90.0
            else:
                angle = 0.0
        else:
            if dx < 0:
                angle = 180 - math.degrees(math.atan(dx/dy))
            elif dx > 0:
                angle = -180 - math.degrees(math.atan(dx/dy))
            else:
                angle = 180.0  

        return distance, angle 


    @staticmethod
    def is_valid_vector(a):
        distance, angle = a
        CALC = -0.008 * angle**2 + 0.4 * angle + 25.0
        threshold_distance = max(10.0, CALC)
        return distance <= threshold_distance

    def update_vehicle(self, vehicle, matches):
        # Find if any of the matches fits this vehicle
        for i, match in enumerate(matches):
            contour, centroid = match

            vector = self.get_vector(vehicle.last_position, centroid)
            if self.is_valid_vector(vector):
                vehicle.add_position(centroid)
                return i

        # No matches fit...
        vehicle.frames_since_seen += 1

        return None

    def verify_match(self, match):
        """
        This method verifies that the car is between the two lines
        """
        _, centroid = match
        y_ = centroid[1]
        x_ = centroid[0]
        if y_ >= self.starter and y_ < self.divider and x_ <= self.vertical_div:
            return True
        return False

    def update_count(self, matches, frame_number, output_image=None, dseg=1):
        k = [x for x in matches if self.verify_match(x)]
        matches = k
        # First update all the existing vehicles
        for vehicle in self.vehicles:
            i = self.update_vehicle(vehicle, matches)
            if i is not None:
                del matches[i]

        # Add new vehicles based on the remaining matches
        for match in matches:
            contour, centroid = match
            new_vehicle = Vehicle(self.next_vehicle_id, centroid, frame_number)
            self.next_vehicle_id += 1
            self.vehicles.append(new_vehicle)

        # Count any uncounted vehicles that are past the divider
        for vehicle in self.vehicles:
            last_y = vehicle.last_position[1]
            if (not vehicle.counted and
               (last_y >= self.divider - 20)):
                self.vehicle_count += 1
                print("CONTANDO", self.vehicle_count)
                seg = ((frame_number - vehicle.first_frame) / 30.0) * dseg
                if seg > 0:
                    distance_ = self.divider - vehicle.positions[0][1]
                    distance = distance_ * self.delta
                    speed = (distance/1000) / (seg/(60*60))
                    print('SPEED', speed, 'SEG', seg)
                vehicle.counted = True

        # Optionally draw the vehicles on an image
        if output_image is not None:
            for vehicle in self.vehicles:
                vehicle.draw(output_image)

            cv2.putText(output_image, ("%02d" % self.vehicle_count), (142, 40),
                        cv2.FONT_HERSHEY_PLAIN, 3, (127, 255, 255), 1)

        self.vehicles[:] = [v for v in self.vehicles
                            if not v.frames_since_seen >= self.max_unseen_frames]



def get_centroid(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)

    cx = x + x1
    cy = y + y1

    return (cx, cy)


def detect_vehicles(fg_mask):
    MIN_CONTOUR_WIDTH = 50
    MIN_CONTOUR_HEIGHT = 50

    # Buscar los contornos
    #_, contours, _ = cv2.findContours(
    #                    fg_mask,
    #                    cv2.RETR_TREE,
    #                    cv2.CHAIN_APPROX_SIMPLE)

    contours, _ = cv2.findContours(
                        fg_mask,
                        cv2.RETR_TREE,
                        cv2.CHAIN_APPROX_SIMPLE)

    matches = []
    i = 0
    for i, contour in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)
        contour_valid = (w >= MIN_CONTOUR_WIDTH) and (h >= MIN_CONTOUR_HEIGHT)

       # cv2.rectangle(fg_mask, (x, y), (x + w - 1, y + h - 1), (255,255,255), -1)

        if not contour_valid:
            continue

        centroid = get_centroid(x, y, w, h)

        matches.append(((x, y, w, h), centroid))

    return matches


def filter_mask(fg_mask):
    #gray = cv2.cvtColor(fg_mask, cv2.COLOR_BGR2GRAY)
    fram1o = cv2.GaussianBlur(fg_mask, (7,7), 0)
    ret,th1 = cv2.threshold(fram1o,127,255,cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # Fill any small holes
    #closing = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    # Remove noise
    #opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)

    # Dilate to merge adjacent blobs
    dilation = cv2.dilate(th1, kernel, iterations=4)

    #added
    new = cv2.erode(dilation, kernel, iterations=3)

    closing = cv2.morphologyEx(new, cv2.MORPH_CLOSE, kernel)
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
    
    return opening


def process_frame(frame_number, frame, bg_subtractor, car_counter, dseg):
    processed = frame.copy()

    # linea  donde se inicia la recoleccion
    cv2.line(processed,
             (0, car_counter.starter),
             (frame.shape[1], car_counter.starter),
             DIVIDER, 1)

    # linea donde finaliza la recoleccion
    cv2.line(processed,
             (0, car_counter.divider),
             (frame.shape[1], car_counter.divider),
             DIVIDER, 1)

   # cv2.line(processed,
    #         (car_counter.vertical_div, 0),
     #        (car_counter.vertical_div, frame.shape[1]),
      #       DIVIDER, 1)

    # Remove the background
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    fg_mask = bg_subtractor.apply(gray, None, 0.1)
    fg_mask = filter_mask(fg_mask)

    matches = detect_vehicles(fg_mask)

    for (i, match) in enumerate(matches):
        contour, centroid = match

        x, y, w, h = contour

        # Mostrar el match
        cv2.rectangle(processed,
                      (x, y),
                      (x + w - 1, y + h - 1),
                      BOX_COLOR, 1)

        cv2.circle(processed, centroid, 2, CENTRO_COLOR, -1)

    car_counter.update_count(matches, frame_number, processed, dseg)

    return processed


def process_image(path):

    print("Process image")
    bg_subtractor = cv2.bgsegm.createBackgroundSubtractorMOG(500, 7, 0.4)
    #client = InsecureClient(master_url, user='hadoop')
    random_ = str(uuid.uuid1())
    random = '/tmp/ori-{}.mov'.format(random_)
    #client.download(path, random)

    #Agregado para Test
    random = path

    save = '/tmp/rs-{}.avi'.format(random_)


    print("****** PRINTING RANDOM ******")
    print(random)
    print(save)	


    # se inicia en None luego se crea en el primer frame
    # Cual es la razon para hacer esto?... Esto causa problemas cuando no hay conteo (videos pequeños)    
    counter = None
    
    time1 = time.time()
    diff = 1

    # Set up image source
    cap = cv2.VideoCapture(random)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    #640 x 480 original pero pruebas con 360
    out = cv2.VideoWriter(save, fourcc, 30.0, (640,480))

    frame_number = -1
    while True:
        frame_number += 1
        ret, frame = cap.read()

        if frame_number % 30 == 0 and frame_number > 0:
            time2 = time.time()
            diff = time2 - time1
            time1 = time2

        if not ret:
            break

        if counter is None:
            div = frame.shape[0] - 140
            counter = VehicleCounter(frame.shape[:2], div, div-190,
                                         frame.shape[0]/2 + 60)

        processed = process_frame(frame_number, frame,
                                  bg_subtractor, counter,
                                  diff)

        out.write(processed)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    #k = open(save,'rb')
    #client.write('results/{}.avi'.format(random_), k)
    #k.close()

    #Remove all files in /tmp	
    remove_files()    

    print("**************** Numero de vehiculos  *********************** "+str(counter.vehicle_count))
    return counter.vehicle_count


def remove_files():
	dir_name= "/tmp/"
	extensions = [".mov", ".avi"]

	test = os.listdir(dir_name)

	for e in extensions:
		for item in test:
			if item.endswith(e):
				os.remove(os.path.join(dir_name,item))


if __name__ == "__main__":
    main()
