# Python kursa gala darbs

## Kā instalēt

```bash
git clone https://github.com/gustasvs/python_kurs-npd
cd python_kurs-npd
pip install -r requirements.txt
```
Lai palaistu projekta bāzes folderī palaist:
```bash
python3 main.py
```

## Par darbu
Darbu veidoja Gustavs Jākobsons, gj22014

Programma ir spēle kurā ir tēls, kurš sastāv no mazām daļiņām (particles)
Spēlētājs var kontrolēt šo grupiņu un pārvietoties uz augšu mapē, lai paildzinātu vienu gājieinu var savākt 
papildus daļiņas.
Kad spēlētājs ir zaudējis var uzlabot sevi ar pelīti.

## Par failiem

fails main.py satur galveno spēles ciklu, uz kura visa apklikācija strādā 
fails sprites.py satur informāciju par dažādām klasēm spēlē, piemēram spēlētājs, sienas, gabaliņi (particles)
fails functions.py satur no interneta ņemtas matemātiskas funckijas, kuras piemēram atrod viduspunktu starp divām līnijām

player_stats.json saglabā spēlētāja informāciju, ja programma tiek aizvērta,


## TODO
Lietas kuras nav izdarītas laika trūkuma dēļ:
* izdomāt īsu programmas nosaukumu, pagaidām speles windows logā ir attēlots cik reizes sekundē tike atjaunota (FPS)
* Ir redzami objekti, kuri atrodas aiz citiem objektiem
* Spēlētāja kopējā nauda saglabājas spēli aizverot, taču nesaglabājas veiktie uzlabojumi
* Uzlaboti komentāri
* Labāki efekti un dizains papildus gabaliņu savākšanai (pagaidām zili kubiciņi)