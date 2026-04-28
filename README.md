# Crypto Analysis Tool 

Ovaj projekt je seminarski rad za kolegij Napredne Tehnike Programiranja. 
Aplikacija služi za dohvaćanje, filtriranje i analizu cijena kriptovaluta u stvarnom vremenu.

## Zahtjevi sustava
* **Verzija Python-a:** 3.13

## Korišteni elementi s predavanja
* **Asinkrono programiranje:** Korištenje `aiohttp` za neblokirajuće API pozive.
* **Threading:** Razdvajanje GUI dretve od logike dretve kako bi aplikacija ostala responzivna.
* **Dekoratori:** `@log_and_time` za praćenje vremena izvršavanja i logiranje grešaka.
* **OOP & Protokoli:** Implementacija `DataSaver` protokola za spremanje u CSV i PDF.
* **GUI:** Izrađeno pomoću `tkinter` knjižnice.

## Upute za pokretanje
1. Instalirajte potrebne knjižnice: `pip install -r requirements.txt`
2. Pokrenite aplikaciju: `python gui.py`
