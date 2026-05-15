# app.py – AgriConnect v2.0 (Amélioré & Corrigé)
import streamlit as st
import sqlite3
import hashlib
import json
import base64
import os
import io
import re
from datetime import datetime, date
from PIL import Image

# ─── Imports optionnels ───────────────────────────────────────────────────────
try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

# ─── Configuration ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgriConnect",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)
DB_FILE = "agriconnect.db"

# ─── 58 Wilayas ───────────────────────────────────────────────────────────────
WILAYAS = {
    "01 - Adrar": ["Adrar", "Reggane", "Timimoun"],
    "02 - Chlef": ["Chlef", "Ténès", "Abou El Hassan"],
    "03 - Laghouat": ["Laghouat", "Aflou", "Ksar El Hirane"],
    "04 - Oum El Bouaghi": ["Oum El Bouaghi", "Aïn Beïda", "Souk Naamane"],
    "05 - Batna": ["Batna", "Timgad", "Arris"],
    "06 - Béjaïa": ["Béjaïa", "Akbou", "Kherrata"],
    "07 - Biskra": ["Biskra", "Tolga", "Sidi Okba"],
    "08 - Béchar": ["Béchar", "Abadla", "Taghit"],
    "09 - Blida": ["Blida", "Boufarik", "Mouzaïa"],
    "10 - Bouira": ["Bouira", "Lakhdaria", "Aïn Bessem"],
    "11 - Tamanrasset": ["Tamanrasset", "In Salah", "Abalessa"],
    "12 - Tébessa": ["Tébessa", "Bir el-Ater", "El Ogla"],
    "13 - Tlemcen": ["Tlemcen", "Maghnia", "Ghazaouet"],
    "14 - Tiaret": ["Tiaret", "Sougueur", "Frenda"],
    "15 - Tizi Ouzou": ["Tizi Ouzou", "Azazga", "Larbaâ Nath Irathen"],
    "16 - Alger": ["Alger Centre", "Bab El Oued", "Hussein Dey", "Bir Mourad Raïs", "El Harrach"],
    "17 - Djelfa": ["Djelfa", "Messaâd", "El Idrissia"],
    "18 - Jijel": ["Jijel", "Taher", "El Milia"],
    "19 - Sétif": ["Sétif", "El Eulma", "Aïn Azel"],
    "20 - Saïda": ["Saïda", "El Hassasna", "Youb"],
    "21 - Skikda": ["Skikda", "Azzaba", "Collo"],
    "22 - Sidi Bel Abbès": ["Sidi Bel Abbès", "Sidi Lahcene", "Telagh"],
    "23 - Annaba": ["Annaba", "El Hadjar", "Berrahal"],
    "24 - Guelma": ["Guelma", "Hammam Debagh", "Oued Zenati"],
    "25 - Constantine": ["Constantine", "El Khroub", "Aïn Abid"],
    "26 - Médéa": ["Médéa", "Berrouaghia", "Tablat"],
    "27 - Mostaganem": ["Mostaganem", "Aïn Tedles", "Sidi Ali"],
    "28 - M'Sila": ["M'Sila", "Bou Saâda", "Magra"],
    "29 - Mascara": ["Mascara", "Sig", "Ghriss"],
    "30 - Ouargla": ["Ouargla", "Hassi Messaoud", "Touggourt"],
    "31 - Oran": ["Oran", "Es Sénia", "Bir El Djir"],
    "32 - El Bayadh": ["El Bayadh", "Bougtob", "El Abiodh Sidi Cheikh"],
    "33 - Illizi": ["Illizi", "Djanet", "Bordj Omar Driss"],
    "34 - Bordj Bou Arreridj": ["Bordj Bou Arreridj", "Ras El Oued", "Bordj Ghedir"],
    "35 - Boumerdès": ["Boumerdès", "Dellys", "Khemis El Khechna"],
    "36 - El Tarf": ["El Tarf", "Bouhadjar", "El Kala"],
    "37 - Tindouf": ["Tindouf", "Oum El Assel"],
    "38 - Tissemsilt": ["Tissemsilt", "Bordj Bounaama", "Lardjem"],
    "39 - El Oued": ["El Oued", "Guemar", "Robbah"],
    "40 - Khenchela": ["Khenchela", "Kaïs", "Babar"],
    "41 - Souk Ahras": ["Souk Ahras", "Taoura", "M'daourouch"],
    "42 - Tipaza": ["Tipaza", "Bou Ismaïl", "Hadjout"],
    "43 - Mila": ["Mila", "Telerghma", "Grarem Gouga"],
    "44 - Aïn Defla": ["Aïn Defla", "Khemis Miliana", "Djendel"],
    "45 - Naâma": ["Naâma", "Mecheria", "Aïn Sefra"],
    "46 - Aïn Témouchent": ["Aïn Témouchent", "Beni Saf", "El Malah"],
    "47 - Ghardaïa": ["Ghardaïa", "Metlili", "Berriane"],
    "48 - Relizane": ["Relizane", "Zemoura", "Oued Rhiou"],
    "49 - Timimoun": ["Timimoun", "Aougrout", "Charouine"],
    "50 - Bordj Badji Mokhtar": ["Bordj Badji Mokhtar", "Timiaouine"],
    "51 - Ouled Djellal": ["Ouled Djellal", "Sidi Khaled", "Besbes"],
    "52 - Béni Abbès": ["Béni Abbès", "Kerzaz", "Tabelbala"],
    "53 - In Salah": ["In Salah", "Foggaret Ezzaouia"],
    "54 - In Guezzam": ["In Guezzam", "Tin Zaouatine"],
    "55 - Touggourt": ["Touggourt", "Témacine", "Megarine"],
    "56 - Djanet": ["Djanet", "Bordj El Haouas"],
    "57 - El M'ghair": ["El M'ghair", "Djamaa", "Sidi Amrane"],
    "58 - El Meniaa": ["El Meniaa", "Hassi Fehal", "Hassi Gara"],
}

# ─── Traductions ──────────────────────────────────────────────────────────────
LANGUAGES = {
    "fr": {
        "app_name": "AgriConnect", "login": "Connexion", "register": "Inscription",
        "logout": "Déconnexion", "home": "Accueil", "market": "Marché",
        "job": "Emploi", "transport": "Transport", "grazing": "Pâturage",
        "pollination": "Pollinisation", "fertilizer": "Engrais",
        "equipment": "Matériel Agricole", "anem": "ANEM", "messages": "Messagerie",
        "reviews": "Évaluations", "contract": "Contrat", "verification": "Vérification",
        "profile": "Mon Profil", "no_announces": "Aucune annonce pour le moment.",
        "publish": "Publier", "list": "Annonces", "map": "Carte",
        "contact": "Contacter", "evaluate": "Évaluer", "contract_btn": "Contrat",
        "send": "Envoyer", "download": "Télécharger", "my_offers": "Dernières annonces",
        "suggestions": "Suggestions", "search": "Rechercher",
        "wilaya": "Wilaya", "commune": "Commune",
        "fill_required": "Veuillez remplir tous les champs obligatoires.",
        "login_required": "Veuillez vous connecter.",
        "published": "Annonce publiée avec succès !",
        "account_created": "Compte créé. Connectez-vous.",
        "phone_used": "Ce numéro est déjà utilisé.",
        "bad_credentials": "Identifiants incorrects.",
        "validated": "Profil validé.",
        "pending_none": "Aucun profil en attente.",
        "no_convo": "Aucune conversation.",
        "msg_sent": "Message envoyé.",
        "rating_sent": "Évaluation soumise, merci !",
        "contract_created": "Contrat enregistré.",
        "doc_sent": "Document soumis pour vérification.",
        "contract_title": "Contrat AgriConnect",
        "page": "Page",
        "next": "Suivant →",
        "prev": "← Précédent",
    },
    "ar": {
        "app_name": "أجريكونكت", "login": "تسجيل الدخول", "register": "التسجيل",
        "logout": "تسجيل الخروج", "home": "الرئيسية", "market": "السوق",
        "job": "وظائف", "transport": "النقل", "grazing": "الرعي",
        "pollination": "التلقيح", "fertilizer": "الأسمدة",
        "equipment": "المعدات الفلاحية", "anem": "الوكالة الوطنية للتشغيل",
        "messages": "الرسائل", "reviews": "التقييمات", "contract": "عقد",
        "verification": "التحقق", "profile": "الملف الشخصي",
        "no_announces": "لا توجد إعلانات", "publish": "نشر",
        "list": "قائمة", "map": "خريطة", "contact": "اتصال",
        "evaluate": "تقييم", "contract_btn": "عقد", "send": "إرسال",
        "download": "تحميل", "my_offers": "آخر الإعلانات",
        "suggestions": "اقتراحات", "search": "بحث",
        "wilaya": "ولاية", "commune": "بلدية",
        "fill_required": "الرجاء ملء جميع الحقول المطلوبة.",
        "login_required": "الرجاء تسجيل الدخول.",
        "published": "تم نشر الإعلان بنجاح!",
        "account_created": "تم إنشاء الحساب. سجل دخولك.",
        "phone_used": "رقم الهاتف مستخدم بالفعل.",
        "bad_credentials": "بيانات الدخول غير صحيحة.",
        "validated": "تم التحقق من الملف.", "pending_none": "لا توجد ملفات معلقة.",
        "no_convo": "لا توجد محادثات.", "msg_sent": "تم إرسال الرسالة.",
        "rating_sent": "شكرًا! تم تقديم التقييم.",
        "contract_created": "تم إنشاء العقد.", "doc_sent": "تم إرسال المستند.",
        "contract_title": "عقد أجريكونكت", "page": "صفحة",
        "next": "التالي →", "prev": "← السابق",
    },
    "en": {
        "app_name": "AgriConnect", "login": "Login", "register": "Register",
        "logout": "Logout", "home": "Home", "market": "Marketplace",
        "job": "Jobs", "transport": "Transport", "grazing": "Grazing",
        "pollination": "Pollination", "fertilizer": "Fertilizer",
        "equipment": "Equipment", "anem": "ANEM", "messages": "Messages",
        "reviews": "Reviews", "contract": "Contract", "verification": "Verification",
        "profile": "My Profile", "no_announces": "No announcements yet.",
        "publish": "Publish", "list": "List", "map": "Map",
        "contact": "Contact", "evaluate": "Rate", "contract_btn": "Contract",
        "send": "Send", "download": "Download", "my_offers": "Latest Listings",
        "suggestions": "Suggestions", "search": "Search",
        "wilaya": "Wilaya", "commune": "Commune",
        "fill_required": "Please fill all required fields.",
        "login_required": "Please log in first.",
        "published": "Announcement published successfully!",
        "account_created": "Account created. Please log in.",
        "phone_used": "Phone number already in use.",
        "bad_credentials": "Incorrect credentials.",
        "validated": "Profile validated.", "pending_none": "No pending profiles.",
        "no_convo": "No conversations yet.", "msg_sent": "Message sent.",
        "rating_sent": "Rating submitted, thank you!",
        "contract_created": "Contract created.", "doc_sent": "Document submitted.",
        "contract_title": "AgriConnect Contract", "page": "Page",
        "next": "Next →", "prev": "← Previous",
    },
}

def _(key):
    lang = st.session_state.get("lang", "fr")
    return LANGUAGES.get(lang, LANGUAGES["fr"]).get(key, key)

# ─── Session State ─────────────────────────────────────────────────────────────
DEFAULTS = {
    "user": None, "page": "home", "lang": "fr",
    "msg_to": None, "msg_announce": None,
    "review_announce": None, "contract_announce": None,
    "search_query": "", "db_initialized": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=Noto+Sans+Arabic:wght@400;600&display=swap');

:root {
    --green-dark: #1b5e20;
    --green: #2e7d32;
    --green-light: #43a047;
    --green-pale: #e8f5e9;
    --amber: #f59e0b;
    --amber-pale: #fffbeb;
    --text: #1a1a1a;
    --text-muted: #6b7280;
    --border: #e5e7eb;
    --card-bg: #ffffff;
    --radius: 14px;
    --shadow: 0 2px 12px rgba(0,0,0,0.07);
    --shadow-hover: 0 8px 28px rgba(0,0,0,0.13);
}

* { font-family: 'Sora', 'Noto Sans Arabic', sans-serif; box-sizing: border-box; }

.main-header {
    background: linear-gradient(135deg, var(--green-dark) 0%, var(--green-light) 100%);
    color: white;
    padding: 2rem 1.5rem;
    border-radius: var(--radius);
    text-align: center;
    margin-bottom: 1.5rem;
}
.main-header h1 { font-size: 2.2rem; font-weight: 700; margin: 0; letter-spacing: -0.5px; }
.main-header p { margin: 0.4rem 0 0; opacity: 0.85; font-size: 1rem; font-weight: 300; }

.card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    margin-bottom: 1.2rem;
    height: 100%;
}
.card:hover { transform: translateY(-4px); box-shadow: var(--shadow-hover); }
.card-img {
    height: 170px; width: 100%; object-fit: cover;
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 3rem;
}
.card-body { padding: 14px; }
.card-title { font-size: 1rem; font-weight: 600; color: var(--text); margin-bottom: 4px; }
.card-desc { color: var(--text-muted); font-size: 0.82rem; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-price { font-size: 1.15rem; font-weight: 700; color: var(--green); }
.card-loc { color: var(--text-muted); font-size: 0.78rem; margin-top: 4px; }

.badge {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.3px;
}
.badge-green { background: var(--green-pale); color: var(--green); }
.badge-amber { background: var(--amber-pale); color: #92400e; }

.stat-card {
    background: white; border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.2rem 1rem;
    text-align: center; box-shadow: var(--shadow);
}
.stat-card .number { font-size: 2rem; font-weight: 700; color: var(--green); }
.stat-card .label { color: var(--text-muted); font-size: 0.82rem; margin-top: 2px; }

.no-announce {
    text-align: center; padding: 3rem; color: var(--text-muted);
    font-size: 1.1rem; background: var(--green-pale);
    border-radius: var(--radius); border: 1px dashed #a5d6a7;
}

.msg-bubble-me {
    background: var(--green-pale); color: var(--text);
    padding: 10px 14px; border-radius: 18px 18px 4px 18px;
    max-width: 75%; margin-left: auto; margin-bottom: 8px;
    font-size: 0.9rem;
}
.msg-bubble-other {
    background: #f3f4f6; color: var(--text);
    padding: 10px 14px; border-radius: 18px 18px 18px 4px;
    max-width: 75%; margin-right: auto; margin-bottom: 8px;
    font-size: 0.9rem;
}
.msg-time { font-size: 0.68rem; color: var(--text-muted); margin-top: 3px; }

.footer {
    text-align: center; padding: 1.5rem;
    color: var(--text-muted); border-top: 1px solid var(--border);
    margin-top: 3rem; font-size: 0.82rem;
}

/* Responsive columns */
@media (max-width: 768px) {
    .main-header h1 { font-size: 1.5rem; }
}
</style>
""", unsafe_allow_html=True)

# ─── DB ────────────────────────────────────────────────────────────────────────
def init_db():
    """Initialise la base de données SANS écraser les données existantes."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Utiliser CREATE TABLE IF NOT EXISTS pour préserver les données
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        profile_type TEXT,
        is_verified INTEGER DEFAULT 0,
        wilaya TEXT,
        commune TEXT,
        location_lat REAL DEFAULT 0,
        location_lon REAL DEFAULT 0,
        documents TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        price REAL DEFAULT 0,
        unit TEXT,
        wilaya TEXT,
        commune TEXT,
        lat REAL DEFAULT 0,
        lon REAL DEFAULT 0,
        data TEXT DEFAULT '{}',
        images TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        announcement_id INTEGER,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id),
        FOREIGN KEY (receiver_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        announcement_id INTEGER NOT NULL,
        reviewer_id INTEGER NOT NULL,
        rating INTEGER CHECK(rating BETWEEN 1 AND 5),
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        announcement_id INTEGER NOT NULL,
        renter_id INTEGER NOT NULL,
        owner_id INTEGER NOT NULL,
        start_date TEXT,
        end_date TEXT,
        terms TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Données de test — insérées seulement si la table est vide
    if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        test_users = [
            ("Agent ANEM", "0555000001", hash_password("anem123"), "ANEM", 1, "16 - Alger", "Alger Centre"),
            ("Ali Ferme", "0555123456", hash_password("123456"), "Agriculteur", 1, "39 - El Oued", "Guemar"),
            ("Fatima Transport", "0555654321", hash_password("123456"), "Transporteur", 1, "31 - Oran", "Es Sénia"),
        ]
        c.executemany(
            "INSERT INTO users (name,phone,password,profile_type,is_verified,wilaya,commune) VALUES (?,?,?,?,?,?,?)",
            test_users
        )
        user_id = c.execute("SELECT id FROM users WHERE phone='0555123456'").fetchone()[0]
        user_t   = c.execute("SELECT id FROM users WHERE phone='0555654321'").fetchone()[0]
        test_ann = [
            (user_id, "market",      "Pommes de terre fraîches",       "Variété Spunta, 10 tonnes disponibles",   45,   "DA/kg",        "39 - El Oued", "Guemar",   '{"product_type":"Légumes","quantity":10000}'),
            (user_id, "grazing",     "Chaumes de blé à louer",         "50 ha, eau disponible, mai–juillet",     200,  "DA/tête/jour", "14 - Tiaret",  "Sougueur", '{"area_ha":50,"cover_type":"Chaume","water":"Oui","max_animals":100}'),
            (user_id, "fertilizer",  "Fumier ovin composté",           "5 tonnes de qualité supérieure",        3000, "DA/tonne",     "17 - Djelfa",  "Messaâd",  '{"fertilizer_type":"Fumier ovin","quantity_tons":5}'),
            (user_t,  "transport",   "Camion frigorifique Alger–Médéa","Capacité 10 t, départ chaque semaine",  8000, "DA/voyage",    "16 - Alger",   "El Harrach",'{"vehicle_type":"Frigorifique","capacity":10}'),
            (user_id, "pollination", "20 ruches disponibles",          "Race locale, zone Béjaïa–Batna",        5000, "DA/ruche/sem", "06 - Béjaïa",  "Akbou",    '{"hive_count":20,"bee_race":"Locale","zone":"Béjaïa-Batna"}'),
            (user_t,  "equipment",   "Tracteur Massey Ferguson 2020",  "Bon état, location journalière",        5000, "DA/jour",      "31 - Oran",    "Es Sénia", '{"offer_type":"Location","equipment_type":"Tracteur","brand":"Massey Ferguson","model":"MF 2020","year":2020,"state":"Bon"}'),
        ]
        c.executemany(
            "INSERT INTO announcements (user_id,type,title,description,price,unit,wilaya,commune,data) VALUES (?,?,?,?,?,?,?,?,?)",
            test_ann
        )

    conn.commit()
    conn.close()


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def query_db(query, params=(), fetch=True):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        if fetch:
            rows = cur.fetchall()
            conn.close()
            return rows
        else:
            conn.commit()
            last_id = cur.lastrowid
            conn.close()
            return last_id
    except sqlite3.Error as e:
        conn.close()
        st.error(f"Erreur DB : {e}")
        return [] if fetch else None


def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()


def validate_phone(phone: str) -> bool:
    return bool(re.match(r'^0[5-7]\d{8}$', phone.strip()))

# ─── Médias ───────────────────────────────────────────────────────────────────
def image_to_base64(img_file, max_size=(800, 600), quality=65) -> str | None:
    if img_file is None:
        return None
    try:
        img_file.seek(0)
        im = Image.open(img_file).convert("RGB")
        im.thumbnail(max_size, Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=quality, optimize=True)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        st.warning(f"Image ignorée : {e}")
        return None


def generate_contract_pdf(ann, renter_name, owner_name, terms: dict) -> bytes | None:
    """Génère un contrat PDF sans dépendance externe (texte simple encodé)."""
    lines = [
        "=" * 50,
        f"  {_('contract_title')}",
        "=" * 50,
        "",
        f"Annonce    : {ann['title']}",
        f"Propriétaire : {owner_name}",
        f"Locataire  : {renter_name}",
        f"Début      : {terms.get('start', '')}",
        f"Fin        : {terms.get('end', '')}",
        "",
        "Conditions :",
        terms.get("details", ""),
        "",
        "=" * 50,
        f"Date de génération : {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "AgriConnect © 2026 — contact@agriconnect.dz",
    ]
    content = "\n".join(lines)

    # Essaie fpdf si disponible
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=11)
        for line in lines:
            pdf.multi_cell(0, 9, txt=line.encode("latin-1", "replace").decode("latin-1"))
        return pdf.output(dest="S").encode("latin-1")
    except Exception:
        pass

    # Fallback : fichier texte simple
    return content.encode("utf-8")

# ─── Card ─────────────────────────────────────────────────────────────────────
MODULE_ICONS = {
    "market": "🥕", "job": "👷", "transport": "🚛",
    "grazing": "🐑", "pollination": "🐝", "fertilizer": "🌱",
    "equipment": "🚜",
}

def render_announce_card(a):
    icon = MODULE_ICONS.get(a["type"], "📌")
    if a["images"]:
        first_b64 = a["images"].split(";")[0]
        img_html = f'<img src="data:image/jpeg;base64,{first_b64}" style="height:170px;width:100%;object-fit:cover;">'
    else:
        img_html = f'<div class="card-img">{icon}</div>'

    desc = (a["description"] or "")[:80]
    if len(a["description"] or "") > 80:
        desc += "…"

    st.markdown(f"""
    <div class="card">
        {img_html}
        <div class="card-body">
            <span class="badge badge-green">{a['type'].upper()}</span>
            <div class="card-title" style="margin-top:6px;">{a['title']}</div>
            <div class="card-desc">{desc}</div>
            <div class="card-price">{a['price']:,.0f} {a['unit'] or ''}</div>
            <div class="card-loc">📍 {a['wilaya']} — {a['commune']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(_("contact"), key=f"msg_{a['id']}", use_container_width=True):
            st.session_state.msg_to = a["user_id"]
            st.session_state.msg_announce = a["id"]
            st.session_state.page = "messages"
            st.rerun()
    with col2:
        if st.button(_("evaluate"), key=f"rev_{a['id']}", use_container_width=True):
            st.session_state.review_announce = a["id"]
            st.session_state.page = "reviews"
            st.rerun()
    with col3:
        if a["type"] in ("grazing", "pollination", "equipment"):
            if st.button(_("contract_btn"), key=f"ct_{a['id']}", use_container_width=True):
                st.session_state.contract_announce = a["id"]
                st.session_state.page = "contract"
                st.rerun()

# ─── Navbar ───────────────────────────────────────────────────────────────────
def render_navbar():
    items = [
        ("home", _("home")), ("market", _("market")), ("job", _("job")),
        ("transport", _("transport")), ("grazing", _("grazing")),
        ("pollination", _("pollination")), ("fertilizer", _("fertilizer")),
        ("equipment", _("equipment")), ("messages", _("messages")),
        ("profile", _("profile")),
    ]
    if st.session_state.user and st.session_state.user.get("profile_type") == "ANEM":
        items.insert(2, ("anem", _("anem")))

    cols = st.columns(len(items))
    for i, (page, label) in enumerate(items):
        active = st.session_state.page == page
        style = "background:#2e7d32;color:white;" if active else ""
        with cols[i]:
            if st.button(label, key=f"nav_{page}", use_container_width=True,
                         help=label, type="primary" if active else "secondary"):
                st.session_state.page = page
                st.rerun()

# ─── Auth pages ───────────────────────────────────────────────────────────────
def login_page():
    col = st.columns([1, 2, 1])[1]
    with col:
        st.markdown("### 🔐 " + _("login"))
        phone = st.text_input("📱 Téléphone (ex: 0555123456)")
        pwd   = st.text_input("🔑 Mot de passe", type="password")
        if st.button(_("login"), use_container_width=True, type="primary"):
            if not phone or not pwd:
                st.warning(_("fill_required"))
            else:
                rows = query_db(
                    "SELECT * FROM users WHERE phone=? AND password=?",
                    (phone.strip(), hash_password(pwd))
                )
                if rows:
                    st.session_state.user = dict(rows[0])
                    st.session_state.page = "home"
                    st.rerun()
                else:
                    st.error(_("bad_credentials"))
        st.markdown("---")
        if st.button(_("register"), use_container_width=True):
            st.session_state.page = "register"
            st.rerun()


def register_page():
    col = st.columns([1, 2, 1])[1]
    with col:
        st.markdown("### 📝 " + _("register"))
        name    = st.text_input("Nom complet *")
        phone   = st.text_input("Téléphone * (ex: 0555123456)")
        pwd     = st.text_input("Mot de passe *", type="password")
        pwd2    = st.text_input("Confirmer le mot de passe *", type="password")
        profile = st.selectbox("Profil *", ["Agriculteur","Éleveur","Apiculteur","Transporteur","Acheteur","ANEM","Travailleur"])
        wilaya  = st.selectbox(_("wilaya") + " *", list(WILAYAS.keys()))
        commune = st.selectbox(_("commune") + " *", WILAYAS[wilaya])

        if st.button("S'inscrire", use_container_width=True, type="primary"):
            errors = []
            if not name.strip():
                errors.append("Nom requis.")
            if not validate_phone(phone):
                errors.append("Numéro de téléphone invalide (format: 0555123456).")
            if len(pwd) < 6:
                errors.append("Mot de passe trop court (min. 6 caractères).")
            if pwd != pwd2:
                errors.append("Les mots de passe ne correspondent pas.")
            if errors:
                for e in errors:
                    st.error(e)
            else:
                try:
                    query_db(
                        "INSERT INTO users (name,phone,password,profile_type,wilaya,commune) VALUES (?,?,?,?,?,?)",
                        (name.strip(), phone.strip(), hash_password(pwd), profile, wilaya, commune),
                        fetch=False
                    )
                    st.success(_("account_created"))
                    st.session_state.page = "login"
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error(_("phone_used"))

# ─── Home ─────────────────────────────────────────────────────────────────────
def home_page():
    st.markdown("""
    <div class="main-header">
        <h1>🌾 AgriConnect</h1>
        <p>Le carrefour numérique de l'agriculture algérienne</p>
    </div>
    """, unsafe_allow_html=True)

    # Statistiques rapides
    total = query_db("SELECT COUNT(*) as n FROM announcements")[0]["n"]
    users = query_db("SELECT COUNT(*) as n FROM users")[0]["n"]
    wilayas_count = query_db("SELECT COUNT(DISTINCT wilaya) as n FROM announcements")[0]["n"]

    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="stat-card"><div class="number">{total}</div><div class="label">Annonces actives</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card"><div class="number">{users}</div><div class="label">Utilisateurs inscrits</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card"><div class="number">{wilayas_count}</div><div class="label">Wilayas couvertes</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Barre de recherche
    c_s, c_w, c_b = st.columns([3, 2, 1])
    with c_s:
        search = st.text_input(_("search"), placeholder="Ex: pommes de terre, tracteur...",
                               value=st.session_state.search_query, label_visibility="collapsed")
    with c_w:
        wilaya_f = st.selectbox(_("wilaya"), ["Toutes"] + list(WILAYAS.keys()), label_visibility="collapsed")
    with c_b:
        if st.button(_("search"), use_container_width=True, type="primary"):
            st.session_state.search_query = search

    # Requête avec recherche + filtre wilaya
    sql = "SELECT a.*, u.name as author FROM announcements a JOIN users u ON a.user_id=u.id WHERE 1=1"
    params = []
    if search:
        sql += " AND (a.title LIKE ? OR a.description LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if wilaya_f != "Toutes":
        sql += " AND a.wilaya=?"
        params.append(wilaya_f)
    sql += " ORDER BY a.created_at DESC LIMIT 12"

    annonces = query_db(sql, tuple(params))

    st.markdown(f"### 📌 {_('my_offers')} ({len(annonces)})")
    if annonces:
        for i in range(0, len(annonces), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(annonces):
                    with cols[j]:
                        render_announce_card(annonces[i + j])
    else:
        st.markdown(f'<div class="no-announce">🌿 {_("no_announces")}</div>', unsafe_allow_html=True)

# ─── Page générique ───────────────────────────────────────────────────────────
PAGE_SIZE = 6  # Annonces par page

def generic_announce_page(module_type: str, fields_config: list, filters: list):
    tab1, tab2, tab3 = st.tabs([f"📋 {_('list')}", f"➕ {_('publish')}", f"🗺️ {_('map')}"])

    # ── Onglet liste ──
    with tab1:
        # Filtres dynamiques
        filter_cols = st.columns(max(len(filters), 1))
        where_clauses = ["a.type=?"]
        params = [module_type]

        for i, f in enumerate(filters):
            with filter_cols[i % len(filter_cols)]:
                if f == "wilaya":
                    val = st.selectbox(_("wilaya"), ["Toutes"] + list(WILAYAS.keys()), key=f"f_w_{module_type}")
                    if val != "Toutes":
                        where_clauses.append("a.wilaya=?")
                        params.append(val)

                elif f == "price_max":
                    val = st.number_input("Prix max (DA)", min_value=0, step=500, key=f"f_p_{module_type}")
                    if val > 0:
                        where_clauses.append("a.price<=?")
                        params.append(val)

                elif f == "type_produit":
                    opts = ["Tous","Légumes","Fruits","Céréales","Bétail","Miel","Lait","Autre"]
                    val = st.selectbox("Type produit", opts, key=f"f_tp_{module_type}")
                    if val != "Tous":
                        # Filtrage en Python après récupération (évite les JSON SQL hacks)
                        st.session_state[f"_filter_product_type_{module_type}"] = val
                    else:
                        st.session_state[f"_filter_product_type_{module_type}"] = None

                elif f == "equipment_type":
                    opts = ["Tous","Tracteur","Moissonneuse","Charrue","Remorque","Irrigation","Épandeur","Semoir","Autre"]
                    val = st.selectbox("Type matériel", opts, key=f"f_et_{module_type}")
                    st.session_state[f"_filter_eq_type_{module_type}"] = val if val != "Tous" else None

                elif f == "offer_type":
                    val = st.selectbox("Offre", ["Tous","Vente","Location"], key=f"f_ot_{module_type}")
                    st.session_state[f"_filter_offer_type_{module_type}"] = val if val != "Tous" else None

        sql = f"SELECT a.*, u.name as author FROM announcements a JOIN users u ON a.user_id=u.id WHERE {' AND '.join(where_clauses)} ORDER BY a.created_at DESC"
        annonces = query_db(sql, tuple(params))

        # Filtrage JSON en Python (fiable sur toutes versions SQLite)
        def match_json_filter(a, key, session_key):
            fval = st.session_state.get(session_key)
            if not fval:
                return True
            try:
                d = json.loads(a["data"] or "{}")
                return d.get(key, "").lower() == fval.lower()
            except Exception:
                return True

        annonces = [
            a for a in annonces
            if match_json_filter(a, "product_type", f"_filter_product_type_{module_type}")
            and match_json_filter(a, "equipment_type", f"_filter_eq_type_{module_type}")
            and match_json_filter(a, "offer_type", f"_filter_offer_type_{module_type}")
        ]

        # Pagination
        total = len(annonces)
        page_key = f"_page_{module_type}"
        if page_key not in st.session_state:
            st.session_state[page_key] = 0
        pg = st.session_state[page_key]
        total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        pg = min(pg, total_pages - 1)

        page_annonces = annonces[pg * PAGE_SIZE:(pg + 1) * PAGE_SIZE]

        if page_annonces:
            for i in range(0, len(page_annonces), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(page_annonces):
                        with cols[j]:
                            render_announce_card(page_annonces[i + j])
        else:
            st.markdown(f'<div class="no-announce">🌿 {_("no_announces")}</div>', unsafe_allow_html=True)

        # Contrôles pagination
        p1, p2, p3 = st.columns([1, 2, 1])
        with p1:
            if pg > 0:
                if st.button(_("prev"), key=f"prev_{module_type}"):
                    st.session_state[page_key] = pg - 1; st.rerun()
        with p2:
            st.markdown(f"<p style='text-align:center;color:#6b7280;'>{_('page')} {pg+1} / {total_pages} ({total} résultats)</p>", unsafe_allow_html=True)
        with p3:
            if pg < total_pages - 1:
                if st.button(_("next"), key=f"next_{module_type}"):
                    st.session_state[page_key] = pg + 1; st.rerun()

    # ── Onglet publication ──
    with tab2:
        if not st.session_state.user:
            st.warning(_("login_required"))
            return

        with st.form(f"form_{module_type}", clear_on_submit=True):
            st.subheader(f"➕ {_('publish')}")
            c1, c2 = st.columns(2)
            title = c1.text_input("Titre *")
            unit  = c2.text_input("Unité (ex: DA/kg)")
            desc  = st.text_area("Description")
            c3, c4 = st.columns(2)
            price  = c3.number_input("Prix (DA) *", min_value=0.0, step=100.0)
            wilaya = c4.selectbox(_("wilaya"), list(WILAYAS.keys()), key=f"pub_w_{module_type}")
            commune = st.selectbox(_("commune"), WILAYAS[wilaya], key=f"pub_c_{module_type}")

            extra = {}
            if fields_config:
                st.markdown("**Détails supplémentaires**")
                f_cols = st.columns(min(len(fields_config), 2))
                for idx, (field, label, opts) in enumerate(fields_config):
                    with f_cols[idx % 2]:
                        if opts == "text":
                            extra[field] = st.text_input(label, key=f"fc_{module_type}_{field}")
                        elif opts == "number":
                            extra[field] = st.number_input(label, min_value=0, key=f"fc_{module_type}_{field}")
                        elif isinstance(opts, list):
                            extra[field] = st.selectbox(label, opts, key=f"fc_{module_type}_{field}")

            images = st.file_uploader("📷 Photos (max 5)", type=["jpg","jpeg","png"],
                                      accept_multiple_files=True, key=f"imgs_{module_type}")

            submitted = st.form_submit_button(_("publish"), use_container_width=True, type="primary")

        if submitted:
            if not title.strip():
                st.error(_("fill_required"))
            else:
                imgs_b64 = []
                if images:
                    for img in images[:5]:
                        b64 = image_to_base64(img)
                        if b64:
                            imgs_b64.append(b64)
                query_db(
                    "INSERT INTO announcements (user_id,type,title,description,price,unit,wilaya,commune,data,images) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (st.session_state.user["id"], module_type, title.strip(), desc, price,
                     unit, wilaya, commune, json.dumps(extra), ";".join(imgs_b64)),
                    fetch=False
                )
                st.success(_("published"))
                st.rerun()

    # ── Onglet carte ──
    with tab3:
        if not HAS_FOLIUM:
            st.info("Installez `streamlit-folium` et `folium` pour voir la carte.")
        else:
            m = folium.Map(location=[28.0339, 1.6596], zoom_start=5)
            anns = query_db(f"SELECT * FROM announcements WHERE type=? AND lat!=0 AND lon!=0", (module_type,))
            for a in anns:
                if a["lat"] and a["lon"]:
                    folium.Marker(
                        [a["lat"], a["lon"]],
                        popup=f"{a['title']}<br>{a['price']} {a['unit']}",
                        icon=folium.Icon(color="green", icon="leaf")
                    ).add_to(m)
            st_folium(m, width=700, height=450)


# ─── Modules ──────────────────────────────────────────────────────────────────
def market_page():
    st.markdown("### 🥕 " + _("market"))
    generic_announce_page("market",
        [("product_type","Type",["Légumes","Fruits","Céréales","Bétail","Miel","Lait","Autre"]),
         ("quantity","Quantité (kg/t)","number")],
        ["wilaya","price_max","type_produit"])

def job_page():
    st.markdown("### 👷 " + _("job"))
    generic_announce_page("job",
        [("contract_type","Type contrat",["Saisonnier","Permanent","Journalier"]),
         ("skills","Compétences requises","text"),
         ("duration","Durée (jours)","number"),
         ("salary","Salaire DA/jour","number")],
        ["wilaya","price_max"])

def transport_page():
    st.markdown("### 🚛 " + _("transport"))
    generic_announce_page("transport",
        [("vehicle_type","Véhicule",["Camion","Bétaillère","Frigorifique","Pickup","Semi-remorque"]),
         ("capacity","Capacité (t)","number"),
         ("route","Trajet","text")],
        ["wilaya","price_max"])

def grazing_page():
    st.markdown("### 🐑 " + _("grazing"))
    generic_announce_page("grazing",
        [("area_ha","Superficie (ha)","number"),
         ("cover_type","Couvert",["Chaume","Jachère","Herbe","Alfa"]),
         ("water","Eau disponible",["Oui","Non"]),
         ("start_date","Date début","text"),
         ("end_date","Date fin","text"),
         ("max_animals","Nombre max animaux","number")],
        ["wilaya","price_max"])

def pollination_page():
    st.markdown("### 🐝 " + _("pollination"))
    generic_announce_page("pollination",
        [("hive_count","Nombre de ruches","number"),
         ("bee_race","Race abeilles",["Locale","Saharan","Hybride"]),
         ("zone","Zone d'intervention","text"),
         ("availability","Disponibilité","text")],
        ["wilaya","price_max"])

def fertilizer_page():
    st.markdown("### 🌱 " + _("fertilizer"))
    generic_announce_page("fertilizer",
        [("fertilizer_type","Type",["Fumier bovin","Fumier ovin","Fiente volaille","Compost","Autre"]),
         ("quantity_tons","Quantité (tonnes)","number"),
         ("packaging","Conditionnement",["Vrac","En sacs","Sur palettes"])],
        ["wilaya","price_max"])

def equipment_page():
    st.markdown("### 🚜 " + _("equipment"))
    generic_announce_page("equipment",
        [("offer_type","Offre",["Vente","Location"]),
         ("equipment_type","Type",["Tracteur","Moissonneuse","Charrue","Remorque","Irrigation","Épandeur","Semoir","Autre"]),
         ("brand","Marque","text"),
         ("model","Modèle","text"),
         ("year","Année fabrication","number"),
         ("state","État",["Neuf","Très bon","Bon","À rénover"]),
         ("rental_period","Période location",["Heure","Jour","Semaine","Mois"]),
         ("availability","Disponibilité","text")],
        ["wilaya","price_max","equipment_type","offer_type"])

# ─── ANEM ─────────────────────────────────────────────────────────────────────
def anem_page():
    st.markdown("### 🏛️ " + _("anem"))
    user = st.session_state.user
    if not user or user.get("profile_type") != "ANEM":
        st.error("⛔ " + _("login_required") + " (profil ANEM requis)")
        return

    total_jobs  = query_db("SELECT COUNT(*) as n FROM announcements WHERE type='job'")[0]["n"]
    total_work  = query_db("SELECT COUNT(*) as n FROM users WHERE profile_type='Travailleur'")[0]["n"]
    total_valid = query_db("SELECT COUNT(*) as n FROM users WHERE profile_type='Travailleur' AND is_verified=1")[0]["n"]
    total_msgs  = query_db("SELECT COUNT(*) as n FROM messages")[0]["n"]

    c1, c2, c3, c4 = st.columns(4)
    for col, num, label in [
        (c1, total_jobs, "Offres d'emploi"),
        (c2, total_work, "Demandeurs"),
        (c3, total_valid, "Profils validés"),
        (c4, total_msgs, "Messages"),
    ]:
        col.markdown(f'<div class="stat-card"><div class="number">{num}</div><div class="label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("✅ Validation des profils travailleurs")
    pending = query_db("SELECT * FROM users WHERE profile_type='Travailleur' AND is_verified=0")
    if pending:
        for t in pending:
            with st.expander(f"{t['name']} — {t['phone']} ({t['wilaya']}, {t['commune']})"):
                if t["documents"]:
                    st.image(f"data:image/jpeg;base64,{t['documents']}", width=280)
                col_v, col_r = st.columns(2)
                with col_v:
                    if st.button("✅ Valider", key=f"val_{t['id']}", type="primary"):
                        query_db("UPDATE users SET is_verified=1 WHERE id=?", (t["id"],), fetch=False)
                        st.success(_("validated"))
                        st.rerun()
                with col_r:
                    if st.button("❌ Rejeter", key=f"rej_{t['id']}"):
                        query_db("DELETE FROM users WHERE id=? AND profile_type='Travailleur' AND is_verified=0", (t["id"],), fetch=False)
                        st.rerun()
    else:
        st.info(_("pending_none"))

    st.markdown("---")
    st.subheader("📋 Offres d'emploi publiées")
    offres = query_db("SELECT a.*, u.name as author FROM announcements a JOIN users u ON a.user_id=u.id WHERE a.type='job' ORDER BY a.created_at DESC")
    for o in offres:
        cnt = query_db("SELECT COUNT(*) as n FROM messages WHERE announcement_id=?", (o["id"],))[0]["n"]
        with st.expander(f"📌 {o['title']} — {o['wilaya']} (📩 {cnt} candidatures)"):
            st.markdown(f"**Description :** {o['description']}")
            st.markdown(f"**Prix :** {o['price']} {o['unit']}")
            postulants = query_db(
                "SELECT DISTINCT u.name, u.phone FROM messages m JOIN users u ON m.sender_id=u.id WHERE m.announcement_id=?",
                (o["id"],)
            )
            if postulants:
                st.markdown("**Candidats :**")
                for p in postulants:
                    st.write(f"• {p['name']} — {p['phone']}")

# ─── Messages ─────────────────────────────────────────────────────────────────
def messages_page():
    st.markdown("### 💬 " + _("messages"))
    user = st.session_state.user
    if not user:
        st.warning(_("login_required"))
        return

    if st.session_state.msg_to:
        other = query_db("SELECT name FROM users WHERE id=?", (st.session_state.msg_to,))
        if not other:
            st.session_state.msg_to = None
            st.rerun()
            return

        st.subheader(f"Conversation avec {other[0]['name']}")
        if st.button("← Retour aux conversations"):
            st.session_state.msg_to = None
            st.session_state.msg_announce = None
            st.rerun()

        msgs = query_db(
            """SELECT * FROM messages
               WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)
               ORDER BY created_at""",
            (user["id"], st.session_state.msg_to, st.session_state.msg_to, user["id"])
        )

        st.markdown('<div style="max-height:400px;overflow-y:auto;padding:10px;background:#f9fafb;border-radius:12px;margin-bottom:12px;">', unsafe_allow_html=True)
        for m in msgs:
            is_me = m["sender_id"] == user["id"]
            css = "msg-bubble-me" if is_me else "msg-bubble-other"
            align = "right" if is_me else "left"
            st.markdown(
                f'<div style="text-align:{align}"><div class="{css}">{m["content"]}<div class="msg-time">{m["created_at"]}</div></div></div>',
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

        with st.form("send_msg", clear_on_submit=True):
            txt = st.text_area("Votre message...", height=80)
            if st.form_submit_button(_("send"), use_container_width=True, type="primary"):
                if txt.strip():
                    query_db(
                        "INSERT INTO messages (sender_id,receiver_id,announcement_id,content) VALUES (?,?,?,?)",
                        (user["id"], st.session_state.msg_to, st.session_state.msg_announce, txt.strip()),
                        fetch=False
                    )
                    st.rerun()
    else:
        # Liste des conversations
        contacts = query_db(
            """SELECT DISTINCT u.id, u.name, u.profile_type,
               MAX(m.created_at) as last_msg
               FROM users u
               JOIN messages m ON u.id IN (m.sender_id, m.receiver_id)
               WHERE (m.sender_id=? OR m.receiver_id=?) AND u.id!=?
               GROUP BY u.id ORDER BY last_msg DESC""",
            (user["id"],) * 3
        )
        if contacts:
            for c in contacts:
                col_n, col_b = st.columns([4, 1])
                col_n.markdown(f"**{c['name']}** — *{c['profile_type']}*")
                with col_b:
                    if st.button("Ouvrir", key=f"open_{c['id']}", use_container_width=True):
                        st.session_state.msg_to = c["id"]
                        st.rerun()
                st.markdown("---")
        else:
            st.info(_("no_convo"))

# ─── Évaluations ──────────────────────────────────────────────────────────────
def reviews_page():
    st.markdown("### ⭐ " + _("reviews"))
    user = st.session_state.user
    if not user:
        st.warning(_("login_required"))
        return

    if st.session_state.review_announce:
        ann = query_db("SELECT * FROM announcements WHERE id=?", (st.session_state.review_announce,))
        if not ann:
            st.session_state.review_announce = None
            st.rerun()
            return

        # Vérifier si déjà évalué
        already = query_db(
            "SELECT id FROM reviews WHERE announcement_id=? AND reviewer_id=?",
            (st.session_state.review_announce, user["id"])
        )
        if already:
            st.warning("Vous avez déjà évalué cette annonce.")
            st.session_state.review_announce = None
            return

        st.subheader(f"Évaluer : {ann[0]['title']}")
        if st.button("← Retour"):
            st.session_state.review_announce = None
            st.rerun()

        with st.form("review_form"):
            rating  = st.slider("Note (/5)", 1, 5, 4)
            comment = st.text_area("Commentaire")
            if st.form_submit_button("Soumettre", type="primary", use_container_width=True):
                query_db(
                    "INSERT INTO reviews (announcement_id,reviewer_id,rating,comment) VALUES (?,?,?,?)",
                    (st.session_state.review_announce, user["id"], rating, comment),
                    fetch=False
                )
                st.success(_("rating_sent"))
                st.session_state.review_announce = None
                st.rerun()

        # Afficher les avis existants
        existing = query_db(
            "SELECT r.*, u.name FROM reviews r JOIN users u ON r.reviewer_id=u.id WHERE r.announcement_id=? ORDER BY r.created_at DESC",
            (st.session_state.review_announce,)
        )
        if existing:
            st.markdown("---")
            st.markdown("**Avis existants :**")
            avg = sum(r["rating"] for r in existing) / len(existing)
            st.markdown(f"Moyenne : {'⭐' * round(avg)} ({avg:.1f}/5, {len(existing)} avis)")
            for r in existing:
                st.markdown(f"- **{r['name']}** — {'⭐' * r['rating']} — *{r['comment']}*")
    else:
        my_anns = query_db("SELECT id,title FROM announcements WHERE user_id=?", (user["id"],))
        if my_anns:
            ids = [str(a["id"]) for a in my_anns]
            revs = query_db(
                f"SELECT r.*, u.name FROM reviews r JOIN users u ON r.reviewer_id=u.id WHERE r.announcement_id IN ({','.join(ids)}) ORDER BY r.created_at DESC"
            )
            if revs:
                for r in revs:
                    st.markdown(f"{'⭐' * r['rating']} **{r['name']}** — *{r['comment']}* <small>({r['created_at'][:10]})</small>", unsafe_allow_html=True)
            else:
                st.info("Aucun avis reçu pour vos annonces.")
        else:
            st.info("Vous n'avez pas encore d'annonces.")

# ─── Contrat ──────────────────────────────────────────────────────────────────
def contract_page():
    st.markdown("### 📄 " + _("contract"))
    user = st.session_state.user
    if not user:
        st.warning(_("login_required"))
        return

    if st.session_state.contract_announce:
        anns = query_db("SELECT * FROM announcements WHERE id=?", (st.session_state.contract_announce,))
        if not anns:
            st.session_state.contract_announce = None
            st.rerun()
            return

        ann   = anns[0]
        owner = query_db("SELECT * FROM users WHERE id=?", (ann["user_id"],))
        if not owner:
            st.error("Propriétaire introuvable.")
            return
        owner = owner[0]

        st.subheader(f"📝 Contrat pour : {ann['title']}")
        if st.button("← Retour"):
            st.session_state.contract_announce = None
            st.rerun()

        c1, c2 = st.columns(2)
        start_date = c1.date_input("Date de début", date.today())
        end_date   = c2.date_input("Date de fin",   date.today())
        terms_text = st.text_area("Conditions particulières", height=120)

        if start_date > end_date:
            st.error("La date de fin doit être après la date de début.")
        elif st.button("📥 Générer et télécharger le contrat", type="primary", use_container_width=True):
            terms = {"start": start_date.isoformat(), "end": end_date.isoformat(), "details": terms_text}
            pdf_bytes = generate_contract_pdf(ann, user["name"], owner["name"], terms)
            if pdf_bytes:
                ext = "pdf" if isinstance(pdf_bytes, bytes) and pdf_bytes[:4] == b'%PDF' else "txt"
                st.download_button(
                    label=f"📥 {_('download')} (.{ext})",
                    data=pdf_bytes,
                    file_name=f"contrat_{ann['id']}.{ext}",
                    mime=f"application/{ext}",
                    use_container_width=True
                )
                query_db(
                    "INSERT INTO contracts (announcement_id,renter_id,owner_id,start_date,end_date,terms,status) VALUES (?,?,?,?,?,?,?)",
                    (ann["id"], user["id"], owner["id"], start_date.isoformat(), end_date.isoformat(), terms_text, "active"),
                    fetch=False
                )
                st.success(_("contract_created"))
    else:
        # Mes contrats
        my_contracts = query_db(
            """SELECT c.*, a.title as ann_title, u.name as owner_name
               FROM contracts c
               JOIN announcements a ON c.announcement_id=a.id
               JOIN users u ON c.owner_id=u.id
               WHERE c.renter_id=? ORDER BY c.created_at DESC""",
            (user["id"],)
        )
        if my_contracts:
            st.subheader("Mes contrats signés")
            for c in my_contracts:
                st.markdown(f"- **{c['ann_title']}** avec *{c['owner_name']}* | {c['start_date']} → {c['end_date']} | Statut : `{c['status']}`")
        else:
            st.info("Aucun contrat pour le moment.")

# ─── Vérification ─────────────────────────────────────────────────────────────
def verification_page():
    st.markdown("### 🪪 " + _("verification"))
    user = st.session_state.user
    if not user:
        st.warning(_("login_required"))
        return

    status = "✅ Vérifié" if user["is_verified"] else "⏳ En attente de vérification"
    st.info(f"Statut actuel : **{status}**")

    if not user["is_verified"]:
        st.markdown("Soumettez une pièce d'identité ou registre de commerce pour être vérifié.")
        doc = st.file_uploader("📎 Document (JPG, PNG, PDF)", type=["jpg","jpeg","png","pdf"])
        if doc and st.button("📤 Envoyer le document", type="primary"):
            if doc.type == "application/pdf":
                b64 = base64.b64encode(doc.read()).decode()
            else:
                b64 = image_to_base64(doc)
            if b64:
                query_db("UPDATE users SET documents=? WHERE id=?", (b64, user["id"]), fetch=False)
                st.success(_("doc_sent"))
            else:
                st.error("Impossible de lire le fichier.")

# ─── Profil ───────────────────────────────────────────────────────────────────
def profile_page():
    st.markdown("### 👤 " + _("profile"))
    user = st.session_state.user
    if not user:
        st.warning(_("login_required"))
        return

    col_info, col_stats = st.columns([2, 1])
    with col_info:
        st.markdown(f"""
        <div class="card">
            <div class="card-body">
                <div class="card-title" style="font-size:1.3rem;">👤 {user['name']}</div>
                <p>📱 <strong>Téléphone :</strong> {user['phone']}</p>
                <p>🏷️ <strong>Profil :</strong> {user['profile_type']}</p>
                <p>📍 <strong>Localisation :</strong> {user['wilaya']} — {user.get('commune','')}</p>
                <p>🪪 <strong>Statut :</strong> {'✅ Vérifié' if user['is_verified'] else '❌ Non vérifié'}</p>
                <p>📅 <strong>Inscrit depuis :</strong> {user.get('created_at','')[:10]}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_stats:
        nb_ann = query_db("SELECT COUNT(*) as n FROM announcements WHERE user_id=?", (user["id"],))[0]["n"]
        nb_msg = query_db("SELECT COUNT(*) as n FROM messages WHERE sender_id=?", (user["id"],))[0]["n"]
        nb_rev = query_db("SELECT COUNT(*) as n FROM reviews r JOIN announcements a ON r.announcement_id=a.id WHERE a.user_id=?", (user["id"],))[0]["n"]
        st.markdown(f'<div class="stat-card"><div class="number">{nb_ann}</div><div class="label">Annonces</div></div><br>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-card"><div class="number">{nb_msg}</div><div class="label">Messages envoyés</div></div><br>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-card"><div class="number">{nb_rev}</div><div class="label">Avis reçus</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Mes annonces")
    my_anns = query_db("SELECT * FROM announcements WHERE user_id=? ORDER BY created_at DESC", (user["id"],))
    if my_anns:
        for a in my_anns:
            col_t, col_del = st.columns([5, 1])
            col_t.markdown(f"**{a['title']}** — {a['price']} {a['unit']} | *{a['wilaya']}*")
            with col_del:
                if st.button("🗑️", key=f"del_{a['id']}", help="Supprimer"):
                    query_db("DELETE FROM announcements WHERE id=? AND user_id=?", (a["id"], user["id"]), fetch=False)
                    st.rerun()
    else:
        st.info("Aucune annonce publiée.")

    st.markdown("---")
    if not user["is_verified"]:
        if st.button("🪪 Demander la vérification", type="primary"):
            st.session_state.page = "verification"
            st.rerun()

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    # Init DB une seule fois par session
    if not st.session_state.db_initialized:
        init_db()
        st.session_state.db_initialized = True

    # Sidebar
    with st.sidebar:
        st.markdown("### 🌐 Langue")
        lang = st.selectbox("", ["fr","ar","en"],
                            index=["fr","ar","en"].index(st.session_state.lang),
                            label_visibility="collapsed")
        if lang != st.session_state.lang:
            st.session_state.lang = lang
            st.rerun()

        st.markdown("---")
        if st.session_state.user:
            u = st.session_state.user
            verified_badge = "✅" if u["is_verified"] else "⏳"
            st.markdown(f"**👤 {u['name']}** {verified_badge}")
            st.caption(f"{u['profile_type']} — {u['wilaya']}")
            if st.button(_("logout"), use_container_width=True):
                st.session_state.user = None
                st.session_state.page = "home"
                st.rerun()
        else:
            if st.button(_("login"), use_container_width=True, type="primary"):
                st.session_state.page = "login"
                st.rerun()
            if st.button(_("register"), use_container_width=True):
                st.session_state.page = "register"
                st.rerun()

        st.markdown("---")
        st.markdown('<div style="background:#fffbeb;border:1px solid #fcd34d;border-radius:10px;padding:10px;text-align:center;font-size:0.8rem;">📢 <strong>Espace publicitaire</strong><br>contact@agriconnect.dz</div>', unsafe_allow_html=True)

    # Navbar
    if st.session_state.user:
        render_navbar()
    else:
        c1, c2, c3 = st.columns(3)
        for col, page, label in [(c1,"home",_("home")),(c2,"login",_("login")),(c3,"register",_("register"))]:
            with col:
                if st.button(label, use_container_width=True, type="primary" if st.session_state.page==page else "secondary"):
                    st.session_state.page = page
                    st.rerun()

    # Routage
    pages = {
        "home": home_page,
        "login": login_page,
        "register": register_page,
        "market": market_page,
        "job": job_page,
        "transport": transport_page,
        "grazing": grazing_page,
        "pollination": pollination_page,
        "fertilizer": fertilizer_page,
        "equipment": equipment_page,
        "anem": anem_page,
        "messages": messages_page,
        "reviews": reviews_page,
        "contract": contract_page,
        "verification": verification_page,
        "profile": profile_page,
    }
    pages.get(st.session_state.page, home_page)()

    st.markdown('<div class="footer">© 2026 AgriConnect — contact@agriconnect.dz | Tous droits réservés</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
