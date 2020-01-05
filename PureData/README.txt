0. Scarica il progetto
0b. Collegati al wifi comune tra rasp e portatile
1. Metti il progetto unity da qualche parte sul tuo pc e fallo andare
2. Metti il file pd sul rasp con filezilla, in una cartella che vuoi. Al momento è configurato per il rasp .0.15, il tuo sarà .0.20 (IP Address), quindi cambia quello nel file
3. Fai partire il file pd con VNC Viewer così vedi dalla UI se i numeri cambiano giusti
4. Fai partire il progetto unity. Vai sull'oggetto chiamato OSC Manager e nel transmitter e receiver a destra metti 192.168.0.20 al posto di .15 e metti il tuo IP al posto di .0.10 (magari è .10 anche il tuo)
5. Facendo play, il progetto unity dovrebbe mandare i messaggi al rasp, ez. A sx di Pd i numeri cambiano veloci da 0 a 80, a destra puoi cliccare 216, 432 o 864 per far cambiare il numero su unity (receiver -> FrequencyReceiver a destra)

Note:
Disabilita il firewall di windows se necessario, per me lo è stato. Se non va o non capisci qualcosa ask me