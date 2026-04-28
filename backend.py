import aiohttp
from typing import Callable, List, Dict, Dict, Protocol, runtime_checkable
import functools
import time
import threading
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


@runtime_checkable
class DataSaver(Protocol):
    def save(self, data: List[Dict]) -> None:
        ...


class CSVSaver:
    def save(self, data: List[Dict]) -> None:
        import csv
        with open("izvjestaj.csv", "w", newline="", encoding="utf-8") as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        print("Spremljeno u CSV.")


class PDFSaver:
    def save(self, data: List[Dict]) -> None:
        """
        Sprema filtrirane podatke o kriptovalutama u PDF izvještaj.
        Uključuje tablicu i kratku analizu.
        """
        file_name = "izvjestaj_kripto.pdf"
        doc = SimpleDocTemplate(file_name, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Naslov izvještaja
        title = Paragraph("Izvještaj o Kriptovalutama", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Priprema podataka za tablicu
        # Zaglavlje tablice
        table_data = [["ID Valute", "Trenutna Cijena", "24h Promjena (%)"]]
        
        # Redovi s podacima
        for item in data:
            # Dinamički pronalazimo ključ za cijenu i promjenu
            price_key = next((k for k in item.keys() if k != 'id' 
                              and 'change' not in k), "N/A")
            change_key = next((k for k in item.keys() if 'change' in k), "N/A")
            
            row = [
                item['id'].upper(),
                f"{item.get(price_key, 0):.2f}",
                f"{item.get(change_key, 0):.2f}%"
            ]
            table_data.append(row)

        # Kreiranje i stiliziranje tablice
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))

        # Dodavanje analize 
        avg_change = sum(float(row[2].replace('%', '')) 
                         for row in table_data[1:]) / (len(table_data) - 1)
        analysis_text = f"Analiza: Ukupno je pronadeno {len(data)} valuta. \
            Prosjecna promjena ovih valuta iznosi {avg_change:.2f}%."
        analysis = Paragraph(analysis_text, styles['Normal'])
        elements.append(analysis)

        # Generiranje PDF-a
        doc.build(elements)
        print(f"PDF uspješno generiran: {file_name}")

def log_and_time(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time : float = time.perf_counter()
        try:
            print(f"Pokrećem {func.__name__}...")
            result = await func(*args, **kwargs)
            end_time : float = time.perf_counter()
            print(f"Završeno u {end_time - start_time:.4f}s")
            return result
        except Exception as e:
            with open("log.txt", "a") as f:
                f.write(f"[{time.ctime()}] Greška u {func.__name__}: {e}\n")
            raise
    return wrapper

def load_coins_from_file(file_path: str) -> List[str]:
    print(f"{threading.current_thread().name} učitava datoteku...")
    with open(file_path, "r", encoding="utf-8") as f:
        data: str = f.read()
        
        # Ako su odvojene zarezom splitaj po zarezu, 
        # inače po novom redu
        if "," in data:
            lista = data.split(",")
        else:
            lista = data.splitlines()
    
    return [coin.strip() for coin in lista if coin.strip()]

@log_and_time
async def fetch_crypto_prices(coins: List[str], 
                              vs_currency: str = "eur"
                             ) -> Dict[str, Dict[str, float]]:
    """
    Asinkrona funkcija za dohvaćanje cijena kriptovaluta 
    s CoinGecko API-ja.

    Args:
        coins (List[str]): Lista ID-ova kriptovaluta 
        				   (npr. ['bitcoin', 'ethereum'])
        vs_currencies (str): Valuta u kojoj se prikazuju cijene 
        				   (zadano 'eur')

    Returns:
        Dict: Rječnik s cijenama kriptovaluta
    """

    url = (
        f"https://api.coingecko.com/api/v3/simple/price?"
        f"ids={','.join(coins)}&vs_currencies={vs_currency}"
        f"&include_24hr_change=true"
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data : Dict[str, Dict[str, float]] = await response.json()
                return data
            else:
                raise Exception(
                    f"Greška pri dohvaćanju podataka: {response.status}"
                )

def filter_by_change(percentage: float, vs_currency: str) -> Callable:
    """
    Vanjska funkcija (generator) koja 'zaključava' željeni prag p%.
    Vraća konfigurabilnu funkciju za filtriranje.
    """
    def filter(crypto_data: Dict[str, float]) -> bool:
        """
        Unutarnja funkcija koja prima rječnik 
        s podacima o jednoj valuti.
        Provjerava je li apsolutna promjena u 24h veća od zadanog praga.
        """
        # Naziv ključa 'price_change_percentage_24h' 
        # odgovara CoinGecko API-ju 
        promjena : float = crypto_data.get(f'{vs_currency}_24h_change', 0)
        
        # Koristimo abs() jer nas zanima i rast i pad veći od p%
        return abs(promjena) > percentage
    
    return filter

