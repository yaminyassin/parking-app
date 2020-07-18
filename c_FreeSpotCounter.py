import time
import cv2
from b_DataBase import updateDB

#array de frames/buffer circular (ex. só 10 frames) e ir buscar as frames mais "proximas" numa questão de timestamps
#timestamp "mais comum" a todas.
#A primeira frame é a mais recente, a última a ter sido adicionada é a que está mais "atrasada"
#Encontrar no buffer a frame cujo timestamp está mais próximo do mais "atrasado"
#Pensar numa estrutura que grava 1 buffer circular em vez de só 1 frame
#------- este Main é que representa o caso associado á contagem -----


class c_FreeSpotCounter:

    def __init__(self, arrayCameras, detector, interval, idPark):
        self.arrayCameras = arrayCameras
        self.detector = detector
        self.idPark = idPark
        self.interval = interval
        self.__nFreeSpotsCurrent = 0
        self.__nFreeSpots = 0
        self.__arrayFrames = []
        self.__arrayRegions = []
        self.__WAIT = 0
        self.__GET_FRAMES = 1
        self.__COUNT_SPOTS = 2
        self.__DB = 3
        self.__END = 4
        self.__state = self.__WAIT


    def state_machine(self):
        for camera in self.arrayCameras:
            self.__arrayRegions.append(camera.getVideoRegions())
            camera.start()

        while self.__state != self.__END:
            if self.__state == self.__WAIT:
                print("STATE - WAIT")
                time.sleep(self.interval)
                self.__state = self.__GET_FRAMES
                continue

            if self.__state == self.__GET_FRAMES:
                print("STATE - GET_FRAMES")
                self.__arrayFrames = []
                for camera in self.arrayCameras:
                    if(camera.isRunning()):
                        self.__arrayFrames.append(camera.getCurrentFrame())
                        self.__state = self.__COUNT_SPOTS
                    else:
                        self.__state = self.__END
                        break
                continue

            if self.__state == self.__COUNT_SPOTS:
                print("STATE - COUNT_SPOTS")
                self.__nFreeSpots = 0
                for i in range(len(self.__arrayFrames)):
                    # resize das frames
                    width = int(self.__arrayFrames[i].shape[1] * 90 / 100)
                    height = int(self.__arrayFrames[i].shape[0] * 90 / 100)
                    dim = (width, height)
                    resized = cv2.resize(self.__arrayFrames[i], dim, interpolation=cv2.INTER_AREA)
                    cv2.imshow('video', resized)
                    count = self.detector.countAvailableSpots(self.__arrayFrames[i], self.__arrayRegions[i], "saved_classifications/c_Main.png")
                    self.__nFreeSpots = self.__nFreeSpots + count
                self.__state = self.__DB
                continue

            # -------------------------------------------------
            # outro boundary para comunicação com parte externa
            if self.__state == self.__DB:
                print("STATE - DB")
                print('CALCULATED nFreeSpots --> ', self.__nFreeSpots)
                if self.__nFreeSpots != self.__nFreeSpotsCurrent:
                    print('DATABASE REFRESHED WITH NEW DATA! --> ', self.__nFreeSpots)
                    updateDB(self.__nFreeSpots, self.idPark)
                    self.__nFreeSpotsCurrent = self.__nFreeSpots
                print("----------------------------------")
                self.__state = self.__WAIT
                continue

            if self.__state == self.__END:
                break

        return self.__state


