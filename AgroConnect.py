# ╔══════════════════════════════════════════════════════════════════╗
# ║  AgriConnect v3.0 — La plateforme agricole algérienne de demain ║
# ║  Fonctionnalités : IA, météo, prix, QR, réputation, urgences    ║
# ╚══════════════════════════════════════════════════════════════════╝

import streamlit as st
import sqlite3
import hashlib
import json
import base64
import os
import io
import re
import math
import random
import time
from datetime import datetime, date, timedelta
from PIL import Image

# ── Imports optionnels ────────────────────────────────────────────────────────
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import qrcode
    HAS_QR = True
except ImportError:
    HAS_QR = False

try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgriConnect 🌾",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)
DB_FILE = "agriconnect_v3.db"

# ── 58 Wilayas avec coordonnées GPS ──────────────────────────────────────────
WILAYAS = {
    "01 - Adrar": {"communes": ["Adrar", "Reggane", "Timimoun"], "lat": 27.87, "lon": -0.29},
    "02 - Chlef": {"communes": ["Chlef", "Ténès", "Abou El Hassan"], "lat": 36.16, "lon": 1.33},
    "03 - Laghouat": {"communes": ["Laghouat", "Aflou", "Ksar El Hirane"], "lat": 33.80, "lon": 2.86},
    "04 - Oum El Bouaghi": {"communes": ["Oum El Bouaghi", "Aïn Beïda"], "lat": 35.87, "lon": 7.11},
    "05 - Batna": {"communes": ["Batna", "Timgad", "Arris"], "lat": 35.56, "lon": 6.17},
    "06 - Béjaïa": {"communes": ["Béjaïa", "Akbou", "Kherrata"], "lat": 36.75, "lon": 5.08},
    "07 - Biskra": {"communes": ["Biskra", "Tolga", "Sidi Okba"], "lat": 34.85, "lon": 5.73},
    "08 - Béchar": {"communes": ["Béchar", "Abadla", "Taghit"], "lat": 31.62, "lon": -2.22},
    "09 - Blida": {"communes": ["Blida", "Boufarik", "Mouzaïa"], "lat": 36.47, "lon": 2.83},
    "10 - Bouira": {"communes": ["Bouira", "Lakhdaria", "Aïn Bessem"], "lat": 36.37, "lon": 3.90},
    "11 - Tamanrasset": {"communes": ["Tamanrasset", "In Salah"], "lat": 22.79, "lon": 5.52},
    "12 - Tébessa": {"communes": ["Tébessa", "Bir el-Ater"], "lat": 35.40, "lon": 8.12},
    "13 - Tlemcen": {"communes": ["Tlemcen", "Maghnia", "Ghazaouet"], "lat": 34.88, "lon": -1.32},
    "14 - Tiaret": {"communes": ["Tiaret", "Sougueur", "Frenda"], "lat": 35.37, "lon": 1.32},
    "15 - Tizi Ouzou": {"communes": ["Tizi Ouzou", "Azazga", "Larbaâ Nath Irathen"], "lat": 36.71, "lon": 4.05},
    "16 - Alger": {"communes": ["Alger Centre", "Bab El Oued", "Hussein Dey", "El Harrach"], "lat": 36.74, "lon": 3.06},
    "17 - Djelfa": {"communes": ["Djelfa", "Messaâd", "El Idrissia"], "lat": 34.67, "lon": 3.26},
    "18 - Jijel": {"communes": ["Jijel", "Taher", "El Milia"], "lat": 36.82, "lon": 5.77},
    "19 - Sétif": {"communes": ["Sétif", "El Eulma", "Aïn Azel"], "lat": 36.19, "lon": 5.41},
    "20 - Saïda": {"communes": ["Saïda", "El Hassasna", "Youb"], "lat": 34.84, "lon": 0.15},
    "21 - Skikda": {"communes": ["Skikda", "Azzaba", "Collo"], "lat": 36.88, "lon": 6.90},
    "22 - Sidi Bel Abbès": {"communes": ["Sidi Bel Abbès", "Telagh"], "lat": 35.19, "lon": -0.63},
    "23 - Annaba": {"communes": ["Annaba", "El Hadjar", "Berrahal"], "lat": 36.90, "lon": 7.75},
    "24 - Guelma": {"communes": ["Guelma", "Hammam Debagh"], "lat": 36.46, "lon": 7.43},
    "25 - Constantine": {"communes": ["Constantine", "El Khroub", "Aïn Abid"], "lat": 36.37, "lon": 6.61},
    "26 - Médéa": {"communes": ["Médéa", "Berrouaghia", "Tablat"], "lat": 36.27, "lon": 2.75},
    "27 - Mostaganem": {"communes": ["Mostaganem", "Aïn Tedles"], "lat": 35.93, "lon": 0.09},
    "28 - M'Sila": {"communes": ["M'Sila", "Bou Saâda", "Magra"], "lat": 35.70, "lon": 4.54},
    "29 - Mascara": {"communes": ["Mascara", "Sig", "Ghriss"], "lat": 35.40, "lon": 0.14},
    "30 - Ouargla": {"communes": ["Ouargla", "Hassi Messaoud", "Touggourt"], "lat": 31.95, "lon": 5.32},
    "31 - Oran": {"communes": ["Oran", "Es Sénia", "Bir El Djir"], "lat": 35.70, "lon": -0.63},
    "32 - El Bayadh": {"communes": ["El Bayadh", "Bougtob"], "lat": 33.68, "lon": 1.02},
    "33 - Illizi": {"communes": ["Illizi", "Djanet"], "lat": 26.50, "lon": 8.48},
    "34 - Bordj Bou Arreridj": {"communes": ["Bordj Bou Arreridj", "Ras El Oued"], "lat": 36.07, "lon": 4.76},
    "35 - Boumerdès": {"communes": ["Boumerdès", "Dellys"], "lat": 36.77, "lon": 3.47},
    "36 - El Tarf": {"communes": ["El Tarf", "El Kala"], "lat": 36.77, "lon": 8.31},
    "37 - Tindouf": {"communes": ["Tindouf", "Oum El Assel"], "lat": 27.67, "lon": -8.15},
    "38 - Tissemsilt": {"communes": ["Tissemsilt", "Bordj Bounaama"], "lat": 35.61, "lon": 1.81},
    "39 - El Oued": {"communes": ["El Oued", "Guemar", "Robbah"], "lat": 33.36, "lon": 6.86},
    "40 - Khenchela": {"communes": ["Khenchela", "Kaïs", "Babar"], "lat": 35.43, "lon": 7.14},
    "41 - Souk Ahras": {"communes": ["Souk Ahras", "Taoura"], "lat": 36.28, "lon": 7.95},
    "42 - Tipaza": {"communes": ["Tipaza", "Bou Ismaïl", "Hadjout"], "lat": 36.59, "lon": 2.45},
    "43 - Mila": {"communes": ["Mila", "Telerghma"], "lat": 36.45, "lon": 6.26},
    "44 - Aïn Defla": {"communes": ["Aïn Defla", "Khemis Miliana"], "lat": 36.26, "lon": 1.97},
    "45 - Naâma": {"communes": ["Naâma", "Mecheria", "Aïn Sefra"], "lat": 33.27, "lon": -0.31},
    "46 - Aïn Témouchent": {"communes": ["Aïn Témouchent", "Beni Saf"], "lat": 35.30, "lon": -1.14},
    "47 - Ghardaïa": {"communes": ["Ghardaïa", "Metlili", "Berriane"], "lat": 32.49, "lon": 3.67},
    "48 - Relizane": {"communes": ["Relizane", "Zemoura"], "lat": 35.74, "lon": 0.56},
    "49 - Timimoun": {"communes": ["Timimoun", "Aougrout"], "lat": 29.26, "lon": 0.24},
    "50 - Bordj Badji Mokhtar": {"communes": ["Bordj Badji Mokhtar"], "lat": 21.33, "lon": 0.95},
    "51 - Ouled Djellal": {"communes": ["Ouled Djellal", "Sidi Khaled"], "lat": 34.42, "lon": 5.07},
    "52 - Béni Abbès": {"communes": ["Béni Abbès", "Kerzaz"], "lat": 30.13, "lon": -2.17},
    "53 - In Salah": {"communes": ["In Salah", "Foggaret Ezzaouia"], "lat": 27.20, "lon": 2.47},
    "54 - In Guezzam": {"communes": ["In Guezzam", "Tin Zaouatine"], "lat": 19.57, "lon": 5.77},
    "55 - Touggourt": {"communes": ["Touggourt", "Témacine"], "lat": 33.10, "lon": 6.07},
    "56 - Djanet": {"communes": ["Djanet", "Bordj El Haouas"], "lat": 24.55, "lon": 9.48},
    "57 - El M'ghair": {"communes": ["El M'ghair", "Djamaa"], "lat": 33.95, "lon": 5.93},
    "58 - El Meniaa": {"communes": ["El Meniaa", "Hassi Fehal"], "lat": 30.58, "lon": 2.88},
}
WILAYA_NAMES = list(WILAYAS.keys())

def get_communes(wilaya):
    return WILAYAS.get(wilaya, {}).get("communes", [wilaya])

def get_wilaya_coords(wilaya):
    d = WILAYAS.get(wilaya, {})
    return d.get("lat", 28.0), d.get("lon", 1.65)

# ── Traductions ───────────────────────────────────────────────────────────────
LANG = {
    "fr": {
        "app_name": "AgriConnect", "login": "Connexion", "register": "Inscription",
        "logout": "Déconnexion", "home": "Accueil", "market": "Marché",
        "job": "Emploi", "transport": "Transport", "grazing": "Pâturage",
        "pollination": "Pollinisation", "fertilizer": "Engrais",
        "equipment": "Matériel", "anem": "ANEM", "messages": "Messages",
        "reviews": "Avis", "contract": "Contrat", "profile": "Profil",
        "weather": "Météo", "prices": "Prix & Tendances", "alerts": "Urgences",
        "assistant": "Assistant IA", "tracability": "Traçabilité",
        "cooperative": "Coopératives", "dashboard": "Tableau de bord",
        "publish": "Publier", "list": "Annonces", "map": "Carte",
        "contact": "Contacter", "evaluate": "Évaluer", "contract_btn": "Contrat",
        "send": "Envoyer", "download": "Télécharger",
        "search": "Rechercher", "wilaya": "Wilaya", "commune": "Commune",
        "no_ann": "Aucune annonce pour le moment.",
        "login_req": "Veuillez vous connecter d'abord.",
        "fill_req": "Remplissez tous les champs obligatoires.",
        "published": "Annonce publiée avec succès !",
        "account_ok": "Compte créé. Connectez-vous.",
        "phone_used": "Numéro déjà utilisé.",
        "bad_creds": "Identifiants incorrects.",
        "next": "Suivant →", "prev": "← Précédent", "page": "Page",
    },
    "ar": {
        "app_name": "أجريكونكت", "login": "تسجيل الدخول", "register": "التسجيل",
        "logout": "خروج", "home": "الرئيسية", "market": "السوق",
        "job": "وظائف", "transport": "النقل", "grazing": "الرعي",
        "pollination": "التلقيح", "fertilizer": "الأسمدة",
        "equipment": "المعدات", "anem": "الوكالة", "messages": "الرسائل",
        "reviews": "التقييمات", "contract": "عقد", "profile": "الملف",
        "weather": "الطقس", "prices": "الأسعار", "alerts": "تنبيهات",
        "assistant": "مساعد ذكي", "tracability": "التتبع",
        "cooperative": "التعاونيات", "dashboard": "لوحة التحكم",
        "publish": "نشر", "list": "قائمة", "map": "خريطة",
        "contact": "اتصال", "evaluate": "تقييم", "contract_btn": "عقد",
        "send": "إرسال", "download": "تحميل",
        "search": "بحث", "wilaya": "ولاية", "commune": "بلدية",
        "no_ann": "لا توجد إعلانات",
        "login_req": "الرجاء تسجيل الدخول أولاً.",
        "fill_req": "يرجى ملء جميع الحقول المطلوبة.",
        "published": "تم نشر الإعلان بنجاح!",
        "account_ok": "تم إنشاء الحساب. سجل دخولك.",
        "phone_used": "رقم الهاتف مستخدم.",
        "bad_creds": "بيانات غير صحيحة.",
        "next": "التالي →", "prev": "← السابق", "page": "صفحة",
    },
    "en": {
        "app_name": "AgriConnect", "login": "Login", "register": "Register",
        "logout": "Logout", "home": "Home", "market": "Market",
        "job": "Jobs", "transport": "Transport", "grazing": "Grazing",
        "pollination": "Pollination", "fertilizer": "Fertilizer",
        "equipment": "Equipment", "anem": "ANEM", "messages": "Messages",
        "reviews": "Reviews", "contract": "Contract", "profile": "Profile",
        "weather": "Weather", "prices": "Prices & Trends", "alerts": "Alerts",
        "assistant": "AI Assistant", "tracability": "Traceability",
        "cooperative": "Cooperatives", "dashboard": "Dashboard",
        "publish": "Publish", "list": "Listings", "map": "Map",
        "contact": "Contact", "evaluate": "Rate", "contract_btn": "Contract",
        "send": "Send", "download": "Download",
        "search": "Search", "wilaya": "Wilaya", "commune": "Commune",
        "no_ann": "No announcements yet.",
        "login_req": "Please log in first.",
        "fill_req": "Please fill all required fields.",
        "published": "Announcement published successfully!",
        "account_ok": "Account created. Please log in.",
        "phone_used": "Phone number already in use.",
        "bad_creds": "Incorrect credentials.",
        "next": "Next →", "prev": "← Previous", "page": "Page",
    },
}

def _(key):
    lang = st.session_state.get("lang", "fr")
    return LANG.get(lang, LANG["fr"]).get(key, key)

# ── Session State ─────────────────────────────────────────────────────────────
DEFAULTS = {
    "user": None, "page": "home", "lang": "fr",
    "msg_to": None, "msg_announce": None,
    "review_announce": None, "contract_announce": None,
    "db_init": False, "search_q": "",
    "urgent_shown": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&display=swap');

:root {
    --green:       #2e7d32;
    --green-d:     #1b5e20;
    --green-l:     #43a047;
    --green-pale:  #e8f5e9;
    --amber:       #f59e0b;
    --amber-pale:  #fffbeb;
    --red:         #dc2626;
    --red-pale:    #fef2f2;
    --blue:        #1d4ed8;
    --blue-pale:   #eff6ff;
    --text:        #111827;
    --muted:       #6b7280;
    --border:      #e5e7eb;
    --bg:          #f9fafb;
    --card:        #ffffff;
    --radius:      14px;
    --shadow:      0 1px 8px rgba(0,0,0,.06);
    --shadow-h:    0 8px 24px rgba(0,0,0,.11);
}
* { font-family: 'Sora', sans-serif; box-sizing: border-box; }

/* ── Header ── */
.hero {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #388e3c 100%);
    color: white; padding: 2rem 2rem 1.5rem; border-radius: var(--radius);
    margin-bottom: 1.5rem; position: relative; overflow: hidden;
}
.hero::before {
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 200px; height: 200px; background: rgba(255,255,255,.05);
    border-radius: 50%;
}
.hero h1 { font-size: 2rem; font-weight: 700; margin: 0; letter-spacing: -.5px; }
.hero p  { margin: .4rem 0 0; opacity: .8; font-size: .95rem; font-weight: 300; }

/* ── Cards ── */
.card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); overflow: hidden;
    box-shadow: var(--shadow); transition: transform .2s, box-shadow .2s;
    margin-bottom: 1rem; height: 100%;
}
.card:hover { transform: translateY(-3px); box-shadow: var(--shadow-h); }
.card-img { height: 160px; width: 100%; object-fit: cover; background: var(--green-pale); display: flex; align-items: center; justify-content: center; font-size: 2.5rem; }
.card-body { padding: 14px; }
.card-title { font-size: .95rem; font-weight: 600; color: var(--text); margin-bottom: 4px; }
.card-desc { color: var(--muted); font-size: .8rem; margin-bottom: 8px; }
.card-price { font-size: 1.1rem; font-weight: 700; color: var(--green); }
.card-loc   { color: var(--muted); font-size: .75rem; margin-top: 4px; }

/* ── Badges ── */
.badge { display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px; border-radius: 20px; font-size: .7rem; font-weight: 600; }
.b-green  { background: var(--green-pale);  color: var(--green-d); }
.b-amber  { background: var(--amber-pale);  color: #92400e; }
.b-red    { background: var(--red-pale);    color: #991b1b; }
.b-blue   { background: var(--blue-pale);   color: var(--blue); }
.b-gray   { background: #f3f4f6; color: #374151; }
.b-verified { background: #ecfdf5; color: #065f46; }

/* ── Stat cards ── */
.stat { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1rem; text-align: center; }
.stat .num  { font-size: 1.8rem; font-weight: 700; color: var(--green); }
.stat .lbl  { color: var(--muted); font-size: .78rem; margin-top: 2px; }

/* ── Urgent banner ── */
.urgent-banner {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    color: white; padding: 12px 16px; border-radius: 10px;
    margin-bottom: 1rem; display: flex; align-items: center; gap: 10px;
    font-weight: 500; font-size: .9rem; animation: pulse-red 2s infinite;
}
@keyframes pulse-red { 0%,100%{box-shadow:0 0 0 0 rgba(220,38,38,.4)} 50%{box-shadow:0 0 0 8px rgba(220,38,38,0)} }

/* ── Weather card ── */
.weather-card {
    background: linear-gradient(135deg, #1565c0, #0277bd);
    color: white; border-radius: var(--radius); padding: 1.5rem;
    text-align: center;
}
.weather-temp { font-size: 3rem; font-weight: 700; }
.weather-desc { font-size: .9rem; opacity: .85; }

/* ── AI chat ── */
.ai-bubble { background: var(--green-pale); border-radius: 12px 12px 12px 0; padding: 12px 16px; margin: 8px 0; font-size: .88rem; line-height: 1.6; color: var(--text); border-left: 3px solid var(--green); }
.user-bubble { background: var(--blue-pale); border-radius: 12px 12px 0 12px; padding: 12px 16px; margin: 8px 0; font-size: .88rem; line-height: 1.6; color: var(--text); text-align: right; }

/* ── Rep score ── */
.rep-ring { width: 70px; height: 70px; border-radius: 50%; background: conic-gradient(var(--green) calc(var(--pct)*1%),var(--border) 0); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: .9rem; color: var(--green); position: relative; }
.rep-ring::before { content:''; position: absolute; width: 52px; height: 52px; border-radius: 50%; background: white; }
.rep-val { position: relative; z-index: 1; }

/* ── Price chart ── */
.price-up   { color: #dc2626; font-weight: 600; }
.price-down { color: #16a34a; font-weight: 600; }

/* ── Timeline ── */
.timeline-item { display: flex; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border); }
.timeline-dot  { width: 10px; height: 10px; border-radius: 50%; background: var(--green); margin-top: 6px; flex-shrink: 0; }
.timeline-date { font-size: .75rem; color: var(--muted); }
.timeline-text { font-size: .85rem; color: var(--text); }

/* ── Misc ── */
.no-announce { text-align: center; padding: 3rem; color: var(--muted); background: var(--green-pale); border-radius: var(--radius); border: 1px dashed #a5d6a7; }
.footer { text-align: center; padding: 1.5rem; color: var(--muted); border-top: 1px solid var(--border); margin-top: 3rem; font-size: .78rem; }
.qr-box { background: white; padding: 12px; border-radius: 10px; border: 1px solid var(--border); text-align: center; }
.score-bar { height: 8px; border-radius: 4px; background: var(--border); overflow: hidden; }
.score-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, var(--green-l), var(--green-d)); }
</style>
""", unsafe_allow_html=True)

# ── DB ─────────────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        profile_type TEXT DEFAULT 'Agriculteur',
        is_verified INTEGER DEFAULT 0,
        wilaya TEXT, commune TEXT,
        lat REAL DEFAULT 0, lon REAL DEFAULT 0,
        documents TEXT,
        reputation_score REAL DEFAULT 0,
        total_transactions INTEGER DEFAULT 0,
        bio TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        price REAL DEFAULT 0,
        unit TEXT DEFAULT '',
        wilaya TEXT DEFAULT '',
        commune TEXT DEFAULT '',
        lat REAL DEFAULT 0, lon REAL DEFAULT 0,
        data TEXT DEFAULT '{}',
        images TEXT DEFAULT '',
        is_urgent INTEGER DEFAULT 0,
        urgent_discount INTEGER DEFAULT 0,
        is_traceable INTEGER DEFAULT 0,
        qr_data TEXT DEFAULT '',
        views INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        announcement_id INTEGER,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        announcement_id INTEGER NOT NULL,
        reviewer_id INTEGER NOT NULL,
        rating INTEGER CHECK(rating BETWEEN 1 AND 5),
        comment TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(announcement_id, reviewer_id)
    );
    CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        announcement_id INTEGER NOT NULL,
        renter_id INTEGER NOT NULL,
        owner_id INTEGER NOT NULL,
        start_date TEXT, end_date TEXT,
        terms TEXT DEFAULT '',
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS cooperatives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        wilaya TEXT, filiere TEXT,
        creator_id INTEGER,
        description TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS coop_members (
        coop_id INTEGER, user_id INTEGER,
        role TEXT DEFAULT 'member',
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (coop_id, user_id)
    );
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT NOT NULL,
        wilaya TEXT NOT NULL,
        price REAL NOT NULL,
        recorded_at DATE DEFAULT (date('now'))
    );
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        wilaya TEXT,
        type TEXT,
        message TEXT,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS ai_conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        role TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Seed data only if empty
    if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        seed_users = [
            ("Agent ANEM Alger", "0555000001", hash_pw("anem123"), "ANEM", 1, "16 - Alger", "Alger Centre", 4.8, 42),
            ("Ali Ferme El Oued",  "0555123456", hash_pw("123456"), "Agriculteur", 1, "39 - El Oued", "Guemar", 4.5, 18),
            ("Fatima Transport",   "0555654321", hash_pw("123456"), "Transporteur", 1, "31 - Oran", "Es Sénia", 4.2, 31),
            ("Karim Apiculteur",   "0556111222", hash_pw("123456"), "Apiculteur", 1, "06 - Béjaïa", "Akbou", 4.7, 12),
            ("Samira Éleveuse",    "0556333444", hash_pw("123456"), "Éleveur", 0, "14 - Tiaret", "Sougueur", 3.9, 7),
        ]
        c.executemany("INSERT INTO users (name,phone,password,profile_type,is_verified,wilaya,commune,reputation_score,total_transactions) VALUES (?,?,?,?,?,?,?,?,?)", seed_users)

        uid_ali   = c.execute("SELECT id FROM users WHERE phone='0555123456'").fetchone()[0]
        uid_fat   = c.execute("SELECT id FROM users WHERE phone='0555654321'").fetchone()[0]
        uid_kar   = c.execute("SELECT id FROM users WHERE phone='0556111222'").fetchone()[0]
        uid_sam   = c.execute("SELECT id FROM users WHERE phone='0556333444'").fetchone()[0]

        seed_ann = [
            (uid_ali, "market",      "Pommes de terre Spunta",          "10 t disponibles, calibre A. Livraison possible.",    45,   "DA/kg",  "39 - El Oued",  "Guemar",   0, '{"product_type":"Légumes","quantity":10000}'),
            (uid_sam, "grazing",     "Chaumes de blé — 50 ha",          "Eau disponible, mai–juillet, max 100 têtes.",        200,  "DA/tête/j","14 - Tiaret","Sougueur",  0, '{"area_ha":50,"cover_type":"Chaume","water":"Oui","max_animals":100}'),
            (uid_ali, "fertilizer",  "Fumier ovin composté",            "5 t de qualité supérieure, ensaché.",               3000, "DA/t",   "17 - Djelfa",   "Messaâd",  0, '{"fertilizer_type":"Fumier ovin","quantity_tons":5}'),
            (uid_fat, "transport",   "Camion frigo Alger–Constantine",  "10 t, départ chaque lundi.",                        8000, "DA/voy", "16 - Alger",    "El Harrach",0,'{"vehicle_type":"Frigorifique","capacity":10}'),
            (uid_kar, "pollination", "20 ruches — zone Béjaïa–Batna",   "Race locale, déplacement inclus.",                  5000, "DA/ruch/sem","06 - Béjaïa","Akbou",  0, '{"hive_count":20,"bee_race":"Locale"}'),
            (uid_fat, "equipment",   "Tracteur MF 2020 — location",     "Bon état, pneus neufs.",                            5000, "DA/j",   "31 - Oran",     "Es Sénia", 0, '{"offer_type":"Location","equipment_type":"Tracteur","brand":"Massey Ferguson","year":2020,"state":"Bon"}'),
            (uid_ali, "market",      "Dattes Deglet Nour",               "Récolte 2025, 500 kg disponibles. URGENT — vente rapide!", 180, "DA/kg","39 - El Oued","Robbah", 1, '{"product_type":"Fruits","quantity":500}'),
            (uid_sam, "job",         "Ouvriers saisonniers moisson",     "10 postes, juin–juillet, logement fourni.",         2500, "DA/j",   "14 - Tiaret",   "Frenda",   0, '{"contract_type":"Saisonnier","duration":45}'),
        ]
        c.executemany("INSERT INTO announcements (user_id,type,title,description,price,unit,wilaya,commune,is_urgent,data) VALUES (?,?,?,?,?,?,?,?,?,?)", seed_ann)

        # Seed price history (30 days, 5 products)
        products = ["Pomme de terre", "Tomate", "Blé dur", "Oignon", "Dattes Deglet"]
        wilayas_ph = ["31 - Oran", "16 - Alger", "19 - Sétif", "39 - El Oued", "25 - Constantine"]
        base_prices = [45, 80, 38, 55, 180]
        today = date.today()
        for p_idx, prod in enumerate(products):
            for w in wilayas_ph:
                price = base_prices[p_idx]
                for days_ago in range(30, -1, -1):
                    d = today - timedelta(days=days_ago)
                    price = max(price * (0.97 + random.random() * 0.06), 10)
                    c.execute("INSERT OR IGNORE INTO price_history (product,wilaya,price,recorded_at) VALUES (?,?,?,?)",
                              (prod, w, round(price, 1), d.isoformat()))

        # Seed cooperatives
        c.execute("INSERT INTO cooperatives (name,wilaya,filiere,creator_id,description) VALUES (?,?,?,?,?)",
                  ("Coopérative des Maraîchers d'El Oued", "39 - El Oued", "Légumes", uid_ali, "Groupement pour ventes collectives aux GMS"))
        coop_id = c.lastrowid
        c.execute("INSERT OR IGNORE INTO coop_members (coop_id,user_id,role) VALUES (?,?,'admin')", (coop_id, uid_ali))
        c.execute("INSERT OR IGNORE INTO coop_members (coop_id,user_id,role) VALUES (?,?,'member')", (coop_id, uid_sam))

    conn.commit()
    conn.close()

def qdb(sql, params=(), fetch=True):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        if fetch:
            rows = cur.fetchall()
            conn.close()
            return rows
        conn.commit()
        lid = cur.lastrowid
        conn.close()
        return lid
    except sqlite3.Error as e:
        conn.close()
        st.error(f"DB : {e}")
        return [] if fetch else None

def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()
def valid_phone(p): return bool(re.match(r'^0[5-7]\d{8}$', p.strip()))

# ── Media ──────────────────────────────────────────────────────────────────────
def img_to_b64(f, size=(800, 600), q=65):
    if not f: return None
    try:
        f.seek(0)
        im = Image.open(f).convert("RGB")
        im.thumbnail(size, Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=q, optimize=True)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception: return None

def make_qr(data):
    if not HAS_QR: return None
    try:
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, "PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception: return None

# ── Weather (Open-Meteo — gratuit, sans clé) ──────────────────────────────────
@st.cache_data(ttl=3600)
def get_weather(lat, lon, wilaya_name=""):
    if not HAS_REQUESTS:
        return _mock_weather(wilaya_name)
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weathercode"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode"
            f"&timezone=Africa/Algiers&forecast_days=7"
        )
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return _mock_weather(wilaya_name)

def _mock_weather(name=""):
    today = date.today()
    wc = [0, 1, 2, 61, 80, 95, 71, 3]
    random.seed(abs(hash(name)) % 999)
    return {
        "current": {
            "temperature_2m": round(15 + random.random() * 20, 1),
            "relative_humidity_2m": random.randint(30, 75),
            "wind_speed_10m": round(random.random() * 30, 1),
            "weathercode": random.choice(wc),
        },
        "daily": {
            "time": [(today + timedelta(days=i)).isoformat() for i in range(7)],
            "temperature_2m_max": [round(20 + random.random() * 15, 1) for _ in range(7)],
            "temperature_2m_min": [round(8 + random.random() * 10, 1) for _ in range(7)],
            "precipitation_sum": [round(random.random() * 5, 1) for _ in range(7)],
            "weathercode": [random.choice(wc) for _ in range(7)],
        }
    }

WMO_ICONS = {
    0: ("☀️", "Ensoleillé"), 1: ("🌤️", "Peu nuageux"), 2: ("⛅", "Nuageux"),
    3: ("☁️", "Couvert"), 45: ("🌫️", "Brouillard"), 51: ("🌦️", "Bruine"),
    61: ("🌧️", "Pluie"), 71: ("🌨️", "Neige"), 80: ("🌦️", "Averses"),
    95: ("⛈️", "Orage"),
}
def wmo(code):
    for k, v in WMO_ICONS.items():
        if abs(code - k) < 5: return v
    return ("🌡️", "Variable")

# ── AI Assistant (règles agro algériennes) ─────────────────────────────────────
AGRO_KB = {
    "calendrier": {
        "tomate": {"semis": "Fév–Mar (sous abri), transplant Avr–Mai", "récolte": "Juil–Oct"},
        "pomme de terre": {"semis": "Fév–Mar ou Sep–Oct", "récolte": "Mai–Jun ou Jan–Feb"},
        "blé dur": {"semis": "Nov–Dec", "récolte": "Jun–Jul"},
        "oignon": {"semis": "Sep–Oct (automne)", "récolte": "Avr–Mai"},
        "pastèque": {"semis": "Avr–Mai", "récolte": "Jul–Sep"},
        "dattes": {"floraison": "Mar–Avr", "récolte": "Sep–Nov"},
    },
    "zones_climatiques": {
        "nord littoral": ["06 - Béjaïa","23 - Annaba","21 - Skikda","18 - Jijel"],
        "hauts plateaux": ["14 - Tiaret","19 - Sétif","28 - M'Sila","17 - Djelfa"],
        "saharien": ["07 - Biskra","39 - El Oued","30 - Ouargla","47 - Ghardaïa"],
        "tellien": ["16 - Alger","09 - Blida","42 - Tipaza","35 - Boumerdès"],
    },
    "maladies": {
        "mildiou": "Traitement : Mancozèbe 2g/L ou Metalaxyl. Prévention : espacer les plants, éviter excès d'eau.",
        "oïdium": "Soufre mouillable 3g/L ou Tebuconazole. Pulvériser tôt le matin.",
        "fusariose": "Pas de traitement curatif. Rotation cultures 3–4 ans, chaux vive sur sol.",
        "pucerons": "Imidaclopride ou savon insecticide bio. Introduire coccinelles.",
        "doryphore": "Deltaméthrine ou Bacillus thuringiensis (bio). Ramassage manuel.",
    }
}

def ai_respond(question, user_wilaya=""):
    question_lower = question.lower()

    # Détection de zone climatique
    zone = "hauts plateaux"
    for z, wilayas in AGRO_KB["zones_climatiques"].items():
        if any(w.lower() in user_wilaya.lower() for w in wilayas):
            zone = z

    # Calendrier cultural
    for culture, cal in AGRO_KB["calendrier"].items():
        if culture in question_lower:
            resp = f"📅 **Calendrier pour {culture.title()}** (zone : {zone})\n\n"
            for k, v in cal.items():
                resp += f"• **{k.capitalize()}** : {v}\n"
            if zone == "saharien":
                resp += "\n⚠️ En zone saharienne : privilégiez les variétés résistantes à la chaleur et l'irrigation goutte-à-goutte."
            elif zone == "hauts plateaux":
                resp += "\n❄️ Sur les hauts plateaux : attention aux gelées tardives en mars–avril."
            return resp

    # Maladies
    for maladie, traitement in AGRO_KB["maladies"].items():
        if maladie in question_lower:
            return f"🦠 **{maladie.title()}** :\n\n{traitement}\n\n💡 Consultez votre DSA locale pour des conseils adaptés à votre wilaya."

    # Prix
    if any(w in question_lower for w in ["prix", "tarif", "combien", "coût"]):
        return (
            "💰 **Prix moyens du marché (mai 2026)** :\n\n"
            "• Pomme de terre : 40–55 DA/kg\n"
            "• Tomate : 60–90 DA/kg\n"
            "• Blé dur : 35–42 DA/kg\n"
            "• Oignon : 50–70 DA/kg\n"
            "• Dattes Deglet : 160–220 DA/kg\n\n"
            "📊 Consultez l'onglet **Prix & Tendances** pour les courbes historiques."
        )

    # Engrais
    if any(w in question_lower for w in ["engrais", "fertilisant", "azote", "npk"]):
        return (
            "🌱 **Recommandations fertilisation** :\n\n"
            "• **NPK 15-15-15** : apport de base, 3–5 q/ha avant semis\n"
            "• **Urée 46%** : couverture azotée, 1–2 q/ha au tallage (céréales)\n"
            "• **Fumier ovin composté** : 20–30 t/ha, apport matière organique\n"
            "• **Phosphate bicalcique** : sur sols pauvres en P, 2–3 q/ha\n\n"
            "💡 Faites une analyse de sol (ITGC) avant tout programme de fertilisation."
        )

    # Irrigation
    if any(w in question_lower for w in ["irrigation", "arrosage", "eau", "goutte"]):
        return (
            "💧 **Conseils irrigation** :\n\n"
            "• **Goutte-à-goutte** : économie de 40–60% d'eau vs aspersion\n"
            "• **Besoins indicatifs** : tomate 600–800 mm/cycle, blé 350–450 mm\n"
            "• En zone saharienne : irriguer tôt le matin ou la nuit\n"
            "• **Subventions** : le FNRDA finance jusqu'à 70% du matériel d'irrigation\n\n"
            "📋 Renseignez-vous auprès de votre DSA pour les aides 2026."
        )

    # Subventions
    if any(w in question_lower for w in ["subvention", "aide", "fnrda", "fdrmvtc"]):
        return (
            "🏦 **Aides et subventions agricoles 2026** :\n\n"
            "• **FNRDA** : soutien à l'investissement (matériel, semences, irrigation)\n"
            "• **FDRMVTC** : filières maraîchage, vigne, tabac\n"
            "• **ANSEJ/CNAC** : financement jeunes agriculteurs\n"
            "• **ANEM** : aide à l'emploi saisonnier (exonération charges)\n\n"
            "📍 Déposez votre dossier à la Direction des Services Agricoles (DSA) de votre wilaya."
        )

    # Default contextuel
    greetings = ["bonjour", "salam", "مرحبا", "مساء", "صباح"]
    if any(g in question_lower for g in greetings):
        return (
            f"السلام عليكم / Bonjour ! 👋\n\n"
            f"Je suis l'assistant agricole d'AgriConnect. Je peux vous aider sur :\n"
            f"• 📅 Calendriers culturaux par wilaya\n"
            f"• 🦠 Diagnostic et traitement des maladies\n"
            f"• 💰 Prix du marché et tendances\n"
            f"• 🌱 Fertilisation et irrigation\n"
            f"• 🏦 Subventions et aides agricoles\n\n"
            f"Que voulez-vous savoir ?"
        )

    return (
        f"🌿 Je n'ai pas trouvé de réponse précise pour «{question}».\n\n"
        f"Essayez des questions comme :\n"
        f"• *«Quand planter les tomates à {user_wilaya or 'Sétif'} ?»*\n"
        f"• *«Comment traiter le mildiou ?»*\n"
        f"• *«Quels engrais pour le blé dur ?»*\n"
        f"• *«Aides FNRDA 2026»*"
    )

# ── Reputation score ──────────────────────────────────────────────────────────
def compute_reputation(user_id):
    reviews  = qdb("SELECT AVG(r.rating) as avg FROM reviews r JOIN announcements a ON r.announcement_id=a.id WHERE a.user_id=?", (user_id,))
    avg_rev  = (reviews[0]["avg"] or 0) if reviews else 0
    nb_ann   = qdb("SELECT COUNT(*) as n FROM announcements WHERE user_id=?", (user_id,))[0]["n"]
    nb_msg   = qdb("SELECT COUNT(*) as n FROM messages WHERE sender_id=?", (user_id,))[0]["n"]
    user     = qdb("SELECT * FROM users WHERE id=?", (user_id,))[0]
    verified = 1 if user["is_verified"] else 0
    since    = (datetime.now() - datetime.strptime(user["created_at"][:10], "%Y-%m-%d")).days / 30
    score = (
        avg_rev        * 0.4 +
        min(nb_ann/10, 5) * 0.2 +
        min(nb_msg/20, 5) * 0.1 +
        verified       * 1.0 +
        min(since/6, 5) * 0.1
    )
    return min(round(score, 2), 5.0)

# ── Render card ────────────────────────────────────────────────────────────────
MOD_ICON = {"market":"🥕","job":"👷","transport":"🚛","grazing":"🐑",
            "pollination":"🐝","fertilizer":"🌱","equipment":"🚜"}

def render_card(a, key_prefix="c"):
    urgent = a["is_urgent"]
    if urgent:
        st.markdown('<div class="urgent-banner">🚨 VENTE URGENTE — Prix réduit disponible !</div>', unsafe_allow_html=True)

    icon = MOD_ICON.get(a["type"], "📌")
    if a["images"]:
        first = a["images"].split(";")[0]
        img_html = f'<img src="data:image/jpeg;base64,{first}" style="height:160px;width:100%;object-fit:cover;">'
    else:
        img_html = f'<div class="card-img">{icon}</div>'

    desc = (a["description"] or "")
    desc_short = desc[:90] + "…" if len(desc) > 90 else desc
    ur_badge = '<span class="badge b-red">🚨 URGENT</span> ' if urgent else ""
    tr_badge = '<span class="badge b-blue">🔍 Traçable</span> ' if a["is_traceable"] else ""

    author_row = qdb("SELECT name, reputation_score, is_verified FROM users WHERE id=?", (a["user_id"],))
    author = author_row[0] if author_row else None
    rep_html = ""
    if author:
        stars = "⭐" * round(author["reputation_score"])
        ver = "✅" if author["is_verified"] else ""
        rep_html = f'<div style="font-size:.75rem;color:#6b7280;margin-top:6px;">{ver} {author["name"]} {stars}</div>'

    st.markdown(f"""
    <div class="card">
        {img_html}
        <div class="card-body">
            {ur_badge}{tr_badge}
            <span class="badge b-gray" style="margin-top:4px;">{a['type'].upper()}</span>
            <div class="card-title" style="margin-top:6px;">{a['title']}</div>
            <div class="card-desc">{desc_short}</div>
            <div class="card-price">{a['price']:,.0f} {a['unit'] or ''}</div>
            <div class="card-loc">📍 {a['wilaya']} — {a['commune']}</div>
            {rep_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💬 " + _("contact"), key=f"{key_prefix}_msg_{a['id']}", use_container_width=True):
            st.session_state.msg_to = a["user_id"]
            st.session_state.msg_announce = a["id"]
            st.session_state.page = "messages"; st.rerun()
    with c2:
        if st.button("⭐ " + _("evaluate"), key=f"{key_prefix}_rev_{a['id']}", use_container_width=True):
            st.session_state.review_announce = a["id"]
            st.session_state.page = "reviews"; st.rerun()
    with c3:
        if a["type"] in ("grazing","pollination","equipment"):
            if st.button("📄 " + _("contract_btn"), key=f"{key_prefix}_ct_{a['id']}", use_container_width=True):
                st.session_state.contract_announce = a["id"]
                st.session_state.page = "contract"; st.rerun()

# ── Navbar ─────────────────────────────────────────────────────────────────────
def navbar():
    pages_all = [
        ("home","🏠"),("market","🥕"),("job","👷"),("transport","🚛"),
        ("grazing","🐑"),("pollination","🐝"),("equipment","🚜"),
        ("weather","🌤️"),("prices","📊"),("alerts","🚨"),
        ("assistant","🤖"),("cooperative","🤝"),("messages","💬"),("profile","👤"),
    ]
    user = st.session_state.user
    if user and user.get("profile_type") == "ANEM":
        pages_all.insert(4, ("anem","🏛️"))

    cols = st.columns(len(pages_all))
    for i, (pg, icon) in enumerate(pages_all):
        label = icon + " " + _(pg)
        is_active = st.session_state.page == pg
        with cols[i]:
            if st.button(label, key=f"nav_{pg}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state.page = pg; st.rerun()

# ── Auth pages ─────────────────────────────────────────────────────────────────
def login_page():
    col = st.columns([1,2,1])[1]
    with col:
        st.markdown("### 🔐 " + _("login"))
        phone = st.text_input("📱 Téléphone")
        pwd   = st.text_input("🔑 Mot de passe", type="password")
        if st.button(_("login"), use_container_width=True, type="primary"):
            if not (phone and pwd):
                st.warning(_("fill_req"))
            else:
                r = qdb("SELECT * FROM users WHERE phone=? AND password=?", (phone.strip(), hash_pw(pwd)))
                if r:
                    st.session_state.user = dict(r[0]); st.session_state.page = "home"; st.rerun()
                else:
                    st.error(_("bad_creds"))
        st.markdown("---")
        if st.button(_("register"), use_container_width=True):
            st.session_state.page = "register"; st.rerun()

def register_page():
    col = st.columns([1,2,1])[1]
    with col:
        st.markdown("### 📝 " + _("register"))
        name    = st.text_input("Nom complet *")
        phone   = st.text_input("Téléphone * (ex: 0555123456)")
        pwd     = st.text_input("Mot de passe * (min 6 car.)", type="password")
        pwd2    = st.text_input("Confirmer le mot de passe *", type="password")
        profile = st.selectbox("Profil", ["Agriculteur","Éleveur","Apiculteur","Transporteur","Acheteur","ANEM","Travailleur"])
        wilaya  = st.selectbox(_("wilaya"), WILAYA_NAMES)
        commune = st.selectbox(_("commune"), get_communes(wilaya))
        bio     = st.text_area("Bio (optionnel)", height=70)

        if st.button("Créer mon compte", use_container_width=True, type="primary"):
            errs = []
            if not name.strip(): errs.append("Nom requis.")
            if not valid_phone(phone): errs.append("Téléphone invalide (ex: 0555123456).")
            if len(pwd) < 6: errs.append("Mot de passe trop court (6 car. min).")
            if pwd != pwd2: errs.append("Mots de passe différents.")
            if errs:
                for e in errs: st.error(e)
            else:
                try:
                    lat, lon = get_wilaya_coords(wilaya)
                    qdb("INSERT INTO users (name,phone,password,profile_type,wilaya,commune,lat,lon,bio) VALUES (?,?,?,?,?,?,?,?,?)",
                        (name.strip(), phone.strip(), hash_pw(pwd), profile, wilaya, commune, lat, lon, bio), fetch=False)
                    st.success(_("account_ok")); st.session_state.page = "login"; st.rerun()
                except sqlite3.IntegrityError:
                    st.error(_("phone_used"))

# ── Home ────────────────────────────────────────────────────────────────────────
def home_page():
    st.markdown("""
    <div class="hero">
        <h1>🌾 AgriConnect</h1>
        <p>La plateforme numérique de l'agriculture algérienne — 58 wilayas, une communauté</p>
    </div>
    """, unsafe_allow_html=True)

    # Alertes urgentes
    urgent_anns = qdb("SELECT COUNT(*) as n FROM announcements WHERE is_urgent=1")
    if urgent_anns[0]["n"] > 0 and not st.session_state.urgent_shown:
        st.markdown(f'<div class="urgent-banner">🚨 {urgent_anns[0]["n"]} vente(s) urgente(s) disponible(s) — <a href="#" style="color:white;">Voir maintenant ↗</a></div>', unsafe_allow_html=True)
        if st.button("🚨 Voir les ventes urgentes", type="primary"):
            st.session_state.page = "alerts"; st.rerun()

    # Stats
    c1, c2, c3, c4 = st.columns(4)
    total_ann = qdb("SELECT COUNT(*) as n FROM announcements")[0]["n"]
    total_usr = qdb("SELECT COUNT(*) as n FROM users")[0]["n"]
    wil_cov   = qdb("SELECT COUNT(DISTINCT wilaya) as n FROM announcements")[0]["n"]
    nb_coop   = qdb("SELECT COUNT(*) as n FROM cooperatives")[0]["n"]
    for col, num, lbl in [
        (c1, total_ann, "Annonces"), (c2, total_usr, "Membres"),
        (c3, wil_cov, "Wilayas"), (c4, nb_coop, "Coopératives"),
    ]:
        col.markdown(f'<div class="stat"><div class="num">{num}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Recherche
    sc, sw, sb = st.columns([3, 2, 1])
    with sc:
        q = st.text_input(_("search"), value=st.session_state.search_q, placeholder="Ex: pomme de terre, tracteur, ouvriers…", label_visibility="collapsed")
    with sw:
        wf = st.selectbox(_("wilaya"), ["Toutes"] + WILAYA_NAMES, label_visibility="collapsed")
    with sb:
        if st.button("🔍", use_container_width=True): st.session_state.search_q = q

    sql = "SELECT a.*, u.name AS author FROM announcements a JOIN users u ON a.user_id=u.id WHERE 1=1"
    params = []
    if q:
        sql += " AND (a.title LIKE ? OR a.description LIKE ?)"; params += [f"%{q}%", f"%{q}%"]
    if wf != "Toutes":
        sql += " AND a.wilaya=?"; params.append(wf)
    sql += " ORDER BY a.is_urgent DESC, a.created_at DESC LIMIT 12"

    anns = qdb(sql, tuple(params))
    st.markdown(f"### 📌 Dernières annonces ({len(anns)})")
    if anns:
        for i in range(0, len(anns), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(anns):
                    with cols[j]: render_card(anns[i+j], "home")
    else:
        st.markdown(f'<div class="no-announce">🌿 {_("no_ann")}</div>', unsafe_allow_html=True)

# ── Generic announce page ──────────────────────────────────────────────────────
PAGE_SIZE = 6

def generic_page(mod, fields, filters):
    t1, t2, t3 = st.tabs([f"📋 {_('list')}", f"➕ {_('publish')}", f"🗺️ {_('map')}"])

    with t1:
        fc = st.columns(max(len(filters), 1))
        where = ["a.type=?"]
        params = [mod]
        _filter_state = {}

        for i, f in enumerate(filters):
            with fc[i % len(fc)]:
                if f == "wilaya":
                    v = st.selectbox(_("wilaya"), ["Toutes"] + WILAYA_NAMES, key=f"fw_{mod}")
                    if v != "Toutes": where.append("a.wilaya=?"); params.append(v)
                elif f == "price_max":
                    v = st.number_input("Prix max (DA)", 0, step=500, key=f"fp_{mod}")
                    if v > 0: where.append("a.price<=?"); params.append(v)
                elif f == "eq_type":
                    v = st.selectbox("Type", ["Tous","Tracteur","Moissonneuse","Charrue","Irrigation","Remorque","Autre"], key=f"feq_{mod}")
                    _filter_state["equipment_type"] = None if v == "Tous" else v
                elif f == "offer_type":
                    v = st.selectbox("Offre", ["Tous","Vente","Location"], key=f"fot_{mod}")
                    _filter_state["offer_type"] = None if v == "Tous" else v
                elif f == "product_type":
                    v = st.selectbox("Type", ["Tous","Légumes","Fruits","Céréales","Bétail","Miel","Autre"], key=f"fpt_{mod}")
                    _filter_state["product_type"] = None if v == "Tous" else v

        sql = f"SELECT a.*, u.name as author FROM announcements a JOIN users u ON a.user_id=u.id WHERE {' AND '.join(where)} ORDER BY a.is_urgent DESC, a.created_at DESC"
        anns = qdb(sql, tuple(params))

        def jmatch(a, key):
            fv = _filter_state.get(key)
            if not fv: return True
            try: return json.loads(a["data"] or "{}").get(key,"").lower() == fv.lower()
            except: return True

        anns = [a for a in anns if all(jmatch(a, k) for k in _filter_state)]

        total = len(anns)
        pg_key = f"pg_{mod}"
        if pg_key not in st.session_state: st.session_state[pg_key] = 0
        pg = min(st.session_state[pg_key], max(0, (total-1)//PAGE_SIZE))
        page_anns = anns[pg*PAGE_SIZE:(pg+1)*PAGE_SIZE]

        if page_anns:
            for i in range(0, len(page_anns), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i+j < len(page_anns):
                        with cols[j]: render_card(page_anns[i+j], mod)
        else:
            st.markdown(f'<div class="no-announce">🌿 {_("no_ann")}</div>', unsafe_allow_html=True)

        total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        p1, p2, p3 = st.columns([1,2,1])
        with p1:
            if pg > 0:
                if st.button(_("prev"), key=f"prev_{mod}"): st.session_state[pg_key] = pg-1; st.rerun()
        with p2:
            st.markdown(f"<p style='text-align:center;color:var(--muted);font-size:.8rem;'>{_('page')} {pg+1}/{total_pages} · {total} résultats</p>", unsafe_allow_html=True)
        with p3:
            if pg < total_pages-1:
                if st.button(_("next"), key=f"next_{mod}"): st.session_state[pg_key] = pg+1; st.rerun()

    with t2:
        user = st.session_state.user
        if not user: st.warning(_("login_req")); return

        with st.form(f"pub_{mod}", clear_on_submit=True):
            st.subheader(f"➕ Publier une annonce — {_(mod)}")
            c1, c2 = st.columns(2)
            title   = c1.text_input("Titre *")
            unit    = c2.text_input("Unité (ex: DA/kg)")
            desc    = st.text_area("Description")
            c3, c4  = st.columns(2)
            price   = c3.number_input("Prix (DA) *", 0.0, step=100.0)
            wilaya  = c4.selectbox(_("wilaya"), WILAYA_NAMES, key=f"pw_{mod}")
            commune = st.selectbox(_("commune"), get_communes(wilaya), key=f"pc_{mod}")

            # Options spéciales
            col_opt1, col_opt2 = st.columns(2)
            is_urgent    = col_opt1.checkbox("🚨 Vente urgente (alerte push)")
            is_traceable = col_opt2.checkbox("🔍 Activer la traçabilité QR code")
            urgent_disc  = 0
            if is_urgent:
                urgent_disc = st.slider("Réduction urgente (%)", 5, 40, 15)

            extra = {}
            if fields:
                st.markdown("**Informations complémentaires**")
                fc2 = st.columns(min(len(fields), 2))
                for idx, (field, label, opts) in enumerate(fields):
                    with fc2[idx % 2]:
                        if opts == "text":   extra[field] = st.text_input(label, key=f"f_{mod}_{field}")
                        elif opts == "num":  extra[field] = st.number_input(label, 0, key=f"f_{mod}_{field}")
                        elif isinstance(opts, list): extra[field] = st.selectbox(label, opts, key=f"f_{mod}_{field}")

            imgs = st.file_uploader("📷 Photos (max 5)", type=["jpg","jpeg","png"], accept_multiple_files=True, key=f"img_{mod}")
            submitted = st.form_submit_button("📤 " + _("publish"), use_container_width=True, type="primary")

        if submitted:
            if not title.strip(): st.error(_("fill_req"))
            else:
                imgs_b64 = [b for b in [img_to_b64(img) for img in (imgs or [])[:5]] if b]
                lat, lon = get_wilaya_coords(wilaya)
                qr_data = json.dumps({"title": title, "wilaya": wilaya, "user": user["name"], "date": date.today().isoformat()}) if is_traceable else ""
                aid = qdb(
                    "INSERT INTO announcements (user_id,type,title,description,price,unit,wilaya,commune,lat,lon,data,images,is_urgent,urgent_discount,is_traceable,qr_data) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (user["id"], mod, title.strip(), desc, price, unit, wilaya, commune, lat, lon,
                     json.dumps(extra), ";".join(imgs_b64), int(is_urgent), urgent_disc, int(is_traceable), qr_data),
                    fetch=False
                )
                if is_urgent:
                    qdb("INSERT INTO alerts (user_id,wilaya,type,message) VALUES (?,?,?,?)",
                        (user["id"], wilaya, "urgent",
                         f"🚨 Vente urgente : «{title}» à {price} DA/{unit} — {wilaya}"), fetch=False)
                st.success(_("published") + (" QR code traçabilité généré ✅" if is_traceable else ""))
                st.rerun()

    with t3:
        if not HAS_FOLIUM:
            st.info("Installez `streamlit-folium` et `folium` pour activer la carte.")
        else:
            m = folium.Map(location=[28.0, 2.5], zoom_start=5, tiles="OpenStreetMap")
            anns_map = qdb(f"SELECT * FROM announcements WHERE type=? AND lat!=0 AND lon!=0", (mod,))
            for a in anns_map:
                color = "red" if a["is_urgent"] else "green"
                folium.Marker(
                    [a["lat"], a["lon"]],
                    popup=f"<b>{a['title']}</b><br>{a['price']} {a['unit']}",
                    tooltip=a["title"],
                    icon=folium.Icon(color=color, icon="leaf", prefix="fa")
                ).add_to(m)
            st_folium(m, width=700, height=450)

# ── Module pages ───────────────────────────────────────────────────────────────
def market_page():
    st.markdown("### 🥕 " + _("market"))
    generic_page("market",
        [("product_type","Type produit",["Légumes","Fruits","Céréales","Bétail","Lait","Miel","Autre"]),
         ("quantity","Quantité (kg/t)","num"),
         ("packaging","Conditionnement",["Vrac","En sacs","En caisses","Palettes"])],
        ["wilaya","price_max","product_type"])

def job_page():
    st.markdown("### 👷 " + _("job"))
    generic_page("job",
        [("contract_type","Type contrat",["Saisonnier","Journalier","Permanent"]),
         ("skills","Compétences","text"),
         ("duration","Durée (jours)","num"),
         ("accommodation","Logement",["Non fourni","Fourni","Indemnisé"])],
        ["wilaya","price_max"])

def transport_page():
    st.markdown("### 🚛 " + _("transport"))
    generic_page("transport",
        [("vehicle_type","Véhicule",["Camion","Bétaillère","Frigorifique","Pickup","Semi-remorque"]),
         ("capacity","Capacité (t)","num"),
         ("route","Trajet","text"),
         ("frequency","Fréquence",["Journalier","Hebdomadaire","À la demande"])],
        ["wilaya","price_max"])

def grazing_page():
    st.markdown("### 🐑 " + _("grazing"))
    generic_page("grazing",
        [("area_ha","Superficie (ha)","num"),
         ("cover_type","Couvert",["Chaume","Jachère","Herbe","Alfa","Maquis"]),
         ("water","Eau disponible",["Oui","Non","Puits"]),
         ("start_date","Début disponibilité","text"),
         ("end_date","Fin disponibilité","text"),
         ("max_animals","Max animaux","num")],
        ["wilaya","price_max"])

def pollination_page():
    st.markdown("### 🐝 " + _("pollination"))
    generic_page("pollination",
        [("hive_count","Nombre de ruches","num"),
         ("bee_race","Race",["Locale (Apis m. intermissa)","Carnica","Hybride","Saharan"]),
         ("zone","Zone intervention","text"),
         ("availability","Disponibilité","text")],
        ["wilaya","price_max"])

def fertilizer_page():
    st.markdown("### 🌱 " + _("fertilizer"))
    generic_page("fertilizer",
        [("fertilizer_type","Type",["Fumier bovin","Fumier ovin","Fiente volaille","Compost végétal","NPK","Urée","Phosphate"]),
         ("quantity_tons","Quantité (t)","num"),
         ("packaging","Conditionnement",["Vrac","Ensaché 50kg","Sur palettes"])],
        ["wilaya","price_max"])

def equipment_page():
    st.markdown("### 🚜 " + _("equipment"))
    generic_page("equipment",
        [("offer_type","Offre",["Vente","Location","Échange"]),
         ("equipment_type","Type",["Tracteur","Moissonneuse","Charrue","Remorque","Irrigation goutte-à-goutte","Épandeur","Semoir","Pulvérisateur","Autre"]),
         ("brand","Marque","text"),
         ("model","Modèle","text"),
         ("year","Année fabrication","num"),
         ("state","État",["Neuf","Très bon","Bon","Fonctionnel","À réviser"]),
         ("rental_period","Période location",["Heure","Jour","Semaine","Mois","Saison"]),
         ("availability","Disponibilité","text")],
        ["wilaya","price_max","eq_type","offer_type"])

# ── WEATHER page ───────────────────────────────────────────────────────────────
def weather_page():
    st.markdown("### 🌤️ Météo agricole")
    user = st.session_state.user
    default_w = user["wilaya"] if user else "16 - Alger"
    wilaya = st.selectbox("Choisir une wilaya", WILAYA_NAMES, index=WILAYA_NAMES.index(default_w) if default_w in WILAYA_NAMES else 15)

    lat, lon = get_wilaya_coords(wilaya)
    with st.spinner("Chargement météo…"):
        data = get_weather(lat, lon, wilaya)

    cur = data.get("current", {})
    temp = cur.get("temperature_2m", 0)
    hum  = cur.get("relative_humidity_2m", 0)
    wind = cur.get("wind_speed_10m", 0)
    wc   = cur.get("weathercode", 0)
    icon, desc = wmo(wc)

    # Current conditions
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="weather-card"><div style="font-size:2.5rem;">{icon}</div><div class="weather-temp">{temp}°C</div><div class="weather-desc">{desc}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat"><div class="num">💧{hum}%</div><div class="lbl">Humidité</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat"><div class="num">💨{wind:.0f}</div><div class="lbl">Vent km/h</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat"><div class="num">📍</div><div class="lbl">{wilaya.split(" - ")[1]}</div></div>', unsafe_allow_html=True)

    # Alerts
    alerts_weather = []
    if temp < 2:  alerts_weather.append("🥶 **Risque de gel** — Protégez vos cultures sensibles cette nuit.")
    if temp > 40: alerts_weather.append("🔥 **Canicule** — Irriguez tôt le matin et en soirée seulement.")
    if wind > 60: alerts_weather.append("💨 **Vent fort** — Évitez les traitements phytosanitaires.")
    if hum < 25:  alerts_weather.append("🏜️ **Air très sec** — Risque d'oïdium et d'araignées rouges.")

    if alerts_weather:
        st.markdown("**⚠️ Alertes agrométéo :**")
        for a in alerts_weather:
            st.warning(a)

    # 7-day forecast
    st.markdown("---")
    st.subheader("📅 Prévisions 7 jours")
    daily = data.get("daily", {})
    days  = daily.get("time", [])
    tmax  = daily.get("temperature_2m_max", [])
    tmin  = daily.get("temperature_2m_min", [])
    rain  = daily.get("precipitation_sum", [])
    wcodes= daily.get("weathercode", [])

    cols = st.columns(len(days[:7]))
    for i, d in enumerate(days[:7]):
        d_obj = datetime.strptime(d, "%Y-%m-%d")
        day_name = d_obj.strftime("%a %d")
        ico, _ = wmo(wcodes[i] if i < len(wcodes) else 0)
        tmin_v = tmin[i] if i < len(tmin) else 0
        tmax_v = tmax[i] if i < len(tmax) else 0
        rain_v = rain[i] if i < len(rain) else 0
        with cols[i]:
            st.markdown(f"""
            <div class="stat" style="padding:.6rem;">
                <div style="font-size:1.5rem;">{ico}</div>
                <div style="font-size:.75rem;font-weight:600;color:#374151;">{day_name}</div>
                <div style="font-size:.8rem;color:#dc2626;">{tmax_v:.0f}°</div>
                <div style="font-size:.75rem;color:#2563eb;">{tmin_v:.0f}°</div>
                <div style="font-size:.7rem;color:#6b7280;">💧{rain_v:.0f}mm</div>
            </div>
            """, unsafe_allow_html=True)

    # Agroconseils basés sur la météo
    st.markdown("---")
    st.subheader("🌾 Conseils agronomiques du jour")
    conseils = []
    if temp > 25 and hum < 40:
        conseils.append("☀️ **Irrigation** : Conditions sèches et chaudes — irriguez au lever du soleil ou après 18h.")
    if sum(rain[:3]) > 10:
        conseils.append("🌧️ **Fongicides** : Pluies prévues — appliquez préventivement un fongicide cuivrique sur vigne et tomate.")
    if 10 < temp < 20 and hum > 60:
        conseils.append("🦠 **Mildiou** : Conditions favorables au développement — surveillance renforcée recommandée.")
    if wind > 20:
        conseils.append("💨 **Traitements** : Vent > 20 km/h — reportez les pulvérisations pour éviter la dérive.")
    if not conseils:
        conseils.append("✅ **Conditions favorables** — Bonne période pour les travaux agricoles habituels.")

    for c in conseils:
        st.info(c)

# ── PRICES page ────────────────────────────────────────────────────────────────
def prices_page():
    st.markdown("### 📊 Prix & Tendances des marchés")

    products = ["Pomme de terre", "Tomate", "Blé dur", "Oignon", "Dattes Deglet"]
    wilayas_list = ["31 - Oran", "16 - Alger", "19 - Sétif", "39 - El Oued", "25 - Constantine"]

    col_p, col_w = st.columns(2)
    prod = col_p.selectbox("Produit", products)
    wil  = col_w.selectbox("Wilaya", wilayas_list)

    rows = qdb("SELECT price, recorded_at FROM price_history WHERE product=? AND wilaya=? ORDER BY recorded_at", (prod, wil))

    if rows:
        dates  = [r["recorded_at"] for r in rows]
        prices = [r["price"] for r in rows]

        # Tendance
        if len(prices) >= 2:
            trend = prices[-1] - prices[-7] if len(prices) >= 7 else prices[-1] - prices[0]
            trend_str = f'<span class="price-up">▲ +{trend:.1f} DA</span>' if trend > 0 else f'<span class="price-down">▼ {trend:.1f} DA</span>'
        else:
            trend_str = "—"

        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="stat"><div class="num">{prices[-1]:.0f} DA</div><div class="lbl">Prix actuel</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="stat"><div class="num">{trend_str}</div><div class="lbl">Variation 7j</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="stat"><div class="num">{sum(prices)/len(prices):.0f} DA</div><div class="lbl">Moyenne 30j</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if HAS_PLOTLY:
            # Prédiction simple (régression linéaire basique)
            n = len(prices)
            x_vals = list(range(n))
            mean_x = sum(x_vals) / n
            mean_y = sum(prices) / n
            num_lr  = sum((x_vals[i] - mean_x) * (prices[i] - mean_y) for i in range(n))
            den_lr  = sum((x_vals[i] - mean_x) ** 2 for i in range(n))
            slope   = num_lr / den_lr if den_lr != 0 else 0
            intercept = mean_y - slope * mean_x

            future_days = 7
            pred_prices = [intercept + slope * (n + i) for i in range(future_days)]
            pred_dates  = [(date.today() + timedelta(days=i+1)).isoformat() for i in range(future_days)]

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=prices, mode='lines+markers', name='Historique', line=dict(color='#2e7d32', width=2)))
            fig.add_trace(go.Scatter(x=pred_dates, y=[round(p, 1) for p in pred_prices], mode='lines+markers', name='Prévision 7j', line=dict(color='#f59e0b', width=2, dash='dash')))
            fig.update_layout(
                title=f"{prod} — {wil.split(' - ')[1]}",
                xaxis_title="Date", yaxis_title="Prix (DA/kg)",
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Sora, sans-serif"), height=350,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Conseil basé sur tendance
            if slope > 0.3:
                st.success(f"📈 **Tendance haussière** — Bon moment pour **vendre** {prod}. Prix attendu dans 7 jours : {pred_prices[-1]:.0f} DA.")
            elif slope < -0.3:
                st.warning(f"📉 **Tendance baissière** — Préférez **vendre maintenant** ou stocker si vous le pouvez. Prix attendu : {pred_prices[-1]:.0f} DA.")
            else:
                st.info(f"➡️ **Prix stable** — Pas de tendance forte sur {prod} pour les 7 prochains jours.")
        else:
            st.info("Installez `plotly` pour les graphiques de prix.")

    # Tableau comparatif multi-wilayas
    st.markdown("---")
    st.subheader("🗺️ Comparaison entre wilayas")
    latest = {}
    for w in wilayas_list:
        r = qdb("SELECT price FROM price_history WHERE product=? AND wilaya=? ORDER BY recorded_at DESC LIMIT 1", (prod, w))
        if r: latest[w.split(" - ")[1]] = r[0]["price"]

    if latest and HAS_PLOTLY:
        wnames = list(latest.keys())
        wprices = [latest[w] for w in wnames]
        colors = ["#2e7d32" if p == min(wprices) else ("#dc2626" if p == max(wprices) else "#43a047") for p in wprices]
        fig2 = go.Figure(go.Bar(x=wnames, y=wprices, marker_color=colors, text=[f"{p:.0f} DA" for p in wprices], textposition='auto'))
        fig2.update_layout(
            title=f"Prix de {prod} par wilaya (aujourd'hui)",
            yaxis_title="DA/kg", plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)', height=280,
        )
        st.plotly_chart(fig2, use_container_width=True)
        min_w = min(latest, key=latest.get)
        max_w = max(latest, key=latest.get)
        st.info(f"💡 Achetez à **{min_w}** ({latest[min_w]:.0f} DA) et revendez à **{max_w}** ({latest[max_w]:.0f} DA) — écart : **{latest[max_w]-latest[min_w]:.0f} DA/kg**")

# ── ALERTS page ────────────────────────────────────────────────────────────────
def alerts_page():
    st.markdown("### 🚨 Alertes & Ventes urgentes")

    # Ventes urgentes
    urgent = qdb("SELECT a.*, u.name as author FROM announcements a JOIN users u ON a.user_id=u.id WHERE a.is_urgent=1 ORDER BY a.created_at DESC")
    if urgent:
        st.markdown(f"**{len(urgent)} vente(s) urgente(s) disponible(s)**")
        for a in urgent:
            disc = a["urgent_discount"] or 0
            orig_p = a["price"] / (1 - disc/100) if disc > 0 else a["price"]
            with st.container():
                st.markdown(f"""
                <div class="urgent-banner">
                    🚨 <strong>{a['title']}</strong> — {a['author']} — {a['wilaya']}
                    <br><span style="font-size:.8rem;">Prix urgent: <strong>{a['price']:.0f} DA/{a['unit']}</strong>
                    {f'(−{disc}% vs {orig_p:.0f} DA)' if disc>0 else ''}</span>
                </div>
                """, unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("💬 Contacter", key=f"urg_msg_{a['id']}", use_container_width=True, type="primary"):
                        st.session_state.msg_to = a["user_id"]; st.session_state.page = "messages"; st.rerun()
                with c2:
                    if st.button("📋 Voir l'annonce", key=f"urg_view_{a['id']}", use_container_width=True):
                        st.session_state.page = a["type"]; st.rerun()
    else:
        st.info("Aucune vente urgente en ce moment. 🎉")

    st.markdown("---")
    # Publish urgent
    st.subheader("📢 Publier une vente urgente")
    if not st.session_state.user:
        st.warning(_("login_req"))
    else:
        with st.form("urgent_form", clear_on_submit=True):
            title   = st.text_input("Titre de l'annonce *")
            c1, c2  = st.columns(2)
            price   = c1.number_input("Prix urgent (DA)", 0.0, step=100.0)
            unit    = c2.text_input("Unité (ex: kg, t)")
            disc    = st.slider("Réduction par rapport au prix normal (%)", 0, 50, 15)
            wilaya  = st.selectbox(_("wilaya"), WILAYA_NAMES)
            desc    = st.text_area("Message d'urgence", placeholder="Ex: 500 kg de tomates doivent être vendus avant demain, calibre A…")
            mod_type = st.selectbox("Type", ["market","equipment","grazing","transport"])
            if st.form_submit_button("🚨 Publier en urgence", use_container_width=True, type="primary"):
                if title.strip():
                    lat, lon = get_wilaya_coords(wilaya)
                    qdb("INSERT INTO announcements (user_id,type,title,description,price,unit,wilaya,commune,lat,lon,is_urgent,urgent_discount) VALUES (?,?,?,?,?,?,?,?,?,?,1,?)",
                        (st.session_state.user["id"], mod_type, title, desc, price, unit, wilaya, get_communes(wilaya)[0], lat, lon, disc), fetch=False)
                    qdb("INSERT INTO alerts (user_id,wilaya,type,message) VALUES (?,?,?,?)",
                        (st.session_state.user["id"], wilaya, "urgent", f"🚨 {title} — {price} DA/{unit}"), fetch=False)
                    st.success("Alerte urgente publiée ! Tous les membres à proximité ont été notifiés. ✅")
                    st.rerun()

    st.markdown("---")
    # Alertes météo
    st.subheader("🌤️ Alertes météo par wilaya")
    if st.session_state.user:
        uw = st.session_state.user.get("wilaya", "16 - Alger")
        lat, lon = get_wilaya_coords(uw)
        data = get_weather(lat, lon)
        cur = data.get("current", {})
        temp = cur.get("temperature_2m", 20)
        rain_sum = sum(data.get("daily", {}).get("precipitation_sum", [0])[:3])
        wind = cur.get("wind_speed_10m", 0)

        alerts_m = []
        if temp < 3:  alerts_m.append(("🥶", "Gel imminent", f"T° = {temp}°C — Couvrez les cultures fragiles.", "error"))
        if temp > 42: alerts_m.append(("🔥", "Canicule", f"T° = {temp}°C — Stress hydrique maximum.", "error"))
        if rain_sum > 15: alerts_m.append(("🌧️", "Fortes pluies prévues", f"{rain_sum:.0f}mm sur 3 jours — Risque mildiou élevé.", "warning"))
        if wind > 60: alerts_m.append(("💨", "Vent violent", f"{wind:.0f} km/h — Danger pour serres et récoltes.", "warning"))
        if not alerts_m: alerts_m.append(("✅", "Conditions normales", f"Météo favorable à {uw.split(' - ')[1]}.", "success"))

        for icon_a, title_a, msg_a, typ_a in alerts_m:
            if typ_a == "error": st.error(f"{icon_a} **{title_a}** — {msg_a}")
            elif typ_a == "warning": st.warning(f"{icon_a} **{title_a}** — {msg_a}")
            else: st.success(f"{icon_a} **{title_a}** — {msg_a}")

# ── AI ASSISTANT page ──────────────────────────────────────────────────────────
def assistant_page():
    st.markdown("### 🤖 Assistant agricole IA")
    user = st.session_state.user
    user_wilaya = user["wilaya"] if user else ""

    # Présentation
    st.markdown("""
    <div style="background:var(--green-pale);border-left:4px solid var(--green);padding:12px 16px;border-radius:8px;margin-bottom:1rem;">
    <strong>🌿 Bienvenue</strong> — Posez-moi vos questions sur les cultures, maladies, prix, calendriers agricoles, subventions FNRDA, et plus encore.
    Je connais les 58 wilayas algériennes et les pratiques locales.
    </div>
    """, unsafe_allow_html=True)

    # Questions suggérées
    st.markdown("**💡 Questions fréquentes :**")
    suggestions = [
        "Quand planter les tomates ?",
        "Comment traiter le mildiou ?",
        "Prix de la pomme de terre",
        "Aides FNRDA 2026",
        "Conseils irrigation goutte-à-goutte",
        "Quand récolter les dattes ?",
    ]
    cols = st.columns(3)
    for i, sug in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(sug, key=f"sug_{i}", use_container_width=True):
                st.session_state["ai_pending"] = sug

    st.markdown("---")

    # Historique conversation
    if user:
        history = qdb("SELECT role,content FROM ai_conversations WHERE user_id=? ORDER BY created_at DESC LIMIT 20", (user["id"],))
        history = list(reversed(history))
    else:
        history = []

    if history:
        for msg in history[-10:]:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-bubble">🧑‍🌾 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-bubble">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

    # Input
    pending = st.session_state.pop("ai_pending", "")
    with st.form("ai_form", clear_on_submit=True):
        question = st.text_input("Votre question…", value=pending, placeholder="Ex: Quand semer le blé dur à Tiaret ?")
        submitted = st.form_submit_button("Envoyer 📤", use_container_width=True, type="primary")

    if submitted and question.strip():
        response = ai_respond(question.strip(), user_wilaya)
        if user:
            qdb("INSERT INTO ai_conversations (user_id,role,content) VALUES (?,?,?)", (user["id"],"user",question.strip()), fetch=False)
            qdb("INSERT INTO ai_conversations (user_id,role,content) VALUES (?,?,?)", (user["id"],"assistant",response), fetch=False)
        st.markdown(f'<div class="user-bubble">🧑‍🌾 {question}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ai-bubble">🤖 {response}</div>', unsafe_allow_html=True)

    if not user:
        st.info("💡 Connectez-vous pour sauvegarder l'historique de vos conversations.")

# ── TRACEABILITY ── (accessible via card QR)
def tracability_page():
    st.markdown("### 🔍 Traçabilité produit")
    st.info("📱 Scannez le QR code d'un produit pour voir son origine et sa certification.")

    ann_id = st.number_input("ID d'annonce tracée", min_value=1, step=1)
    if st.button("🔍 Consulter la traçabilité", type="primary"):
        ann = qdb("SELECT * FROM announcements WHERE id=? AND is_traceable=1", (int(ann_id),))
        if ann:
            a = ann[0]
            owner = qdb("SELECT * FROM users WHERE id=?", (a["user_id"],))
            o = owner[0] if owner else {}

            st.markdown("---")
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"### {a['title']}")
                st.markdown(f"**🌍 Origine :** {a['wilaya']} — {a['commune']}")
                st.markdown(f"**📅 Date publication :** {a['created_at'][:10]}")
                st.markdown(f"**👤 Producteur :** {o.get('name','—')}")
                st.markdown(f"**✅ Producteur vérifié :** {'Oui ✅' if o.get('is_verified') else 'Non ❌'}")
                st.markdown(f"**⭐ Réputation :** {o.get('reputation_score', 0):.1f}/5")

                try:
                    d = json.loads(a["data"] or "{}")
                    if d:
                        st.markdown("**📋 Caractéristiques :**")
                        for k, v in d.items():
                            st.write(f"• {k.replace('_',' ').title()} : {v}")
                except: pass

            with c2:
                qr_b64 = make_qr(f"AgriConnect|ID:{a['id']}|{a['title']}|{a['wilaya']}")
                if qr_b64:
                    st.markdown(f'<div class="qr-box"><img src="data:image/png;base64,{qr_b64}" width="140"><br><small>QR Traçabilité #{a["id"]}</small></div>', unsafe_allow_html=True)
                else:
                    st.info("Installez `qrcode` pour générer le QR code.")
        else:
            st.error("Annonce introuvable ou traçabilité non activée pour cet ID.")

# ── COOPERATIVES page ──────────────────────────────────────────────────────────
def cooperative_page():
    st.markdown("### 🤝 Coopératives agricoles numériques")
    user = st.session_state.user

    tab1, tab2, tab3 = st.tabs(["📋 Liste", "➕ Créer", "👥 Mes coopératives"])

    with tab1:
        coops = qdb("""
            SELECT c.*, u.name as creator_name,
                   (SELECT COUNT(*) FROM coop_members cm WHERE cm.coop_id=c.id) as nb_members
            FROM cooperatives c JOIN users u ON c.creator_id=u.id ORDER BY c.created_at DESC
        """)
        if coops:
            for co in coops:
                with st.expander(f"🤝 {co['name']} — {co['wilaya']} ({co['nb_members']} membres)"):
                    st.markdown(f"**Filière :** {co['filiere']} | **Fondateur :** {co['creator_name']}")
                    st.markdown(f"**Description :** {co['description'] or '—'}")
                    st.markdown(f"**Créée le :** {co['created_at'][:10]}")

                    # Membres
                    members = qdb("SELECT u.name, u.wilaya, cm.role FROM coop_members cm JOIN users u ON cm.user_id=u.id WHERE cm.coop_id=?", (co["id"],))
                    if members:
                        st.markdown(f"**Membres :** " + ", ".join([f"{m['name']} ({m['role']})" for m in members]))

                    if user:
                        already = qdb("SELECT 1 FROM coop_members WHERE coop_id=? AND user_id=?", (co["id"], user["id"]))
                        if not already:
                            if st.button(f"Rejoindre", key=f"join_{co['id']}", type="primary"):
                                qdb("INSERT OR IGNORE INTO coop_members (coop_id,user_id,role) VALUES (?,?,'member')", (co["id"], user["id"]), fetch=False)
                                st.success("Vous avez rejoint la coopérative !"); st.rerun()
                        else:
                            st.success("✅ Vous êtes membre.")
        else:
            st.info("Aucune coopérative pour le moment.")

    with tab2:
        if not user: st.warning(_("login_req")); return
        with st.form("coop_form", clear_on_submit=True):
            c_name    = st.text_input("Nom de la coopérative *")
            c_filiere = st.selectbox("Filière", ["Légumes","Fruits","Céréales","Élevage","Apiculture","Lait","Dattes","Autre"])
            c_wilaya  = st.selectbox(_("wilaya"), WILAYA_NAMES)
            c_desc    = st.text_area("Objectif / Description")
            if st.form_submit_button("🤝 Créer la coopérative", use_container_width=True, type="primary"):
                if c_name.strip():
                    cid = qdb("INSERT INTO cooperatives (name,wilaya,filiere,creator_id,description) VALUES (?,?,?,?,?)",
                              (c_name, c_wilaya, c_filiere, user["id"], c_desc), fetch=False)
                    qdb("INSERT OR IGNORE INTO coop_members (coop_id,user_id,role) VALUES (?,?,'admin')", (cid, user["id"]), fetch=False)
                    st.success("Coopérative créée ! Invitez des membres. ✅"); st.rerun()

    with tab3:
        if not user: st.warning(_("login_req")); return
        my_coops = qdb("""
            SELECT c.*, cm.role FROM cooperatives c
            JOIN coop_members cm ON c.id=cm.coop_id
            WHERE cm.user_id=?
        """, (user["id"],))
        if my_coops:
            for co in my_coops:
                st.markdown(f"**🤝 {co['name']}** — {co['filiere']} — Rôle : `{co['role']}`")
        else:
            st.info("Vous n'êtes membre d'aucune coopérative.")

# ── DASHBOARD page ─────────────────────────────────────────────────────────────
def dashboard_page():
    st.markdown("### 📊 Tableau de bord personnel")
    user = st.session_state.user
    if not user: st.warning(_("login_req")); return

    uid = user["id"]
    nb_ann  = qdb("SELECT COUNT(*) as n FROM announcements WHERE user_id=?", (uid,))[0]["n"]
    nb_msg  = qdb("SELECT COUNT(*) as n FROM messages WHERE sender_id=?", (uid,))[0]["n"]
    nb_msg_r = qdb("SELECT COUNT(*) as n FROM messages WHERE receiver_id=?", (uid,))[0]["n"]
    nb_ct   = qdb("SELECT COUNT(*) as n FROM contracts WHERE renter_id=? OR owner_id=?", (uid, uid))[0]["n"]
    rep     = compute_reputation(uid)

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, num, lbl in [
        (c1, nb_ann, "Annonces"), (c2, nb_msg, "Msg envoyés"),
        (c3, nb_msg_r, "Msg reçus"), (c4, nb_ct, "Contrats"),
        (c5, f"{rep:.1f}/5", "Réputation"),
    ]:
        col.markdown(f'<div class="stat"><div class="num">{num}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Réputation détaillée
    col_rep, col_ann = st.columns(2)
    with col_rep:
        st.subheader("⭐ Score de réputation")
        pct = int((rep / 5) * 100)
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:16px;margin:10px 0;">
            <div class="rep-ring" style="--pct:{pct}"><span class="rep-val">{rep:.1f}</span></div>
            <div>
                <div style="font-weight:600;font-size:1.1rem;">{rep:.1f} / 5 étoiles</div>
                <div class="score-bar" style="width:180px;margin:6px 0;"><div class="score-fill" style="width:{pct}%;"></div></div>
                <div style="font-size:.78rem;color:var(--muted);">
                {"✅ Profil vérifié" if user["is_verified"] else "❌ Non vérifié — Vérifiez votre compte"}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        badges = []
        if user["is_verified"]:       badges.append(("✅", "Membre vérifié", "b-verified"))
        if rep >= 4.5:                 badges.append(("🏆", "Top vendeur", "b-amber"))
        if nb_ann >= 5:               badges.append(("📦", "Vendeur actif", "b-green"))
        if nb_ct >= 3:                badges.append(("📄", "Contractant fiable", "b-blue"))

        if badges:
            st.markdown("**Badges :**")
            for icon_b, label_b, cls_b in badges:
                st.markdown(f'<span class="badge {cls_b}">{icon_b} {label_b}</span> ', unsafe_allow_html=True)

    with col_ann:
        st.subheader("📌 Mes annonces récentes")
        my_anns = qdb("SELECT * FROM announcements WHERE user_id=? ORDER BY created_at DESC LIMIT 5", (uid,))
        if my_anns:
            for a in my_anns:
                urgent_tag = " 🚨" if a["is_urgent"] else ""
                trace_tag  = " 🔍" if a["is_traceable"] else ""
                cols_a = st.columns([4, 1])
                cols_a[0].markdown(f"**{a['title']}**{urgent_tag}{trace_tag}<br><small style='color:var(--muted);'>{a['price']} {a['unit']} · {a['wilaya']}</small>", unsafe_allow_html=True)
                with cols_a[1]:
                    if st.button("🗑️", key=f"del_{a['id']}", help="Supprimer"):
                        qdb("DELETE FROM announcements WHERE id=? AND user_id=?", (a["id"], uid), fetch=False); st.rerun()
        else:
            st.info("Aucune annonce.")

    st.markdown("---")

    # Activité récente (timeline)
    st.subheader("🕐 Activité récente")
    recent_msgs = qdb("SELECT m.content, m.created_at, u.name FROM messages m JOIN users u ON m.receiver_id=u.id WHERE m.sender_id=? ORDER BY m.created_at DESC LIMIT 5", (uid,))
    recent_revs = qdb("SELECT r.comment, r.rating, r.created_at FROM reviews r JOIN announcements a ON r.announcement_id=a.id WHERE a.user_id=? ORDER BY r.created_at DESC LIMIT 3", (uid,))

    events = []
    for m in recent_msgs:
        events.append({"date": m["created_at"][:16], "text": f"💬 Message envoyé à {m['name']}: «{m['content'][:40]}…»"})
    for r in recent_revs:
        events.append({"date": r["created_at"][:16], "text": f"⭐ {'⭐'*r['rating']} Avis reçu: «{r['comment'][:40]}…»"})

    events.sort(key=lambda x: x["date"], reverse=True)
    if events:
        for ev in events[:8]:
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div><div class="timeline-date">{ev['date']}</div><div class="timeline-text">{ev['text']}</div></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Aucune activité récente.")

# ── ANEM page ──────────────────────────────────────────────────────────────────
def anem_page():
    st.markdown("### 🏛️ " + _("anem"))
    user = st.session_state.user
    if not user or user.get("profile_type") != "ANEM":
        st.error("⛔ Accès réservé aux agents ANEM."); return

    c1, c2, c3, c4 = st.columns(4)
    for col, sql, lbl in [
        (c1, "SELECT COUNT(*) as n FROM announcements WHERE type='job'", "Offres d'emploi"),
        (c2, "SELECT COUNT(*) as n FROM users WHERE profile_type='Travailleur'", "Demandeurs"),
        (c3, "SELECT COUNT(*) as n FROM users WHERE profile_type='Travailleur' AND is_verified=1", "Validés"),
        (c4, "SELECT COUNT(*) as n FROM messages", "Messages total"),
    ]:
        n = qdb(sql)[0]["n"]
        col.markdown(f'<div class="stat"><div class="num">{n}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("✅ Validation profils travailleurs")
    pending = qdb("SELECT * FROM users WHERE profile_type='Travailleur' AND is_verified=0")
    if pending:
        for t in pending:
            with st.expander(f"{t['name']} — {t['phone']} — {t['wilaya']}"):
                if t["documents"]:
                    st.image(f"data:image/jpeg;base64,{t['documents']}", width=250)
                c1, c2 = st.columns(2)
                if c1.button("✅ Valider", key=f"v_{t['id']}", type="primary"):
                    qdb("UPDATE users SET is_verified=1 WHERE id=?", (t["id"],), fetch=False); st.rerun()
                if c2.button("❌ Rejeter", key=f"r_{t['id']}"):
                    qdb("DELETE FROM users WHERE id=? AND is_verified=0", (t["id"],), fetch=False); st.rerun()
    else:
        st.success("Aucun profil en attente. ✅")

    st.markdown("---")
    st.subheader("📋 Offres d'emploi")
    jobs = qdb("SELECT a.*, u.name as author FROM announcements a JOIN users u ON a.user_id=u.id WHERE a.type='job' ORDER BY a.created_at DESC")
    for j in jobs:
        cnt = qdb("SELECT COUNT(*) as n FROM messages WHERE announcement_id=?", (j["id"],))[0]["n"]
        with st.expander(f"📌 {j['title']} — {j['wilaya']} (📩 {cnt})"):
            st.write(j["description"])
            posts = qdb("SELECT DISTINCT u.name, u.phone, u.wilaya FROM messages m JOIN users u ON m.sender_id=u.id WHERE m.announcement_id=?", (j["id"],))
            if posts:
                st.markdown("**Candidats :**")
                for p in posts:
                    st.write(f"• {p['name']} ({p['phone']}) — {p['wilaya']}")

# ── Messages page ──────────────────────────────────────────────────────────────
def messages_page():
    st.markdown("### 💬 " + _("messages"))
    user = st.session_state.user
    if not user: st.warning(_("login_req")); return

    if st.session_state.msg_to:
        other = qdb("SELECT name, profile_type FROM users WHERE id=?", (st.session_state.msg_to,))
        if not other: st.session_state.msg_to = None; st.rerun()

        if st.button("← Retour aux conversations"):
            st.session_state.msg_to = None; st.rerun()

        oth = other[0]
        st.subheader(f"Conversation avec {oth['name']} ({oth['profile_type']})")

        msgs = qdb("""SELECT * FROM messages
            WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)
            ORDER BY created_at""",
            (user["id"], st.session_state.msg_to, st.session_state.msg_to, user["id"]))

        st.markdown('<div style="max-height:380px;overflow-y:auto;padding:8px;background:#f9fafb;border-radius:10px;margin-bottom:10px;">', unsafe_allow_html=True)
        for m in msgs:
            css = "user-bubble" if m["sender_id"] == user["id"] else "ai-bubble"
            st.markdown(f'<div class="{css}">{m["content"]}<div style="font-size:.65rem;color:var(--muted);margin-top:3px;">{m["created_at"][:16]}</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        with st.form("send_msg", clear_on_submit=True):
            txt = st.text_area("Votre message…", height=80)
            if st.form_submit_button("Envoyer 📤", use_container_width=True, type="primary"):
                if txt.strip():
                    qdb("INSERT INTO messages (sender_id,receiver_id,announcement_id,content) VALUES (?,?,?,?)",
                        (user["id"], st.session_state.msg_to, st.session_state.msg_announce, txt.strip()), fetch=False)
                    st.rerun()
    else:
        contacts = qdb("""SELECT DISTINCT u.id, u.name, u.profile_type, u.reputation_score,
            MAX(m.created_at) as last_msg
            FROM users u JOIN messages m ON u.id IN (m.sender_id,m.receiver_id)
            WHERE (m.sender_id=? OR m.receiver_id=?) AND u.id!=?
            GROUP BY u.id ORDER BY last_msg DESC""",
            (user["id"],)*3)

        if contacts:
            for c in contacts:
                co1, co2 = st.columns([5, 1])
                stars = "⭐" * round(c["reputation_score"] or 0)
                co1.markdown(f"**{c['name']}** — {c['profile_type']} {stars}<br><small style='color:var(--muted);'>Dernier message : {c['last_msg'][:10] if c['last_msg'] else '—'}</small>", unsafe_allow_html=True)
                with co2:
                    if st.button("Ouvrir", key=f"open_{c['id']}", use_container_width=True):
                        st.session_state.msg_to = c["id"]; st.rerun()
                st.markdown('<div style="border-bottom:1px solid var(--border);margin:6px 0;"></div>', unsafe_allow_html=True)
        else:
            st.info("Aucune conversation. Contactez un vendeur depuis une annonce.")

# ── Reviews page ───────────────────────────────────────────────────────────────
def reviews_page():
    st.markdown("### ⭐ Évaluations")
    user = st.session_state.user
    if not user: st.warning(_("login_req")); return

    if st.session_state.review_announce:
        ann = qdb("SELECT * FROM announcements WHERE id=?", (st.session_state.review_announce,))
        if not ann: st.session_state.review_announce = None; st.rerun()

        already = qdb("SELECT id FROM reviews WHERE announcement_id=? AND reviewer_id=?", (st.session_state.review_announce, user["id"]))
        if already:
            st.warning("Vous avez déjà évalué cette annonce.")
            st.session_state.review_announce = None; return

        st.subheader(f"Évaluer : {ann[0]['title']}")
        if st.button("← Retour"): st.session_state.review_announce = None; st.rerun()

        with st.form("rev_form"):
            rating  = st.slider("Note", 1, 5, 4)
            comment = st.text_area("Commentaire")
            if st.form_submit_button("Soumettre ✅", use_container_width=True, type="primary"):
                qdb("INSERT OR IGNORE INTO reviews (announcement_id,reviewer_id,rating,comment) VALUES (?,?,?,?)",
                    (st.session_state.review_announce, user["id"], rating, comment), fetch=False)
                # Update reputation
                new_rep = compute_reputation(ann[0]["user_id"])
                qdb("UPDATE users SET reputation_score=? WHERE id=?", (new_rep, ann[0]["user_id"]), fetch=False)
                st.success("Merci pour votre évaluation !"); st.session_state.review_announce = None; st.rerun()
    else:
        my = qdb("SELECT id FROM announcements WHERE user_id=?", (user["id"],))
        if my:
            ids = [str(a["id"]) for a in my]
            revs = qdb(f"SELECT r.*,u.name FROM reviews r JOIN users u ON r.reviewer_id=u.id WHERE r.announcement_id IN ({','.join(ids)}) ORDER BY r.created_at DESC")
            if revs:
                avg = sum(r["rating"] for r in revs) / len(revs)
                st.markdown(f"**Moyenne : {'⭐'*round(avg)} ({avg:.1f}/5 sur {len(revs)} avis)**")
                for r in revs:
                    st.markdown(f"{'⭐'*r['rating']} **{r['name']}** — *{r['comment']}* <small style='color:var(--muted);'>({r['created_at'][:10]})</small>", unsafe_allow_html=True)
            else:
                st.info("Aucun avis reçu pour vos annonces.")
        else:
            st.info("Publiez des annonces pour recevoir des avis.")

# ── Contract page ──────────────────────────────────────────────────────────────
def contract_page():
    st.markdown("### 📄 Contrats")
    user = st.session_state.user
    if not user: st.warning(_("login_req")); return

    if st.session_state.contract_announce:
        ann = qdb("SELECT * FROM announcements WHERE id=?", (st.session_state.contract_announce,))
        if not ann: st.session_state.contract_announce = None; st.rerun()
        a = ann[0]
        owner = qdb("SELECT * FROM users WHERE id=?", (a["user_id"],))
        if not owner: st.error("Propriétaire introuvable."); return
        o = owner[0]

        st.subheader(f"Contrat pour : {a['title']}")
        if st.button("← Retour"): st.session_state.contract_announce = None; st.rerun()

        c1, c2 = st.columns(2)
        start = c1.date_input("Date de début", date.today())
        end   = c2.date_input("Date de fin", date.today() + timedelta(days=7))
        terms = st.text_area("Conditions particulières", height=100)

        if start > end:
            st.error("La date de fin doit être après la date de début.")
        else:
            if st.button("📥 Générer le contrat PDF", type="primary", use_container_width=True):
                lines = [
                    "=" * 52,
                    "         CONTRAT AGRICONNECT",
                    "=" * 52,
                    f"Annonce      : {a['title']}",
                    f"Propriétaire : {o['name']} ({o['phone']})",
                    f"Locataire    : {user['name']} ({user['phone']})",
                    f"Période      : {start.isoformat()} → {end.isoformat()}",
                    f"Wilaya       : {a['wilaya']}",
                    f"Prix         : {a['price']:,.0f} {a['unit']}",
                    "",
                    "Conditions particulières :",
                    terms or "(aucune)",
                    "",
                    "=" * 52,
                    f"Généré le : {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                    "AgriConnect © 2026 — contact@agriconnect.dz",
                ]
                content = "\n".join(lines).encode("utf-8")
                st.download_button("📥 Télécharger le contrat", data=content,
                                   file_name=f"contrat_agriconnect_{a['id']}.txt", mime="text/plain", use_container_width=True)
                qdb("INSERT INTO contracts (announcement_id,renter_id,owner_id,start_date,end_date,terms,status) VALUES (?,?,?,?,?,?,?)",
                    (a["id"], user["id"], o["id"], start.isoformat(), end.isoformat(), terms, "active"), fetch=False)
                st.success("Contrat enregistré et disponible au téléchargement. ✅")
    else:
        my_contracts = qdb("""SELECT c.*, a.title as ann_title, u.name as owner_name
            FROM contracts c JOIN announcements a ON c.announcement_id=a.id
            JOIN users u ON c.owner_id=u.id WHERE c.renter_id=? ORDER BY c.created_at DESC""", (user["id"],))
        if my_contracts:
            st.subheader("Mes contrats")
            for c in my_contracts:
                status_badge = "b-green" if c["status"] == "active" else "b-gray"
                st.markdown(f"""<div class="timeline-item"><div class="timeline-dot"></div>
                <div><div class="timeline-text">📄 <strong>{c['ann_title']}</strong> — avec {c['owner_name']}</div>
                <div class="timeline-date">{c['start_date']} → {c['end_date']} &nbsp;
                <span class="badge {status_badge}">{c['status']}</span></div></div></div>""", unsafe_allow_html=True)
        else:
            st.info("Aucun contrat signé.")

# ── Profile page ───────────────────────────────────────────────────────────────
def profile_page():
    st.markdown("### 👤 " + _("profile"))
    user = st.session_state.user
    if not user: st.warning(_("login_req")); return

    uid  = user["id"]
    rep  = compute_reputation(uid)
    pct  = int((rep / 5) * 100)

    c_info, c_stats = st.columns([2, 1])
    with c_info:
        st.markdown(f"""
        <div class="card">
            <div class="card-body">
                <div style="display:flex;align-items:center;gap:14px;margin-bottom:12px;">
                    <div style="width:52px;height:52px;border-radius:50%;background:var(--green-pale);display:flex;align-items:center;justify-content:center;font-size:1.5rem;">👤</div>
                    <div>
                        <div style="font-size:1.15rem;font-weight:600;">{user['name']}</div>
                        <div><span class="badge {'b-verified' if user['is_verified'] else 'b-amber'}">{'✅ Vérifié' if user['is_verified'] else '⏳ Non vérifié'}</span></div>
                    </div>
                </div>
                <p>📱 <strong>{user['phone']}</strong></p>
                <p>🏷️ {user['profile_type']}</p>
                <p>📍 {user['wilaya']} — {user.get('commune','')}</p>
                <p>📅 Membre depuis {user.get('created_at','')[:10]}</p>
                {f"<p>📝 {user.get('bio','')}</p>" if user.get('bio') else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Vérification
        if not user["is_verified"]:
            st.markdown("---")
            st.subheader("🪪 Demander la vérification")
            doc = st.file_uploader("Pièce d'identité / Registre de commerce", type=["jpg","jpeg","png","pdf"])
            if doc and st.button("📤 Soumettre", type="primary"):
                if doc.type == "application/pdf":
                    b64 = base64.b64encode(doc.read()).decode()
                else:
                    b64 = img_to_b64(doc)
                if b64:
                    qdb("UPDATE users SET documents=? WHERE id=?", (b64, uid), fetch=False)
                    st.success("Document soumis. Un agent ANEM validera votre profil sous 48h.")

    with c_stats:
        nb_ann = qdb("SELECT COUNT(*) as n FROM announcements WHERE user_id=?", (uid,))[0]["n"]
        nb_rev = qdb("SELECT COUNT(*) as n FROM reviews r JOIN announcements a ON r.announcement_id=a.id WHERE a.user_id=?", (uid,))[0]["n"]
        nb_ct  = qdb("SELECT COUNT(*) as n FROM contracts WHERE renter_id=? OR owner_id=?", (uid, uid))[0]["n"]
        st.markdown(f'<div class="stat"><div class="num">{nb_ann}</div><div class="lbl">Annonces</div></div><br>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat"><div class="num">{nb_rev}</div><div class="lbl">Avis reçus</div></div><br>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat"><div class="num">{nb_ct}</div><div class="lbl">Contrats</div></div><br>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="stat">
            <div class="rep-ring" style="--pct:{pct};margin:0 auto;">
                <span class="rep-val" style="font-size:.85rem;">{rep:.1f}</span>
            </div>
            <div class="lbl" style="margin-top:6px;">Réputation</div>
        </div>
        """, unsafe_allow_html=True)

# ── Main ────────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.db_init:
        init_db(); st.session_state.db_init = True

    with st.sidebar:
        st.markdown("### 🌐 Langue / اللغة")
        lang = st.selectbox("", ["fr","ar","en"],
                            index=["fr","ar","en"].index(st.session_state.lang),
                            label_visibility="collapsed")
        if lang != st.session_state.lang:
            st.session_state.lang = lang; st.rerun()

        st.markdown("---")
        user = st.session_state.user
        if user:
            rep = compute_reputation(user["id"])
            st.markdown(f"**👤 {user['name']}**")
            st.caption(f"{user['profile_type']} · ⭐{rep:.1f}/5")
            st.caption(f"{'✅ Vérifié' if user['is_verified'] else '⏳ Non vérifié'}")
            if st.button(_("logout"), use_container_width=True):
                st.session_state.user = None; st.session_state.page = "home"; st.rerun()
            st.markdown("---")
            if st.button("📊 Tableau de bord", use_container_width=True):
                st.session_state.page = "dashboard"; st.rerun()
            if st.button("🔍 Traçabilité QR", use_container_width=True):
                st.session_state.page = "tracability"; st.rerun()
        else:
            if st.button(_("login"), use_container_width=True, type="primary"):
                st.session_state.page = "login"; st.rerun()
            if st.button(_("register"), use_container_width=True):
                st.session_state.page = "register"; st.rerun()

        st.markdown("---")
        nb_urg = qdb("SELECT COUNT(*) as n FROM announcements WHERE is_urgent=1")[0]["n"]
        if nb_urg > 0:
            st.markdown(f'<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:8px 12px;font-size:.78rem;color:#991b1b;">🚨 <strong>{nb_urg} vente(s) urgente(s)</strong></div>', unsafe_allow_html=True)
            if st.button("Voir les urgences", use_container_width=True):
                st.session_state.page = "alerts"; st.rerun()

        st.markdown("---")
        st.markdown('<div style="background:var(--amber-pale);border:1px solid #fcd34d;border-radius:8px;padding:10px;text-align:center;font-size:.75rem;">📢 Espace pub<br><strong>contact@agriconnect.dz</strong></div>', unsafe_allow_html=True)

    # Navigation bar
    if st.session_state.user:
        navbar()
    else:
        c1, c2, c3 = st.columns(3)
        for col, pg, lbl in [(c1,"home","🏠 Accueil"),(c2,"login","🔐 Connexion"),(c3,"register","📝 Inscription")]:
            with col:
                if st.button(lbl, use_container_width=True, type="primary" if st.session_state.page==pg else "secondary"):
                    st.session_state.page = pg; st.rerun()

    # Router
    PAGES = {
        "home": home_page, "login": login_page, "register": register_page,
        "market": market_page, "job": job_page, "transport": transport_page,
        "grazing": grazing_page, "pollination": pollination_page,
        "fertilizer": fertilizer_page, "equipment": equipment_page,
        "anem": anem_page, "messages": messages_page, "reviews": reviews_page,
        "contract": contract_page, "profile": profile_page,
        "weather": weather_page, "prices": prices_page, "alerts": alerts_page,
        "assistant": assistant_page, "cooperative": cooperative_page,
        "dashboard": dashboard_page, "tracability": tracability_page,
    }
    PAGES.get(st.session_state.page, home_page)()

    st.markdown("""
    <div class="footer">
        🌾 <strong>AgriConnect v3.0</strong> — La plateforme numérique de l'agriculture algérienne<br>
        © 2026 · contact@agriconnect.dz · 58 wilayas · Fait 🇩🇿 avec ❤️
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
