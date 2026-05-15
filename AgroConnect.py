# app.py – AgriConnect complet (58 wilayas, annonces test, publicité)
import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import json
import base64
import os
import io
import re
import requests
import tempfile
import subprocess
from datetime import datetime, date
from PIL import Image
import folium
from streamlit_folium import st_folium

# ---------- Données des wilayas et communes ----------
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

# ---------- Configuration multilingue ----------
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
        "messages": "الرسائل",
        "reviews": "التقييمات",
        "contract": "عقد",
        "verification": "التحقق",
        "profile": "الملف الشخصي",
        "no_announces": "لا توجد إعلانات حالياً",
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
    }
}

def _(text):
    lang = st.session_state.get("lang", "fr")
    return LANGUAGES.get(lang, LANGUAGES["fr"]).get(text, text)

# ---------- Configuration page ----------
st.set_page_config(page_title="AgriConnect", layout="wide", initial_sidebar_state="expanded")
DB_FILE = "agriconnect.db"

# ---------- Initialisation de la session state ----------
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"
if "lang" not in st.session_state:
    st.session_state.lang = "fr"
if "msg_to" not in st.session_state:
    st.session_state.msg_to = None
if "msg_announce" not in st.session_state:
    st.session_state.msg_announce = None
if "review_announce" not in st.session_state:
    st.session_state.review_announce = None
if "contract_announce" not in st.session_state:
    st.session_state.contract_announce = None

# ---------- Initialisation base de données (avec annonces test) ----------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
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
    # Création d'un utilisateur test et d'annonces test si la table est vide
    existing = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if existing == 0:
        # Utilisateur admin/test
        c.execute("INSERT INTO users (name, phone, password, profile_type, is_verified, wilaya, commune) VALUES (?,?,?,?,?,?,?)",
                  ("Ali Ferme", "0555123456", hashlib.sha256("123456".encode()).hexdigest(), "Agriculteur", 1, "16 - Alger", "Bir Mourad Raïs"))
        user_id = c.lastrowid
        # Annonces test
        annonces_test = [
            ("market", "Pommes de terre fraîches", "Variété Spunta, 10 tonnes disponibles", 45, "DA/kg", "39 - El Oued", "Guemar",
             json.dumps({"product_type": "Légumes", "quantity": 10000})),
            ("grazing", "Chaumes de blé à louer", "50 hectares, eau disponible, période mai-juillet", 200, "DA/tête/jour", "14 - Tiaret", "Sougueur",
             json.dumps({"area_ha": 50, "cover_type": "Chaume", "water": "Oui", "start_date": "2026-05-01", "end_date": "2026-07-31", "max_animals": 100})),
            ("fertilizer", "Fumier ovin de qualité", "5 tonnes de fumier composté", 3000, "DA/tonne", "17 - Djelfa", "Messaâd",
             json.dumps({"fertilizer_type": "Fumier ovin", "quantity_tons": 5})),
            ("transport", "Camion frigorifique disponible", "Capacité 10 tonnes, trajets Alger-Médéa", 8000, "DA/voyage", "16 - Alger", "El Harrach",
             json.dumps({"vehicle_type": "Frigorifique", "capacity": 10})),
            ("pollination", "Location de ruches pour pollinisation", "20 ruches, race locale, déplacement Béjaïa-Batna", 5000, "DA/ruche/semaine", "06 - Béjaïa", "Akbou",
             json.dumps({"hive_count": 20, "bee_race": "Locale", "zone": "Béjaïa - Batna"})),
            ("equipment", "Tracteur à louer", "Tracteur Massey Ferguson 2020, bon état", 5000, "DA/jour", "31 - Oran", "Es Sénia",
             json.dumps({"offer_type": "Location", "equipment_type": "Tracteur", "brand": "Massey Ferguson", "model": "MF 2020", "year": 2020, "state": "Bon", "rental_period": "Jour", "availability": "Toute l'année"})),
        ]
        for typ, titre, desc, prix, unit, wilaya, commune, data in annonces_test:
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

# ---------- Utilitaires (inchangés) ----------
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def image_to_base64(img, max_size=(800,600)):
    if img is not None:
        try:
            image = Image.open(img)
            image.thumbnail(max_size)
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=60)
            return base64.b64encode(buffered.getvalue()).decode()
        except:
            return None
    return None

def compress_video(input_path, output_path):
    try:
        subprocess.run(["ffmpeg", "-i", input_path, "-vcodec", "libx264", "-crf", "28", "-preset", "fast", "-an", output_path], check=True, capture_output=True)
        return True
    except:
        return False

def send_sms(phone, message):
    if "twilio_sid" in st.secrets:
        from twilio.rest import Client
        client = Client(st.secrets["twilio_sid"], st.secrets["twilio_token"])
        client.messages.create(body=message, from_=st.secrets["twilio_from"], to=phone)
        return True
    return False

def moderate_image(image_base64):
    if "sightengine_user" in st.secrets:
        api_user = st.secrets["sightengine_user"]
        api_secret = st.secrets["sightengine_secret"]
        params = {
            'models': 'nudity-2.0,offensive,scam',
            'api_user': api_user,
            'api_secret': api_secret,
        }
        files = {'media': base64.b64decode(image_base64)}
        r = requests.post('https://api.sightengine.com/1.0/check.json', files=files, data=params)
        if r.status_code == 200:
            out = r.json()
            if out.get('nudity', {}).get('safe') is False:
                return False
            if out.get('offensive', {}).get('prob') > 0.9:
                return False
    return True

def generate_contract(announcement, renter_name, owner_name, terms):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Contrat de location Agricole", ln=1, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 10, f"Annonce: {announcement['title']}\nPropriétaire: {owner_name}\nLocataire: {renter_name}\nDurée: {terms['start']} au {terms['end']}\nConditions: {terms['details']}")
    pdf.output("/tmp/contrat.pdf")
    return "/tmp/contrat.pdf"

def display_images(images_str):
    if images_str:
        img_list = images_str.split(";")
        cols = st.columns(min(len(img_list), 3))
        for i, img_b64 in enumerate(img_list[:3]):
            if img_b64:
                cols[i].image(f"data:image/jpeg;base64,{img_b64}", use_column_width=True)

# ---------- Espace publicitaire ----------
def show_ad_space():
    # Bannière publicitaire factice (image placeholder avec lien)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📢 Publicité")
    st.sidebar.image("https://placehold.co/300x150?text=Votre+Pub+Ici", use_column_width=True)
    st.sidebar.markdown("[Visitez notre sponsor](https://example.com)")
    st.sidebar.markdown("---")

# ---------- Pages d'authentification ----------
def login_page():
    st.title(_("login"))
    phone = st.text_input("Téléphone")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        row = query_db("SELECT * FROM users WHERE phone=? AND password=?", (phone, hash_password(password)))
        if row:
            st.session_state.user = dict(row[0])
            st.session_state.page = "home"
            st.rerun()
        else:
            st.error("Identifiants incorrects")

def register_page():
    st.title(_("register"))
    name = st.text_input("Nom complet")
    phone = st.text_input("Téléphone")
    password = st.text_input("Mot de passe", type="password")
    profile = st.selectbox("Profil", ["Agriculteur","Éleveur","Apiculteur","Transporteur","Acheteur","ANEM","Travailleur"])
    wilaya = st.selectbox("Wilaya", list(WILAYAS.keys()))
    commune = st.selectbox("Commune", WILAYAS[wilaya])
    if st.button("S'inscrire"):
        if name and phone and password:
            try:
                query_db("INSERT INTO users (name, phone, password, profile_type, wilaya, commune) VALUES (?,?,?,?,?,?)",
                         (name, phone, hash_password(password), profile, wilaya, commune), fetch=False)
                st.success("Compte créé, connectez-vous.")
            except sqlite3.IntegrityError:
                st.error("Ce numéro est déjà utilisé")
        else:
            st.error("Champs obligatoires")

# ---------- Page d'accueil ----------
def home_page():
    st.title(_("home"))
    if st.session_state.user is not None:
        profile = st.session_state.user['profile_type']
        if profile == 'Agriculteur':
            st.info("Suggestions: Louez vos parcelles après récolte, trouvez des apiculteurs pour pollinisation.")
    annonces = query_db("SELECT a.*, u.name as author FROM announcements a JOIN users u ON a.user_id=u.id ORDER BY a.created_at DESC LIMIT 10")
    if annonces:
        for a in annonces:
            st.markdown(f"**{a['title']}** ({a['type']}) - {a['wilaya']} - {a['price']} {a['unit']} - par {a['author']}")
            if a['images']:
                display_images(a['images'])
            if a['video_base64']:
                st.video(base64.b64decode(a['video_base64']), format="video/mp4")
            elif a['video_url']:
                st.video(a['video_url'])
            st.markdown("---")
    else:
        st.info(_("no_announces"))

# ---------- Module générique avec communes ----------
def generic_announce_page(module_type, fields_config, filters):
    tab1, tab2, tab3 = st.tabs(["📋 " + _("list"), "➕ " + _("publish"), "🗺️ " + _("map")])
    with tab1:
        col_filt = st.columns(len(filters))
        filter_vals = []
        for i, f in enumerate(filters):
            if f == "wilaya":
                val = col_filt[i].selectbox("Wilaya", ["Toutes"] + list(WILAYAS.keys()))
                if val != "Toutes": filter_vals.append(("wilaya", val))
            elif f == "price_max":
                max_price = col_filt[i].number_input("Prix max", min_value=0, step=100)
                if max_price > 0: filter_vals.append(("price", max_price, "<="))
            elif f == "type_produit":
                val = col_filt[i].selectbox("Type", ["Tous", "Légumes", "Fruits", "Céréales", "Bétail", "Miel"])
                if val != "Tous": filter_vals.append(("data->>'product_type'", val))
            elif f == "equipment_type":
                val = col_filt[i].selectbox("Type", ["Tous", "Tracteur", "Moissonneuse", "Charrue", "Remorque", "Irrigation", "Autre"])
                if val != "Tous": filter_vals.append(("data->>'equipment_type'", val))
            elif f == "offer_type":
                val = col_filt[i].selectbox("Offre", ["Tous", "Vente", "Location"])
                if val != "Tous": filter_vals.append(("data->>'offer_type'", val))
        sql = f"SELECT a.*, u.name as author FROM announcements a JOIN users u ON a.user_id=u.id WHERE a.type='{module_type}'"
        params = []
        for fv in filter_vals:
            if len(fv)==2:
                sql += f" AND a.{fv[0]}=?"
                params.append(fv[1])
            else:
                sql += f" AND a.{fv[0]}<=?"
                params.append(fv[1])
        sql += " ORDER BY a.created_at DESC"
        annonces = query_db(sql, tuple(params))
        if annonces:
            for a in annonces:
                col1, col2, col3 = st.columns([3,1,1])
                col1.markdown(f"### {a['title']}")
                col1.write(a['description'])
                col1.write(f"📍 {a['wilaya']} - {a['commune']} | 💰 {a['price']} {a['unit']} | 🕒 {a['created_at']}")
                col1.write(f"👤 {a['author']}")
                if a['images']:
                    display_images(a['images'])
                if a['video_base64']:
                    col1.video(base64.b64decode(a['video_base64']), format="video/mp4")
                elif a['video_url']:
                    col1.video(a['video_url'])
                with col2:
                    if st.button(_("contact"), key=f"msg_{a['id']}"):
                        st.session_state.msg_to = a['user_id']
                        st.session_state.msg_announce = a['id']
                        st.session_state.page = "messages"
                        st.rerun()
                    if st.button(_("evaluate"), key=f"rev_{a['id']}"):
                        st.session_state.review_announce = a['id']
                        st.session_state.page = "reviews"
                        st.rerun()
                with col3:
                    if module_type in ["grazing","pollination","equipment"]:
                        if st.button(_("contract_btn"), key=f"contract_{a['id']}"):
                            st.session_state.contract_announce = a['id']
                            st.session_state.page = "contract"
                            st.rerun()
                st.markdown("---")
        else:
            st.info("Aucune annonce.")
    with tab2:
        with st.form(f"form_{module_type}", clear_on_submit=True):
            st.subheader("Nouvelle annonce")
            title = st.text_input("Titre")
            desc = st.text_area("Description")
            price = st.number_input("Prix", min_value=0.0)
            unit = st.text_input("Unité (ex: DA/kg, DA/jour)")
            wilaya = st.selectbox("Wilaya", list(WILAYAS.keys()))
            commune = st.selectbox("Commune", WILAYAS[wilaya])
            lat = st.number_input("Latitude (optionnel)", value=0.0, step=0.01)
            lon = st.number_input("Longitude (optionnel)", value=0.0, step=0.01)
            extra_data = {}
            for field, label, options in fields_config:
                if options == "text":
                    extra_data[field] = st.text_input(label)
                elif options == "number":
                    extra_data[field] = st.number_input(label, min_value=0)
                elif isinstance(options, list):
                    extra_data[field] = st.selectbox(label, options)
            images = st.file_uploader("Photos (max 5)", type=["jpg","jpeg","png"], accept_multiple_files=True)
            video_file = st.file_uploader("Vidéo (max 10 Mo)", type=["mp4","mov"])
            video_url = st.text_input("Ou lien vidéo (YouTube/Vimeo)")
            submitted = st.form_submit_button(_("publish"))
            if submitted:
                if st.session_state.user is None:
                    st.error("Connectez-vous d'abord")
                else:
                    img_b64_list = []
                    if images:
                        for img in images[:5]:
                            b64 = image_to_base64(img)
                            if b64 and moderate_image(b64):
                                img_b64_list.append(b64)
                            else:
                                st.error("Image rejetée par la modération")
                    img_str = ";".join(img_b64_list)
                    vid_b64 = None
                    if video_file is not None:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
                            tmp.write(video_file.read())
                            tmp_path = tmp.name
                        out_path = tmp_path + "_comp.mp4"
                        compress_video(tmp_path, out_path)
                        with open(out_path, "rb") as f:
                            vid_b64 = base64.b64encode(f.read()).decode()
                    data_json = json.dumps(extra_data)
                    query_db("INSERT INTO announcements (user_id, type, title, description, price, unit, wilaya, commune, lat, lon, data, images, video_base64, video_url) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                             (st.session_state.user['id'], module_type, title, desc, price, unit, wilaya, commune, lat, lon, data_json, img_str, vid_b64, video_url), fetch=False)
                    if st.session_state.user.get('phone'):
                        send_sms(st.session_state.user['phone'], "Votre annonce a été publiée sur AgriConnect!")
                    st.success("Annonce publiée !")
                    st.rerun()
    with tab3:
        st.subheader("Carte des annonces")
        m = folium.Map(location=[28.0339, 1.6596], zoom_start=6)
        annonces_all = query_db(f"SELECT * FROM announcements WHERE type='{module_type}' AND lat != 0 AND lon != 0")
        for a in annonces_all:
            if a['lat'] and a['lon']:
                folium.Marker([a['lat'], a['lon']], popup=a['title']).add_to(m)
        st_folium(m, width=700)

# ---------- Pages spécifiques (inchangées sauf paramètres) ----------
def market_page():
    fields = [
        ("product_type", "Type de produit", ["Légumes","Fruits","Céréales","Bétail","Miel"]),
        ("quantity", "Quantité disponible (kg/têtes)", "number")
    ]
    filters = ["wilaya", "price_max", "type_produit"]
    generic_announce_page("market", fields, filters)

def job_page():
    fields = [
        ("contract_type", "Type de contrat", ["Saisonnier","Permanent","Journalier"]),
        ("skills", "Compétences requises", "text"),
        ("duration", "Durée (jours)", "number")
    ]
    filters = ["wilaya"]
    generic_announce_page("job", fields, filters)

def transport_page():
    fields = [
        ("vehicle_type", "Type de véhicule", ["Camion","Bétaillère","Frigorifique"]),
        ("capacity", "Capacité (tonnes)", "number")
    ]
    filters = ["wilaya"]
    generic_announce_page("transport", fields, filters)

def grazing_page():
    fields = [
        ("area_ha", "Superficie (hectares)", "number"),
        ("cover_type", "Type de couvert", ["Chaume","Jachère","Herbe"]),
        ("water", "Eau disponible", ["Oui","Non"]),
        ("start_date", "Date début (AAAA-MM-JJ)", "text"),
        ("end_date", "Date fin", "text"),
        ("max_animals", "Nombre max d'animaux", "number")
    ]
    filters = ["wilaya"]
    generic_announce_page("grazing", fields, filters)

def pollination_page():
    fields = [
        ("hive_count", "Nombre de ruches", "number"),
        ("bee_race", "Race d'abeille", ["Locale","Hybride"]),
        ("zone", "Zone de déplacement", "text")
    ]
    filters = ["wilaya"]
    generic_announce_page("pollination", fields, filters)

def fertilizer_page():
    fields = [
        ("fertilizer_type", "Type", ["Fumier bovin","Fumier ovin","Fiente volaille","Compost"]),
        ("quantity_tons", "Quantité (tonnes)", "number")
    ]
    filters = ["wilaya"]
    generic_announce_page("fertilizer", fields, filters)

def equipment_page():
    fields = [
        ("offer_type", "Type d'offre", ["Vente", "Location"]),
        ("equipment_type", "Type de matériel", ["Tracteur","Moissonneuse","Charrue","Remorque","Système d'irrigation","Épandeur","Semoir","Autre"]),
        ("brand", "Marque", "text"),
        ("model", "Modèle", "text"),
        ("year", "Année", "number"),
        ("state", "État", ["Neuf","Très bon","Bon","À rénover"]),
        ("rental_period", "Période de location (si location)", ["Heure","Jour","Semaine","Mois"]),
        ("availability", "Disponibilité", "text")
    ]
    filters = ["wilaya", "price_max", "equipment_type", "offer_type"]
    generic_announce_page("equipment", fields, filters)

# ---------- Messagerie, évaluations, contrats, vérification, profil (inchangés) ----------
# (Les fonctions restent les mêmes, juste les conditions d'accès à st.session_state.user modifiées)

def messages_page():
    st.title(_("messages"))
    if st.session_state.user is None:
        st.warning("Connectez-vous")
        return
    # ... (copie conforme du code précédent pour messages_page)
    # On va mettre le code complet pour éviter les erreurs
    if st.session_state.msg_to is not None and st.session_state.msg_to != st.session_state.user['id']:
        other_user = query_db("SELECT name FROM users WHERE id=?", (st.session_state.msg_to,))
        if other_user:
            st.subheader(f"Conversation avec {other_user[0]['name']}")
            msgs = query_db("SELECT * FROM messages WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?) ORDER BY created_at",
                            (st.session_state.user['id'], st.session_state.msg_to, st.session_state.msg_to, st.session_state.user['id']))
            for m in msgs:
                align = "left" if m['sender_id'] == st.session_state.user['id'] else "right"
                st.markdown(f"<div style='text-align:{align};background:#f0f2f6;padding:10px;border-radius:10px;margin:5px'>{m['content']}<br><small>{m['created_at']}</small></div>", unsafe_allow_html=True)
            with st.form("send_msg"):
                msg_text = st.text_area("Message")
                if st.form_submit_button(_("send")):
                    query_db("INSERT INTO messages (sender_id, receiver_id, announcement_id, content) VALUES (?,?,?,?)",
                             (st.session_state.user['id'], st.session_state.msg_to, st.session_state.msg_announce, msg_text), fetch=False)
                    st.rerun()
    else:
        contacts = query_db("SELECT DISTINCT u.id, u.name FROM users u JOIN messages m ON (u.id=m.sender_id OR u.id=m.receiver_id) WHERE (m.sender_id=? OR m.receiver_id=?) AND u.id!=?",
                            (st.session_state.user['id'], st.session_state.user['id'], st.session_state.user['id']))
        contact_dict = {c['name']: c['id'] for c in contacts}
        st.write("Sélectionnez un contact")
        for name, uid in contact_dict.items():
            if st.button(name):
                st.session_state.msg_to = uid
                st.session_state.msg_announce = None
                st.rerun()
        if st.session_state.msg_announce:
            annonce = query_db("SELECT * FROM announcements WHERE id=?", (st.session_state.msg_announce,))
            if annonce:
                st.session_state.msg_to = annonce[0]['user_id']
                st.rerun()

def reviews_page():
    st.title(_("reviews"))
    if st.session_state.user is None:
        st.warning("Connectez-vous")
        return
    if st.session_state.review_announce:
        annonce = query_db("SELECT * FROM announcements WHERE id=?", (st.session_state.review_announce,))
        if annonce:
            st.subheader(f"Évaluer : {annonce[0]['title']}")
            rating = st.slider("Note", 1, 5, 3)
            comment = st.text_area("Commentaire")
            if st.button("Soumettre"):
                query_db("INSERT INTO reviews (announcement_id, reviewer_id, rating, comment) VALUES (?,?,?,?)",
                         (st.session_state.review_announce, st.session_state.user['id'], rating, comment), fetch=False)
                st.success("Merci !")
                st.session_state.review_announce = None
                st.rerun()
    else:
        st.write("Évaluations sur mes annonces")
        my_announces = query_db("SELECT id, title FROM announcements WHERE user_id=?", (st.session_state.user['id'],))
        my_ids = [a['id'] for a in my_announces]
        if my_ids:
            reviews = query_db(f"SELECT r.*, u.name FROM reviews r JOIN users u ON r.reviewer_id=u.id WHERE r.announcement_id IN ({','.join('?'*len(my_ids))}) ORDER BY r.created_at DESC", tuple(my_ids))
            for r in reviews:
                st.write(f"⭐ {r['rating']}/5 - {r['comment']} (par {r['name']})")
        else:
            st.info("Aucune annonce à évaluer.")

def contract_page():
    st.title(_("contract"))
    if st.session_state.user is None:
        st.warning("Connectez-vous")
        return
    if st.session_state.contract_announce:
        annonce = query_db("SELECT * FROM announcements WHERE id=?", (st.session_state.contract_announce,))[0]
        owner = query_db("SELECT * FROM users WHERE id=?", (annonce['user_id'],))[0]
        renter = st.session_state.user
        st.write(f"Annonce: {annonce['title']}")
        st.write(f"Propriétaire: {owner['name']}")
        start = st.date_input("Date début", date.today())
        end = st.date_input("Date fin", date.today())
        terms = st.text_area("Conditions supplémentaires")
        if st.button("Générer et signer"):
            contract_pdf = generate_contract(annonce, renter['name'], owner['name'], {"start": start.isoformat(), "end": end.isoformat(), "details": terms})
            with open(contract_pdf, "rb") as f:
                st.download_button(_("download"), f, file_name="contrat.pdf")
            query_db("INSERT INTO contracts (announcement_id, renter_id, owner_id, start_date, end_date, terms, status) VALUES (?,?,?,?,?,?,?)",
                     (annonce['id'], renter['id'], owner['id'], start.isoformat(), end.isoformat(), terms, "active"), fetch=False)
            st.success("Contrat créé!")

def verification_page():
    st.title(_("verification"))
    if st.session_state.user is None:
        st.warning("Connectez-vous")
        return
    st.write("Téléchargez votre pièce d'identité ou registre de commerce.")
    doc = st.file_uploader("Document", type=["jpg","jpeg","png","pdf"])
    if doc and st.button("Envoyer"):
        if doc.type == "application/pdf":
            doc_b64 = base64.b64encode(doc.read()).decode()
        else:
            doc_b64 = image_to_base64(doc)
        query_db("UPDATE users SET documents=? WHERE id=?", (doc_b64, st.session_state.user['id']), fetch=False)
        st.success("Document soumis pour vérification.")

def profile_page():
    st.title(_("profile"))
    if st.session_state.user is None:
        st.warning("Connectez-vous")
        return
    user = st.session_state.user
    st.write(f"**Nom :** {user['name']}")
    st.write(f"**Téléphone :** {user['phone']}")
    st.write(f"**Profil :** {user['profile_type']}")
    st.write(f"**Wilaya :** {user['wilaya']}")
    st.write(f"**Commune :** {user.get('commune', 'Non spécifiée')}")
    st.write(f"**Vérifié :** {'✅' if user['is_verified'] else '❌'}")
    if st.button("Demander la vérification"):
        query_db("UPDATE users SET is_verified=1 WHERE id=?", (user['id'],), fetch=False)
        st.session_state.user['is_verified'] = 1
        st.success("Vérifié !")

# ---------- Gestion des langues ----------
def setup_language():
    if st.session_state.lang not in ["fr", "ar"]:
        st.session_state.lang = "fr"
    col1, col2 = st.columns([0.9, 0.1])
    with col2:
        lang = st.selectbox("🌐", ["fr", "ar"], index=0 if st.session_state.lang == "fr" else 1, key="lang_selector")
        if lang != st.session_state.lang:
            st.session_state.lang = lang
            st.rerun()

# ---------- Routeur principal ----------
PAGES = {
    "home": home_page,
    "market": market_page,
    "job": job_page,
    "transport": transport_page,
    "grazing": grazing_page,
    "pollination": pollination_page,
    "fertilizer": fertilizer_page,
    "equipment": equipment_page,
    "messages": messages_page,
    "reviews": reviews_page,
    "contract": contract_page,
    "verification": verification_page,
    "profile": profile_page
}

def main():
    init_db()
    setup_language()
    st.sidebar.title(_("app_name"))
    show_ad_space()  # <-- Publicité
    if st.session_state.user is not None:
        st.sidebar.write(f"👤 {st.session_state.user['name']} ({st.session_state.user['profile_type']})")
        nav_items = [
            ("home", _("home")),
            ("market", _("market")),
            ("job", _("job")),
            ("transport", _("transport")),
            ("grazing", _("grazing")),
            ("pollination", _("pollination")),
            ("fertilizer", _("fertilizer")),
            ("equipment", _("equipment")),
            ("messages", _("messages")),
            ("reviews", _("reviews")),
            ("contract", _("contract")),
            ("verification", _("verification")),
            ("profile", _("profile"))
        ]
        for page_key, label in nav_items:
            if st.sidebar.button(label):
                st.session_state.page = page_key
                st.rerun()
        if st.sidebar.button(_("logout")):
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()
    else:
        menu = st.sidebar.radio("", [_("login"), _("register")])
        if menu == _("login"):
            login_page()
        else:
            register_page()

    # Affichage de la page sélectionnée
    if st.session_state.page in PAGES:
        PAGES[st.session_state.page]()
    else:
        st.error("Page inconnue")

if __name__ == "__main__":
    main()
