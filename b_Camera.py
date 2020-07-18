import threading
import cv2



#em vez de gravar 1 frame, grva-se 1 buffer de frames, em que o getCurrentFrame é getCurrentFrameBuffer
#criar um b_Video e meter na câmera, e tentar criar video com o móvel
class b_Camera(threading.Thread):

    def __init__(self, b_Video, video_scale):
        threading.Thread.__init__(self)
        self.__video = b_Video.getVideo()
        self.__regions = b_Video.getRegions()
        self.video_scale = video_scale
        self.__frame = None
        self.__running = False

    def run(self):
        print(" ------------- VIDEO STARTED RUNNING! --------------- \n")
        video_capture = cv2.VideoCapture(self.__video)

        while video_capture.isOpened():
            self.setRunning(True)
            success, frame = video_capture.read()
            if not success:
                self.setRunning(False)
                break

            #atualizar frame guardada
            self.setCurrentFrame(frame)

            #resize das frames
            width = int(frame.shape[1] * self.video_scale / 100)
            height = int(frame.shape[0] * self.video_scale / 100)
            dim = (width, height)
            resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
            cv2.imshow('video', resized)
            if cv2.waitKey(30)>=0:
                self.setRunning(False)
                break

        video_capture.release()
        cv2.destroyAllWindows()
        return


    def isRunning(self):
        return self.__running

    def setRunning(self, running):
        self.__running = running

    def getCurrentFrame(self):
        return self.__frame

    def setCurrentFrame(self, frame):
        self.__frame = frame

    def getVideoRegions(self):
        return self.__regions



