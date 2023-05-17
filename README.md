# Corso docenti Python-IoT-AI per il monitoraggio ambientale

In questo repository trovate il codice in MicroPython per ESP32 per il corso tenuto dalla nostra scuola (a.s. 2022/23) rivolto ai docenti per la creazione di una stazione di monitoraggio ambientale che copre gli argomenti di Python, IoT ed Intelligenza Artificiale.

Riferimenti:

- [Sito di presentazione](https://marconi.my.canva.site/corso-docenti-python-iot-ai)
- Corsi su [ScuolaFutura](https://scuolafutura.pubblica.istruzione.it/):
  - ID.120087 Modulo 1: Python
  - ID.120182  Modulo 2: IoT
  - ID.120238 Modulo 3: Intelligenza Artificiale

## Il progetto

Il progetto attualmente prevede la lettura dei dati da un sensore [SDS011](https://nettigo.pl/attachments/398) per il rilevamento delle polveri sottili PM 2.5 e PM 10. La scheda legge ed invia anche il timestamp di lettura, leggendo l'orario da Internet con la libreria `ntptime`.

I dati vengono inviati tramite il protocollo MQTT ad un broker online e successivamente trattati attraverso Python con la libreria Scikit-learn di intelligenza artificiale per analizzare correlazioni tra i dati (attualmente solo PM e orario).

## Strumenti

Per il progetto abbiamo usato:
- [Mu Editor](https://codewith.mu/) e [Thonny IDE](https://thonny.org/) come editor e per caricare il firmware di MicroPython sulle schede ESP32.

- per gestire la scheda in modo wireless si consiglia anche [WebREPL](https://bhave.sh/micropython-webrepl-thonny/?authuser=0)
