from __future__ import annotations

import json
import os
from collections.abc import Mapping


Number = int | float


def _is_number(value: object) -> bool:
    """Prüft numerische JSON-Werte, ohne bool als Zahl zu akzeptieren."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)

class DataBinCapacity: # Erstellung der Bin Kapazität
    """Speichert die maximale Kapazität eines Bins."""

    def __init__(self, capacity: Number) -> None:
        """Initialisiert die Bin-Kapazität."""
        self.__capacity = capacity

    def __str__(self) -> str:
        """Gibt eine lesbare Beschreibung der Bin-Kapazität zurück."""
        return f"The bin weight capacity is {self.__capacity}"

    @property
    def capacity(self) -> Number:
        """Gibt die gespeicherte Bin-Kapazität zurück."""
        return self.__capacity

class DataItem: # "Erstellung" der Items mit ID und Gewicht
    """Speichert ein Item mit ID und Gewicht."""

    def __init__(self, idItem: int, weight: Number) -> None:
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
    def weight(self) -> Number:
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

            if not isinstance(inputData, Mapping):
                raise ValueError("Die JSON-Datei muss ein Objekt enthalten.")

            if "BinCapacity" not in inputData:
                raise ValueError("Pflichtfeld 'BinCapacity' fehlt.")

            binCapacity = inputData["BinCapacity"]
            if not _is_number(binCapacity) or binCapacity <= 0:
                raise ValueError("'BinCapacity' muss eine positive Zahl sein.")

            if "Items" not in inputData:
                raise ValueError("Pflichtfeld 'Items' fehlt.")

            items = inputData["Items"]
            if not isinstance(items, list):
                raise ValueError("'Items' muss eine Liste sein.")

            inputItems = []
            seenItemIds = set()

            for itemIndex, item in enumerate(items):
                if not isinstance(item, Mapping):
                    raise ValueError(f"Item an Position {itemIndex} muss ein Objekt sein.")

                if "Id" not in item:
                    raise ValueError(f"Item an Position {itemIndex} enthält keine 'Id'.")

                if "Weight" not in item:
                    raise ValueError(f"Item an Position {itemIndex} enthält kein 'Weight'.")

                itemId = item["Id"]
                itemWeight = item["Weight"]

                if not isinstance(itemId, int) or isinstance(itemId, bool):
                    raise ValueError(f"Item an Position {itemIndex}: 'Id' muss eine ganze Zahl sein.")

                if itemId in seenItemIds:
                    raise ValueError(f"Item-ID {itemId} kommt mehrfach vor.")

                if not _is_number(itemWeight) or itemWeight <= 0:
                    raise ValueError(f"Item {itemId}: 'Weight' muss eine positive Zahl sein.")

                if itemWeight > binCapacity:
                    raise ValueError(
                        f"Item {itemId}: Gewicht {itemWeight} überschreitet BinCapacity {binCapacity}."
                    )

                seenItemIds.add(itemId)
                inputItems.append(DataItem(itemId, itemWeight))

            self.InputItems = inputItems
            self.InputBinCapacity = DataBinCapacity(binCapacity)

            print(f'Number of items: {len(self.InputItems)}')
            print(f'Bincapacity: {self.InputBinCapacity.capacity}\n')


        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.__path}") from None
        except json.JSONDecodeError as exc:
            raise ValueError(f"Error decoding JSON from file: {self.__path}") from exc
        

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
        if os.path.isabs(self.Folder):
            dataPath = self.Folder
            relativePrefix = dataPath
        else:
            basePath = os.path.dirname(os.path.abspath(__file__))
            dataPath = os.path.abspath(os.path.join(basePath, "..", self.Folder))
            relativePrefix = os.path.join("..", self.Folder)

        if not os.path.isdir(dataPath):
            raise FileNotFoundError(f"Data folder not found: {dataPath}")

        paths = []

        for datei in os.listdir(dataPath):
            fullPath = os.path.join(dataPath, datei)
            if os.path.isfile(fullPath) and datei.lower().endswith(".json"):
                paths.append(os.path.join(relativePrefix, datei))

        return sorted(paths)
