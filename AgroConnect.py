# app.py – AgriConnect Final (full featured, modern UI, multilingual, all wilayas, test data, ANEM)
import streamlit as st
import sqlite3
import hashlib
import json
import base64
import os
import io
import tempfile
import subprocess
from datetime import datetime, date
from PIL import Image
import folium
from streamlit_folium import st_folium
import requests

# ---------- 58 Wilayas et communes ----------
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
    "58 - El Meniaa": ["El Meniaa", "Hassi Fehal", "Hassi Gara"]
}

# ---------- Multilingual ----------
LANGUAGES = {
    "fr": {
        "app_name": "AgriConnect",
        "login": "Connexion",
        "register": "Inscription",
        "logout": "Déconnexion",
        "home": "Accueil",
        "market": "Marché",
        "job": "Emploi",
        "transport": "Transport",
        "grazing": "Pâturage",
        "pollination": "Pollinisation",
        "fertilizer": "Engrais",
        "equipment": "Matériel Agricole",
        "anem": "ANEM",
        "messages": "Messagerie",
        "reviews": "Évaluations",
        "contract": "Contrat",
        "verification": "Vérification",
        "profile": "Mon Profil",
        "no_announces": "Aucune annonce pour le moment.",
        "publish": "Publier",
        "list": "Annonces",
        "map": "Carte",
        "contact": "Contacter",
        "evaluate": "Évaluer",
        "contract_btn": "Contrat",
        "send": "Envoyer",
        "download": "Télécharger",
        "my_offers": "Mes offres",
        "suggestions": "Suggestions",
        "search": "Rechercher",
        "wilaya": "Wilaya",
        "commune": "Commune"
    },
    "ar": {
        "app_name": "أجريكونكت",
        "login": "تسجيل الدخول",
        "register": "التسجيل",
        "logout": "تسجيل الخروج",
        "home": "الرئيسية",
        "market": "السوق",
        "job": "وظائف",
        "transport": "النقل",
        "grazing": "الرعي",
        "pollination": "التلقيح",
        "fertilizer": "الأسمدة",
        "equipment": "المعدات الفلاحية",
        "anem": "الوكالة الوطنية للتشغيل",
        "messages": "الرسائل",
        "reviews": "التقييمات",
        "contract": "عقد",
        "verification": "التحقق",
        "profile": "الملف الشخصي",
        "no_announces": "لا توجد إعلانات",
        "publish": "نشر",
        "list": "قائمة",
        "map": "خريطة",
        "contact": "اتصال",
        "evaluate": "تقييم",
        "contract_btn": "عقد",
        "send": "إرسال",
        "download": "تحميل",
        "my_offers": "عروضي",
        "suggestions": "اقتراحات",
        "search": "بحث",
        "wilaya": "ولاية",
        "commune": "بلدية"
    },
    "en": {
        "app_name": "AgriConnect",
        "login": "Login",
        "register": "Register",
        "logout": "Logout",
        "home": "Home",
        "market": "Marketplace",
        "job": "Jobs",
        "transport": "Transport",
        "grazing": "Grazing",
        "pollination": "Pollination",
        "fertilizer": "Fertilizer",
        "equipment": "Equipment",
        "anem": "ANEM",
        "messages": "Messages",
        "reviews": "Reviews",
        "contract": "Contract",
        "verification": "Verification",
        "profile": "My Profile",
        "no_announces": "No announcements yet.",
        "publish": "Publish",
        "list": "List",
        "map": "Map",
        "contact": "Contact",
        "evaluate": "Rate",
        "contract_btn": "Contract",
        "send": "Send",
        "download": "Download",
        "my_offers": "My Offers",
        "suggestions": "Suggestions",
        "search": "Search",
        "wilaya": "Wilaya",
        "commune": "Commune"
    }
}

def _(text):
    lang = st.session_state.get("lang", "fr")
    return LANGUAGES.get(lang, LANGUAGES["fr"]).get(text, text)

# ---------- Page config ----------
st.set_page_config(page_title="AgriConnect", page_icon="🌾", layout="wide", initial_sidebar_state="collapsed")
DB_FILE = "agriconnect.db"

# ---------- Session state init ----------
keys = ["user", "page", "lang", "msg_to", "msg_announce", "review_announce", "contract_announce"]
for k in keys:
    if k not in st.session_state:
        if k == "user":
            st.session_state[k] = None
        elif k == "page":
            st.session_state[k] = "home"
        elif k == "lang":
            st.session_state[k] = "fr"
        else:
            st.session_state[k] = None

# ---------- CSS ----------
def apply_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    * { font-family: 'Roboto', sans-serif; }
    .main-header { font-size: 2.5rem; font-weight: 700; color: #2e7d32; text-align: center; padding: 1rem 0; }
    .navbar { display: flex; justify-content: center; background-color: #2e7d32; padding: 0.5rem; border-radius: 8px; margin-bottom: 20px; }
    .nav-item { color: white; padding: 10px 20px; margin: 0 5px; border-radius: 5px; cursor: pointer; text-decoration: none; font-weight: 500; }
    .card { border: 1px solid #e0e0e0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: transform 0.2s; background: white; margin-bottom: 20px; }
    .card:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }
    .card-img { height: 180px; object-fit: cover; background: #f5f5f5; }
    .card-body { padding: 15px; }
    .card-title { font-size: 1.2rem; font-weight: 600; color: #333; }
    .card-price { font-size: 1.3rem; font-weight: bold; color: #2e7d32; }
    .ad-banner { background: linear-gradient(135deg, #ffd54f, #ffb300); padding: 15px; border-radius: 12px; text-align: center; font-weight: bold; }
    .footer { text-align: center; padding: 20px; color: #999; border-top: 1px solid #eee; margin-top: 40px; }
    .no-announce { text-align: center; padding: 50px; color: #aaa; font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)
apply_css()

# ---------- DB ----------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Création des tables une par une
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT UNIQUE,
        password TEXT,
        profile_type TEXT,
        is_verified INTEGER DEFAULT 0,
        wilaya TEXT,
        commune TEXT,
        location_lat REAL,
        location_lon REAL,
        documents TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        title TEXT,
        description TEXT,
        price REAL,
        unit TEXT,
        wilaya TEXT,
        commune TEXT,
        lat REAL,
        lon REAL,
        data TEXT,
        images TEXT,
        video_base64 TEXT,
        video_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER,
        receiver_id INTEGER,
        announcement_id INTEGER,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id),
        FOREIGN KEY (receiver_id) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        announcement_id INTEGER,
        reviewer_id INTEGER,
        rating INTEGER,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (announcement_id) REFERENCES announcements(id),
        FOREIGN KEY (reviewer_id) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        announcement_id INTEGER,
        renter_id INTEGER,
        owner_id INTEGER,
        start_date TEXT,
        end_date TEXT,
        terms TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Insertion des données de test uniquement si la table announcements est vide
    cnt = c.execute("SELECT COUNT(*) FROM announcements").fetchone()[0]
    if cnt == 0:
        # Utilisateur ANEM
        c.execute("INSERT OR IGNORE INTO users (name, phone, password, profile_type, is_verified, wilaya, commune) VALUES (?,?,?,?,?,?,?)",
                  ("Agent ANEM", "0555000001", hashlib.sha256("anem123".encode()).hexdigest(), "ANEM", 1, "16 - Alger", "Alger Centre"))
        # Utilisateur agriculteur
        c.execute("INSERT OR IGNORE INTO users (name, phone, password, profile_type, is_verified, wilaya, commune) VALUES (?,?,?,?,?,?,?)",
                  ("Ali Ferme", "0555123456", hashlib.sha256("123456".encode()).hexdigest(), "Agriculteur", 1, "39 - El Oued", "Guemar"))
        
        # Récupérer l'id de l'utilisateur agriculteur
        res = c.execute("SELECT id FROM users WHERE phone='0555123456'").fetchone()
        if res:
            user_id = res[0]
            annonces = [
                ("market", "Pommes de terre fraîches", "Variété Spunta, 10 tonnes", 45, "DA/kg", "39 - El Oued", "Guemar",
                 json.dumps({"product_type":"Légumes","quantity":10000})),
                ("grazing", "Chaumes de blé à louer", "50 ha, eau disponible, mai-juillet", 200, "DA/tête/jour", "14 - Tiaret", "Sougueur",
                 json.dumps({"area_ha":50,"cover_type":"Chaume","water":"Oui","start_date":"2026-05-01","end_date":"2026-07-31","max_animals":100})),
                ("fertilizer", "Fumier ovin composté", "5 tonnes", 3000, "DA/tonne", "17 - Djelfa", "Messaâd",
                 json.dumps({"fertilizer_type":"Fumier ovin","quantity_tons":5})),
                ("transport", "Camion frigorifique Alger-Médéa", "10 tonnes", 8000, "DA/voyage", "16 - Alger", "El Harrach",
                 json.dumps({"vehicle_type":"Frigorifique","capacity":10})),
                ("pollination", "20 ruches disponibles", "Race locale, déplacement Béjaïa-Batna", 5000, "DA/ruche/semaine", "06 - Béjaïa", "Akbou",
                 json.dumps({"hive_count":20,"bee_race":"Locale","zone":"Béjaïa-Batna"})),
                ("equipment", "Tracteur Massey Ferguson 2020", "Bon état, location", 5000, "DA/jour", "31 - Oran", "Es Sénia",
                 json.dumps({"offer_type":"Location","equipment_type":"Tracteur","brand":"Massey Ferguson","model":"MF 2020","year":2020,"state":"Bon","rental_period":"Jour","availability":"Toute l'année"}))
            ]
            for typ, titre, desc, prix, unit, wilaya, commune, data in annonces:
                c.execute("INSERT INTO announcements (user_id, type, title, description, price, unit, wilaya, commune, data) VALUES (?,?,?,?,?,?,?,?,?)",
                          (user_id, typ, titre, desc, prix, unit, wilaya, commune, data))
    
    conn.commit()
    conn.close()

def query_db(query, params=(), fetch=True):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, params)
    if fetch:
        rows = cur.fetchall()
        conn.close()
        return rows
    else:
        conn.commit()
        conn.close()

def hash_password(pwd): return hashlib.sha256(pwd.encode()).hexdigest()

# ---------- Media utils ----------
def image_to_base64(img, max_size=(800,600)):
    if img is None: return None
    try:
        im = Image.open(img); im.thumbnail(max_size)
        buf = io.BytesIO(); im.save(buf, format="JPEG", quality=60)
        return base64.b64encode(buf.getvalue()).decode()
    except: return None

def moderate_image(b64): return True  # placeholder

def generate_contract(ann, renter_name, owner_name, terms):
    from fpdf import FPDF
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.cell(0,10,"Contrat AgriConnect",ln=1,align='C')
    pdf.ln(5)
    pdf.multi_cell(0,10,f"Annonce: {ann['title']}\nPropriétaire: {owner_name}\nLocataire: {renter_name}\nDurée: {terms['start']} au {terms['end']}\nConditions: {terms['details']}")
    path = "/tmp/contrat.pdf"; pdf.output(path); return path

def display_images(img_str):
    if not img_str: return
    imgs = img_str.split(";")
    cols = st.columns(min(len(imgs),3))
    for i, b64 in enumerate(imgs[:3]):
        if b64: cols[i].image(f"data:image/jpeg;base64,{b64}", use_column_width=True)

# ---------- Render card ----------
def render_announce_card(a):
    img_html = '<div class="card-img" style="background:#ddd;"></div>'
    if a['images']:
        first = a['images'].split(";")[0]
        img_html = f'<img src="data:image/jpeg;base64,{first}" class="card-img">'
    html = f"""
    <div class="card">
        {img_html}
        <div class="card-body">
            <div class="card-title">{a['title']}</div>
            <div style="color:#666;margin:5px 0;">{a['description'][:80]}...</div>
            <div class="card-price">{a['price']} {a['unit']}</div>
            <div style="color:#999;">📍 {a['wilaya']} - {a['commune']}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(_("contact"), key=f"msg_{a['id']}"):
            st.session_state.msg_to = a['user_id']; st.session_state.msg_announce = a['id']; st.session_state.page = "messages"; st.rerun()
    with col2:
        if st.button(_("evaluate"), key=f"rev_{a['id']}"):
            st.session_state.review_announce = a['id']; st.session_state.page = "reviews"; st.rerun()
    with col3:
        if a['type'] in ["grazing","pollination","equipment"]:
            if st.button(_("contract_btn"), key=f"contract_{a['id']}"):
                st.session_state.contract_announce = a['id']; st.session_state.page = "contract"; st.rerun()

# ---------- Navbar ----------
def render_navbar():
    items = [
        ("home", _("home")), ("market", _("market")), ("job", _("job")),
        ("transport", _("transport")), ("grazing", _("grazing")),
        ("pollination", _("pollination")), ("fertilizer", _("fertilizer")),
        ("equipment", _("equipment")), ("messages", _("messages")),
        ("profile", _("profile"))
    ]
    if st.session_state.user and st.session_state.user.get('profile_type') == 'ANEM':
        items.insert(2, ("anem", _("anem")))
    cols = st.columns(len(items))
    for i, (page, label) in enumerate(items):
        with cols[i]:
            if st.button(label, key=f"nav_{page}", use_container_width=True):
                st.session_state.page = page; st.rerun()

# ---------- Login / Register ----------
def login_page():
    st.title(_("login"))
    phone = st.text_input("Téléphone"); pwd = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        row = query_db("SELECT * FROM users WHERE phone=? AND password=?", (phone, hash_password(pwd)))
        if row:
            st.session_state.user = dict(row[0]); st.session_state.page = "home"; st.rerun()
        else: st.error("Identifiants incorrects")

def register_page():
    st.title(_("register"))
    name = st.text_input("Nom complet"); phone = st.text_input("Téléphone")
    pwd = st.text_input("Mot de passe", type="password")
    profile = st.selectbox("Profil", ["Agriculteur","Éleveur","Apiculteur","Transporteur","Acheteur","ANEM","Travailleur"])
    wilaya = st.selectbox(_("wilaya"), list(WILAYAS.keys()))
    commune = st.selectbox(_("commune"), WILAYAS[wilaya])
    if st.button("S'inscrire"):
        try:
            query_db("INSERT INTO users (name, phone, password, profile_type, wilaya, commune) VALUES (?,?,?,?,?,?)",
                     (name, phone, hash_password(pwd), profile, wilaya, commune), fetch=False)
            st.success("Compte créé, connectez-vous.")
        except sqlite3.IntegrityError:
            st.error("Numéro déjà utilisé")

# ---------- Home ----------
def home_page():
    st.markdown('<div class="main-header">🌾 AgriConnect - Le carrefour de l\'agriculture algérienne</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([3,2,1])
    with col1: st.text_input(_("search"), placeholder="Ex: pommes de terre, tracteur...")
    with col2: st.selectbox(_("wilaya"), ["Toutes"] + list(WILAYAS.keys()))
    with col3: st.write(""); st.button(_("search"))
    st.subheader("📌 " + _("my_offers"))
    annonces = query_db("SELECT a.*, u.name as author FROM announcements a JOIN users u ON a.user_id=u.id ORDER BY a.created_at DESC LIMIT 6")
    if annonces:
        for i in range(0, len(annonces), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(annonces):
                    with cols[j]: render_announce_card(annonces[i+j])
    else: st.markdown('<div class="no-announce">' + _("no_announces") + '</div>', unsafe_allow_html=True)

# ---------- Generic announce page (all modules) ----------
def generic_announce_page(module_type, fields_config, filters):
    tab1, tab2, tab3 = st.tabs([_("list"), _("publish"), _("map")])
    with tab1:
        # Filters
        cols = st.columns(len(filters))
        filter_vals = []
        for i, f in enumerate(filters):
            if f == "wilaya":
                val = cols[i].selectbox(_("wilaya"), ["Toutes"] + list(WILAYAS.keys()), key=f"filt_wilaya_{module_type}")
                if val != "Toutes": filter_vals.append(("wilaya", val))
            elif f == "price_max":
                val = cols[i].number_input("Prix max", min_value=0, step=100, key=f"filt_price_{module_type}")
                if val > 0: filter_vals.append(("price", val, "<="))
            elif f == "type_produit":
                val = cols[i].selectbox("Type", ["Tous","Légumes","Fruits","Céréales","Bétail","Miel"], key=f"filt_type_{module_type}")
                if val != "Tous": filter_vals.append(("data->>'product_type'", val))
            elif f == "equipment_type":
                val = cols[i].selectbox("Type", ["Tous","Tracteur","Moissonneuse","Charrue","Remorque","Irrigation","Autre"], key=f"filt_eqtype_{module_type}")
                if val != "Tous": filter_vals.append(("data->>'equipment_type'", val))
            elif f == "offer_type":
                val = cols[i].selectbox("Offre", ["Tous","Vente","Location"], key=f"filt_offer_{module_type}")
                if val != "Tous": filter_vals.append(("data->>'offer_type'", val))
        sql = f"SELECT a.*, u.name as author FROM announcements a JOIN users u ON a.user_id=u.id WHERE a.type='{module_type}'"
        params = []
        for fv in filter_vals:
            if len(fv)==2:
                sql += f" AND a.{fv[0]}=?"; params.append(fv[1])
            else:
                sql += f" AND a.{fv[0]}<=?"; params.append(fv[1])
        sql += " ORDER BY a.created_at DESC"
        annonces = query_db(sql, tuple(params))
        if annonces:
            for a in annonces: render_announce_card(a)
        else: st.info(_("no_announces"))
    with tab2:
        with st.form(f"form_{module_type}"):
            st.subheader(_("publish"))
            title = st.text_input("Titre"); desc = st.text_area("Description")
            price = st.number_input("Prix", min_value=0.0); unit = st.text_input("Unité")
            wilaya = st.selectbox(_("wilaya"), list(WILAYAS.keys()), key=f"pub_wilaya_{module_type}")
            commune = st.selectbox(_("commune"), WILAYAS[wilaya], key=f"pub_commune_{module_type}")
            extra = {}
            for field, label, opts in fields_config:
                if opts == "text": extra[field] = st.text_input(label)
                elif opts == "number": extra[field] = st.number_input(label, min_value=0)
                elif isinstance(opts, list): extra[field] = st.selectbox(label, opts)
            images = st.file_uploader("Photos", type=["jpg","jpeg","png"], accept_multiple_files=True)
            if st.form_submit_button(_("publish")):
                if not st.session_state.user: st.error("Connectez-vous")
                else:
                    imgs = []
                    if images:
                        for img in images[:5]:
                            b64 = image_to_base64(img)
                            if b64: imgs.append(b64)
                    data_json = json.dumps(extra)
                    query_db("INSERT INTO announcements (user_id, type, title, description, price, unit, wilaya, commune, data, images) VALUES (?,?,?,?,?,?,?,?,?,?)",
                             (st.session_state.user['id'], module_type, title, desc, price, unit, wilaya, commune, data_json, ";".join(imgs)), fetch=False)
                    st.success("Publié !"); st.rerun()
    with tab3:
        m = folium.Map(location=[28.0339, 1.6596], zoom_start=5)
        anns = query_db(f"SELECT * FROM announcements WHERE type='{module_type}' AND lat!=0 AND lon!=0")
        for a in anns:
            if a['lat'] and a['lon']: folium.Marker([a['lat'], a['lon']], popup=a['title']).add_to(m)
        st_folium(m, width=700)

# ---------- All module pages ----------
def market_page(): 
    generic_announce_page("market", [("product_type","Type de produit",["Légumes","Fruits","Céréales","Bétail","Miel"]),("quantity","Quantité","number")], ["wilaya","price_max","type_produit"])
def job_page():
    generic_announce_page("job", [("contract_type","Type de contrat",["Saisonnier","Permanent","Journalier"]),("skills","Compétences","text"),("duration","Durée (jours)","number")], ["wilaya"])
def transport_page():
    generic_announce_page("transport", [("vehicle_type","Véhicule",["Camion","Bétaillère","Frigorifique"]),("capacity","Capacité (t)","number")], ["wilaya"])
def grazing_page():
    generic_announce_page("grazing", [("area_ha","Superficie (ha)","number"),("cover_type","Couvert",["Chaume","Jachère","Herbe"]),("water","Eau",["Oui","Non"]),("start_date","Début (AAAA-MM-JJ)","text"),("end_date","Fin","text"),("max_animals","Max animaux","number")], ["wilaya"])
def pollination_page():
    generic_announce_page("pollination", [("hive_count","Nb ruches","number"),("bee_race","Race",["Locale","Hybride"]),("zone","Zone","text")], ["wilaya"])
def fertilizer_page():
    generic_announce_page("fertilizer", [("fertilizer_type","Type",["Fumier bovin","Fumier ovin","Fiente volaille","Compost"]),("quantity_tons","Quantité (t)","number")], ["wilaya"])
def equipment_page():
    generic_announce_page("equipment", [("offer_type","Offre",["Vente","Location"]),("equipment_type","Type",["Tracteur","Moissonneuse","Charrue","Remorque","Système d'irrigation","Épandeur","Semoir","Autre"]),("brand","Marque","text"),("model","Modèle","text"),("year","Année","number"),("state","État",["Neuf","Très bon","Bon","À rénover"]),("rental_period","Période location",["Heure","Jour","Semaine","Mois"]),("availability","Disponibilité","text")], ["wilaya","price_max","equipment_type","offer_type"])

# ---------- ANEM page ----------
def anem_page():
    st.markdown('<div class="main-header">🏛️ ' + _("anem") + '</div>', unsafe_allow_html=True)
    if not st.session_state.user or st.session_state.user.get('profile_type') != 'ANEM':
        st.error("Accès réservé"); return
    col1, col2, col3 = st.columns(3)
    col1.metric("Offres publiées", query_db("SELECT COUNT(*) as n FROM announcements WHERE type='job'")[0]['n'])
    col2.metric("Demandeurs inscrits", query_db("SELECT COUNT(*) as n FROM users WHERE profile_type='Travailleur'")[0]['n'])
    col3.metric("Messages échangés", query_db("SELECT COUNT(*) as n FROM messages")[0]['n'])
    st.markdown("---")
    st.subheader("✅ Validation des profils travailleurs")
    travailleurs = query_db("SELECT * FROM users WHERE profile_type='Travailleur' AND is_verified=0")
    if travailleurs:
        for t in travailleurs:
            with st.expander(f"{t['name']} - {t['phone']} ({t['wilaya']})"):
                if t.get('documents'): st.image(f"data:image/jpeg;base64,{t['documents']}", width=300)
                if st.button("Valider", key=f"val_{t['id']}"):
                    query_db("UPDATE users SET is_verified=1 WHERE id=?", (t['id'],), fetch=False)
                    st.success("Validé"); st.rerun()
    else: st.info("Aucun profil en attente")
    st.markdown("---")
    st.subheader("📋 Offres d'emploi")
    offres = query_db("SELECT * FROM announcements WHERE type='job' ORDER BY created_at DESC")
    for o in offres:
        cnt = query_db("SELECT COUNT(*) as n FROM messages WHERE announcement_id=?", (o['id'],))[0]['n']
        with st.expander(f"{o['title']} (📩 {cnt})"):
            st.write(o['description'])
            if st.button("Voir postulants", key=f"post_{o['id']}"):
                postulants = query_db("SELECT DISTINCT u.name, u.phone FROM messages m JOIN users u ON m.sender_id=u.id WHERE m.announcement_id=?", (o['id'],))
                for p in postulants: st.write(f"- {p['name']} ({p['phone']})")

# ---------- Messages ----------
def messages_page():
    st.title(_("messages"))
    if not st.session_state.user: st.warning("Connectez-vous"); return
    if st.session_state.msg_to:
        other = query_db("SELECT name FROM users WHERE id=?", (st.session_state.msg_to,))
        if other:
            st.subheader(f"Avec {other[0]['name']}")
            msgs = query_db("SELECT * FROM messages WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?) ORDER BY created_at",
                            (st.session_state.user['id'], st.session_state.msg_to, st.session_state.msg_to, st.session_state.user['id']))
            for m in msgs:
                side = "left" if m['sender_id']==st.session_state.user['id'] else "right"
                st.markdown(f"<div style='text-align:{side};background:#f0f2f6;padding:8px;border-radius:8px;margin:4px'>{m['content']}<br><small>{m['created_at']}</small></div>", unsafe_allow_html=True)
            with st.form("send"):
                txt = st.text_area("Message"); 
                if st.form_submit_button(_("send")):
                    query_db("INSERT INTO messages (sender_id, receiver_id, announcement_id, content) VALUES (?,?,?,?)",
                             (st.session_state.user['id'], st.session_state.msg_to, st.session_state.msg_announce, txt), fetch=False)
                    st.rerun()
    else:
        contacts = query_db("SELECT DISTINCT u.id, u.name FROM users u JOIN messages m ON u.id IN (m.sender_id,m.receiver_id) WHERE (m.sender_id=? OR m.receiver_id=?) AND u.id!=?",
                            (st.session_state.user['id'],)*3)
        if contacts:
            for c in contacts:
                if st.button(c['name']): st.session_state.msg_to = c['id']; st.rerun()
        else: st.info("Aucune conversation")

# ---------- Reviews ----------
def reviews_page():
    st.title(_("reviews"))
    if not st.session_state.user: st.warning("Connectez-vous"); return
    if st.session_state.review_announce:
        ann = query_db("SELECT * FROM announcements WHERE id=?", (st.session_state.review_announce,))
        if ann:
            st.subheader(f"Évaluer {ann[0]['title']}")
            rating = st.slider("Note", 1,5,3); comment = st.text_area("Commentaire")
            if st.button("Soumettre"):
                query_db("INSERT INTO reviews (announcement_id, reviewer_id, rating, comment) VALUES (?,?,?,?)",
                         (st.session_state.review_announce, st.session_state.user['id'], rating, comment), fetch=False)
                st.success("Merci"); st.session_state.review_announce = None; st.rerun()
    else:
        my = query_db("SELECT id, title FROM announcements WHERE user_id=?", (st.session_state.user['id'],))
        if my:
            ids = [m['id'] for m in my]
            revs = query_db(f"SELECT r.*, u.name FROM reviews r JOIN users u ON r.reviewer_id=u.id WHERE r.announcement_id IN ({','.join('?'*len(ids))}) ORDER BY r.created_at DESC", ids)
            for r in revs: st.write(f"⭐ {r['rating']} - {r['comment']} ({r['name']})")
        else: st.info("Aucune annonce")

# ---------- Contract ----------
def contract_page():
    st.title(_("contract"))
    if not st.session_state.user: st.warning("Connectez-vous"); return
    if st.session_state.contract_announce:
        ann = query_db("SELECT * FROM announcements WHERE id=?", (st.session_state.contract_announce,))[0]
        owner = query_db("SELECT * FROM users WHERE id=?", (ann['user_id'],))[0]
        start = st.date_input("Début", date.today()); end = st.date_input("Fin", date.today())
        terms = st.text_area("Conditions")
        if st.button("Générer contrat"):
            path = generate_contract(ann, st.session_state.user['name'], owner['name'], {"start":start.isoformat(), "end":end.isoformat(), "details":terms})
            with open(path, "rb") as f: st.download_button(_("download"), f, file_name="contrat.pdf")
            query_db("INSERT INTO contracts (announcement_id, renter_id, owner_id, start_date, end_date, terms, status) VALUES (?,?,?,?,?,?,?)",
                     (ann['id'], st.session_state.user['id'], owner['id'], start.isoformat(), end.isoformat(), terms, "active"), fetch=False)
            st.success("Contrat créé")

# ---------- Verification ----------
def verification_page():
    st.title(_("verification"))
    if not st.session_state.user: st.warning("Connectez-vous"); return
    doc = st.file_uploader("Pièce d'identité / Registre de commerce", type=["jpg","jpeg","png","pdf"])
    if doc and st.button("Envoyer"):
        if doc.type == "application/pdf": b64 = base64.b64encode(doc.read()).decode()
        else: b64 = image_to_base64(doc)
        query_db("UPDATE users SET documents=? WHERE id=?", (b64, st.session_state.user['id']), fetch=False)
        st.success("Document soumis")

# ---------- Profile ----------
def profile_page():
    st.title(_("profile"))
    if not st.session_state.user: st.warning("Connectez-vous"); return
    u = st.session_state.user
    st.write(f"**Nom:** {u['name']}")
    st.write(f"**Téléphone:** {u['phone']}")
    st.write(f"**Profil:** {u['profile_type']}")
    st.write(f"**Wilaya:** {u['wilaya']} - {u.get('commune','')}")
    st.write(f"**Vérifié:** {'✅' if u['is_verified'] else '❌'}")
    if st.button("Demander vérification"):
        query_db("UPDATE users SET is_verified=1 WHERE id=?", (u['id'],), fetch=False)
        st.session_state.user['is_verified'] = 1; st.success("Vérifié!")

# ---------- Language selector ----------
def language_selector():
    lang = st.sidebar.selectbox("🌐 Langue", ["fr","ar","en"], index=["fr","ar","en"].index(st.session_state.lang))
    if lang != st.session_state.lang:
        st.session_state.lang = lang; st.rerun()

# ---------- Main ----------
def main():
    init_db()
    # Sidebar
    with st.sidebar:
        language_selector()
        st.markdown("---")
        st.markdown("### 📢 Publicité")
        st.image("https://placehold.co/300x250?text=Votre+Pub+Ici", use_column_width=True)
        if st.session_state.user:
            st.markdown("---")
            st.write(f"👤 {st.session_state.user['name']}")
            if st.button(_("logout")): st.session_state.user = None; st.session_state.page = "home"; st.rerun()
        else:
            st.markdown("---")
            if st.button(_("login")): st.session_state.page = "login"; st.rerun()
            if st.button(_("register")): st.session_state.page = "register"; st.rerun()

    # Navigation bar
    if st.session_state.user: render_navbar()
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(_("home"), use_container_width=True): st.session_state.page = "home"; st.rerun()
        with col2:
            if st.button(_("login"), use_container_width=True): st.session_state.page = "login"; st.rerun()
        with col3:
            if st.button(_("register"), use_container_width=True): st.session_state.page = "register"; st.rerun()

    # Page routing
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
    func = pages.get(st.session_state.page, home_page)
    func()
    st.markdown('<div class="footer">© 2026 AgriConnect - contact@agriconnect.dz</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
