import pickle
import cv2
import numpy as np
from shapely.geometry import Polygon as shapely_poly
from b_Model import model
import mrcnn.config
import mrcnn.utils
#from mrcnn.model import MaskRCNN




class c_Detector_2():
    def __init__(self, model):
        self.model = model

    def getModel(self):
        return self.model

    def setModel(self, model):
        self.model = model

    def get_car_boxes(self, boxes, class_ids):
        car_boxes = []

        for i, box in enumerate(boxes):
            #12, 68
            #bicycle, car, motorcycle, airplane, bus, train, truck, boat
            if class_ids[i] in [3, 4, 5, 6, 7, 8, 9, 10, 13, 68]:
                car_boxes.append(box)
        return np.array(car_boxes)

    def compute_overlaps(self, parked_car_boxes, car_boxes):
        new_car_boxes = []
        for box in car_boxes:
            y1 = box[0]
            x1 = box[1]
            y2 = box[2]
            x2 = box[3]

            p1 = (x1, y1)
            p2 = (x2, y1)
            p3 = (x2, y2)
            p4 = (x1, y2)
            new_car_boxes.append([p1, p2, p3, p4])

        overlaps = np.zeros((len(parked_car_boxes), len(new_car_boxes)))
        for i in range(len(parked_car_boxes)):
            for j in range(car_boxes.shape[0]):
                pol1_xy = parked_car_boxes[i]
                pol2_xy = new_car_boxes[j]
                polygon1_shape = shapely_poly(pol1_xy)
                polygon2_shape = shapely_poly(pol2_xy)

                polygon_intersection = polygon1_shape.intersection(polygon2_shape).area
                polygon_union = polygon1_shape.union(polygon2_shape).area
                IOU = polygon_intersection / polygon_union
                overlaps[i][j] = IOU
        return overlaps







    def countAvailableSpots(self, frame, regions, saved):
        nFreeSpots = 0
        nSpotsTotal = 0
        overlay = frame
        print("\n------------ DETECTING FREE PARKING SPOTS ----------------")

        # Convert the image from BGR color (which OpenCV uses) to RGB color
        rgb_image = frame[:, :, ::-1]

        # Run the image through the Mask R-CNN model to get results.
        results = model.detect([rgb_image], verbose=0)

        # Mask R-CNN assumes we are running detection on multiple images.
        # We only passed in one image to detect, so only grab the first result.
        r = results[0]




        with open(regions, 'rb') as f:
            parked_car_boxes = pickle.load(f)


        car_boxes = self.get_car_boxes(r['rois'], r['class_ids']) #array de arrays com tamanho do nr carros detetados (6)
        # See how much those cars overlap with the known parking spaces
        overlaps = self.compute_overlaps(parked_car_boxes, car_boxes)
        #overlaps = mrcnn.utils.compute_overlaps(parked_car_boxes, car_boxes)



        # Loop through each known parking space box
        for parking_area, overlap_areas in zip(parked_car_boxes, overlaps):
            nSpotsTotal +=1
            # For this parking space, find the max amount it was covered by any
            # car that was detected in our image (doesn't really matter which car)
            max_IoU_overlap = np.max(overlap_areas)

            # Get the top-left and bottom-right coordinates of the parking area
            y1, x1, y2, x2 = parking_area
            pts = np.array([x1, y1, x2, y2], np.int32)


            # Check if the parking space is occupied by seeing if any car overlaps
            if max_IoU_overlap < 0.15:
                 cv2.polylines(frame, [pts], True, (0, 255, 0), thickness= 5)
                 #cv2.fillPoly(overlay, [np.array(parking_area)], (71, 27, 92))
                 nFreeSpots +=1
            else:
                cv2.polylines(frame, [pts], True, (0, 0, 255), thickness= 5)
                #cv2.fillPoly(overlay, [np.array(parking_area)], (56, 224, 120))

        cv2.putText(frame, 'Free Spots Detected -> '+ str(nFreeSpots), (10,40), cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255), thickness = 1)
        print('Total Spots detected:  ', nSpotsTotal)
        print('Free Spots detected:  ', nFreeSpots)
        cv2.imwrite(saved, frame)
        # resize das frames
        video_scale = 70
        width = int(frame.shape[1] * video_scale / 100)
        height = int(frame.shape[0] * video_scale / 100)
        dim = (width, height)
        resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
        cv2.imshow('frame', resized)
        cv2.waitKey(0)

        print("------------------------ END -----------------------------\n")
        return nFreeSpots














