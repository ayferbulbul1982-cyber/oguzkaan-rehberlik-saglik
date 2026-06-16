import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from pathlib import Path
from io import BytesIO
import base64
import random

DB_NAME = "ogrenci_saglik.db"
LOGO_PATH = "oguzkaan_logo.png"
PHOTO_DIR = Path("student_photos")
PHOTO_DIR.mkdir(exist_ok=True)

USERS = {
    "mudur": {"password": "1234", "role": "Müdür"},
    "rehber": {"password": "1234", "role": "Rehber Öğretmen"},
    "ogretmen": {"password": "1234", "role": "Öğretmen"},
}


# ---------------- TASARIM ----------------
def apply_design():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #f7f8fb 0%, #eef1f5 100%);
    }
    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    .main .block-container {
        padding-top: 1.2rem;
        max-width: 1320px;
    }
    h1, h2, h3 {
        color: #1f2937;
        letter-spacing: -0.03em;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        padding: 18px;
        border-radius: 18px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    }
    .ok-hero {
        background: linear-gradient(135deg, #111827 0%, #2b2f38 55%, #b91c1c 100%);
        border-radius: 24px;
        padding: 24px 28px;
        margin-bottom: 24px;
        color: white;
        box-shadow: 0 16px 40px rgba(17, 24, 39, 0.18);
        display: flex;
        gap: 22px;
        align-items: center;
    }
    .ok-hero img {
        width: 92px;
        height: 92px;
        object-fit: contain;
        background: white;
        padding: 8px;
        border-radius: 18px;
    }
    .ok-hero-title {
        font-size: 32px;
        font-weight: 900;
        margin: 0;
        letter-spacing: -0.04em;
    }
    .ok-hero-subtitle {
        font-size: 17px;
        opacity: 0.92;
        margin-top: 4px;
        font-weight: 600;
    }
    .ok-student-card {
        border-radius: 20px;
        padding: 18px;
        min-height: 168px;
        background: #ffffff;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.07);
        border: 1px solid #e5e7eb;
        margin-bottom: 10px;
    }
    .ok-student-name {
        font-size: 20px;
        font-weight: 900;
        color: #111827;
        margin-bottom: 4px;
    }
    .ok-student-meta {
        color: #6b7280;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .ok-note {
        color: #4b5563;
        font-size: 13px;
        line-height: 1.45;
    }
    .ok-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-weight: 800;
        font-size: 13px;
        background: #f3f4f6;
        color: #111827;
        border: 1px solid #e5e7eb;
    }
    .ok-badge.high {
        background: #fee2e2;
        color: #991b1b;
        border-color: #fecaca;
    }
    .ok-badge.medium {
        background: #fef3c7;
        color: #92400e;
        border-color: #fde68a;
    }
    .ok-badge.low {
        background: #dcfce7;
        color: #166534;
        border-color: #bbf7d0;
    }
    .stButton button {
        border-radius: 12px;
        font-weight: 800;
        border: 1px solid #d1d5db;
        transition: 0.15s ease;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        border-color: #b91c1c;
        color: #b91c1c;
    }
    div[data-testid="stDataFrame"] {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
    }
    .stTabs [data-baseweb="tab"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 999px;
        padding: 10px 16px;
        font-weight: 700;
    }
    .stTabs [aria-selected="true"] {
        background: #111827 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)


def show_brand_header():
    logo_html = ""
    if Path(LOGO_PATH).exists():
        logo_bytes = Path(LOGO_PATH).read_bytes()
        logo_b64 = base64.b64encode(logo_bytes).decode("utf-8")
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" />'

    st.markdown(f"""
    <div class="ok-hero">
        {logo_html}
        <div>
            <div class="ok-hero-title">Oğuzkaan Koleji</div>
            <div class="ok-hero-subtitle">Öğrenci Rehberlik ve Sağlık Takip Sistemi</div>
            <div style="font-size:13px;opacity:.82;margin-top:6px;">
                Akademik, psikolojik ve fiziksel gelişimi yapay zeka destekli takip sistemi
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------- VERİTABANI ----------------
def connect():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def create_tables():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad TEXT,
        sinif TEXT,
        yas INTEGER,
        saglik_notu TEXT,
        foto TEXT DEFAULT '',
        kan_grubu TEXT DEFAULT '',
        kullandigi_ilaclar TEXT DEFAULT '',
        alerjiler TEXT DEFAULT '',
        kronik_hastaliklar TEXT DEFAULT '',
        acil_kisi TEXT DEFAULT '',
        acil_telefon TEXT DEFAULT ''
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS boy_kilo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        tarih TEXT,
        boy REAL,
        kilo REAL,
        vki REAL,
        not_text TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS rehberlik (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        tarih TEXT,
        ruh_hali TEXT,
        sosyal TEXT,
        ders TEXT,
        not_text TEXT,
        risk TEXT,
        risk_puani INTEGER DEFAULT 0,
        yorum TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS veli_gorusmeleri (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        tarih TEXT,
        veli_adi TEXT,
        gorusme_turu TEXT,
        ozet TEXT,
        sonraki_tarih TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS takip_randevulari (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        tarih TEXT,
        konu TEXT,
        durum TEXT DEFAULT 'Bekliyor',
        not_text TEXT
    )
    """)

    # Eski veritabanı varsa kolonları tamamla
    extra_cols = {
        "students": {
            "foto": "TEXT DEFAULT ''",
            "kan_grubu": "TEXT DEFAULT ''",
            "kullandigi_ilaclar": "TEXT DEFAULT ''",
            "alerjiler": "TEXT DEFAULT ''",
            "kronik_hastaliklar": "TEXT DEFAULT ''",
            "acil_kisi": "TEXT DEFAULT ''",
            "acil_telefon": "TEXT DEFAULT ''"
        },
        "rehberlik": {
            "risk_puani": "INTEGER DEFAULT 0"
        }
    }

    for table, cols in extra_cols.items():
        for col, col_type in cols.items():
            try:
                c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError:
                pass

    conn.commit()
    conn.close()


# ---------------- YARDIMCI FONKSİYONLAR ----------------
def calculate_vki(boy, kilo):
    return round(kilo / ((boy / 100) ** 2), 2)


def bmi_category(vki):
    if vki < 18.5:
        return "Zayıf"
    elif vki < 25:
        return "Normal"
    elif vki < 30:
        return "Fazla Kilolu"
    return "Obezite Riski"


def risk_from_score(score):
    if score >= 70:
        return "Yüksek"
    elif score >= 40:
        return "Orta"
    return "Düşük"


def create_ai_comment(risk, score):
    if risk == "Yüksek":
        return f"Öğrencide dikkat gerektiren sosyal veya duygusal risk göstergeleri vardır. Risk puanı {score}/100. Rehberlik servisi yakın takip yapmalı, veli görüşmesi planlamalı ve gerekirse uzman desteğine yönlendirmelidir."
    elif risk == "Orta":
        return f"Öğrencide takip edilmesi gereken bazı değişimler görülmektedir. Risk puanı {score}/100. Düzenli görüşme yapılması ve veliyle iletişim kurulması önerilir."
    return f"Belirgin yüksek risk göstergesi görülmemektedir. Risk puanı {score}/100. Rutin aylık takip devam edebilir."


def get_students():
    conn = connect()
    df = pd.read_sql_query("SELECT * FROM students ORDER BY id", conn)
    conn.close()
    return df


def get_student(student_id):
    conn = connect()
    df = pd.read_sql_query("SELECT * FROM students WHERE id=?", conn, params=(student_id,))
    conn.close()
    if df.empty:
        return None
    return df.iloc[0]


def get_health(student_id):
    conn = connect()
    df = pd.read_sql_query(
        "SELECT id, tarih, boy, kilo, vki, not_text FROM boy_kilo WHERE student_id=? ORDER BY tarih",
        conn,
        params=(student_id,)
    )
    conn.close()
    return df


def get_guidance(student_id):
    conn = connect()
    df = pd.read_sql_query(
        "SELECT id, tarih, ruh_hali, sosyal, ders, not_text, risk, COALESCE(risk_puani, 0) AS risk_puani, yorum FROM rehberlik WHERE student_id=? ORDER BY tarih",
        conn,
        params=(student_id,)
    )
    conn.close()
    return df


def get_parent_meetings(student_id):
    conn = connect()
    df = pd.read_sql_query(
        "SELECT id, tarih, veli_adi, gorusme_turu, ozet, sonraki_tarih FROM veli_gorusmeleri WHERE student_id=? ORDER BY tarih DESC",
        conn,
        params=(student_id,)
    )
    conn.close()
    return df


def get_followups(student_id=None, only_pending=False):
    conn = connect()
    query = """
    SELECT t.id, t.student_id, s.ad, s.sinif, t.tarih, t.konu, t.durum, t.not_text
    FROM takip_randevulari t
    JOIN students s ON s.id = t.student_id
    """
    params = []
    cond = []
    if student_id is not None:
        cond.append("t.student_id=?")
        params.append(student_id)
    if only_pending:
        cond.append("t.durum='Bekliyor'")
    if cond:
        query += " WHERE " + " AND ".join(cond)
    query += " ORDER BY t.tarih ASC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def add_student(ad, sinif, yas, saglik_notu, kan_grubu, kullandigi_ilaclar, alerjiler, kronik_hastaliklar, acil_kisi, acil_telefon):
    conn = connect()
    c = conn.cursor()
    c.execute("""
    INSERT INTO students
    (ad, sinif, yas, saglik_notu, kan_grubu, kullandigi_ilaclar, alerjiler, kronik_hastaliklar, acil_kisi, acil_telefon)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ad, sinif, yas, saglik_notu, kan_grubu, kullandigi_ilaclar, alerjiler, kronik_hastaliklar, acil_kisi, acil_telefon))
    conn.commit()
    conn.close()


def update_student(student_id, ad, sinif, yas, saglik_notu, kan_grubu, kullandigi_ilaclar, alerjiler, kronik_hastaliklar, acil_kisi, acil_telefon):
    conn = connect()
    c = conn.cursor()
    c.execute("""
    UPDATE students SET ad=?, sinif=?, yas=?, saglik_notu=?, kan_grubu=?, kullandigi_ilaclar=?,
    alerjiler=?, kronik_hastaliklar=?, acil_kisi=?, acil_telefon=? WHERE id=?
    """, (ad, sinif, yas, saglik_notu, kan_grubu, kullandigi_ilaclar, alerjiler, kronik_hastaliklar, acil_kisi, acil_telefon, student_id))
    conn.commit()
    conn.close()


def delete_student(student_id):
    conn = connect()
    c = conn.cursor()
    student = get_student(student_id)
    if student is not None and str(student.get("foto", "")).strip():
        try:
            Path(student["foto"]).unlink(missing_ok=True)
        except Exception:
            pass
    c.execute("DELETE FROM boy_kilo WHERE student_id=?", (student_id,))
    c.execute("DELETE FROM rehberlik WHERE student_id=?", (student_id,))
    c.execute("DELETE FROM veli_gorusmeleri WHERE student_id=?", (student_id,))
    c.execute("DELETE FROM takip_randevulari WHERE student_id=?", (student_id,))
    c.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()


def save_uploaded_photo(student_id, uploaded_file):
    ext = uploaded_file.name.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        ext = "png"
    path = PHOTO_DIR / f"student_{student_id}.{ext}"
    path.write_bytes(uploaded_file.getbuffer())

    conn = connect()
    c = conn.cursor()
    c.execute("UPDATE students SET foto=? WHERE id=?", (str(path), student_id))
    conn.commit()
    conn.close()


def add_health(student_id, tarih, boy, kilo, not_text):
    vki = calculate_vki(boy, kilo)
    conn = connect()
    c = conn.cursor()
    c.execute("""
    INSERT INTO boy_kilo (student_id, tarih, boy, kilo, vki, not_text)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (student_id, str(tarih), boy, kilo, vki, not_text))
    conn.commit()
    conn.close()


def calculate_risk_score(ruh_hali, sosyal, ders, not_text, health_df=None):
    score = 10
    text = f"{ruh_hali} {sosyal} {ders} {not_text}".lower()

    if ruh_hali in ["Üzgün", "Kaygılı", "İçe kapanık", "Öfkeli"]:
        score += 15
    if sosyal in ["Zayıf", "Yalnız kalıyor", "Arkadaş problemi var"]:
        score += 20
    if ders in ["Azalmış", "Çok düşük"]:
        score += 15

    medium_words = ["motivasyon", "stres", "kaygı", "yalnız", "özgüven", "ailevi"]
    high_words = ["zorbalık", "panik", "şiddet", "kendine zarar", "intihar", "ağlama"]

    for word in medium_words:
        if word in text:
            score += 5
    for word in high_words:
        if word in text:
            score += 20

    if health_df is not None and not health_df.empty:
        h_ai = create_health_ai_comment(health_df)
        if h_ai["risk"] == "Orta":
            score += 10
        elif h_ai["risk"] == "Yüksek":
            score += 20

    return min(100, max(0, score))


def add_guidance(student_id, tarih, ruh_hali, sosyal, ders, not_text):
    health_df = get_health(student_id)
    score = calculate_risk_score(ruh_hali, sosyal, ders, not_text, health_df)
    risk = risk_from_score(score)
    yorum = create_ai_comment(risk, score)
    conn = connect()
    c = conn.cursor()
    c.execute("""
    INSERT INTO rehberlik (student_id, tarih, ruh_hali, sosyal, ders, not_text, risk, risk_puani, yorum)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (student_id, str(tarih), ruh_hali, sosyal, ders, not_text, risk, score, yorum))
    conn.commit()
    conn.close()


def add_parent_meeting(student_id, tarih, veli_adi, gorusme_turu, ozet, sonraki_tarih):
    conn = connect()
    c = conn.cursor()
    c.execute("""
    INSERT INTO veli_gorusmeleri (student_id, tarih, veli_adi, gorusme_turu, ozet, sonraki_tarih)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (student_id, str(tarih), veli_adi, gorusme_turu, ozet, str(sonraki_tarih)))
    conn.commit()
    conn.close()


def add_followup(student_id, tarih, konu, not_text):
    conn = connect()
    c = conn.cursor()
    c.execute("""
    INSERT INTO takip_randevulari (student_id, tarih, konu, durum, not_text)
    VALUES (?, ?, ?, 'Bekliyor', ?)
    """, (student_id, str(tarih), konu, not_text))
    conn.commit()
    conn.close()


def complete_followup(followup_id):
    conn = connect()
    c = conn.cursor()
    c.execute("UPDATE takip_randevulari SET durum='Tamamlandı' WHERE id=?", (followup_id,))
    conn.commit()
    conn.close()


def get_latest_risk_students():
    conn = connect()
    df = pd.read_sql_query("""
    SELECT s.id, s.ad, s.sinif, s.yas, s.foto, r.tarih, r.risk, COALESCE(r.risk_puani, 0) AS risk_puani, r.yorum
    FROM students s
    LEFT JOIN rehberlik r ON s.id = r.student_id
    WHERE r.tarih = (
        SELECT MAX(r2.tarih)
        FROM rehberlik r2
        WHERE r2.student_id = s.id
    )
    ORDER BY COALESCE(r.risk_puani, 0) DESC, s.ad
    """, conn)
    conn.close()
    return df


# ---------------- YAPAY ZEKA YORUMLARI ----------------
def create_health_ai_comment(health_df):
    if health_df.empty:
        return {
            "risk": "Kayıt Yok",
            "kategori": "Kayıt Yok",
            "yorum": "Henüz boy-kilo kaydı yok. Sağlık analizi için aylık ölçüm girilmelidir.",
            "son_vki": None,
            "kilo_degisim": None,
            "boy_degisim": None
        }

    df = health_df.copy()
    df["tarih"] = pd.to_datetime(df["tarih"])
    df = df.sort_values("tarih")
    last = df.iloc[-1]
    son_vki = float(last["vki"])
    kategori = bmi_category(son_vki)

    kilo_degisim = 0
    boy_degisim = 0
    if len(df) >= 2:
        prev = df.iloc[-2]
        kilo_degisim = float(last["kilo"]) - float(prev["kilo"])
        boy_degisim = float(last["boy"]) - float(prev["boy"])

    risk_puan = 0
    if son_vki < 18.5 or son_vki >= 25:
        risk_puan += 1
    if son_vki >= 30:
        risk_puan += 2
    if abs(kilo_degisim) >= 4:
        risk_puan += 1
    if abs(kilo_degisim) >= 7:
        risk_puan += 2

    risk = "Yüksek" if risk_puan >= 3 else "Orta" if risk_puan >= 1 else "Düşük"

    yorum = f"Son ölçüme göre VKİ {son_vki:.2f}, kategori '{kategori}'. "
    if kategori == "Zayıf":
        yorum += "Öğrencinin beslenme alışkanlıkları takip edilmeli. "
    elif kategori == "Normal":
        yorum += "Boy-kilo dengesi normal aralıkta görünmektedir. "
    elif kategori == "Fazla Kilolu":
        yorum += "Kilo artışı eğilimi takip edilmeli, fiziksel aktivite ve beslenme düzeni değerlendirilebilir. "
    else:
        yorum += "Kilo durumu yakından takip edilmeli, gerekirse sağlık uzmanına yönlendirme değerlendirilebilir. "

    if len(df) >= 2:
        yorum += f"Önceki aya göre kilo değişimi {kilo_degisim:+.1f} kg, boy değişimi {boy_degisim:+.1f} cm. "
        if abs(kilo_degisim) >= 7:
            yorum += "Kısa sürede belirgin kilo değişimi vardır. "
        elif abs(kilo_degisim) >= 4:
            yorum += "Kilo değişimi dikkat çekicidir. "
    else:
        yorum += "Değişim analizi için en az iki kayıt gereklidir. "

    yorum += "Bu yorum tıbbi tanı değildir; rehberlik ve erken farkındalık amacıyla oluşturulmuştur."

    return {
        "risk": risk,
        "kategori": kategori,
        "yorum": yorum,
        "son_vki": son_vki,
        "kilo_degisim": kilo_degisim,
        "boy_degisim": boy_degisim
    }


def create_combined_ai_analysis(student_id):
    student = get_student(student_id)
    health_df = get_health(student_id)
    guidance_df = get_guidance(student_id)
    parent_df = get_parent_meetings(student_id)
    follow_df = get_followups(student_id)

    points = []
    score = 10

    if health_df.empty:
        points.append("Boy-kilo kaydı olmadığı için fiziksel gelişim analizi sınırlıdır.")
    else:
        h = health_df.copy()
        h["tarih"] = pd.to_datetime(h["tarih"])
        h = h.sort_values("tarih").tail(12)
        first = h.iloc[0]
        last = h.iloc[-1]
        kilo_change = float(last["kilo"]) - float(first["kilo"])
        boy_change = float(last["boy"]) - float(first["boy"])
        vki_change = float(last["vki"]) - float(first["vki"])
        health_ai = create_health_ai_comment(h)

        points.append(f"Son {len(h)} sağlık kaydında boy değişimi {boy_change:+.1f} cm, kilo değişimi {kilo_change:+.1f} kg, VKİ değişimi {vki_change:+.2f}.")
        points.append(health_ai["yorum"])

        if health_ai["risk"] == "Orta":
            score += 12
        elif health_ai["risk"] == "Yüksek":
            score += 25

        if abs(kilo_change) >= 8:
            score += 15
            points.append("12 aylık süreçte belirgin kilo değişimi olduğu için fiziksel gelişim yakından izlenmelidir.")
        elif abs(kilo_change) >= 5:
            score += 8
            points.append("Kilo değişimi dikkat çekici düzeydedir.")

    if guidance_df.empty:
        points.append("Rehberlik görüşme kaydı olmadığı için psikososyal analiz sınırlıdır.")
    else:
        g = guidance_df.copy()
        g["tarih"] = pd.to_datetime(g["tarih"])
        g = g.sort_values("tarih").tail(12)

        high_count = len(g[g["risk"] == "Yüksek"])
        mid_count = len(g[g["risk"] == "Orta"])
        low_count = len(g[g["risk"] == "Düşük"])
        avg_score = int(g["risk_puani"].mean()) if "risk_puani" in g.columns else 0

        points.append(f"Son {len(g)} rehberlik kaydında {high_count} yüksek, {mid_count} orta, {low_count} düşük risk kaydı var.")
        points.append(f"Rehberlik risk puanı ortalaması {avg_score}/100.")

        score += min(30, int(avg_score * 0.25))
        if high_count >= 2:
            score += 15
            points.append("Birden fazla yüksek risk kaydı olduğu için öğrenci öncelikli takip listesinde değerlendirilmelidir.")
        elif high_count == 1:
            score += 10
            points.append("En az bir yüksek risk kaydı bulunduğu için yakın takip önerilir.")

    if parent_df.empty:
        score += 5
        points.append("Veli görüşme kaydı yok. Risk orta veya yüksekse veli iletişimi planlanabilir.")
    else:
        points.append(f"{len(parent_df)} veli görüşmesi kaydı var. Son görüşme tarihi: {parent_df.iloc[0]['tarih']}.")

    if follow_df.empty:
        points.append("Takip randevusu yok.")
    else:
        pending = follow_df[follow_df["durum"] == "Bekliyor"]
        done = follow_df[follow_df["durum"] == "Tamamlandı"]
        points.append(f"Takip randevularında {len(pending)} bekleyen, {len(done)} tamamlanan kayıt var.")
        if len(pending) >= 2:
            score += 10
        elif len(pending) == 1:
            score += 5

    score = max(0, min(100, score))
    risk = risk_from_score(score)

    if risk == "Yüksek":
        final = "Genel değerlendirme: Öğrenci yüksek öncelikli takip grubunda değerlendirilmelidir."
    elif risk == "Orta":
        final = "Genel değerlendirme: Öğrencide izlenmesi gereken bazı göstergeler vardır."
    else:
        final = "Genel değerlendirme: Mevcut kayıtlara göre belirgin yüksek risk görünmemektedir."

    points.append(final)
    points.append("Not: Bu sistem tıbbi veya psikolojik tanı koymaz; rehberlik ve erken farkındalık amacıyla destek sağlar.")

    return {"score": score, "risk": risk, "analysis": "\n\n".join(points)}


# ---------------- PDF ----------------
def make_pdf_bytes(student, health_df, guidance_df):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
    except Exception:
        return None

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    def line(text, size=10, gap=15):
        nonlocal y
        if y < 2 * cm:
            p.showPage()
            y = height - 2 * cm
        p.setFont("Helvetica", size)
        p.drawString(2 * cm, y, str(text)[:115])
        y -= gap

    line("Oguzkaan Koleji - Ogrenci Rehberlik ve Saglik Takip Sistemi Raporu", 14, 24)
    line(f"Ad Soyad: {student['ad']}")
    line(f"Sinif: {student['sinif']}")
    line(f"Yas: {student['yas']}")
    line(f"Kan Grubu: {student.get('kan_grubu', '') or '-'}")
    line(f"Kullandigi Ilaclar: {student.get('kullandigi_ilaclar', '') or '-'}")
    line(f"Alerjiler: {student.get('alerjiler', '') or '-'}")
    line(f"Kronik Hastaliklar: {student.get('kronik_hastaliklar', '') or '-'}")
    line(f"Saglik Notu: {student.get('saglik_notu', '') or '-'}", 10, 22)

    line("Son Boy-Kilo Kayitlari", 12, 18)
    for _, r in health_df.tail(6).iterrows():
        line(f"{r['tarih']} | Boy: {r['boy']} | Kilo: {r['kilo']} | VKI: {r['vki']} | Not: {r['not_text']}", 8, 12)

    y -= 8
    line("Son Rehberlik Kayitlari", 12, 18)
    for _, r in guidance_df.tail(6).iterrows():
        line(f"{r['tarih']} | Ruh: {r['ruh_hali']} | Sosyal: {r['sosyal']} | Ders: {r['ders']} | Risk: {r['risk']} | Puan: {r['risk_puani']}", 8, 12)

    p.save()
    buffer.seek(0)
    return buffer.getvalue()


# ---------------- ÖRNEK VERİ ----------------
def seed_data():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM students")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    students = [
        ("Ali Yılmaz", "5-A", 11), ("Ayşe Demir", "6-B", 12), ("Mehmet Kaya", "7-A", 13),
        ("Zeynep Şahin", "8-C", 14), ("Eren Çelik", "6-A", 12), ("Elif Aydın", "5-B", 11),
        ("Mert Koç", "7-C", 13), ("Defne Arslan", "8-A", 14), ("Can Özkan", "6-C", 12),
        ("Nisa Yıldız", "7-B", 13)
    ]

    bloods = ["A Rh+", "A Rh-", "B Rh+", "B Rh-", "AB Rh+", "0 Rh+", "0 Rh-"]
    low_notes = ["Derslere düzenli katılıyor.", "Arkadaş ilişkileri olumlu.", "Genel durumu normal.", "Okula uyumu iyi."]
    mid_notes = ["Motivasyon düşüklüğü gözlendi.", "Arkadaş ilişkilerinde zaman zaman sorun yaşıyor.", "Sınav kaygısı yüksek.", "Derslere ilgisi azalmış."]
    high_notes = ["Sınıfta içine kapanık davranıyor.", "Yalnız kalmayı tercih ediyor.", "Ailevi sebeplerden dolayı stresli.", "Özgüveni düşük gözlemlendi."]

    for ad, sinif, yas in students:
        add_student(
            ad, sinif, yas,
            "Düzenli takip önerilir.",
            random.choice(bloods),
            random.choice(["Yok", "Vitamin desteği", "Alerji ilacı", ""]),
            random.choice(["Yok", "Polen", "Toz", "Fıstık"]),
            random.choice(["Yok", "Astım takibi", "Migren takibi"]),
            "Veli",
            "05xx xxx xx xx"
        )
        student_id = int(get_students().iloc[-1]["id"])

        boy = random.randint(135, 165)
        kilo = random.randint(32, 72)

        for ay in range(1, 13):
            boy += random.choice([0, 0, 1])
            kilo += random.choice([-2, -1, 0, 1, 2, 3])
            vki = calculate_vki(boy, kilo)

            if vki < 18.5:
                fiziksel_not = "Zayıf görünüyor, beslenme takibi önerilir."
            elif vki < 25:
                fiziksel_not = "Fiziksel gelişim normal aralıkta."
            else:
                fiziksel_not = "Kilo artışı takip edilmeli."

            c.execute("""
            INSERT INTO boy_kilo (student_id, tarih, boy, kilo, vki, not_text)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (student_id, f"2026-{ay:02d}-01", boy, kilo, vki, fiziksel_not))

        for ay in range(1, 13):
            tip = random.choice(["dusuk", "dusuk", "dusuk", "orta", "orta", "yuksek"])
            if tip == "dusuk":
                ruh = random.choice(["İyi", "Normal"])
                sosyal = random.choice(["İyi", "Normal"])
                ders = random.choice(["İyi", "Normal"])
                not_text = random.choice(low_notes)
            elif tip == "orta":
                ruh = random.choice(["Üzgün", "Kaygılı"])
                sosyal = random.choice(["Normal", "Zayıf"])
                ders = random.choice(["Normal", "Azalmış"])
                not_text = random.choice(mid_notes)
            else:
                ruh = random.choice(["İçe kapanık", "Öfkeli", "Kaygılı"])
                sosyal = random.choice(["Yalnız kalıyor", "Arkadaş problemi var"])
                ders = random.choice(["Azalmış", "Çok düşük"])
                not_text = random.choice(high_notes)

            score = calculate_risk_score(ruh, sosyal, ders, not_text, get_health(student_id))
            risk = risk_from_score(score)
            yorum = create_ai_comment(risk, score)

            c.execute("""
            INSERT INTO rehberlik (student_id, tarih, ruh_hali, sosyal, ders, not_text, risk, risk_puani, yorum)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (student_id, f"2026-{ay:02d}-15", ruh, sosyal, ders, not_text, risk, score, yorum))

    conn.commit()
    conn.close()


# ---------------- GÖRSEL BİLEŞENLER ----------------
def show_student_photo(student, width=150):
    photo = str(student.get("foto", "") or "").strip()
    if photo and Path(photo).exists():
        st.image(photo, width=width)
    else:
        st.markdown(
            f"""
            <div style="width:{width}px;height:{width}px;border-radius:16px;background:#eef2f6;
            border:1px solid #d6dde6;display:flex;align-items:center;justify-content:center;
            color:#7a8696;font-weight:bold;text-align:center;">Fotoğraf Yok</div>
            """,
            unsafe_allow_html=True
        )


def student_card(row):
    risk = row.get("risk", "Kayıt Yok")
    score = int(row.get("risk_puani", 0))
    border = "#ef4444" if risk == "Yüksek" else "#f59e0b" if risk == "Orta" else "#22c55e"
    badge_cls = "high" if risk == "Yüksek" else "medium" if risk == "Orta" else "low"
    yorum = str(row.get("yorum", ""))
    if len(yorum) > 120:
        yorum = yorum[:120] + "..."

    st.markdown(
        f"""
        <div class="ok-student-card" style="border-top:5px solid {border};">
            <div class="ok-student-name">{row['ad']}</div>
            <div class="ok-student-meta">{row['sinif']} · {row['yas']} yaş</div>
            <span class="ok-badge {badge_cls}">Risk: {risk} / {score}/100</span>
            <div class="ok-note" style="margin-top:12px;">{yorum}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def open_student(student_id):
    st.session_state.selected_student_id = int(student_id)
    st.session_state.menu = "Öğrenci Detay"
    st.rerun()


# ---------------- GİRİŞ ----------------
def login_screen():
    show_brand_header()
    st.subheader("Sisteme Giriş")
    username = st.text_input("Kullanıcı adı")
    password = st.text_input("Şifre", type="password")

    if st.button("Giriş"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = USERS[username]["role"]
            st.session_state.menu = "Ana Panel"
            st.session_state.selected_student_id = None
            st.rerun()
        else:
            st.error("Kullanıcı adı veya şifre hatalı.")


# ---------------- ÖĞRENCİ DETAY ----------------
def student_detail_page(student_id, role):
    student = get_student(student_id)
    if student is None:
        st.error("Öğrenci bulunamadı.")
        return

    if st.button("← Ana panele dön"):
        st.session_state.menu = "Ana Panel"
        st.session_state.selected_student_id = None
        st.rerun()

    col_photo, col_info = st.columns([1, 3])

    with col_photo:
        show_student_photo(student, width=190)
        if role in ["Müdür", "Rehber Öğretmen"]:
            uploaded = st.file_uploader("Fotoğraf yükle", type=["png", "jpg", "jpeg", "webp"], key=f"photo_{student_id}")
            if uploaded is not None:
                save_uploaded_photo(student_id, uploaded)
                st.success("Fotoğraf yüklendi.")
                st.rerun()

    with col_info:
        st.title(student["ad"])
        st.write(f"**Sınıf:** {student['sinif']}")
        st.write(f"**Yaş:** {student['yas']}")
        st.write(f"**Kan Grubu:** {student.get('kan_grubu', '') or '-'}")
        st.write(f"**Kullandığı İlaçlar:** {student.get('kullandigi_ilaclar', '') or '-'}")
        st.write(f"**Alerjiler:** {student.get('alerjiler', '') or '-'}")
        st.write(f"**Kronik Hastalıklar:** {student.get('kronik_hastaliklar', '') or '-'}")
        st.write(f"**Acil Durum Kişisi:** {student.get('acil_kisi', '') or '-'}")
        st.write(f"**Acil Telefon:** {student.get('acil_telefon', '') or '-'}")
        st.write(f"**Sağlık Notu:** {student.get('saglik_notu', '') or '-'}")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "Boy-Kilo", "12 Aylık Gelişim", "Yapay Zeka Analizi", "Rehberlik",
        "Veli Görüşmeleri", "Takip Randevuları", "Rapor", "Düzenle/Sil"
    ])

    with tab1:
        if role in ["Müdür", "Rehber Öğretmen"]:
            st.subheader("Aylık Boy-Kilo Girişi")
            tarih = st.date_input("Tarih", date.today(), key=f"hdate_{student_id}")
            boy = st.number_input("Boy (cm)", min_value=50.0, max_value=250.0, value=150.0, key=f"height_{student_id}")
            kilo = st.number_input("Kilo (kg)", min_value=10.0, max_value=250.0, value=45.0, key=f"weight_{student_id}")
            not_text = st.text_input("Fiziksel Not", key=f"hnote_{student_id}")

            if st.button("Boy-Kilo Kaydet", key=f"save_health_{student_id}"):
                add_health(student_id, tarih, boy, kilo, not_text)
                st.success("Boy-kilo kaydı eklendi")
                st.rerun()

        health_df = get_health(student_id)
        st.dataframe(health_df, use_container_width=True)

    with tab2:
        st.subheader("12 Aylık Gelişim Grafikleri")
        health_df = get_health(student_id).tail(12)
        guidance_df = get_guidance(student_id).tail(12)

        if not health_df.empty:
            h = health_df.copy()
            h["tarih"] = pd.to_datetime(h["tarih"])
            h = h.set_index("tarih")
            st.write("### Boy-Kilo Gelişimi")
            st.line_chart(h[["boy", "kilo"]])
            st.write("### VKİ Gelişimi")
            st.line_chart(h[["vki"]])

            first = h.iloc[0]
            last = h.iloc[-1]
            c1, c2, c3 = st.columns(3)
            c1.metric("Boy Değişimi", f"{float(last['boy']) - float(first['boy']):+.1f} cm")
            c2.metric("Kilo Değişimi", f"{float(last['kilo']) - float(first['kilo']):+.1f} kg")
            c3.metric("VKİ Değişimi", f"{float(last['vki']) - float(first['vki']):+.2f}")
        else:
            st.info("Boy-kilo kaydı yok.")

        if not guidance_df.empty:
            g = guidance_df.copy()
            g["tarih"] = pd.to_datetime(g["tarih"])
            g = g.set_index("tarih")
            st.write("### Rehberlik Risk Puanı")
            st.line_chart(g[["risk_puani"]])
        else:
            st.info("Rehberlik kaydı yok.")

    with tab3:
        st.subheader("Yapay Zeka Birleşik Analizi")
        analysis = create_combined_ai_analysis(student_id)
        c1, c2 = st.columns(2)
        c1.metric("Birleşik Risk Puanı", f"{analysis['score']}/100")
        c2.metric("Risk Seviyesi", analysis["risk"])

        if analysis["risk"] == "Yüksek":
            st.error(analysis["analysis"])
        elif analysis["risk"] == "Orta":
            st.warning(analysis["analysis"])
        else:
            st.success(analysis["analysis"])

        st.divider()
        st.subheader("Sağlık Yorumu")
        h_ai = create_health_ai_comment(get_health(student_id))
        if h_ai["risk"] == "Yüksek":
            st.error(h_ai["yorum"])
        elif h_ai["risk"] == "Orta":
            st.warning(h_ai["yorum"])
        else:
            st.success(h_ai["yorum"])

    with tab4:
        if role in ["Müdür", "Rehber Öğretmen"]:
            st.subheader("Aylık Rehberlik Görüşmesi")
            r_tarih = st.date_input("Görüşme Tarihi", date.today(), key=f"gdate_{student_id}")
            ruh_hali = st.selectbox("Ruh Hali", ["İyi", "Normal", "Üzgün", "Kaygılı", "İçe kapanık", "Öfkeli"], key=f"mood_{student_id}")
            sosyal = st.selectbox("Sosyal İlişkiler", ["İyi", "Normal", "Zayıf", "Yalnız kalıyor", "Arkadaş problemi var"], key=f"social_{student_id}")
            ders = st.selectbox("Ders İlgisi", ["İyi", "Normal", "Azalmış", "Çok düşük"], key=f"lesson_{student_id}")
            gorusme_notu = st.text_area("Görüşme Notu", key=f"gnote_{student_id}")

            if st.button("Rehberlik Kaydı Ekle", key=f"save_guidance_{student_id}"):
                add_guidance(student_id, r_tarih, ruh_hali, sosyal, ders, gorusme_notu)
                st.success("Rehberlik kaydı eklendi")
                st.rerun()

        guidance_df = get_guidance(student_id)
        st.dataframe(guidance_df, use_container_width=True)

    with tab5:
        st.subheader("Veli Görüşmeleri")
        if role in ["Müdür", "Rehber Öğretmen"]:
            v_tarih = st.date_input("Görüşme Tarihi", date.today(), key=f"parent_date_{student_id}")
            veli_adi = st.text_input("Veli Adı", key=f"parent_name_{student_id}")
            gorusme_turu = st.selectbox("Görüşme Türü", ["Telefon", "Yüz yüze", "Online", "Mesaj"], key=f"parent_type_{student_id}")
            ozet = st.text_area("Görüşme Özeti", key=f"parent_summary_{student_id}")
            sonraki_tarih = st.date_input("Sonraki Görüşme Tarihi", date.today(), key=f"parent_next_{student_id}")

            if st.button("Veli Görüşmesini Kaydet", key=f"save_parent_{student_id}"):
                add_parent_meeting(student_id, v_tarih, veli_adi, gorusme_turu, ozet, sonraki_tarih)
                st.success("Veli görüşmesi kaydedildi.")
                st.rerun()

        st.dataframe(get_parent_meetings(student_id), use_container_width=True)

    with tab6:
        st.subheader("Takip Randevuları")
        if role in ["Müdür", "Rehber Öğretmen"]:
            t_tarih = st.date_input("Takip Tarihi", date.today(), key=f"follow_date_{student_id}")
            konu = st.text_input("Takip Konusu", key=f"follow_subject_{student_id}")
            takip_not = st.text_area("Takip Notu", key=f"follow_note_{student_id}")

            if st.button("Takip Randevusu Oluştur", key=f"save_follow_{student_id}"):
                add_followup(student_id, t_tarih, konu, takip_not)
                st.success("Takip randevusu oluşturuldu.")
                st.rerun()

        follow_df = get_followups(student_id)
        st.dataframe(follow_df, use_container_width=True)

        bekleyen = follow_df[follow_df["durum"] == "Bekliyor"] if not follow_df.empty else pd.DataFrame()
        if not bekleyen.empty and role in ["Müdür", "Rehber Öğretmen"]:
            secili_takip = st.selectbox(
                "Tamamlanacak randevu",
                bekleyen["id"].tolist(),
                format_func=lambda x: f"#{x} - " + bekleyen[bekleyen["id"] == x].iloc[0]["konu"],
                key=f"complete_select_{student_id}"
            )
            if st.button("Seçili Randevuyu Tamamlandı Yap", key=f"complete_follow_{student_id}"):
                complete_followup(secili_takip)
                st.success("Randevu tamamlandı.")
                st.rerun()

    with tab7:
        health_df = get_health(student_id)
        guidance_df = get_guidance(student_id)
        st.subheader("Öğrenci Raporu")
        st.write("### Boy-Kilo Kayıtları")
        st.dataframe(health_df, use_container_width=True)
        st.write("### Rehberlik Kayıtları")
        st.dataframe(guidance_df, use_container_width=True)

        pdf_bytes = make_pdf_bytes(student, health_df, guidance_df)
        if pdf_bytes:
            st.download_button(
                "PDF Rapor İndir",
                data=pdf_bytes,
                file_name=f"{student['ad'].replace(' ', '_')}_rapor.pdf",
                mime="application/pdf",
                key=f"pdf_{student_id}"
            )
        else:
            st.warning("PDF için reportlab gerekli. Kurmak için: pip install reportlab")

    with tab8:
        if role == "Müdür":
            st.subheader("Öğrenci Düzenle")
            blood_options = ["", "A Rh+", "A Rh-", "B Rh+", "B Rh-", "AB Rh+", "AB Rh-", "0 Rh+", "0 Rh-"]
            current_blood = student.get("kan_grubu", "") if student.get("kan_grubu", "") in blood_options else ""

            new_ad = st.text_input("Ad Soyad", value=student["ad"], key=f"edit_name_{student_id}")
            new_sinif = st.text_input("Sınıf", value=student["sinif"], key=f"edit_class_{student_id}")
            new_yas = st.number_input("Yaş", min_value=5, max_value=25, value=int(student["yas"]), key=f"edit_age_{student_id}")
            new_saglik = st.text_area("Sağlık Notu", value=student.get("saglik_notu", "") or "", key=f"edit_note_{student_id}")
            new_kan = st.selectbox("Kan Grubu", blood_options, index=blood_options.index(current_blood), key=f"edit_blood_{student_id}")
            new_ilac = st.text_area("Kullandığı İlaçlar", value=student.get("kullandigi_ilaclar", "") or "", key=f"edit_meds_{student_id}")
            new_alerji = st.text_area("Alerjiler", value=student.get("alerjiler", "") or "", key=f"edit_allergy_{student_id}")
            new_kronik = st.text_area("Kronik Hastalıklar", value=student.get("kronik_hastaliklar", "") or "", key=f"edit_chronic_{student_id}")
            new_acil_kisi = st.text_input("Acil Durum Kişisi", value=student.get("acil_kisi", "") or "", key=f"edit_emergency_person_{student_id}")
            new_acil_tel = st.text_input("Acil Durum Telefonu", value=student.get("acil_telefon", "") or "", key=f"edit_emergency_phone_{student_id}")

            if st.button("Bilgileri Güncelle", key=f"update_{student_id}"):
                update_student(student_id, new_ad, new_sinif, new_yas, new_saglik, new_kan, new_ilac, new_alerji, new_kronik, new_acil_kisi, new_acil_tel)
                st.success("Öğrenci bilgileri güncellendi")
                st.rerun()

            st.divider()
            confirm = st.checkbox("Bu öğrenciyi ve tüm kayıtlarını silmek istiyorum.", key=f"delete_confirm_{student_id}")
            if st.button("Öğrenciyi Sil", key=f"delete_{student_id}"):
                if confirm:
                    delete_student(student_id)
                    st.session_state.selected_student_id = None
                    st.session_state.menu = "Ana Panel"
                    st.success("Öğrenci silindi")
                    st.rerun()
                else:
                    st.warning("Silmek için onay kutusunu işaretle.")
        else:
            st.info("Düzenleme ve silme yetkisi sadece Müdür rolündedir.")


# ---------------- ANA UYGULAMA ----------------
st.set_page_config(page_title="Öğrenci Rehberlik ve Sağlık Takip Sistemi", layout="wide")
apply_design()

create_tables()
seed_data()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "menu" not in st.session_state:
    st.session_state.menu = "Ana Panel"
if "selected_student_id" not in st.session_state:
    st.session_state.selected_student_id = None

if not st.session_state.logged_in:
    login_screen()
    st.stop()

role = st.session_state.role

if Path(LOGO_PATH).exists():
    st.sidebar.image(LOGO_PATH, width=92)

st.sidebar.success(f"Giriş: {st.session_state.username} / {role}")

if st.sidebar.button("Çıkış Yap"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.selected_student_id = None
    st.rerun()

menu_options = ["Ana Panel", "Öğrenciler", "Riskli Öğrenciler", "Raporlar"]
selected_menu = st.sidebar.radio(
    "Menü",
    menu_options,
    index=menu_options.index(st.session_state.menu) if st.session_state.menu in menu_options else 0
)

if selected_menu != st.session_state.menu and st.session_state.menu != "Öğrenci Detay":
    st.session_state.menu = selected_menu

if st.session_state.menu == "Öğrenci Detay" and st.session_state.selected_student_id:
    show_brand_header()
    student_detail_page(st.session_state.selected_student_id, role)
    st.stop()

show_brand_header()

students_df = get_students()

if selected_menu == "Ana Panel":
    st.header("Dashboard ve Erken Uyarı Paneli")
    latest_df = get_latest_risk_students()
    followups_df = get_followups(only_pending=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Toplam Öğrenci", len(students_df))
    col2.metric("Yüksek Risk", len(latest_df[latest_df["risk"] == "Yüksek"]))
    col3.metric("Orta Risk", len(latest_df[latest_df["risk"] == "Orta"]))
    col4.metric("Bekleyen Takip", len(followups_df))
    col5.metric("Ortalama Risk", "-" if latest_df.empty else int(latest_df["risk_puani"].mean()))

    st.subheader("Öğrenci Kartları")
    if latest_df.empty:
        st.warning("Henüz rehberlik kaydı yok.")
    else:
        cols = st.columns(3)
        for i, (_, row) in enumerate(latest_df.iterrows()):
            with cols[i % 3]:
                student_card(row)
                st.progress(int(row["risk_puani"]))
                if st.button(f"Detaya Git: {row['ad']}", key=f"open_home_{row['id']}"):
                    open_student(row["id"])

        st.subheader("Risk Puanı Dağılımı")
        st.bar_chart(latest_df[["ad", "risk_puani"]].set_index("ad"))

    st.subheader("Bekleyen Takip Randevuları")
    if followups_df.empty:
        st.success("Bekleyen takip randevusu yok.")
    else:
        st.dataframe(followups_df, use_container_width=True)

elif selected_menu == "Öğrenciler":
    st.header("Öğrenciler")

    if role in ["Müdür", "Rehber Öğretmen"]:
        with st.expander("Yeni Öğrenci Ekle"):
            ad = st.text_input("Ad Soyad")
            sinif = st.text_input("Sınıf")
            yas = st.number_input("Yaş", min_value=5, max_value=25, value=12)
            saglik_notu = st.text_area("Genel Sağlık Notu")
            kan_grubu = st.selectbox("Kan Grubu", ["", "A Rh+", "A Rh-", "B Rh+", "B Rh-", "AB Rh+", "AB Rh-", "0 Rh+", "0 Rh-"])
            kullandigi_ilaclar = st.text_area("Kullandığı İlaçlar")
            alerjiler = st.text_area("Alerjiler")
            kronik_hastaliklar = st.text_area("Kronik Hastalıklar")
            acil_kisi = st.text_input("Acil Durum Kişisi")
            acil_telefon = st.text_input("Acil Durum Telefonu")
            foto = st.file_uploader("Öğrenci Fotoğrafı", type=["png", "jpg", "jpeg", "webp"], key="new_photo")

            if st.button("Öğrenciyi Kaydet"):
                if ad.strip():
                    add_student(ad, sinif, yas, saglik_notu, kan_grubu, kullandigi_ilaclar, alerjiler, kronik_hastaliklar, acil_kisi, acil_telefon)
                    new_id = int(get_students().iloc[-1]["id"])
                    if foto is not None:
                        save_uploaded_photo(new_id, foto)
                    st.success("Öğrenci kaydedildi")
                    st.rerun()
                else:
                    st.warning("Ad soyad giriniz.")

    search = st.text_input("Öğrenci ara")
    class_filter = st.selectbox("Sınıfa göre filtrele", ["Tümü"] + sorted(students_df["sinif"].dropna().unique().tolist()))

    filtered = students_df.copy()
    if search:
        filtered = filtered[filtered["ad"].str.contains(search, case=False, na=False)]
    if class_filter != "Tümü":
        filtered = filtered[filtered["sinif"] == class_filter]

    st.dataframe(filtered, use_container_width=True)

    st.subheader("Öğrenci Listesi")
    for _, row in filtered.iterrows():
        col1, col2, col3, col4 = st.columns([1, 3, 3, 2])
        with col1:
            show_student_photo(row, width=70)
        with col2:
            st.write(f"**{row['ad']}**")
            st.write(f"{row['sinif']} / {row['yas']} yaş")
        with col3:
            st.write(f"Kan grubu: {row.get('kan_grubu', '') or '-'}")
            st.write(f"İlaç: {row.get('kullandigi_ilaclar', '') or '-'}")
        with col4:
            if st.button("Öğrenci Sayfası", key=f"open_list_{row['id']}"):
                open_student(row["id"])
        st.divider()

elif selected_menu == "Riskli Öğrenciler":
    st.header("Riskli Öğrenciler Paneli")
    risky_df = get_latest_risk_students()
    risk_filter = st.selectbox("Risk filtresi", ["Tümü", "Yüksek", "Orta", "Düşük"])

    if risk_filter != "Tümü":
        risky_df = risky_df[risky_df["risk"] == risk_filter]

    st.dataframe(risky_df, use_container_width=True)

    for _, row in risky_df.iterrows():
        col1, col2 = st.columns([4, 1])
        msg = f"{row['ad']} / {row['sinif']} - Risk Puanı: {int(row['risk_puani'])}/100 - {row['yorum']}"
        with col1:
            if row["risk"] == "Yüksek":
                st.error(msg)
            elif row["risk"] == "Orta":
                st.warning(msg)
            else:
                st.success(msg)
        with col2:
            if st.button("Aç", key=f"risk_open_{row['id']}"):
                open_student(row["id"])

elif selected_menu == "Raporlar":
    st.header("Raporlar")

    if students_df.empty:
        st.warning("Öğrenci yok.")
    else:
        secili_ad = st.selectbox("Rapor alınacak öğrenci", students_df["ad"].tolist())
        secili = students_df[students_df["ad"] == secili_ad].iloc[0]
        student_id = int(secili["id"])

        if st.button("Öğrenci Sayfasını Aç"):
            open_student(student_id)

        health_df = get_health(student_id)
        guidance_df = get_guidance(student_id)

        st.write("### Öğrenci Bilgileri")
        st.write("**Ad Soyad:**", secili["ad"])
        st.write("**Sınıf:**", secili["sinif"])
        st.write("**Yaş:**", secili["yas"])
        st.write("**Kan Grubu:**", secili.get("kan_grubu", "") or "-")
        st.write("**Kullandığı İlaçlar:**", secili.get("kullandigi_ilaclar", "") or "-")
        st.write("**Alerjiler:**", secili.get("alerjiler", "") or "-")
        st.write("**Kronik Hastalıklar:**", secili.get("kronik_hastaliklar", "") or "-")

        st.write("### Boy-Kilo Kayıtları")
        st.dataframe(health_df, use_container_width=True)

        st.write("### Rehberlik Kayıtları")
        st.dataframe(guidance_df, use_container_width=True)

        st.write("### Yapay Zeka Birleşik Analizi")
        analysis = create_combined_ai_analysis(student_id)
        st.info(f"{analysis['risk']} - {analysis['score']}/100\n\n{analysis['analysis']}")

        pdf_bytes = make_pdf_bytes(secili, health_df, guidance_df)
        if pdf_bytes:
            st.download_button(
                "PDF Rapor İndir",
                data=pdf_bytes,
                file_name=f"{secili['ad'].replace(' ', '_')}_rapor.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("PDF için reportlab gerekli. Kurmak için: pip install reportlab")
