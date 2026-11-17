import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(CURRENT_DIR, "fungun_net_hileler.txt")
OUTPUT_FILE = os.path.join(CURRENT_DIR, "hileci_nickleri.txt")

def extract_clean_nicknames():
    if not os.path.exists(INPUT_FILE):
        print(f"[!] Hata: {INPUT_FILE} dosyası bulunamadı! Önce tarama yapıp dosyayı oluşturduğunuzdan emin olun.")
        return

    nicknames = set()
    total_lines = 0

    print(f"[*] {INPUT_FILE} dosyası okunuyor ve nickler ayıklanıyor...")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            total_lines += 1
            # Örnek satır: NICK: OyuncuAdi | IP: 1.2.3.4 | DURUM: ...
            if "NICK:" in line and "|" in line:
                parts = line.split("|")
                for part in parts:
                    if "NICK:" in part:
                        # "NICK: " ifadesini temizle ve boşlukları al
                        nick = part.replace("NICK:", "").strip()
                        if nick and nick != "-":
                            nicknames.add(nick)

    # Temizlenen ve benzersiz hale getirilen nickleri yeni dosyaya yaz
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for nick in sorted(nicknames):
            f.write(nick + "\n")

    print(f"\n[✔] İşlem Başarılı!")
    print(f"    - İncelenen toplam satır: {total_lines}")
    print(f"    - Ayıklanan benzersiz hileci nicki: {len(nicknames)}")
    print(f"    - Kaydedilen dosya: {OUTPUT_FILE}")

if __name__ == "__main__":
    extract_clean_nicknames()
