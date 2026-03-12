"""
Proje kaynak guvenilirligi PDF olusturucu — beyaz/siyah tema
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# --- Font kayit ---
def try_register_font():
    candidates = [
        (r"C:\Windows\Fonts\arial.ttf",   "Arial"),
        (r"C:\Windows\Fonts\arialbd.ttf", "Arial-Bold"),
        (r"C:\Windows\Fonts\ariali.ttf",  "Arial-Italic"),
    ]
    for path, name in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
            except Exception:
                pass

try_register_font()

def pick(reg, bold):
    try:
        pdfmetrics.getFont(reg)
        return reg, bold
    except Exception:
        return "Helvetica", "Helvetica-Bold"

FR, FB = pick("Arial", "Arial-Bold")

# --- Renkler (beyaz tema) ---
BLACK   = colors.HexColor("#1a1a1a")
DARK    = colors.HexColor("#2c2c2c")
MEDIUM  = colors.HexColor("#555555")
MUTED   = colors.HexColor("#888888")
ACCENT  = colors.HexColor("#b85000")   # koyu turuncu — baslik
BLUE    = colors.HexColor("#1a5a8a")   # koyu mavi — alt baslik
GREEN   = colors.HexColor("#1a6b2a")   # koyu yesil — checkmark
BGCARD  = colors.HexColor("#f4f6f8")   # cok acik gri kart
BGHEAD  = colors.HexColor("#e8edf2")   # tablo baslik
BORDER  = colors.HexColor("#ccd4dd")
WHITE   = colors.white

# --- Stiller ---
def S(name, **kw):
    base = dict(fontName=FR, fontSize=10, leading=15,
                textColor=BLACK, spaceAfter=0, spaceBefore=0)
    base.update(kw)
    return ParagraphStyle(name, **base)

sTitle    = S("Title",  fontName=FB,  fontSize=20, textColor=ACCENT,  leading=26, spaceAfter=4)
sSub      = S("Sub",    fontName=FR,  fontSize=10, textColor=MEDIUM,  leading=14)
sH1       = S("H1",     fontName=FB,  fontSize=12, textColor=ACCENT,  leading=17, spaceBefore=20, spaceAfter=6)
sH2       = S("H2",     fontName=FB,  fontSize=10, textColor=BLUE,    leading=15, spaceBefore=10, spaceAfter=4)
sBody     = S("Body",   fontName=FR,  fontSize=9.5, textColor=DARK,   leading=15, spaceAfter=4)
sBold     = S("Bold",   fontName=FB,  fontSize=9.5, textColor=BLACK,  leading=15)
sCheck    = S("Check",  fontName=FB,  fontSize=9.5, textColor=GREEN,  leading=15)
sSmall    = S("Small",  fontName=FR,  fontSize=8,   textColor=MUTED,  leading=13)
sFooter   = S("Footer", fontName=FR,  fontSize=7.5, textColor=MUTED,  leading=12, alignment=1)

def HR():
    return HRFlowable(width="100%", thickness=0.6, color=BORDER,
                      spaceAfter=10, spaceBefore=2)

def reason_table(rows_data, col_w=(4.2*cm, 12.3*cm)):
    """Checkmark sol sutun + aciklama sag sutun tablosu."""
    rows = []
    for title, desc in rows_data:
        rows.append([
            Paragraph(f"✓  {title}", sCheck),
            Paragraph(desc, sBody),
        ])
    t = Table(rows, colWidths=col_w, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), BGCARD),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [BGCARD, WHITE]),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 10),
        ("BOX",           (0,0),(-1,-1), 0.5, BORDER),
        ("LINEBELOW",     (0,0),(-1,-2), 0.3, BORDER),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    return t


# ============================================================
# ICERIK
# ============================================================
def build():
    out = os.path.join(os.path.dirname(__file__), "kaynaklar.pdf")
    doc = SimpleDocTemplate(
        out, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2.2*cm,  bottomMargin=2*cm,
        title="FWI Sistemi — Kullanilan Kaynaklar",
        author="Meteoroloji Muhendisligi Tasarim Projesi",
    )

    story = []

    # Baslik
    story.append(Paragraph("FWI Yangin Erken Uyari Sistemi", sTitle))
    story.append(Paragraph("Kullanilan Kaynaklar ve Guvenilirlik Degerlendirmesi", sSub))
    story.append(Spacer(1, 8))
    story.append(HR())

    # Giris
    story.append(Paragraph("Giris", sH1))
    story.append(Paragraph(
        "Bu belgede, orman yangini erken uyari sisteminin FWI (Fire Weather Index) "
        "bileseni gelistirilirken basvurulan kaynaklar sade bir dille aciklanmaktadir. "
        "Her kaynak icin neden tercih edildigi ve ne olcude guvenilir oldugu ayrica "
        "belirtilmistir.", sBody))

    # ── 1. VAN WAGNER 1987 ──────────────────────────────────
    story.append(Paragraph("1. Temel Formul Kaynagi — Van Wagner (1987)", sH1))

    story.append(Paragraph("Ne?", sH2))
    story.append(Paragraph(
        "C. E. Van Wagner'in 1987 yilinda Kanada Orman Servisi icin yayimladigi "
        "teknik rapordur: <i>Development and Structure of the Canadian Forest Fire "
        "Weather Index System</i> (Forestry Technical Report 35). Bu rapor, FWI "
        "sisteminin alti bileseni olan FFMC, DMC, DC, ISI, BUI ve FWI'yi matematiksel "
        "olarak tanimlayan kurucu belgedir.", sBody))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Neden Guvenilir?", sH2))
    story.append(reason_table([
        ("Resmi devlet kurumu",
         "Kanada Orman Servisi (Canadian Forest Service) tarafindan yayimlanmistir. "
         "Hukumet kurumlarinin teknik raporlari bagimsiz uzmanlar tarafindan gozden gecirilir."),
        ("Dunya genelinde kullanim",
         "Ayni formuller bugun onlarca ulkenin meteoroloji ve orman idarelerinde standart "
         "olarak uygulanmaktadir (Avrupa, Avustralya, Turkiye vb.)."),
        ("Uzun sureli dogrulama",
         "37 yili askin sahada uygulama gecmisine sahiptir. Binlerce gercek yangin olayinda "
         "sonuclar gozlemlerle karsilastirilmistir."),
        ("Akademik atif",
         "Google Scholar'da 1.000'den fazla akademik makale bu raporu kaynak gostermektedir."),
    ]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Sistemdeki Kullanimi", sH2))
    story.append(Paragraph(
        "Projede hesaplanan tum formuller (FFMC guncelleme denklemi, DMC ve DC gun boyu "
        "nem degisimi, ISI/BUI/FWI birlestirme esitlikleri) dogrudan bu rapordan "
        "alinmistir. Raporun Tablo 1 ve Tablo 2'sindeki sabit degerler olan Lf ay "
        "faktorleri ve Le islanma faktorleri de bire bir uygulanmistir.", sBody))

    # ── 2. CFFDRS R PAKETI ──────────────────────────────────
    story.append(Paragraph("2. Dogrulama Kaynagi — cffdrs R Paketi", sH1))

    story.append(Paragraph("Ne?", sH2))
    story.append(Paragraph(
        "Kanada Orman Servisi'nin resmi acik kaynakli yazilimidir. GitHub'da "
        "<i>bcgov/cffdrs</i> deposunda yayimlanan bu paket, R programlama dilinde "
        "Van Wagner (1987) formullerinin referans uygulamasini icerir.", sBody))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Neden Guvenilir?", sH2))
    story.append(reason_table([
        ("Resmi referans uygulama",
         "Kanada hukumetinin kendi formullerini kodladigi pakettir. Formullerin "
         "dogru uygulanip uygulanmadigini herkes kaynak kod uzerinden dogrudan kontrol edebilir."),
        ("Acik kaynak seffaflik",
         "Kodun tamami herkese aciktir; gizli bir kara kutu degil, denetlenebilir "
         "bir referans kaynaktir."),
        ("Surum kontrolu",
         "Git gecmisiyle her degisiklik kayit altindadir; olasi hatalar hizla tespit "
         "edilip duzeltilmektedir."),
    ]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Sistemdeki Kullanimi", sH2))
    story.append(Paragraph(
        "DC hesabinda kullanilan ay faktorleri (Lf) bu paketin kaynak koduyla "
        "dogrulanmistir. Temmuz ayi icin Lf = 6.4 degeri, cffdrs R kodundaki "
        "<i>fl01[7]</i> dizisiyle urtusturunce dogru oldugu kesinlesmistir. "
        "Bunun yaninda Van Wagner referans test girdileri (T = 17 C, H = %42, "
        "W = 25 km/h, r = 0 mm) icin beklenen cikti degerleri bu paket uzerinden "
        "dogrulanmistir.", sBody))

    # ── 3. OPEN-METEO ───────────────────────────────────────
    story.append(Paragraph("3. Hava Verisi Kaynagi — Open-Meteo / ERA5", sH1))

    story.append(Paragraph("Ne?", sH2))
    story.append(Paragraph(
        "Open-Meteo, acik kaynakli ve ucretsiz bir hava durumu API'sidir. "
        "Avrupa Orta Vadeli Hava Tahminleri Merkezi'nin (ECMWF) ERA5 yeniden "
        "analiz veri setini kullanarak dunya genelinde herhangi bir koordinat icin "
        "saatlik meteorolojik verilere erisim saglar.", sBody))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Neden Guvenilir?", sH2))
    story.append(reason_table([
        ("ERA5 altyapisi",
         "Asil veri saglayicisi ECMWF'dir. ERA5, dunyada en cok kullanilan atmosfer "
         "yeniden analiz veri setidir ve onlarca yillik saatlik veriyi kapsar."),
        ("Akademik kalibre",
         "ERA5 verisi binlerce iklim ve meteoroloji arastirmasinda kullanilmistir; "
         "kalitesi uluslararasi bilimsel topluluk tarafindan kabul gormektedir."),
        ("Seffaf metodoloji",
         "Open-Meteo, veri kaynagini ve islem yontemini acikca belgelemektedir."),
        ("Ucretsiz erisim",
         "Akademik ve ticari olmayan kullanim icin tamamen ucretsizdir; "
         "lisans kisitlamasi yoktur."),
    ]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Sistemdeki Kullanimi", sH2))
    story.append(Paragraph(
        "Kullanici koordinat ve tarih girdiginde sistem, Open-Meteo API'sinden "
        "ogle saati (12:00 LST) sicaklik, bagil nem, ruzgar hizi ve yagis verilerini "
        "otomatik olarak cekmektedir. Van Wagner (1987) metodolojisi, FWI "
        "hesaplamalarinda ogle degerlerinin kullanilmasini ongorurmektedir.", sBody))

    # ── OZET TABLO ──────────────────────────────────────────
    story.append(Paragraph("Ozet Karsilastirma", sH1))

    header = [
        Paragraph("Kaynak", sBold),
        Paragraph("Yayimlayan", sBold),
        Paragraph("Kullanim Amaci", sBold),
        Paragraph("Guvenilirlik", sBold),
    ]
    body_data = [
        ["Van Wagner (1987)",        "Kanada Orman Servisi",          "Tum FWI formuller",           "Cok Yuksek"],
        ["cffdrs R paketi",          "Kanada Hukumeti (acik kaynak)", "Formul / katsayi dogrulama",  "Cok Yuksek"],
        ["Open-Meteo / ERA5",        "ECMWF (Avrupa)",                "Gercek zamanli hava verisi",  "Yuksek"],
    ]
    tbl_rows = [header] + [
        [Paragraph(c, sBody) for c in row] for row in body_data
    ]
    t_sum = Table(tbl_rows, colWidths=[4*cm, 5*cm, 5.2*cm, 2.4*cm], hAlign="LEFT")
    t_sum.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  BGHEAD),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, BGCARD]),
        ("FONTNAME",      (0,0),(-1,0),  FB),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("LEADING",       (0,0),(-1,-1), 14),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 10),
        ("BOX",           (0,0),(-1,-1), 0.6, BORDER),
        ("LINEBELOW",     (0,0),(-1,-2), 0.3, BORDER),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(t_sum)
    story.append(Spacer(1, 14))

    # Sonuc
    story.append(HR())
    story.append(Paragraph("Sonuc", sH1))
    story.append(Paragraph(
        "Projede kullanilan uc ana kaynagin tamami ya resmi devlet kurumlari tarafindan "
        "yayimlanmis ya da uluslararasi bilimsel topluluk tarafindan kabul gormustir. "
        "Temel formul kaynagi Van Wagner (1987), 37 yildir dunya standardi olarak "
        "uygulanmaktadir. Dogrulama icin basvurulan cffdrs R paketi, Kanada "
        "hukumetinin kendi referans uygulamasidir. Hava verisi icin tercih edilen "
        "Open-Meteo ise ECMWF'nin ERA5 yeniden analiz urununu temel almaktadir. "
        "Bu kaynak yapisi, projenin bilimsel guvenilirligini en ust duzeyde tutmaktadir.",
        sBody))

    story.append(Spacer(1, 12))

    # Dipnot
    story.append(Paragraph(
        "Kaynakca: Van Wagner, C.E. (1987). Forestry Technical Report 35, Canadian "
        "Forest Service, Ottawa.  |  bcgov/cffdrs, GitHub.  |  "
        "Open-Meteo (open-meteo.com), ERA5 / ECMWF.", sSmall))

    story.append(Spacer(1, 18))
    story.append(HR())
    story.append(Paragraph(
        "Meteoroloji Muhendisligi Tasarim Projesi  |  FWI Yangin Erken Uyari Sistemi  |  2025-2026",
        sFooter))

    doc.build(story)
    return out

if __name__ == "__main__":
    out = build()
    print(f"PDF olusturuldu: {out}")
