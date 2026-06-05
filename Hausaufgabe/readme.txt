# Ausführung

Für die Abgabe muss nur eine der beiden Varianten ausgeführt werden. Entweder wird das Notebook `Code/SimulatedAnnealing.ipynb` ausgeführt oder alternativ die Python-Datei `Code/SimulatedAnnealing.py`. Beide Varianten laden die Datensätze, erzeugen eine Startlösung, wenden Simulated Annealing an und speichern die gefundene Lösung im Ordner `Solutions`.

Die betrachteten Datensätze können in den Ordner `Data` gelegt werden. Alle JSON-Dateien in diesem Ordner werden geladen und nacheinander bearbeitet. Die Ausgabedateien werden als CSV in `Solutions` gespeichert.

Die Python-Datei kann zum Beispiel aus dem Ordner `Hausaufgabe` mit folgendem Befehl gestartet werden:

```text
python Code/SimulatedAnnealing.py
```

Das Notebook kann direkt in Jupyter geöffnet und von oben nach unten ausgeführt werden.

# Parameter

Die wichtigsten Hyperparameter werden im Notebook im Abschnitt `Imports und globale Einstellungen` gesetzt. Dort stehen `START_HEURISTIC` und `SA_PARAMETERS`. `START_HEURISTIC` wählt die konstruktive Startlösung. In `SA_PARAMETERS` stehen die Parameter für Simulated Annealing, also Nachbarschaft, Temperatur, Abkühlgeschwindigkeit, Schwellenwert, Markov-Länge und Anzahl der erzeugten Moves.

In der Python-Datei stehen dieselben Werte direkt am Anfang der Datei. Wenn nur ein normaler Lauf ohne Grid Search gewünscht ist, reicht es aus, diese Werte dort oder im Notebook anzupassen.

# Grid Search

Der Grid Search ist nur im Notebook enthalten. Die Python-Datei enthält ihn bewusst nicht, damit sie eine einfache ausführbare Variante ohne Dokumentation und ohne Parameterstudie bleibt.

Im Notebook befindet sich der Grid Search im Abschnitt `Optionaler Grid Search zur Parameterwahl`. Gestartet wird er, indem `DO_OPTIMIZATION = True` gesetzt wird. Wenn `DO_OPTIMIZATION = False` gesetzt ist, wird der Grid Search übersprungen und die vorher gesetzten `SA_PARAMETERS` werden verwendet.

Das Suchgitter wird über `SA_PARAMETER_GRID` angepasst. Dort können weitere Werte für `temperature`, `coolingSpeed`, `neighborhoodTypes`, `maxMarkovLength` und `numberOfMoves` eingetragen oder entfernt werden. Je mehr Werte im Grid stehen, desto mehr Simulated-Annealing-Läufe müssen ausgeführt werden. Deshalb wurde der Grid Search nur auf dem kleinsten Datensatz verwendet.

Nach dem Grid Search werden mehrere Empfehlungen ausgegeben. Die beste Qualität betrachtet die kleinste Anzahl verwendeter Bins. Die schnellste Variante betrachtet nur die Laufzeit. Die ausgewogene Variante bewertet Qualität und Laufzeit gemeinsam. Im Code wird nach dem Grid Search diese ausgewogene Variante als `SA_PARAMETERS` gesetzt.

Die erzeugten Grafiken werden im Ordner `Figures` gespeichert. Sie zeigen die wichtigsten Vergleiche der getesteten Parameter, ohne dass jede Kombination einzeln im Text betrachtet werden muss.
