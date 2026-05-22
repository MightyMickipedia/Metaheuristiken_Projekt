from __future__ import annotations

import json
import os

class DataBinCapacity: # Erstellung der Bin Kapazität
    """Speichert die maximale Kapazität eines Bins."""

    def __init__(self, capacity: int | float) -> None:
        """Initialisiert die Bin-Kapazität."""
        self.__capacity = capacity

    def __str__(self) -> str:
        """Gibt eine lesbare Beschreibung der Bin-Kapazität zurück."""
        return f"The bin weight capacity is {self.__capacity}"

    @property
    def capacity(self) -> int | float:
        """Gibt die gespeicherte Bin-Kapazität zurück."""
        return self.__capacity

class DataItem: # "Erstellung" der Items mit ID und Gewicht
    """Speichert ein Item mit ID und Gewicht."""

    def __init__(self, idItem: int, weight: int | float) -> None:
        """Initialisiert ein Item mit seiner ID und seinem Gewicht."""
        self.__itemId = idItem
        self.__weight = weight

    def __str__(self) -> str:
        """Gibt eine lesbare Beschreibung des Items zurück."""
        return f"Item {self.__itemId} weights {self.__weight}"
    
    @property
    def itemId(self) -> int:
        """Gibt die ID des Items zurück."""
        return self.__itemId

    @property
    def weight(self) -> int | float:
        """Gibt das Gewicht des Items zurück."""
        return self.__weight

class InputData:
    """Lädt und speichert die Eingabedaten einer Probleminstanz."""

    def __init__(self, path: str) -> None:
        """Initialisiert die Eingabedaten aus dem angegebenen Dateipfad."""
        self.__path = path
        self.__filename = os.path.basename(path)
        self.DataLoad()

    def DataLoad(self) -> None: # Laden der Daten aus dem zugeörigen Dateipfad
        """Lädt Items und Bin-Kapazität aus einer JSON-Datei."""
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
    def path(self) -> str:
        """Gibt den Dateipfad der Eingabedaten zurück."""
        return self.__path
    
    @property
    def filename(self) -> str:
        """Gibt den Dateinamen der Eingabedaten zurück."""
        return self.__filename
    

class Files:
    """Sucht verfügbare Datendateien in einem Ordner."""

    def __init__(self, folder: str = 'Data') -> None:
        """Initialisiert den Dateihelfer mit dem Namen des Datenordners."""
        self.Folder = folder

    def GetFiles(self) -> list[str]:
        """Gibt relative Pfade aller Dateien im Datenordner zurück."""
        basePath = os.getcwd()
        dataPath = os.path.join(basePath, f'../{self.Folder}')
        paths = list()

        for datei in os.listdir(dataPath):
            paths.append(f'../{self.Folder}/{datei}')

        return paths
