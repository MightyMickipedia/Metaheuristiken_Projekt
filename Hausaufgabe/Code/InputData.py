import json
import os

class DataBinCapacity: # Erstellung der Bin Kapazität
    def __init__(self, capacity):
        self.__capacity = capacity

    def __str__(self):
        return f"The bin weight capacity is {self.__capacity}"

    @property
    def capacity(self):
        return self.__capacity

class DataItem: # "Erstellung" der Items mit ID und Gewicht
    def __init__(self, idItem, weight):
        self.__itemId = idItem
        self.__weight = weight

    def __str__(self):
        return f"Item {self.__itemId} weights {self.__weight}"
    
    @property
    def itemId(self):
        return self.__itemId

    @property
    def weight(self):
        return self.__weight

class InputData:
    def __init__(self, path):
        self.__path = path
        self.__filename = os.path.basename(path)
        self.DataLoad()

    def DataLoad(self): # Laden der Daten aus dem zugeörigen Dateipfad
        try:
            with open(self.__path, "r") as inputFile:
                inputData = json.load(inputFile)

            self.InputItems = []
            self.InputBinCapacity = DataBinCapacity(inputData["BinCapacity"])

            for item in inputData["Items"]:
                self.InputItems.append(DataItem(item["Id"], item["Weight"]))

            print(f'Number of items: {len(self.InputItems)}')
            print(f'Bincapacity: {self.InputBinCapacity.capacity}\n')


        except FileNotFoundError:
            print(f"File not found: {self.__path}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file: {self.__path}")
        except KeyError as e:
            print(f"Missing key in JSON data: {e}")


    @property
    def path(self):
        return self.__path
    
    @property
    def filename(self):
        return self.__filename
    

class Files:
    def __init__(self, folder = 'Data'):
        self.Folder = folder

    def GetFiles(self):
        basePath = os.getcwd()
        dataPath = os.path.join(basePath, f'../{self.Folder}')
        paths = list()

        for datei in os.listdir(dataPath):
            paths.append(f'../{self.Folder}/{datei}')

        return paths
