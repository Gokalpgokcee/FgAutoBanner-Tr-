import threading
import time
import tkinter as tk
from tkinter import scrolledtext
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://fungun.top/ecd/list/"
AJAX_URL = "https://fungun.top/ecd/ajax/ecd_front.php?method=list"
OUTPUT_FILE = "fungun_net_hileler.txt"


def clean_html_text(html_content):
    """HTML etiketlerini temizler ve attribute değerlerini (title/alt) yakalar."""
    if not html_content:
        return "-", []

    soup = BeautifulSoup(str(html_content), "html.parser")

    title_attrs = []
    for elem in soup.find_all(True):
        if elem.get("title"):
            title_attrs.append(elem.get("title"))
        elif elem.get("alt"):
            title_attrs.append(elem.get("alt"))

    text_content = soup.get_text(strip=True)
    return text_content, title_attrs


class CMDInterface:

    def __init__(self, root):
        self.root = root
        self.root.title("FunGun Result Danger TR Logger (Fixed)")
        self.root.geometry("1000x680")
        self.root.configure(bg="black")

        self.is_scanning = False

        self.console = scrolledtext.ScrolledText(
            root,
            bg="black",
            fg="#00FF00",
            insertbackground="white",
            font=("Consolas", 11),
            wrap=tk.WORD,
        )
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.entry_frame = tk.Frame(root, bg="black")
        self.entry_frame.pack(fill=tk.X, padx=5, pady=5)

        self.prompt_label = tk.Label(
            self.entry_frame,
            text="CMD>",
            bg="black",
            fg="#00FF00",
            font=("Consolas", 11, "bold"),
        )
        self.prompt_label.pack(side=tk.LEFT)

        self.entry = tk.Entry(
            self.entry_frame,
            bg="black",
            fg="white",
            insertbackground="white",
            font=("Consolas", 11),
            bd=0,
        )
        self.entry.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=5)
        self.entry.bind("<Return>", self.process_command)
        self.entry.focus_set()

        self.print_to_console(
            "=========================================================="
        )
        self.print_to_console(
            " FunGun Result Danger TR Logger v5.1 (Hata Giderildi)"
        )
        self.print_to_console(" Komut Listesi:")
        self.print_to_console(
            "    !kaydet           -> Tüm danger kayıtlarını eksiksiz tarar, Türkleri TXT'ye kaydeder"
        )
        self.print_to_console(
            "    !dur              -> İşlemi durdurur"
        )
        self.print_to_console(
            "    cls               -> Ekranı temizler"
        )
        self.print_to_console(
            " Geliştirici: Gökalp GÖKÇE"
        )
        self.print_to_console(
            "==========================================================\n"
        )

    def print_to_console(self, text):
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, text + "\n")
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)

    def process_command(self, event):
        cmd = self.entry.get().strip()
        self.entry.delete(0, tk.END)

        if not cmd:
            return

        self.print_to_console(f"CMD> {cmd}")

        if cmd == "!kaydet":
            if not self.is_scanning:
                self.is_scanning = True
                self.print_to_console(
                    "[*] Tam kapsamlı result:danger taraması başlatıldı..."
                )
                threading.Thread(
                    target=self.start_full_danger_scan, daemon=True
                ).start()

        elif cmd in ["!dur", "!durdur"]:
            if self.is_scanning:
                self.is_scanning = False
                self.print_to_console("[*] İşlem durduruldu.")

        elif cmd in ["clear", "cls"]:
            self.console.config(state=tk.NORMAL)
            self.console.delete("1.0", tk.END)
            self.console.config(state=tk.DISABLED)

        else:
            self.print_to_console("[!] Geçersiz komut.")

    def start_full_danger_scan(self):
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; x86) AppleWebKit/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": BASE_URL,
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }

        try:
            session.get(BASE_URL, headers=headers, timeout=10)

            start = 0
            length = 50000  # Tek seferde yüksek sayıda kayıt çekiyoruz
            saved_count = 0
            file_lines = []
            file_lines.append(
                "=== FUNGUN RESULT:DANGER TAM ARŞİV (TÜRK OYUNCULAR) ===\n"
            )

            while self.is_scanning:
                payload = {
                    "draw": "1",
                    "start": str(start),
                    "length": str(length),
                    "search[value]": "result:danger",
                    "search[regex]": "false",
                }

                res = session.post(
                    AJAX_URL, data=payload, headers=headers, timeout=20
                )
                if res.status_code != 200:
                    self.root.after(
                        0,
                        self.print_to_console,
                        f"[!] Sunucu hatası: {res.status_code}",
                    )
                    break

                data = res.json()
                records = data.get("data", [])
                
                # HATA ÇÖZÜMÜ: Veri tipini güvenli bir şekilde integer (sayı) yapıyoruz
                total_filtered = int(data.get("recordsFiltered", 0) or 0)

                if not records:
                    break

                page_saved = 0
                for row in records:
                    if not self.is_scanning:
                        break

                    nick, _ = clean_html_text(row.get("nick", ""))
                    ip, ip_attrs = clean_html_text(row.get("user_ip", ""))
                    host, _ = clean_html_text(row.get("hostname", ""))
                    status, _ = clean_html_text(
                        row.get("result_status", "")
                    )
                    time_val, _ = clean_html_text(row.get("time", ""))

                    # IP veya etiketlerden Türk oyuncu kontrolü
                    all_ip_data = f"{ip} {' '.join(ip_attrs)}".lower()
                    is_turkey = "turkey" in all_ip_data or "tr" in all_ip_data

                    if is_turkey:
                        saved_count += 1
                        page_saved += 1
                        line = f"NICK: {nick} | IP: {ip} | DURUM: {status} | SUNUCU: {host} | TARIH: {time_val}"
                        file_lines.append(line)

                        msg = f"🚨 [TÜRK DANGER] Nick: {nick} | IP: {ip}"
                        self.root.after(0, self.print_to_console, msg)

                # Sayfa sayacını gelen kayıt miktarı kadar artırıyoruz
                start += len(records)
                time.sleep(0.3)

                # Eğer taranan toplam kayıt, sunucudaki toplam filtrelenmiş kayıt sayısına ulaştıysa döngüyü bitir
                if start >= total_filtered or len(records) == 0:
                    break

            # Dosyaya tüm sonuçları yaz
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(file_lines))

            self.root.after(
                0,
                self.print_to_console,
                f"\n[*] Tam Tarama Bitti! Toplam {saved_count} adet Türk danger hileli oyuncu '{OUTPUT_FILE}' dosyasına kaydedildi.\n",
            )

        except Exception as e:
            self.root.after(
                0, self.print_to_console, f"[!] Hata Oluştu: {str(e)}\n"
            )

        self.is_scanning = False


if __name__ == "__main__":
    root = tk.Tk()
    app = CMDInterface(root)
    root.mainloop()
