import pickle
import cv2
import numpy as np
from shapely.geometry import Polygon as shapely_poly
from b_Model import model




class c_Detector_1():
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
        limit = 0.15
        alpha = 0.5
        print(" ------------ countAvailableSpots ----------------")
        cv2.addWeighted(frame, alpha, frame, 1 - alpha, 0, frame)
        overlay = frame.copy()
        nFreeSpots = 0
        #------------- modelo --------------
        with open(regions, 'rb') as f:
            parked_car_boxes = pickle.load(f)


        coco = np.zeros(len(parked_car_boxes)).tolist()
        Spots = np.array([parked_car_boxes, coco])
        nSpotsTotal = len(Spots[0])
        print('Total Parking Spots: ', nSpotsTotal)

        # Convert the image from BGR color (which OpenCV uses) to RGB color
        rgb_image = frame[:, :, ::-1]
        results = self.getModel().detect([rgb_image], verbose=0)

        car_boxes = self.get_car_boxes(results[0]['rois'], results[0]['class_ids'])
        overlaps = self.compute_overlaps(parked_car_boxes, car_boxes)

        for parking_area, overlap_areas in zip(parked_car_boxes, overlaps):
            max_IoU_overlap = np.max(overlap_areas)
            if max_IoU_overlap < limit:
                cv2.fillPoly(overlay, [np.array(parking_area)], (71, 27, 92))
                nFreeSpots += 1
            else:
                cv2.fillPoly(overlay, [np.array(parking_area)], (56, 224, 120))

        cv2.imwrite(saved, overlay)
        video_scale = 70
        width = int(overlay.shape[1] * video_scale / 100)
        height = int(overlay.shape[0] * video_scale / 100)
        dim = (width, height)
        resized = cv2.resize(overlay, dim, interpolation=cv2.INTER_AREA)
        cv2.imshow('frame', resized)
        cv2.waitKey(0)
        print('Free Parking Spots: ', nFreeSpots)
        return nFreeSpots




