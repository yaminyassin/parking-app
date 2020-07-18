from b_Video import b_Video
from b_Camera import b_Camera
from c_Detector_1 import c_Detector_1
from c_Detector_2 import c_Detector_2
from b_Model import model
from c_FreeSpotCounter import c_FreeSpotCounter
from b_DataBase import updateDB


class c_Main():
    def __init__(self, arrayCameras, detector, interval, idPark):
        self.__algorithm = c_FreeSpotCounter(arrayCameras, detector, interval, idPark)

    def init(self):
        self.__algorithm.state_machine()



if __name__ == "__main__":
    video1 = b_Video("data/video3.mp4", "repo_spot/video3regions.p")
    #video1 = b_Video("data/playing1.mp4", "repo_spot/playing1regions.p")
    camera1 = b_Camera(video1, 80)
    #camera2 = b_Camera(video2, 20)
    detector = c_Detector_2(model)
    arrayCameras = [camera1]
    main = c_Main(arrayCameras, detector, interval=0.5, idPark=2)
    main.init()



