import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import asyncio
import os
import time
import backend


class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Analysis Tool - Dashboard")
        self.root.geometry("900x600") 
        
        self.selected_coins = []
        self._setup_ui()

    def _setup_ui(self):
        # --- GLAVNI KONTEJNERI ---
        # Lijeva strana za unos
        self.left_frame = tk.Frame(self.root, padx=20, pady=20, width=400)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        

        # Vertikalna crta (separator)
        separator = ttk.Separator(self.root, orient='vertical')
        separator.pack(side=tk.LEFT, fill='y', padx=5)

        # Desna strana za izvještaj
        self.right_frame = tk.Frame(self.root, padx=20, pady=20)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- LIJEVA STRANA: KONTROLE ---
        tk.Label(self.left_frame, text="POSTAVKE UNOSA", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))

        # Ručni unos
        tk.Label(self.left_frame, text="Ručni unos valuta:").pack(anchor="w")
        self.coin_entry = tk.Entry(self.left_frame, width=40)
        self.coin_entry.insert(0, "bitcoin, ethereum, solana")
        self.coin_entry.pack(pady=5)

        tk.Label(self.left_frame, text="ILI", 
                 font=("Arial", 8, "bold")).pack(pady=5)

        # Datoteka
        self.upload_btn = tk.Button(self.left_frame, 
                                    text="Učitaj .txt datoteku", 
                                    command=self.upload_file, 
                                    width=25)
        self.upload_btn.pack(pady=5)
        
        self.clear_file_btn = tk.Button(self.left_frame, 
                                        text="Ukloni datoteku", 
                                        command=self.clear_file, 
                                        state=tk.DISABLED, 
                                        width=25)
        self.clear_file_btn.pack(pady=5)

        self.file_label = tk.Label(self.left_frame, 
                                   text="Nije odabrana datoteka", 
                                   fg="gray", 
                                   font=("Arial", 8, "italic"))
        self.file_label.pack(pady=5)

        tk.Label(
            self.left_frame, text="Odaberi valutu:", pady=10
            ).pack(anchor="w")
        self.currency_var = tk.StringVar(value="eur")
        self.currency_combo = ttk.Combobox(self.left_frame, 
                                           textvariable=self.currency_var, 
                                           state="readonly")
        self.currency_combo['values'] = ("eur", "usd", "gbp", "jpy")
        self.currency_combo.pack(anchor="w")
        # Prag i Format
        tk.Label(
            self.left_frame, text="Prag promjene cijene (%):", pady=10
            ).pack(anchor="w")
        self.perc_entry = tk.Entry(self.left_frame, width=15)
        self.perc_entry.insert(0, "1.0")
        self.perc_entry.pack(anchor="w")

        tk.Label(
            self.left_frame, text="Format izvještaja:", pady=10
            ).pack(anchor="w")
        self.format_var = tk.StringVar(value="CSV")
        tk.Radiobutton(self.left_frame, 
                       text="Spremi kao CSV", 
                       variable=self.format_var, 
                       value="CSV").pack(anchor="w")
        tk.Radiobutton(self.left_frame, 
                       text="Spremi kao PDF", 
                       variable=self.format_var, 
                       value="PDF").pack(anchor="w")

        # Gumb za pokretanje na dnu lijevog okvira
        self.run_btn = tk.Button(self.left_frame, 
                                 text="POKRENI ANALIZU", 
                                 command=self.start_task, 
                                bg="#27ae60", 
                                fg="white", 
                                font=("Arial", 10, "bold"), 
                                height=2, width=30)
        self.run_btn.pack(pady=30)

        # --- DESNA STRANA: REZULTATI ---
        tk.Label(self.right_frame, text="IZVJEŠTAJ I STATUS", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        self.log_area = scrolledtext.ScrolledText(self.right_frame, 
                                                  state='disabled', 
                                                  bg="#2c3e50", 
                                                  fg="#ecf0f1", 
                                                  font=("Consolas", 10))
        self.log_area.pack(fill=tk.BOTH, expand=True)

    # --- LOGIKA ---

    def write_log(self, text):
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {text}\n")
        self.log_area.configure(state='disabled')
        self.log_area.see(tk.END)

    def upload_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            try:
                self.selected_coins = backend.load_coins_from_file(path)
                self.file_label.config(
                    text=f"Aktivno: {os.path.basename(path)}", 
                    fg="#16a085")
                self.clear_file_btn.config(state=tk.NORMAL)
                self.coin_entry.config(state=tk.DISABLED)
                self.write_log(f"Datoteka učitana: \
                               {len(self.selected_coins)} valuta spremno.")
            except Exception as e:
                messagebox.showerror("Greška", f"Problem s datotekom: {e}")

    def clear_file(self):
        self.selected_coins = []
        self.file_label.config(text="Nije odabrana datoteka", fg="gray")
        self.clear_file_btn.config(state=tk.DISABLED)
        self.coin_entry.config(state=tk.NORMAL)
        self.write_log("Korištenje datoteke poništeno.")

    def start_task(self):
        coins = self.selected_coins if self.selected_coins else \
            [c.strip() for c in self.coin_entry.get().split(",") if c.strip()]
        if not coins:
            messagebox.showwarning("Upozorenje", "Niste unijeli valute!")
            return
        try:
            threshold = float(self.perc_entry.get())
        except:
            messagebox.showerror("Greška", "Prag mora biti broj!")
            return

        self.run_btn.config(state=tk.DISABLED)
        self.write_log("Analiza pokrenuta...")
        threading.Thread(target=self.run_async_wrapper, 
                         args=(coins, threshold), 
                         daemon=True).start()

    def run_async_wrapper(self, coins, threshold):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.execute_logic(coins, threshold))
        except Exception as e:
            self.root.after(0, lambda: self.write_log(f"GREŠKA: {e}"))
            # Pisanje u log.txt (Append mod)
            with open("log.txt", "a") as f:
                f.write(f"[{time.ctime()}] {e}\n")
        finally:
            self.root.after(0, lambda: self.run_btn.config(state=tk.NORMAL))
    
    async def execute_logic(self, coins, threshold):
        try:
            # Dohvaćamo odabranu valutu iz GUI-ja
            selected_curr = self.currency_var.get()
            
            # Fetch (Backend)
            self.root.after(0, lambda: self.write_log(
                f"Dohvaćam podatke za {len(coins)} valuta..."))
            prices = await backend.fetch_crypto_prices(coins, selected_curr)
            
            # Filter (Closure iz backenda)
            p_filter = backend.filter_by_change(threshold, selected_curr)
            filtered = [{"id": name, **data} for name, data in prices.items() \
                        if p_filter(data)]
            
            self.root.after(0, lambda: self.write_log(
                f"API odgovorio. Pronađeno {len(filtered)} valuta koje zadovoljavaju kriterij."))

            # Odabir savera (Protocol)
            if self.format_var.get() == "CSV":
                saver = backend.CSVSaver()
            else:
                saver = backend.PDFSaver()
                
            if filtered:
                # Spremanje datoteke u pozadini
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, saver.save, filtered)
                self.root.after(0, lambda: self.write_log(
                    f"USPJEH: Izvještaj spremljen u {self.format_var.get()} formatu."))
                
                # --- VIZUALNI IZVJEŠTAJ U DESNOM PROZORU ---
                self.root.after(0, lambda: self.write_log("-" * 30))
                self.root.after(0, lambda: self.write_log(
                    "DETALJAN IZVJEŠTAJ:"))
                
                for item in filtered:
                    coin_name = item['id'].upper()
                    price = item.get(selected_curr, 0)
                    change = item.get(f'{selected_curr}_24h_change', 0)
                    
                    # Ispis u desni prozor
                    self.root.after(0, lambda n=coin_name, p=price, 
                                    c=change, cur=selected_curr.upper(): 
                        self.write_log(f"{n}: {p:.2f} {cur} (Promjena: {c:.2f}%)"))
                
                self.root.after(0, lambda: self.write_log("-" * 30))
            else:
                self.root.after(0, lambda: self.write_log(
                    "INFO: Niti jedna valuta ne zadovoljava prag promjene."))
        except Exception as e:
            # Ako se dogodi greška, ispiši tehnički detalj...
            self.root.after(0, lambda: self.write_log(f"GREŠKA: {e}"))
            
            # ... i dodaj kratko objašnjenje za korisnika
            if "429" in str(e):
                objašnjenje = (
                    "\n--- OBJAŠNJENJE ---\n"
                    "Dosegnut je limit besplatnih zahtjeva (Rate Limit).\n"
                    "CoinGecko dozvoljava ograničen broj upita u minuti.\n"
                    "Molimo pričekajte 30-60 sekundi i pokušajte ponovno."
                )
                self.root.after(0, lambda: self.write_log(objašnjenje))
            
            # Zapiši i u datoteku log.txt
            with open("log.txt", "a", encoding="utf-8") as f:
                f.write(f"[{time.ctime()}] {e}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()