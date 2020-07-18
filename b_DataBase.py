import requests


def updateDB(freeSpots, idPark):
    # api-endpoint
    URL = "http://localhost:3000/movel/parkUpdate/"+str(idPark)+"/"+str(freeSpots)
    # sending get request and saving the response as response object
    r = requests.get(url=URL)