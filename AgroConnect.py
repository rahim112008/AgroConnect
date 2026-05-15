# app.py – AgriConnect DZ (version intégrale)
import streamlit as st
import sqlite3
import hashlib
import json
import base64
import io
import re
import math
import random
from datetime import datetime, date, timedelta
from PIL import Image

# ── Imports optionnels ────────────────────────────────────────────────────────
try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

try:
    import qrcode
    HAS_QR = True
except ImportError:
    HAS_QR = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ── Config page ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgriConnect DZ",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)
DB_FILE = "agriconnect.db"

# ══════════════════════════════════════════════════════════════════════════════
#  DONNÉES : WILAYAS + CULTURES + PRIX + CALENDRIER
# ══════════════════════════════════════════════════════════════════════════════
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

# Prix de référence marchés algériens (DA/kg) avec historique simulé
MARKET_PRICES = {
    "Pomme de terre": {"base": 45, "unit": "DA/kg", "trend": "stable", "zone": "El Oued / Biskra"},
    "Tomate":         {"base": 60, "unit": "DA/kg", "trend": "hausse", "zone": "Tipaza / Blida"},
    "Oignon":         {"base": 35, "unit": "DA/kg", "trend": "baisse", "zone": "Relizane / Mascara"},
    "Carotte":        {"base": 55, "unit": "DA/kg", "trend": "stable", "zone": "Médéa / Aïn Defla"},
    "Courgette":      {"base": 50, "unit": "DA/kg", "trend": "hausse", "zone": "Tizi Ouzou / Béjaïa"},
    "Pastèque":       {"base": 25, "unit": "DA/kg", "trend": "baisse", "zone": "Adrar / Laghouat"},
    "Datte Deglet":   {"base": 800, "unit": "DA/kg", "trend": "stable", "zone": "Biskra / El Oued"},
    "Blé dur":        {"base": 65, "unit": "DA/kg", "trend": "stable", "zone": "Sétif / Tiaret"},
    "Orge":           {"base": 45, "unit": "DA/kg", "trend": "stable", "zone": "Tiaret / M'Sila"},
    "Lait vache":     {"base": 95, "unit": "DA/litre", "trend": "hausse", "zone": "National"},
    "Miel":           {"base": 3500, "unit": "DA/kg", "trend": "stable", "zone": "Béjaïa / Batna"},
    "Agneau vif":     {"base": 1200, "unit": "DA/kg", "trend": "hausse", "zone": "Djelfa / Laghouat"},
}

# Calendrier cultural par wilaya/zone (mois = 1..12)
CALENDRIER = {
    "Pomme de terre": {
        "zones": {"Nord (Alger, Blida, Tipaza)": {"semis": [1,2,8,9], "recolte": [4,5,11,12], "irrigation": [3,4,5,9,10,11]},
                  "Hauts plateaux (Sétif, Tiaret)": {"semis": [3,4], "recolte": [7,8], "irrigation": [4,5,6,7]},
                  "Sud (Biskra, El Oued)": {"semis": [9,10,11], "recolte": [1,2,3], "irrigation": [10,11,12,1,2]}},
        "conseils": ["Éviter les gelées nocturnes lors de la levée", "Sol bien drainé, pH 5.5–6.5", "Traitement fongique préventif au stade 20cm"],
        "emoji": "🥔"
    },
    "Tomate": {
        "zones": {"Nord (Alger, Blida, Tipaza)": {"semis": [2,3], "recolte": [6,7,8], "irrigation": [4,5,6,7,8]},
                  "Hauts plateaux (Sétif, Tiaret)": {"semis": [4,5], "recolte": [8,9], "irrigation": [5,6,7,8,9]},
                  "Sud (Biskra, El Oued)": {"semis": [9,10], "recolte": [12,1,2], "irrigation": [10,11,12,1,2]}},
        "conseils": ["Tuteurer à partir de 30cm", "Taille des gourmands hebdomadaire", "Fertilisation potassique en phase fructification"],
        "emoji": "🍅"
    },
    "Blé dur": {
        "zones": {"Nord (Alger, Blida, Tipaza)": {"semis": [11,12], "recolte": [6,7], "irrigation": [2,3,4]},
                  "Hauts plateaux (Sétif, Tiaret)": {"semis": [11,12], "recolte": [6,7], "irrigation": [3,4,5]},
                  "Sud (Biskra, El Oued)": {"semis": [10,11], "recolte": [4,5], "irrigation": [11,12,1,2,3]}},
        "conseils": ["Traitement fongicide au stade épi", "Respecter les densités ITGC : 350 grains/m²", "Fertilisation azotée fractionnée en 2 apports"],
        "emoji": "🌾"
    },
    "Oignon": {
        "zones": {"Nord (Alger, Blida, Tipaza)": {"semis": [10,11], "recolte": [5,6], "irrigation": [2,3,4,5]},
                  "Hauts plateaux (Sétif, Tiaret)": {"semis": [3,4], "recolte": [8,9], "irrigation": [5,6,7,8]},
                  "Sud (Biskra, El Oued)": {"semis": [9,10], "recolte": [2,3], "irrigation": [10,11,12,1,2]}},
        "conseils": ["Sécher les bulbes 2 semaines avant stockage", "Densité : 400 000 plants/ha", "Rotation minimale 3 ans pour éviter la fusariose"],
        "emoji": "🧅"
    },
    "Datte": {
        "zones": {"Sud (Biskra, El Oued)": {"semis": [], "recolte": [10,11], "irrigation": [4,5,6,7,8,9]},
                  "Extrême-Sud (Adrar, Tamanrasset)": {"semis": [], "recolte": [9,10,11], "irrigation": [3,4,5,6,7,8,9]}},
        "conseils": ["Pollinisation manuelle en mars–avril", "Ensacher les régimes en août", "Récolte progressive selon maturité des variétés"],
        "emoji": "🌴"
    },
}

MOIS = ["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"]

# Données météo simulées par wilaya (pour alertes et calendrier)
METEO_WILAYAS = {
    "07 - Biskra": {"zone": "Sud", "precip_mm": 130, "t_min_jan": 5, "t_max_jul": 44, "gel_risque": "Faible"},
    "39 - El Oued": {"zone": "Sud", "precip_mm": 70, "t_min_jan": 3, "t_max_jul": 46, "gel_risque": "Faible"},
    "19 - Sétif": {"zone": "Hauts plateaux", "precip_mm": 420, "t_min_jan": -2, "t_max_jul": 32, "gel_risque": "Modéré"},
    "14 - Tiaret": {"zone": "Hauts plateaux", "precip_mm": 350, "t_min_jan": -3, "t_max_jul": 35, "gel_risque": "Modéré"},
    "16 - Alger": {"zone": "Nord", "precip_mm": 680, "t_min_jan": 8, "t_max_jul": 30, "gel_risque": "Très faible"},
    "31 - Oran": {"zone": "Nord", "precip_mm": 380, "t_min_jan": 7, "t_max_jul": 31, "gel_risque": "Très faible"},
    "06 - Béjaïa": {"zone": "Nord", "precip_mm": 820, "t_min_jan": 6, "t_max_jul": 28, "gel_risque": "Très faible"},
    "09 - Blida": {"zone": "Nord", "precip_mm": 720, "t_min_jan": 7, "t_max_jul": 32, "gel_risque": "Très faible"},
    "17 - Djelfa": {"zone": "Hauts plateaux", "precip_mm": 300, "t_min_jan": -5, "t_max_jul": 36, "gel_risque": "Élevé"},
}

# ══════════════════════════════════════════════════════════════════════════════
#  TRADUCTIONS
# ══════════════════════════════════════════════════════════════════════════════
LANGUAGES = {
    "fr": {
        "app_name": "AgriConnect", "login": "Connexion", "register": "Inscription",
        "logout": "Déconnexion", "home": "Accueil", "market": "Marché",
        "job": "Emploi", "transport": "Transport", "grazing": "Pâturage",
        "pollination": "Pollinisation", "fertilizer": "Engrais",
        "equipment": "Matériel", "anem": "ANEM", "messages": "Messages",
        "reviews": "Évaluations", "contract": "Contrat", "verification": "Vérification",
        "profile": "Profil", "no_announces": "Aucune annonce pour le moment.",
        "publish": "Publier", "list": "Annonces", "map": "Carte",
        "contact": "Contacter", "evaluate": "Évaluer", "contract_btn": "Contrat",
        "send": "Envoyer", "download": "Télécharger", "my_offers": "Dernières annonces",
        "search": "Rechercher", "wilaya": "Wilaya", "commune": "Commune",
        "fill_required": "Veuillez remplir tous les champs obligatoires.",
        "login_required": "Veuillez vous connecter d'abord.",
        "published": "Annonce publiée avec succès !",
        "account_created": "Compte créé. Connectez-vous.",
        "phone_used": "Ce numéro est déjà utilisé.",
        "bad_credentials": "Identifiants incorrects.",
        "validated": "Profil validé.",
        "pending_none": "Aucun profil en attente.",
        "no_convo": "Aucune conversation.",
        "rating_sent": "Évaluation soumise, merci !",
        "contract_created": "Contrat enregistré.",
        "doc_sent": "Document soumis pour vérification.",
        "page": "Page", "next": "Suivant →", "prev": "← Précédent",
        "assistant_ia": "Assistant IA", "prix_marche": "Prix Marchés",
        "alertes": "🚨 Urgences", "tracabilite": "Traçabilité QR",
        "calendrier": "Calendrier", "surplus_title": "Vente urgente / Surplus",
    },
    "ar": {
        "app_name": "أجريكونكت", "login": "تسجيل الدخول", "register": "التسجيل",
        "logout": "تسجيل الخروج", "home": "الرئيسية", "market": "السوق",
        "job": "وظائف", "transport": "النقل", "grazing": "الرعي",
        "pollination": "التلقيح", "fertilizer": "الأسمدة",
        "equipment": "المعدات", "anem": "الوكالة الوطنية للتشغيل",
        "messages": "الرسائل", "reviews": "التقييمات", "contract": "عقد",
        "verification": "التحقق", "profile": "ملفي",
        "no_announces": "لا توجد إعلانات", "publish": "نشر",
        "list": "قائمة", "map": "خريطة", "contact": "اتصال",
        "evaluate": "تقييم", "contract_btn": "عقد", "send": "إرسال",
        "download": "تحميل", "my_offers": "آخر الإعلانات",
        "search": "بحث", "wilaya": "ولاية", "commune": "بلدية",
        "fill_required": "الرجاء ملء جميع الحقول.", "login_required": "سجل دخولك أولاً.",
        "published": "تم نشر الإعلان!", "account_created": "تم إنشاء الحساب.",
        "phone_used": "الرقم مستخدم.", "bad_credentials": "بيانات خاطئة.",
        "validated": "تم التحقق.", "pending_none": "لا توجد ملفات.",
        "no_convo": "لا محادثات.", "rating_sent": "شكراً على التقييم.",
        "contract_created": "تم إنشاء العقد.", "doc_sent": "تم إرسال المستند.",
        "page": "صفحة", "next": "التالي →", "prev": "← السابق",
        "assistant_ia": "المساعد الذكي", "prix_marche": "أسعار الأسواق",
        "alertes": "🚨 طوارئ", "tracabilite": "رمز QR",
        "calendrier": "التقويم الزراعي", "surplus_title": "بيع عاجل / فائض",
    },
    "en": {
        "app_name": "AgriConnect", "login": "Login", "register": "Register",
        "logout": "Logout", "home": "Home", "market": "Marketplace",
        "job": "Jobs", "transport": "Transport", "grazing": "Grazing",
        "pollination": "Pollination", "fertilizer": "Fertilizer",
        "equipment": "Equipment", "anem": "ANEM", "messages": "Messages",
        "reviews": "Reviews", "contract": "Contract", "verification": "Verification",
        "profile": "Profile", "no_announces": "No announcements yet.",
        "publish": "Publish", "list": "List", "map": "Map",
        "contact": "Contact", "evaluate": "Rate", "contract_btn": "Contract",
        "send": "Send", "download": "Download", "my_offers": "Latest Listings",
        "search": "Search", "wilaya": "Wilaya", "commune": "Commune",
        "fill_required": "Please fill all required fields.",
        "login_required": "Please log in first.",
        "published": "Announcement published!",
        "account_created": "Account created. Please log in.",
        "phone_used": "Phone number already in use.",
        "bad_credentials": "Incorrect credentials.",
        "validated": "Profile validated.", "pending_none": "No pending profiles.",
        "no_convo": "No conversations.", "rating_sent": "Rating submitted!",
        "contract_created": "Contract created.", "doc_sent": "Document submitted.",
        "page": "Page", "next": "Next →", "prev": "← Previous",
        "assistant_ia": "AI Assistant", "prix_marche": "Market Prices",
        "alertes": "🚨 Urgent", "tracabilite": "QR Traceability",
        "calendrier": "Crop Calendar", "surplus_title": "Urgent sale / Surplus",
    },
}

def _(key):
    lang = st.session_state.get("lang", "fr")
    return LANGUAGES.get(lang, LANGUAGES["fr"]).get(key, key)

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
DEFAULTS = {
    "user": None, "page": "home", "lang": "fr",
    "msg_to": None, "msg_announce": None,
    "review_announce": None, "contract_announce": None,
    "search_query": "", "db_initialized": False,
    "ai_messages": [],  # Pour l'assistant IA
    "surplus_notifs": [],  # File de notifications urgence
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
#  CSS  — Thème terroir algérien
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

:root {
    --olive:      #3d5a2e;
    --olive-mid:  #5a7d3f;
    --olive-pale: #eef4e8;
    --sand:       #f5f0e8;
    --sand-dark:  #e8dfc8;
    --terracotta: #c0522a;
    --terra-pale: #fdf0ea;
    --sky:        #2a6496;
    --sky-pale:   #e8f2f9;
    --text:       #1c1c1c;
    --muted:      #6b7060;
    --border:     #ddd8cc;
    --radius:     14px;
    --shadow-sm:  0 1px 6px rgba(0,0,0,0.06);
    --shadow-md:  0 4px 18px rgba(0,0,0,0.09);
}

* { font-family: 'DM Sans', sans-serif; box-sizing: border-box; }

.main > .block-container { background: var(--sand); border-radius: 0; max-width: 1200px; }

.hero {
    background: linear-gradient(135deg, var(--olive) 0%, var(--olive-mid) 60%, #7a9e52 100%);
    color: white;
    padding: 2.2rem 2rem 1.8rem;
    border-radius: var(--radius);
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: "🌾";
    position: absolute; right: 2rem; top: 1rem;
    font-size: 5rem; opacity: 0.15;
}
.hero h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem; font-weight: 400;
    margin: 0 0 0.3rem; line-height: 1.15;
}
.hero p { margin: 0; opacity: 0.82; font-size: 1rem; font-weight: 300; }

.card {
    background: white;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
    margin-bottom: 1rem;
}
.card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); }
.card-img { height: 160px; width: 100%; object-fit: cover; background: var(--olive-pale); display: flex; align-items: center; justify-content: center; font-size: 3rem; }
.card-body { padding: 14px 16px; }
.card-title { font-size: 0.97rem; font-weight: 500; color: var(--text); margin-bottom: 3px; }
.card-desc { color: var(--muted); font-size: 0.82rem; margin-bottom: 8px; }
.card-price { font-size: 1.1rem; font-weight: 500; color: var(--olive); }
.card-loc { color: var(--muted); font-size: 0.76rem; margin-top: 3px; }

.badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.71rem; font-weight: 500; }
.badge-green { background: var(--olive-pale); color: var(--olive); }
.badge-orange { background: var(--terra-pale); color: var(--terracotta); }
.badge-blue { background: var(--sky-pale); color: var(--sky); }
.badge-urgent { background: #fde8e8; color: #9b1c1c; animation: pulse-border 1.5s infinite; }

@keyframes pulse-border {
    0%,100% { box-shadow: 0 0 0 0 rgba(155,28,28,0.35); }
    50%      { box-shadow: 0 0 0 5px rgba(155,28,28,0); }
}

.stat-card {
    background: white; border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.1rem;
    text-align: center; box-shadow: var(--shadow-sm);
}
.stat-card .num { font-family: 'DM Serif Display', serif; font-size: 2rem; color: var(--olive); }
.stat-card .lbl { color: var(--muted); font-size: 0.78rem; margin-top: 1px; }

.prix-card {
    background: white; border: 1px solid var(--border);
    border-radius: 10px; padding: 12px 16px;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 8px; transition: background 0.15s;
}
.prix-card:hover { background: var(--olive-pale); }
.prix-nom { font-weight: 500; font-size: 0.92rem; color: var(--text); }
.prix-zone { font-size: 0.74rem; color: var(--muted); margin-top: 1px; }
.prix-val { font-family: 'DM Serif Display', serif; font-size: 1.3rem; color: var(--olive); }
.prix-unit { font-size: 0.72rem; color: var(--muted); }
.trend-up   { color: #c0522a; font-size: 0.75rem; font-weight: 500; }
.trend-down { color: var(--sky); font-size: 0.75rem; font-weight: 500; }
.trend-eq   { color: var(--muted); font-size: 0.75rem; }

.cal-grid {
    display: grid; grid-template-columns: 110px repeat(12, 1fr);
    gap: 3px; font-size: 0.73rem;
}
.cal-header { font-weight: 500; color: var(--muted); text-align: center; padding: 4px 0; }
.cal-label { font-weight: 500; color: var(--text); padding: 5px 6px; font-size: 0.8rem; }
.cal-cell { height: 22px; border-radius: 4px; }
.cal-semis { background: #c8e6c9; }
.cal-recolte { background: var(--olive); opacity: 0.85; }
.cal-irrigation { background: #bbdefb; }
.cal-nothing { background: var(--sand-dark); opacity: 0.5; }

.ai-bubble-user {
    background: var(--olive-pale); color: var(--text);
    padding: 10px 14px; border-radius: 18px 18px 4px 18px;
    max-width: 78%; margin-left: auto; margin-bottom: 10px; font-size: 0.9rem;
}
.ai-bubble-bot {
    background: white; border: 1px solid var(--border); color: var(--text);
    padding: 10px 14px; border-radius: 18px 18px 18px 4px;
    max-width: 85%; margin-right: auto; margin-bottom: 10px; font-size: 0.9rem;
    line-height: 1.65;
}
.ai-time { font-size: 0.68rem; color: var(--muted); margin-top: 3px; }

.alerte-banner {
    background: linear-gradient(90deg, #9b1c1c, #c0522a);
    color: white; padding: 12px 18px; border-radius: 10px;
    margin-bottom: 1rem; font-weight: 500;
    display: flex; align-items: center; gap: 10px;
}
.alerte-card {
    background: #fff5f5; border: 1px solid #fca5a5;
    border-left: 4px solid #ef4444;
    border-radius: 10px; padding: 14px 16px; margin-bottom: 10px;
}
.alerte-card .titre { font-weight: 500; color: #7f1d1d; font-size: 0.95rem; }
.alerte-card .meta { font-size: 0.78rem; color: #9b1c1c; margin-top: 3px; }

.qr-card {
    background: white; border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.5rem;
    text-align: center; box-shadow: var(--shadow-sm);
}
.qr-info {
    background: var(--olive-pale); border-radius: 10px; padding: 14px; text-align: left; margin-top: 1rem;
}
.qr-info table { width: 100%; font-size: 0.85rem; }
.qr-info td { padding: 4px 6px; color: var(--muted); }
.qr-info td:first-child { font-weight: 500; color: var(--text); width: 130px; }

.msg-me {
    background: var(--olive-pale); padding: 9px 13px; border-radius: 16px 16px 3px 16px;
    max-width: 75%; margin-left: auto; margin-bottom: 7px; font-size: 0.88rem;
}
.msg-other {
    background: white; border: 1px solid var(--border); padding: 9px 13px;
    border-radius: 16px 16px 16px 3px; max-width: 75%; margin-right: auto; margin-bottom: 7px; font-size: 0.88rem;
}
.msg-t { font-size: 0.67rem; color: var(--muted); margin-top: 2px; }

.no-ann {
    background: var(--olive-pale); border: 1px dashed #a5c882;
    border-radius: var(--radius); padding: 3rem; text-align: center; color: var(--muted); font-size: 1rem;
}
.footer { text-align: center; padding: 1.5rem; color: var(--muted); border-top: 1px solid var(--border); margin-top: 2.5rem; font-size: 0.8rem; }
.btn-urgence { background: #ef4444 !important; color: white !important; border: none !important; font-weight: 500 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  BASE DE DONNÉES
# ══════════════════════════════════════════════════════════════════════════════
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, phone TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
        profile_type TEXT, is_verified INTEGER DEFAULT 0,
        wilaya TEXT, commune TEXT,
        location_lat REAL DEFAULT 0, location_lon REAL DEFAULT 0,
        documents TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL, type TEXT NOT NULL,
        title TEXT NOT NULL, description TEXT,
        price REAL DEFAULT 0, unit TEXT,
        wilaya TEXT, commune TEXT,
        lat REAL DEFAULT 0, lon REAL DEFAULT 0,
        data TEXT DEFAULT '{}', images TEXT DEFAULT '',
        is_urgent INTEGER DEFAULT 0,
        urgent_qty TEXT DEFAULT '',
        urgent_expires TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL, receiver_id INTEGER NOT NULL,
        announcement_id INTEGER, content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        announcement_id INTEGER NOT NULL, reviewer_id INTEGER NOT NULL,
        rating INTEGER CHECK(rating BETWEEN 1 AND 5), comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        announcement_id INTEGER NOT NULL,
        renter_id INTEGER NOT NULL, owner_id INTEGER NOT NULL,
        start_date TEXT, end_date TEXT, terms TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS ai_conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL, role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        users = [
            ("Agent ANEM", "0555000001", hash_pw("anem123"), "ANEM", 1, "16 - Alger", "Alger Centre"),
            ("Ali Ferme", "0555123456", hash_pw("123456"), "Agriculteur", 1, "39 - El Oued", "Guemar"),
            ("Fatima Transport", "0555654321", hash_pw("123456"), "Transporteur", 1, "31 - Oran", "Es Sénia"),
            ("Karim Apiculture", "0555111222", hash_pw("123456"), "Apiculteur", 1, "06 - Béjaïa", "Akbou"),
        ]
        c.executemany("INSERT INTO users (name,phone,password,profile_type,is_verified,wilaya,commune) VALUES (?,?,?,?,?,?,?)", users)
        u1 = c.execute("SELECT id FROM users WHERE phone='0555123456'").fetchone()[0]
        u2 = c.execute("SELECT id FROM users WHERE phone='0555654321'").fetchone()[0]
        u3 = c.execute("SELECT id FROM users WHERE phone='0555111222'").fetchone()[0]
        anns = [
            (u1,"market","Pommes de terre fraîches","Variété Spunta, 10 tonnes",45,"DA/kg","39 - El Oued","Guemar",'{"product_type":"Légumes","quantity":10000}',0),
            (u1,"grazing","Chaumes de blé à louer","50 ha, eau disponible mai–juillet",200,"DA/tête/jour","14 - Tiaret","Sougueur",'{"area_ha":50,"cover_type":"Chaume","water":"Oui","max_animals":100}',0),
            (u1,"fertilizer","Fumier ovin composté","5 tonnes qualité supérieure",3000,"DA/tonne","17 - Djelfa","Messaâd",'{"fertilizer_type":"Fumier ovin","quantity_tons":5}',0),
            (u2,"transport","Camion frigorifique Alger–Médéa","Capacité 10 t, départ chaque semaine",8000,"DA/voyage","16 - Alger","El Harrach",'{"vehicle_type":"Frigorifique","capacity":10}',0),
            (u3,"pollination","20 ruches disponibles","Race locale, zone Béjaïa–Batna",5000,"DA/ruche/sem","06 - Béjaïa","Akbou",'{"hive_count":20,"bee_race":"Locale","zone":"Béjaïa-Batna"}',0),
            (u2,"equipment","Tracteur Massey Ferguson 2020","Bon état, location journalière",5000,"DA/jour","31 - Oran","Es Sénia",'{"offer_type":"Location","equipment_type":"Tracteur","brand":"MF","year":2020}',0),
            (u1,"market","🚨 URGENT — Tomates cerises surplus","3 tonnes à écouler avant vendredi !",30,"DA/kg","39 - El Oued","Robbah",'{"product_type":"Légumes","quantity":3000}',1),
        ]
        c.executemany("INSERT INTO announcements (user_id,type,title,description,price,unit,wilaya,commune,data,is_urgent) VALUES (?,?,?,?,?,?,?,?,?,?)", anns)

    conn.commit()
    conn.close()

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def qdb(sql, params=(), fetch=True):
    conn = get_conn()
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

def validate_phone(p): return bool(re.match(r'^0[5-7]\d{8}$', p.strip()))

def img_to_b64(f, maxsz=(800,600)):
    if not f: return None
    try:
        f.seek(0)
        im = Image.open(f).convert("RGB")
        im.thumbnail(maxsz, Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=65, optimize=True)
        return base64.b64encode(buf.getvalue()).decode()
    except:
        return None

MODULE_ICONS = {"market":"🥕","job":"👷","transport":"🚛","grazing":"🐑",
                "pollination":"🐝","fertilizer":"🌱","equipment":"🚜"}

# ══════════════════════════════════════════════════════════════════════════════
#  NAVBAR
# ══════════════════════════════════════════════════════════════════════════════
def render_navbar():
    items = [
        ("home","🏠"),("market","🛒"),("job","👷"),("transport","🚛"),
        ("grazing","🐑"),("pollination","🐝"),("fertilizer","🌱"),
        ("equipment","🚜"),("alertes","🚨"),("prix_marche","📊"),
        ("assistant_ia","🤖"),("calendrier","📅"),("tracabilite","📱"),
        ("messages","💬"),("profile","👤"),
    ]
    if st.session_state.user and st.session_state.user.get("profile_type") == "ANEM":
        items.insert(2, ("anem","🏛️"))
    cols = st.columns(len(items))
    for i, (page, icon) in enumerate(items):
        with cols[i]:
            label = icon
            btn_type = "primary" if st.session_state.page == page else "secondary"
            if st.button(label, key=f"nav_{page}", use_container_width=True,
                         type=btn_type, help=_(page)):
                st.session_state.page = page
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  RENDER CARD
# ══════════════════════════════════════════════════════════════════════════════
def render_card(a):
    icon = MODULE_ICONS.get(a["type"], "📌")
    if a["images"]:
        img_html = f'<img src="data:image/jpeg;base64,{a["images"].split(";")[0]}" style="height:160px;width:100%;object-fit:cover;">'
    else:
        img_html = f'<div class="card-img">{icon}</div>'

    urgent_badge = '<span class="badge badge-urgent">🚨 URGENT</span>' if a["is_urgent"] else ''
    desc = (a["description"] or "")[:75] + ("…" if len(a["description"] or "") > 75 else "")

    st.markdown(f"""
    <div class="card">
        {img_html}
        <div class="card-body">
            <span class="badge badge-green">{a['type'].upper()}</span> {urgent_badge}
            <div class="card-title" style="margin-top:6px;">{a['title']}</div>
            <div class="card-desc">{desc}</div>
            <div class="card-price">{a['price']:,.0f} {a['unit'] or ''}</div>
            <div class="card-loc">📍 {a['wilaya']} — {a['commune']}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button(_("contact"), key=f"c_{a['id']}", use_container_width=True):
            st.session_state.msg_to = a["user_id"]
            st.session_state.msg_announce = a["id"]
            st.session_state.page = "messages"; st.rerun()
    with c2:
        if st.button(_("evaluate"), key=f"e_{a['id']}", use_container_width=True):
            st.session_state.review_announce = a["id"]
            st.session_state.page = "reviews"; st.rerun()
    with c3:
        if a["type"] in ("grazing","pollination","equipment"):
            if st.button(_("contract_btn"), key=f"k_{a['id']}", use_container_width=True):
                st.session_state.contract_announce = a["id"]
                st.session_state.page = "contract"; st.rerun()
        elif a["is_urgent"]:
            if st.button("📱 QR", key=f"q_{a['id']}", use_container_width=True):
                st.session_state.qr_ann_id = a["id"]
                st.session_state.page = "tracabilite"; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════════════════════
def login_page():
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown("### 🔐 " + _("login"))
        phone = st.text_input("📱 Téléphone", key="login_phone")
        pwd   = st.text_input("🔑 Mot de passe", type="password", key="login_pwd")
        if st.button(_("login"), key="login_btn", use_container_width=True, type="primary"):
            rows = qdb("SELECT * FROM users WHERE phone=? AND password=?",
                       (phone.strip(), hash_pw(pwd)))
            if rows:
                st.session_state.user = dict(rows[0])
                st.session_state.page = "home"; st.rerun()
            else:
                st.error(_("bad_credentials"))
        st.markdown("---")
        if st.button(_("register"), key="goto_reg", use_container_width=True):
            st.session_state.page = "register"; st.rerun()

def register_page():
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown("### 📝 " + _("register"))
        name    = st.text_input("Nom complet *", key="reg_name")
        phone   = st.text_input("Téléphone * (0555xxxxxxx)", key="reg_phone")
        pwd     = st.text_input("Mot de passe * (min. 6 car.)", type="password", key="reg_pwd")
        pwd2    = st.text_input("Confirmer *", type="password", key="reg_pwd2")
        profile = st.selectbox("Profil *", ["Agriculteur","Éleveur","Apiculteur","Transporteur","Acheteur","ANEM","Travailleur"], key="reg_profile")
        wilaya  = st.selectbox(_("wilaya") + " *", list(WILAYAS.keys()), key="reg_wilaya")
        commune = st.selectbox(_("commune") + " *", WILAYAS[wilaya], key="reg_commune")
        if st.button("S'inscrire", key="reg_submit", use_container_width=True, type="primary"):
            errs = []
            if not name.strip(): errs.append("Nom requis.")
            if not validate_phone(phone): errs.append("Numéro invalide.")
            if len(pwd) < 6: errs.append("Mot de passe trop court.")
            if pwd != pwd2: errs.append("Mots de passe différents.")
            for e in errs: st.error(e)
            if not errs:
                try:
                    qdb("INSERT INTO users (name,phone,password,profile_type,wilaya,commune) VALUES (?,?,?,?,?,?)",
                        (name.strip(), phone.strip(), hash_pw(pwd), profile, wilaya, commune), fetch=False)
                    st.success(_("account_created"))
                    st.session_state.page = "login"; st.rerun()
                except sqlite3.IntegrityError:
                    st.error(_("phone_used"))

# ══════════════════════════════════════════════════════════════════════════════
#  HOME
# ══════════════════════════════════════════════════════════════════════════════
def home_page():
    st.markdown("""
    <div class="hero">
        <h1>AgriConnect DZ</h1>
        <p>Le carrefour numérique de l'agriculture algérienne — 58 wilayas, un seul réseau</p>
    </div>""", unsafe_allow_html=True)

    urgents = qdb("SELECT a.*,u.name as author FROM announcements a JOIN users u ON a.user_id=u.id WHERE a.is_urgent=1 ORDER BY a.created_at DESC LIMIT 3")
    if urgents:
        st.markdown(f'<div class="alerte-banner">🚨 {len(urgents)} vente(s) urgente(s) en cours — cliquez pour voir</div>', unsafe_allow_html=True)

    t = qdb("SELECT COUNT(*) as n FROM announcements")[0]["n"]
    u = qdb("SELECT COUNT(*) as n FROM users")[0]["n"]
    w = qdb("SELECT COUNT(DISTINCT wilaya) as n FROM announcements")[0]["n"]
    urgent_cnt = qdb("SELECT COUNT(*) as n FROM announcements WHERE is_urgent=1")[0]["n"]
    c1,c2,c3,c4 = st.columns(4)
    for col, num, lbl in [(c1,t,"Annonces"),(c2,u,"Agriculteurs"),(c3,w,"Wilayas"),(c4,urgent_cnt,"🚨 Urgences")]:
        col.markdown(f'<div class="stat-card"><div class="num">{num}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    cs, cw, cb = st.columns([3,2,1])
    with cs: search = st.text_input(_("search"), placeholder="Ex: pommes de terre, tracteur...", label_visibility="collapsed", value=st.session_state.search_query, key="home_search")
    with cw: wf = st.selectbox(_("wilaya"), ["Toutes"]+list(WILAYAS.keys()), key="home_wilaya", label_visibility="collapsed")
    with cb:
        if st.button(_("search"), key="home_search_btn", use_container_width=True, type="primary"):
            st.session_state.search_query = search

    sql = "SELECT a.*,u.name as author FROM announcements a JOIN users u ON a.user_id=u.id WHERE 1=1"
    params = []
    if search:
        sql += " AND (a.title LIKE ? OR a.description LIKE ?)"; params += [f"%{search}%"]*2
    if wf != "Toutes":
        sql += " AND a.wilaya=?"; params.append(wf)
    sql += " ORDER BY a.is_urgent DESC, a.created_at DESC LIMIT 12"
    anns = qdb(sql, tuple(params))

    st.markdown(f"### 📌 {_('my_offers')} ({len(anns)})")
    if anns:
        for i in range(0, len(anns), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(anns):
                    with cols[j]: render_card(anns[i+j])
    else:
        st.markdown(f'<div class="no-ann">🌿 {_("no_announces")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PAGES GÉNÉRIQUES MODULES
# ══════════════════════════════════════════════════════════════════════════════
PAGE_SIZE = 6

def generic_page(mtype, fields_cfg, filters):
    tab1, tab2, tab3 = st.tabs([f"📋 {_('list')}", f"➕ {_('publish')}", f"🗺️ {_('map')}"])

    with tab1:
        fc = st.columns(max(len(filters),1))
        wclauses = ["a.type=?"]; params = [mtype]
        _json_filters = {}

        for i, f in enumerate(filters):
            with fc[i % len(fc)]:
                if f == "wilaya":
                    v = st.selectbox(_("wilaya"), ["Toutes"]+list(WILAYAS.keys()), key=f"fw_{mtype}")
                    if v != "Toutes": wclauses.append("a.wilaya=?"); params.append(v)
                elif f == "price_max":
                    v = st.number_input("Prix max (DA)", min_value=0, step=500, key=f"fp_{mtype}")
                    if v > 0: wclauses.append("a.price<=?"); params.append(v)
                elif f == "type_produit":
                    v = st.selectbox("Type produit", ["Tous","Légumes","Fruits","Céréales","Bétail","Miel","Lait","Autre"], key=f"ft_{mtype}")
                    if v != "Tous": _json_filters["product_type"] = v
                elif f == "equipment_type":
                    v = st.selectbox("Type matériel", ["Tous","Tracteur","Moissonneuse","Charrue","Remorque","Irrigation","Autre"], key=f"fe_{mtype}")
                    if v != "Tous": _json_filters["equipment_type"] = v
                elif f == "offer_type":
                    v = st.selectbox("Offre", ["Tous","Vente","Location"], key=f"fo_{mtype}")
                    if v != "Tous": _json_filters["offer_type"] = v

        sql = f"SELECT a.*,u.name as author FROM announcements a JOIN users u ON a.user_id=u.id WHERE {' AND '.join(wclauses)} ORDER BY a.is_urgent DESC, a.created_at DESC"
        anns = qdb(sql, tuple(params))

        def jf(a):
            try:
                d = json.loads(a["data"] or "{}")
                return all(d.get(k,"").lower()==v.lower() for k,v in _json_filters.items())
            except: return True

        anns = [a for a in anns if jf(a)]
        total = len(anns)
        pk = f"_p_{mtype}"
        if pk not in st.session_state: st.session_state[pk] = 0
        pg = min(st.session_state[pk], max(0,(total-1)//PAGE_SIZE))
        tp = max(1,(total+PAGE_SIZE-1)//PAGE_SIZE)
        paged = anns[pg*PAGE_SIZE:(pg+1)*PAGE_SIZE]

        if paged:
            for i in range(0, len(paged), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i+j < len(paged):
                        with cols[j]: render_card(paged[i+j])
        else:
            st.markdown(f'<div class="no-ann">🌿 {_("no_announces")}</div>', unsafe_allow_html=True)

        p1,p2,p3 = st.columns([1,2,1])
        with p1:
            if pg > 0 and st.button(_("prev"), key=f"prev_{mtype}"):
                st.session_state[pk] = pg-1; st.rerun()
        with p2:
            st.caption(f"{_('page')} {pg+1}/{tp} ({total} résultats)")
        with p3:
            if pg < tp-1 and st.button(_("next"), key=f"next_{mtype}"):
                st.session_state[pk] = pg+1; st.rerun()

    with tab2:
        if not st.session_state.user:
            st.warning(_("login_required")); return

        is_urgent = st.checkbox("🚨 Marquer comme VENTE URGENTE (alerte géolocalisée)", key=f"urg_{mtype}")
        if is_urgent:
            st.info("⚡ Cette annonce sera mise en avant et notifiera les acheteurs proches.")

        with st.form(f"f_{mtype}", clear_on_submit=True):
            c1,c2 = st.columns(2)
            title = c1.text_input("Titre *", key=f"title_{mtype}")
            unit  = c2.text_input("Unité (DA/kg, DA/jour…)", key=f"unit_{mtype}")
            desc  = st.text_area("Description", key=f"desc_{mtype}")
            c3,c4 = st.columns(2)
            price  = c3.number_input("Prix (DA) *", min_value=0.0, step=100.0, key=f"price_{mtype}")
            wilaya = c4.selectbox(_("wilaya"), list(WILAYAS.keys()), key=f"wilaya_{mtype}")
            commune= st.selectbox(_("commune"), WILAYAS[wilaya], key=f"commune_{mtype}")
            extra = {}
            if fields_cfg:
                st.markdown("**Détails**")
                fc2 = st.columns(min(len(fields_cfg),2))
                for idx,(field,label,opts) in enumerate(fields_cfg):
                    with fc2[idx%2]:
                        if opts=="text":    extra[field]=st.text_input(label, key=f"f_{mtype}_{field}")
                        elif opts=="number":extra[field]=st.number_input(label, min_value=0, key=f"f_{mtype}_{field}")
                        elif isinstance(opts,list): extra[field]=st.selectbox(label, opts, key=f"f_{mtype}_{field}")
            imgs = st.file_uploader("📷 Photos (max 5)", type=["jpg","jpeg","png"], accept_multiple_files=True, key=f"imgs_{mtype}")
            ok = st.form_submit_button(_("publish"), use_container_width=True, type="primary")

        if ok:
            if not title.strip(): st.error(_("fill_required"))
            else:
                b64s = [b for b in [img_to_b64(im) for im in (imgs or [])[:5]] if b]
                qdb("INSERT INTO announcements (user_id,type,title,description,price,unit,wilaya,commune,data,images,is_urgent) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (st.session_state.user["id"], mtype, title.strip(), desc, price, unit,
                     wilaya, commune, json.dumps(extra), ";".join(b64s), 1 if is_urgent else 0), fetch=False)
                st.success(_("published"))
                if is_urgent: st.balloons()
                st.rerun()

    with tab3:
        if not HAS_FOLIUM:
            st.info("Installez `streamlit-folium` pour la carte.")
        else:
            m = folium.Map(location=[28.0,1.66], zoom_start=5)
            anns2 = qdb(f"SELECT * FROM announcements WHERE type=? AND lat!=0 AND lon!=0", (mtype,))
            for a in anns2:
                if a["lat"] and a["lon"]:
                    col = "red" if a["is_urgent"] else "green"
                    folium.Marker([a["lat"],a["lon"]], popup=f"{a['title']}\n{a['price']} {a['unit']}",
                                  icon=folium.Icon(color=col, icon="leaf")).add_to(m)
            st_folium(m, width=700, height=450, key=f"map_{mtype}")


def market_page():
    st.markdown("### 🥕 " + _("market"))
    generic_page("market",[("product_type","Type",["Légumes","Fruits","Céréales","Bétail","Miel","Lait","Autre"]),("quantity","Quantité (kg/t)","number")],["wilaya","price_max","type_produit"])

def job_page():
    st.markdown("### 👷 " + _("job"))
    generic_page("job",[("contract_type","Type",["Saisonnier","Permanent","Journalier"]),("skills","Compétences","text"),("duration","Durée (j)","number"),("salary","Salaire DA/j","number")],["wilaya","price_max"])

def transport_page():
    st.markdown("### 🚛 " + _("transport"))
    generic_page("transport",[("vehicle_type","Véhicule",["Camion","Bétaillère","Frigorifique","Pickup","Semi"]),("capacity","Capacité (t)","number"),("route","Trajet","text")],["wilaya","price_max"])

def grazing_page():
    st.markdown("### 🐑 " + _("grazing"))
    generic_page("grazing",[("area_ha","Superficie (ha)","number"),("cover_type","Couvert",["Chaume","Jachère","Herbe","Alfa"]),("water","Eau",["Oui","Non"]),("start_date","Début","text"),("end_date","Fin","text"),("max_animals","Max animaux","number")],["wilaya","price_max"])

def pollination_page():
    st.markdown("### 🐝 " + _("pollination"))
    generic_page("pollination",[("hive_count","Nb ruches","number"),("bee_race","Race",["Locale","Saharan","Hybride"]),("zone","Zone","text"),("availability","Disponibilité","text")],["wilaya","price_max"])

def fertilizer_page():
    st.markdown("### 🌱 " + _("fertilizer"))
    generic_page("fertilizer",[("fertilizer_type","Type",["Fumier bovin","Fumier ovin","Fiente volaille","Compost","Autre"]),("quantity_tons","Quantité (t)","number"),("packaging","Conditionnement",["Vrac","En sacs","Sur palettes"])],["wilaya","price_max"])

def equipment_page():
    st.markdown("### 🚜 " + _("equipment"))
    generic_page("equipment",[("offer_type","Offre",["Vente","Location"]),("equipment_type","Type",["Tracteur","Moissonneuse","Charrue","Remorque","Irrigation","Épandeur","Semoir","Autre"]),("brand","Marque","text"),("model","Modèle","text"),("year","Année","number"),("state","État",["Neuf","Très bon","Bon","À rénover"]),("rental_period","Période",["Heure","Jour","Semaine","Mois"]),("availability","Disponibilité","text")],["wilaya","price_max","equipment_type","offer_type"])

# ══════════════════════════════════════════════════════════════════════════════
#  ★ FONCTIONNALITÉ 1 : ASSISTANT IA AGRICOLE
# ══════════════════════════════════════════════════════════════════════════════
AI_KNOWLEDGE = {
    "pomme de terre": "La pomme de terre se plante en Algérie en 2 saisons : primeur (jan–fév au Nord, sep–oct au Sud) et arrière-saison (août–sep). Variétés recommandées par ITGC : Spunta, Désirée, Sahel. Rendement moyen : 20–35 t/ha. Prix marché actuel : ~45 DA/kg.",
    "tomate":         "La tomate est cultivée principalement à Tipaza, Blida et Bouira. Semis en pépinière 6–8 semaines avant la transplantation. Stade floraison : réduire l'azote, augmenter le potassium. Attention aux maladies fongiques (mildiou, alternariose) en période humide.",
    "blé":            "Le blé dur (variété Waha, Mohamed Ben Bachir) se sème entre octobre et décembre selon l'altitude. Densité ITGC : 350 grains/m². Fertilisation : 2 apports azotés (tallage + montaison). Récolte juin–juillet sur les hauts plateaux.",
    "oignon":         "L'oignon est la 2e culture maraîchère algérienne. Zone principale : Relizane, Mascara, Mostaganem. Semis octobre–novembre pour récolte mai–juin. Sécher les bulbes 2 semaines avant stockage pour éviter la pourriture.",
    "irrigation":     "En Algérie, le goutte-à-goutte est subventionné à 50% via le FNDIA (Fonds National de Développement Agricole). Pour 1 ha de maraîchage : kit ~180 000 DA, subvention ~90 000 DA. Contact : Chambre d'Agriculture.",
    "prix":           "Selon les dernières données ONAB, les prix actuels : Pomme de terre 45 DA/kg, Tomate 60 DA/kg, Oignon 35 DA/kg, Blé dur 65 DA/kg, Datte Deglet 800 DA/kg.",
    "subvention":     "Principales subventions agricoles en Algérie 2024 : FNDIA (matériel irrigation), FNRDA (intrants et semences), Crédit BADR/BNA à taux bonifié 0–5%.",
    "sol":            "Pour tester votre sol gratuitement : ITGC (Institut Technique des Grandes Cultures) propose des analyses à prix réduit. pH idéal maraîchage : 6–7.",
    "maladie":        "Principales maladies en Algérie : Mildiou (tomate, pomme de terre) → traitement fongicide cuivrique préventif. Fusariose (oignon) → rotation 3 ans.",
    "datte":          "La datte Deglet Nour de Biskra et El Oued est la plus valorisée (800–1200 DA/kg). Pollinisation manuelle en mars–avril indispensable.",
    "default":        "Je suis l'assistant agricole d'AgriConnect DZ. Je peux vous aider sur : cultures (blé, tomates, pommes de terre, dattes...), irrigation, prix marchés, subventions, maladies, et réglementation agricole algérienne."
}

DARIJA_RESPONSES = {
    "sbah": "Sbah lkhir! Ana l'assistant ta3 AgriConnect, kifash nkhdmek?",
    "kifash": "Rani hna bach n3awnak fi kol haja tkhoss lfilaha. Siwil 3la les prix, les cultures, wla les subventions!",
    "prix": "Les prix daba : Batata 45 DA/kg, Tomatich 60 DA/kg, Basal 35 DA/kg, Qamh 65 DA/kg. Wesh tabghi ta3raf akthar?",
    "9ach": "Les prix daba : Batata 45 DA/kg, Tomatich 60 DA/kg, Basal 35 DA/kg. Siwil 3la ay mante9a !",
}

def ai_response(question: str) -> str:
    q = question.lower()
    for kw, resp in DARIJA_RESPONSES.items():
        if kw in q:
            return f"🇩🇿 {resp}"
    for kw, resp in AI_KNOWLEDGE.items():
        if kw in q:
            return f"🌾 {resp}"
    if any(w in q for w in ["annonce","acheter","vendre","disponible","cherche"]):
        anns = qdb("SELECT title, price, unit, wilaya FROM announcements ORDER BY created_at DESC LIMIT 5")
        if anns:
            lines = "\n".join([f"• {a['title']} — {a['price']} {a['unit']} ({a['wilaya']})" for a in anns])
            return f"🛒 Dernières annonces disponibles sur AgriConnect :\n\n{lines}\n\nConsultez le marché pour plus de détails."
    mois_actuel = datetime.now().month
    if any(w in q for w in ["quand","planter","semer","période","saison","calendrier"]):
        return f"📅 Pour le mois de {MOIS[mois_actuel-1]}, je vous recommande de consulter le Calendrier Cultural (menu 📅)."
    if any(w in q for w in ["météo","pluie","gel","chaleur","sirocco"]):
        return "🌦️ Pour la météo en temps réel, je recommande l'application Météo Algérie ou le site ONM."
    return f"🤖 {AI_KNOWLEDGE['default']}\n\nVotre question : *\"{question}\"*"

def assistant_ia_page():
    st.markdown(f"### 🤖 {_('assistant_ia')}")
    st.caption("Assistant agricole intelligent — Parlez en français, darija ou arabe")
    user = st.session_state.user
    if user:
        if not st.session_state.ai_messages:
            hist = qdb("SELECT role,content FROM ai_conversations WHERE user_id=? ORDER BY created_at DESC LIMIT 20", (user["id"],))
            st.session_state.ai_messages = [{"role":h["role"],"content":h["content"]} for h in reversed(hist)]
    else:
        if "ai_messages_anon" not in st.session_state:
            st.session_state.ai_messages_anon = []
    msgs = st.session_state.ai_messages if user else st.session_state.get("ai_messages_anon",[])
    st.markdown("**💡 Questions fréquentes :**")
    suggestions = ["Prix du marché aujourd'hui","Quand planter la tomate à Blida ?","Comment obtenir une subvention irrigation ?","Maladies de la pomme de terre","Sbah lkhir, kifach nkhdmek?"]
    scols = st.columns(len(suggestions))
    for i, sug in enumerate(suggestions):
        with scols[i]:
            if st.button(sug[:25]+"…" if len(sug)>25 else sug, key=f"sug_{i}", use_container_width=True):
                response = ai_response(sug)
                ts = datetime.now().strftime("%H:%M")
                msgs.append({"role":"user","content":sug,"ts":ts})
                msgs.append({"role":"assistant","content":response,"ts":ts})
                if user:
                    qdb("INSERT INTO ai_conversations (user_id,role,content) VALUES (?,?,?)", (user["id"],"user",sug), fetch=False)
                    qdb("INSERT INTO ai_conversations (user_id,role,content) VALUES (?,?,?)", (user["id"],"assistant",response), fetch=False)
                st.rerun()
    st.markdown("---")
    chat_container = st.container()
    with chat_container:
        if not msgs:
            st.markdown("""<div style="text-align:center;padding:2rem;color:var(--muted);">🌱 Bonjour ! Je suis votre assistant agricole.<br>Posez-moi une question sur vos cultures, les prix, ou les subventions.</div>""", unsafe_allow_html=True)
        for m in msgs[-20:]:
            ts = m.get("ts","")
            if m["role"] == "user":
                st.markdown(f'<div class="ai-bubble-user">{m["content"]}<div class="ai-time">{ts}</div></div>', unsafe_allow_html=True)
            else:
                content = m["content"].replace("\n","<br>")
                st.markdown(f'<div class="ai-bubble-bot">{content}<div class="ai-time">{ts} · AgriConnect IA</div></div>', unsafe_allow_html=True)
    with st.form("ai_form", clear_on_submit=True):
        c1, c2 = st.columns([5,1])
        with c1: question = st.text_input("Votre question…", placeholder="Ex: quand irriguer le blé à Sétif ?", label_visibility="collapsed")
        with c2: ok = st.form_submit_button(_("send"), use_container_width=True, type="primary")
    if ok and question.strip():
        response = ai_response(question.strip())
        ts = datetime.now().strftime("%H:%M")
        msgs.append({"role":"user","content":question.strip(),"ts":ts})
        msgs.append({"role":"assistant","content":response,"ts":ts})
        if user:
            qdb("INSERT INTO ai_conversations (user_id,role,content) VALUES (?,?,?)", (user["id"],"user",question.strip()), fetch=False)
            qdb("INSERT INTO ai_conversations (user_id,role,content) VALUES (?,?,?)", (user["id"],"assistant",response), fetch=False)
            st.session_state.ai_messages = msgs
        else:
            st.session_state.ai_messages_anon = msgs
        st.rerun()
    if msgs and st.button("🗑️ Effacer la conversation", key="clear_ai", type="secondary"):
        if user:
            qdb("DELETE FROM ai_conversations WHERE user_id=?", (user["id"],), fetch=False)
            st.session_state.ai_messages = []
        else:
            st.session_state.ai_messages_anon = []
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  ★ FONCTIONNALITÉ 2 : PRIX MARCHÉS + PRÉDICTION
# ══════════════════════════════════════════════════════════════════════════════
def generate_price_history(base, days=30):
    prices = [base]
    for _ in range(days-1):
        delta = random.gauss(0, base*0.03)
        prices.append(max(base*0.5, prices[-1] + delta))
    return prices

def simple_forecast(history, days=7):
    n = min(10, len(history))
    recent = history[-n:]
    x = list(range(n))
    xm = sum(x)/n; ym = sum(recent)/n
    num = sum((x[i]-xm)*(recent[i]-ym) for i in range(n))
    den = sum((x[i]-xm)**2 for i in range(n)) or 1
    slope = num/den
    last = recent[-1]
    return [max(0, last + slope*(i+1)) for i in range(days)]

def sparkline_html(values, width=80, height=30, color="#3d5a2e"):
    if not values: return ""
    mn, mx = min(values), max(values)
    rng = mx - mn if mx != mn else 1
    pts = []
    for i, v in enumerate(values):
        x = int(i * (width-4) / max(1, len(values)-1)) + 2
        y = int((1 - (v-mn)/rng) * (height-4)) + 2
        pts.append(f"{x},{y}")
    polyline = " ".join(pts)
    last_color = "#c0522a" if values[-1] > values[0] else "#2a6496"
    return f'<svg width="{width}" height="{height}" style="vertical-align:middle"><polyline points="{polyline}" fill="none" stroke="{last_color}" stroke-width="1.5" stroke-linejoin="round"/><circle cx="{pts[-1].split(",")[0]}" cy="{pts[-1].split(",")[1]}" r="2.5" fill="{last_color}"/></svg>'

def prix_marche_page():
    st.markdown(f"### 📊 {_('prix_marche')}")
    st.caption("Cours du marché de gros — actualisé quotidiennement — Prédiction 7 jours")
    c1, c2 = st.columns([2,2])
    with c1: selected_prod = st.selectbox("Produit", list(MARKET_PRICES.keys()), key="pm_prod")
    with c2: view_mode = st.radio("Vue", ["Tableau général","Détail + prédiction"], horizontal=True, key="pm_view")
    if view_mode == "Tableau général":
        st.markdown("<br>", unsafe_allow_html=True)
        for produit, info in MARKET_PRICES.items():
            hist = generate_price_history(info["base"])
            current = hist[-1]
            prev    = hist[-2]
            delta   = current - prev
            trend_html = f'<span class="trend-up">▲ +{delta:.0f}</span>' if delta > 0 else f'<span class="trend-down">▼ {delta:.0f}</span>' if delta < 0 else '<span class="trend-eq">— stable</span>'
            spark = sparkline_html(hist[-14:])
            badge = {'hausse':'<span class="badge badge-orange">↑ hausse</span>',
                     'baisse':'<span class="badge badge-blue">↓ baisse</span>',
                     'stable':'<span class="badge badge-green">→ stable</span>'}[info["trend"]]
            st.markdown(f"""
            <div class="prix-card">
                <div>
                    <div class="prix-nom">{produit}</div>
                    <div class="prix-zone">📍 {info['zone']}</div>
                </div>
                <div style="display:flex;align-items:center;gap:14px;">
                    {spark}
                    <div style="text-align:right">
                        <div class="prix-val">{current:.0f}</div>
                        <div class="prix-unit">{info['unit']}</div>
                        {trend_html}
                    </div>
                    {badge}
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        info = MARKET_PRICES[selected_prod]
        hist = generate_price_history(info["base"], 30)
        forecast = simple_forecast(hist, 7)
        st.markdown(f"#### {selected_prod} — {info['zone']}")
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Prix actuel", f"{hist[-1]:.0f} {info['unit'].split('/')[0]}", f"{hist[-1]-hist[-2]:.0f} vs hier")
        mc2.metric("Prévision J+7", f"{forecast[-1]:.0f}", f"{forecast[-1]-hist[-1]:.0f}")
        mc3.metric("Min 30 jours", f"{min(hist):.0f}")
        mc4.metric("Max 30 jours", f"{max(hist):.0f}")
        dates_hist = [(date.today() - timedelta(days=29-i)).strftime("%d/%m") for i in range(30)]
        dates_fore = [(date.today() + timedelta(days=i+1)).strftime("%d/%m") for i in range(7)]
        df_hist = pd.DataFrame({"Date": dates_hist, "Prix": [round(p) for p in hist]}).set_index("Date")
        df_fore = pd.DataFrame({"Date": dates_hist[-1:] + dates_fore, "Prévision": [round(hist[-1])] + [round(f) for f in forecast]}).set_index("Date")
        st.markdown("**Historique 30 jours**")
        st.line_chart(df_hist)
        st.markdown("**Prévision 7 jours (modèle tendance)**")
        st.line_chart(df_fore)
        direction = "hausse" if forecast[-1] > hist[-1] * 1.05 else ("baisse" if forecast[-1] < hist[-1] * 0.95 else "stable")
        conseil_map = {
            "hausse": f"📈 **Tendance haussière** : Le prix de {selected_prod} devrait monter de {((forecast[-1]/hist[-1])-1)*100:.1f}% dans 7 jours. **Recommandation : attendez avant de vendre si vous le pouvez.**",
            "baisse": f"📉 **Tendance baissière** : Le prix risque de baisser de {((1-forecast[-1]/hist[-1]))*100:.1f}%. **Recommandation : vendez rapidement ou cherchez un contrat à terme.**",
            "stable": f"📊 **Marché stable** : Les prix devraient rester autour de {forecast[-1]:.0f} DA. Bon moment pour des contrats à long terme."
        }
        st.info(conseil_map[direction])
        st.caption("⚠️ Prédictions à titre indicatif basées sur les tendances récentes. Consultez les marchés de gros locaux pour confirmation.")

# ══════════════════════════════════════════════════════════════════════════════
#  ★ FONCTIONNALITÉ 3 : ALERTES URGENCES / SURPLUS
# ══════════════════════════════════════════════════════════════════════════════
def alertes_page():
    st.markdown(f"### 🚨 {_('alertes')} — {_('surplus_title')}")
    st.caption("Vendez vos surplus avant qu'ils ne se perdent. Contactez les acheteurs autour de vous en temps réel.")
    tab1, tab2 = st.tabs(["📋 Alertes en cours", "➕ Publier une urgence"])
    with tab1:
        urgents = qdb("""
            SELECT a.*, u.name as author, u.phone as author_phone, u.wilaya as author_wilaya
            FROM announcements a JOIN users u ON a.user_id=u.id
            WHERE a.is_urgent=1 ORDER BY a.created_at DESC
        """)
        if urgents:
            st.markdown(f'<div class="alerte-banner">⚡ {len(urgents)} vente(s) urgente(s) active(s) — acheteurs notifiés</div>', unsafe_allow_html=True)
            for a in urgents:
                created = a["created_at"][:16] if a["created_at"] else ""
                icon = MODULE_ICONS.get(a["type"],"📌")
                st.markdown(f"""
                <div class="alerte-card">
                    <div class="titre">{icon} {a['title']}</div>
                    <div style="font-size:0.88rem;color:#1c1c1c;margin:6px 0;">{a['description']}</div>
                    <div class="meta">
                        💰 {a['price']:,.0f} {a['unit'] or ''}
                        &nbsp;·&nbsp; 📍 {a['wilaya']} — {a['commune']}
                        &nbsp;·&nbsp; 👤 {a['author']}
                        &nbsp;·&nbsp; 🕐 {created}
                    </div>
                </div>""", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button(f"📞 Contacter", key=f"ua_{a['id']}", use_container_width=True, type="primary"):
                        st.session_state.msg_to = a["user_id"]
                        st.session_state.msg_announce = a["id"]
                        st.session_state.page = "messages"; st.rerun()
                with c2:
                    if st.button(f"📱 QR Code", key=f"uq_{a['id']}", use_container_width=True):
                        st.session_state.qr_ann_id = a["id"]
                        st.session_state.page = "tracabilite"; st.rerun()
                with c3:
                    if st.session_state.user and st.session_state.user["id"] == a["user_id"]:
                        if st.button("✅ Vendu — Retirer", key=f"ud_{a['id']}", use_container_width=True):
                            qdb("UPDATE announcements SET is_urgent=0 WHERE id=?", (a["id"],), fetch=False)
                            st.success("Annonce urgente retirée.")
                            st.rerun()
        else:
            st.markdown('<div class="no-ann">✅ Aucune vente urgente en ce moment. Revenez plus tard ou publiez la vôtre.</div>', unsafe_allow_html=True)
    with tab2:
        if not st.session_state.user:
            st.warning(_("login_required")); return
        st.markdown("#### Publier une alerte surplus")
        st.info("💡 Votre annonce sera marquée 🚨 URGENT et apparaîtra en tête de toutes les listes.")
        with st.form("urgent_form", clear_on_submit=True):
            title    = st.text_input("Produit et description *", placeholder="Ex: Tomates cerises — 3 tonnes à écouler", key="urg_title")
            c1,c2    = st.columns(2)
            price    = c1.number_input("Prix (DA/kg ou DA/unité) *", min_value=0.0, step=5.0, key="urg_price")
            unit     = c2.text_input("Unité *", value="DA/kg", key="urg_unit")
            qty      = st.text_input("Quantité disponible", placeholder="Ex: 3 tonnes, 500 kg, 200 caisses", key="urg_qty")
            desc     = st.text_area("Détails (état, délai, conditions…)", height=80, key="urg_desc")
            c3,c4    = st.columns(2)
            wilaya   = c3.selectbox(_("wilaya"), list(WILAYAS.keys()), key="urg_wilaya")
            commune  = c4.selectbox(_("commune"), WILAYAS[wilaya], key="urg_commune")
            cat      = st.selectbox("Catégorie", ["market","transport","equipment","grazing","pollination","fertilizer"], key="urg_cat")
            imgs     = st.file_uploader("📷 Photo", type=["jpg","jpeg","png"], accept_multiple_files=True, key="urg_imgs")
            ok = st.form_submit_button("🚨 Publier l'alerte urgence", use_container_width=True, type="primary")
        if ok:
            if not title.strip() or price == 0:
                st.error(_("fill_required"))
            else:
                b64s = [b for b in [img_to_b64(im) for im in (imgs or [])[:3]] if b]
                qdb("INSERT INTO announcements (user_id,type,title,description,price,unit,wilaya,commune,data,images,is_urgent,urgent_qty) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (st.session_state.user["id"], cat, title.strip(),
                     desc, price, unit, wilaya, commune,
                     json.dumps({"product_type":"Urgence","quantity":qty}),
                     ";".join(b64s), 1, qty), fetch=False)
                st.success("🚨 Alerte publiée ! Les acheteurs dans votre wilaya sont notifiés.")
                st.balloons()
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  ★ FONCTIONNALITÉ 4 : TRAÇABILITÉ QR CODE
# ══════════════════════════════════════════════════════════════════════════════
def generate_qr_svg(content: str, size: int = 200) -> str:
    if HAS_QR:
        try:
            import qrcode
            import qrcode.image.svg
            factory = qrcode.image.svg.SvgImage
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=3, border=2)
            qr.add_data(content)
            qr.make(fit=True)
            img = qr.make_image(image_factory=factory)
            buf = io.BytesIO()
            img.save(buf)
            svg_str = buf.getvalue().decode()
            start = svg_str.find("<svg")
            return svg_str[start:] if start != -1 else _placeholder_qr(size)
        except:
            return _placeholder_qr(size)
    return _placeholder_qr(size)

def _placeholder_qr(size):
    cells = 21
    cell_size = size // cells
    rects = []
    for r in range(cells):
        for c in range(cells):
            val = (r * 37 + c * 13 + 42) % 2
            if (r < 7 and c < 7) or (r < 7 and c >= cells-7) or (r >= cells-7 and c < 7):
                if r in [0,6] or c in [0,6] or (2<=r<=4 and 2<=c<=4) or (2<=r<=4 and cells-5<=c<=cells-3) or (cells-5<=r<=cells-3 and 2<=c<=4):
                    val = 1
                else:
                    val = 0
            if val:
                x, y = c*cell_size, r*cell_size
                rects.append(f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="#1c1c1c"/>')
    return f'<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg" style="border:4px solid white;border-radius:8px;background:white">{"".join(rects)}</svg>'

def tracabilite_page():
    st.markdown(f"### 📱 {_('tracabilite')} — Certificat produit")
    st.caption("Générez un QR code pour certifier l'origine de votre produit. Scannable par les acheteurs et GMS.")
    ann_id = st.session_state.get("qr_ann_id", None)
    user = st.session_state.user
    if user:
        my_anns = qdb("SELECT id, title, type FROM announcements WHERE user_id=? ORDER BY created_at DESC", (user["id"],))
    else:
        my_anns = []
    tab1, tab2 = st.tabs(["🔍 Scanner / Vérifier", "📄 Générer mon certificat"])
    with tab1:
        st.markdown("#### Vérifier l'authenticité d'un produit")
        ann_id_input = st.number_input("Entrez l'ID du produit (sur le QR code)", min_value=1, step=1, value=ann_id if ann_id else 1, key="qr_id_input")
        if st.button("🔍 Vérifier le produit", type="primary", use_container_width=True, key="verify_qr"):
            ann_id = ann_id_input
        if ann_id:
            ann = qdb("SELECT a.*, u.name as nom_prod, u.phone, u.wilaya as w_prod, u.is_verified FROM announcements a JOIN users u ON a.user_id=u.id WHERE a.id=?", (ann_id,))
            if ann:
                a = ann[0]
                verified = "✅ Producteur vérifié AgriConnect" if a["is_verified"] else "⏳ Producteur non encore vérifié"
                badge_color = "#eef4e8" if a["is_verified"] else "#fff8e1"
                lot = f"LOT-{a['id']:04d}-{a['created_at'][:7].replace('-','')}"
                url_trace = f"https://agriconnect.dz/trace/{a['id']}"
                col_qr, col_info = st.columns([1, 2])
                with col_qr:
                    st.markdown('<div class="qr-card">', unsafe_allow_html=True)
                    qr_svg = generate_qr_svg(url_trace)
                    st.markdown(qr_svg, unsafe_allow_html=True)
                    st.caption(f"ID: {lot}")
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_info:
                    st.markdown(f"""
                    <div class="qr-info">
                        <div style="font-size:1rem;font-weight:500;margin-bottom:10px;color:#1c1c1c;">
                            {MODULE_ICONS.get(a['type'],'📌')} {a['title']}
                        </div>
                        <div style="background:{badge_color};border-radius:8px;padding:8px 12px;margin-bottom:12px;font-size:0.82rem;font-weight:500;">
                            {verified}
                        </div>
                        <table>
                            <tr><td>👤 Producteur</td><td><strong>{a['nom_prod']}</strong></td></tr>
                            <tr><td>📍 Origine</td><td>{a['wilaya']} — {a['commune']}</td></tr>
                            <tr><td>🏷️ Catégorie</td><td>{a['type'].upper()}</td></tr>
                            <tr><td>💰 Prix</td><td>{a['price']:,.0f} {a['unit'] or ''}</td></tr>
                            <tr><td>📅 Date publication</td><td>{a['created_at'][:10]}</td></tr>
                            <tr><td>🔢 Numéro de lot</td><td>{lot}</td></tr>
                            <tr><td>🌐 URL traçabilité</td><td style="color:#2a6496;">{url_trace}</td></tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("💬 Contacter le producteur", use_container_width=True, type="primary", key="contact_prod_qr"):
                            st.session_state.msg_to = a["user_id"]
                            st.session_state.msg_announce = a["id"]
                            st.session_state.page = "messages"; st.rerun()
                    with c2:
                        cert = f"""
CERTIFICAT D'ORIGINE AGRICONNECT DZ
====================================
Lot          : {lot}
Produit      : {a['title']}
Producteur   : {a['nom_prod']}
Wilaya       : {a['wilaya']} — {a['commune']}
Catégorie    : {a['type'].upper()}
Prix         : {a['price']} {a['unit'] or ''}
Date         : {a['created_at'][:10]}
Statut       : {'Vérifié' if a['is_verified'] else 'Non vérifié'}
URL          : {url_trace}
====================================
© 2026 AgriConnect DZ — contact@agriconnect.dz
"""
                        st.download_button("📥 Télécharger certificat", data=cert.encode("utf-8"), file_name=f"certificat_{lot}.txt", mime="text/plain", use_container_width=True, key="dl_cert")
            else:
                st.error(f"Aucun produit trouvé avec l'ID {ann_id}.")
    with tab2:
        if not user:
            st.warning(_("login_required")); return
        st.markdown("#### Générer le QR code de votre annonce")
        if my_anns:
            choices = {f"#{a['id']} — {a['title']}": a["id"] for a in my_anns}
            selected = st.selectbox("Sélectionner une annonce", list(choices.keys()), key="qr_ann_sel")
            chosen_id = choices[selected]
            if st.button("📱 Générer le QR Code", type="primary", use_container_width=True, key="gen_qr"):
                st.session_state.qr_ann_id = chosen_id
                st.rerun()
        else:
            st.info("Publiez d'abord une annonce pour générer son QR code.")

# ══════════════════════════════════════════════════════════════════════════════
#  ★ FONCTIONNALITÉ 5 : CALENDRIER CULTURAL
# ══════════════════════════════════════════════════════════════════════════════
def calendrier_page():
    st.markdown(f"### 📅 {_('calendrier')}")
    st.caption("Planifiez vos semis, irrigations et récoltes selon votre wilaya et vos cultures.")
    c1, c2 = st.columns(2)
    with c1:
        culture = st.selectbox("🌱 Culture", list(CALENDRIER.keys()), key="cal_culture")
    with c2:
        wilaya = st.selectbox(_("wilaya"), list(WILAYAS.keys()), key="cal_wilaya")
    cal = CALENDRIER[culture]
    mois_actuel = datetime.now().month
    wnum = int(wilaya.split(" - ")[0]) if " - " in wilaya else 16
    if wnum in [7,39,30,49,51,53,54,55,56,57,58,37,32,1,11,17,3,28]:
        default_zone = "Sud (Biskra, El Oued)" if "Sud" in " ".join(cal["zones"]) else list(cal["zones"].keys())[0]
    elif wnum in [5,14,19,34,20,28,48,38]:
        default_zone = "Hauts plateaux (Sétif, Tiaret)" if "Hauts plateaux" in " ".join(cal["zones"]) else list(cal["zones"].keys())[0]
    else:
        default_zone = list(cal["zones"].keys())[0]
    zone_options = list(cal["zones"].keys())
    def find_best_zone():
        for z in zone_options:
            if default_zone.split("(")[0].strip().lower() in z.lower():
                return z
        return zone_options[0]
    zone = st.selectbox("Zone climatique", zone_options, index=zone_options.index(find_best_zone()) if find_best_zone() in zone_options else 0, key="cal_zone")
    z_data = cal["zones"][zone]
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"**{cal['emoji']} {culture} — {zone}**")
    col_leg = st.columns(4)
    col_leg[0].markdown('<div style="display:flex;align-items:center;gap:6px;font-size:0.8rem;"><div style="width:16px;height:16px;background:#c8e6c9;border-radius:3px;"></div> Semis</div>', unsafe_allow_html=True)
    col_leg[1].markdown('<div style="display:flex;align-items:center;gap:6px;font-size:0.8rem;"><div style="width:16px;height:16px;background:#3d5a2e;border-radius:3px;"></div> Récolte</div>', unsafe_allow_html=True)
    col_leg[2].markdown('<div style="display:flex;align-items:center;gap:6px;font-size:0.8rem;"><div style="width:16px;height:16px;background:#bbdefb;border-radius:3px;"></div> Irrigation</div>', unsafe_allow_html=True)
    col_leg[3].markdown('<div style="display:flex;align-items:center;gap:6px;font-size:0.8rem;"><div style="width:16px;height:16px;background:#e8dfc8;border-radius:3px;opacity:0.6"></div> Aucune action</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    rows_html = ""
    rows_html += '<div class="cal-grid" style="margin-bottom:4px;">'
    rows_html += '<div class="cal-label" style="font-weight:600;">Action</div>'
    for m in MOIS:
        today_marker = ' style="background:#f0f7e6;border-radius:4px;"' if MOIS.index(m)+1 == mois_actuel else ""
        rows_html += f'<div class="cal-header"{today_marker}>{m}</div>'
    rows_html += '</div>'
    if z_data.get("semis"):
        rows_html += '<div class="cal-grid" style="margin-bottom:4px;">'
        rows_html += '<div class="cal-label">🌱 Semis</div>'
        for m in range(1,13):
            css = "cal-semis" if m in z_data["semis"] else "cal-nothing"
            today_ring = ' style="outline:2px solid #3d5a2e;outline-offset:1px;"' if m == mois_actuel else ""
            rows_html += f'<div class="cal-cell {css}"{today_ring}></div>'
        rows_html += '</div>'
    if z_data.get("irrigation"):
        rows_html += '<div class="cal-grid" style="margin-bottom:4px;">'
        rows_html += '<div class="cal-label">💧 Irrigation</div>'
        for m in range(1,13):
            css = "cal-irrigation" if m in z_data["irrigation"] else "cal-nothing"
            today_ring = ' style="outline:2px solid #1565c0;outline-offset:1px;"' if m == mois_actuel else ""
            rows_html += f'<div class="cal-cell {css}"{today_ring}></div>'
        rows_html += '</div>'
    if z_data.get("recolte"):
        rows_html += '<div class="cal-grid" style="margin-bottom:4px;">'
        rows_html += '<div class="cal-label">🏆 Récolte</div>'
        for m in range(1,13):
            css = "cal-recolte" if m in z_data["recolte"] else "cal-nothing"
            today_ring = ' style="outline:2px solid #c0522a;outline-offset:1px;"' if m == mois_actuel else ""
            rows_html += f'<div class="cal-cell {css}"{today_ring}></div>'
        rows_html += '</div>'
    st.markdown(rows_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    now_actions = []
    if mois_actuel in z_data.get("semis",[]): now_actions.append("🌱 **C'est le moment de semer !**")
    if mois_actuel in z_data.get("irrigation",[]): now_actions.append("💧 **Irriguer ce mois-ci**")
    if mois_actuel in z_data.get("recolte",[]): now_actions.append("🏆 **Période de récolte !**")
    if now_actions:
        st.success(f"**Ce mois ({MOIS[mois_actuel-1]}) pour {culture} en {zone} :**\n\n" + "\n\n".join(now_actions))
    else:
        st.info(f"**{MOIS[mois_actuel-1]} :** Pas d'action majeure ce mois pour {culture}. Profitez pour préparer le sol ou traiter les maladies.")
    st.markdown("#### 📚 Conseils techniques ITGC")
    for conseil in cal["conseils"]:
        st.markdown(f"• {conseil}")
    wilaya_key = next((k for k in METEO_WILAYAS if k in wilaya), None)
    if wilaya_key:
        m_data = METEO_WILAYAS[wilaya_key]
        st.markdown("#### 🌡️ Profil climatique de votre wilaya")
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Zone", m_data["zone"])
        mc2.metric("Précip. annuelles", f"{m_data['precip_mm']} mm")
        mc3.metric("T° min janvier", f"{m_data['t_min_jan']}°C")
        mc4.metric("Risque gel", m_data["gel_risque"])
    st.markdown("---")
    if st.session_state.user:
        if st.button(f"📣 Publier une annonce de {culture}", type="primary", key="pub_from_cal"):
            st.session_state.page = "market"; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  AUTRES PAGES (ANEM, Messages, Reviews, Contract, Verification, Profile)
# ══════════════════════════════════════════════════════════════════════════════
def anem_page():
    st.markdown("### 🏛️ " + _("anem"))
    user = st.session_state.user
    if not user or user.get("profile_type") != "ANEM":
        st.error("⛔ Accès réservé au profil ANEM.")
        return
    tj = qdb("SELECT COUNT(*) as n FROM announcements WHERE type='job'")[0]["n"]
    tw = qdb("SELECT COUNT(*) as n FROM users WHERE profile_type='Travailleur'")[0]["n"]
    tv = qdb("SELECT COUNT(*) as n FROM users WHERE profile_type='Travailleur' AND is_verified=1")[0]["n"]
    tm = qdb("SELECT COUNT(*) as n FROM messages")[0]["n"]
    c1,c2,c3,c4 = st.columns(4)
    for col,n,l in [(c1,tj,"Offres emploi"),(c2,tw,"Demandeurs"),(c3,tv,"Validés"),(c4,tm,"Messages")]:
        col.markdown(f'<div class="stat-card"><div class="num">{n}</div><div class="lbl">{l}</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("✅ Validation des travailleurs")
    pending = qdb("SELECT * FROM users WHERE profile_type='Travailleur' AND is_verified=0")
    if pending:
        for t in pending:
            with st.expander(f"{t['name']} — {t['phone']} ({t['wilaya']})"):
                if t["documents"]: st.image(f"data:image/jpeg;base64,{t['documents']}", width=260)
                c1,c2 = st.columns(2)
                with c1:
                    if st.button("✅ Valider", key=f"v_{t['id']}", type="primary"):
                        qdb("UPDATE users SET is_verified=1 WHERE id=?", (t["id"],), fetch=False)
                        st.success(_("validated")); st.rerun()
                with c2:
                    if st.button("❌ Rejeter", key=f"r_{t['id']}"):
                        qdb("DELETE FROM users WHERE id=? AND is_verified=0", (t["id"],), fetch=False)
                        st.rerun()
    else:
        st.info(_("pending_none"))
    st.markdown("---")
    st.subheader("📋 Offres d'emploi")
    offres = qdb("SELECT a.*, u.name as auth FROM announcements a JOIN users u ON a.user_id=u.id WHERE a.type='job' ORDER BY a.created_at DESC")
    for o in offres:
        cnt = qdb("SELECT COUNT(*) as n FROM messages WHERE announcement_id=?", (o["id"],))[0]["n"]
        with st.expander(f"{o['title']} — {o['wilaya']} (📩 {cnt})"):
            st.write(o["description"])
            postulants = qdb("SELECT DISTINCT u.name,u.phone FROM messages m JOIN users u ON m.sender_id=u.id WHERE m.announcement_id=?", (o["id"],))
            for p in postulants: st.write(f"• {p['name']} — {p['phone']}")

def messages_page():
    st.markdown("### 💬 " + _("messages"))
    user = st.session_state.user
    if not user: st.warning(_("login_required")); return
    if st.session_state.msg_to:
        other = qdb("SELECT name FROM users WHERE id=?", (st.session_state.msg_to,))
        if not other: st.session_state.msg_to = None; st.rerun(); return
        st.subheader(f"Conversation avec {other[0]['name']}")
        if st.button("← Retour", key="back_msg"):
            st.session_state.msg_to = None; st.session_state.msg_announce = None; st.rerun()
        msgs = qdb("SELECT * FROM messages WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?) ORDER BY created_at",
                   (user["id"], st.session_state.msg_to, st.session_state.msg_to, user["id"]))
        st.markdown('<div style="max-height:380px;overflow-y:auto;padding:10px;background:#fafaf7;border-radius:12px;border:1px solid #ddd8cc;margin-bottom:12px;">', unsafe_allow_html=True)
        for m in msgs:
            css = "msg-me" if m["sender_id"] == user["id"] else "msg-other"
            align = "right" if m["sender_id"] == user["id"] else "left"
            st.markdown(f'<div style="text-align:{align}"><div class="{css}">{m["content"]}<div class="msg-t">{m["created_at"][11:16]}</div></div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        with st.form("snd_msg", clear_on_submit=True):
            txt = st.text_area("Message…", height=70, key="msg_txt")
            if st.form_submit_button(_("send"), use_container_width=True, type="primary"):
                if txt.strip():
                    qdb("INSERT INTO messages (sender_id,receiver_id,announcement_id,content) VALUES (?,?,?,?)",
                        (user["id"], st.session_state.msg_to, st.session_state.msg_announce, txt.strip()), fetch=False)
                    st.rerun()
    else:
        contacts = qdb("SELECT DISTINCT u.id,u.name,u.profile_type,MAX(m.created_at) as lm FROM users u JOIN messages m ON u.id IN (m.sender_id,m.receiver_id) WHERE (m.sender_id=? OR m.receiver_id=?) AND u.id!=? GROUP BY u.id ORDER BY lm DESC",
                       (user["id"],)*3)
        if contacts:
            for c in contacts:
                cx, cb = st.columns([4,1])
                cx.markdown(f"**{c['name']}** — *{c['profile_type']}*")
                with cb:
                    if st.button("Ouvrir", key=f"op_{c['id']}", use_container_width=True):
                        st.session_state.msg_to = c["id"]; st.rerun()
                st.markdown("---")
        else:
            st.info(_("no_convo"))

def reviews_page():
    st.markdown("### ⭐ " + _("reviews"))
    user = st.session_state.user
    if not user: st.warning(_("login_required")); return
    if st.session_state.review_announce:
        ann = qdb("SELECT * FROM announcements WHERE id=?", (st.session_state.review_announce,))
        if not ann: st.session_state.review_announce = None; st.rerun(); return
        already = qdb("SELECT id FROM reviews WHERE announcement_id=? AND reviewer_id=?",
                      (st.session_state.review_announce, user["id"]))
        if already:
            st.warning("Vous avez déjà évalué cette annonce.")
            st.session_state.review_announce = None; return
        st.subheader(f"Évaluer : {ann[0]['title']}")
        if st.button("← Retour", key="back_rev"):
            st.session_state.review_announce = None; st.rerun()
        with st.form("rev_form"):
            rating  = st.slider("Note", 1, 5, 4, key="rev_rating")
            comment = st.text_area("Commentaire", key="rev_comment")
            if st.form_submit_button("Soumettre", type="primary", use_container_width=True):
                qdb("INSERT INTO reviews (announcement_id,reviewer_id,rating,comment) VALUES (?,?,?,?)",
                    (st.session_state.review_announce, user["id"], rating, comment), fetch=False)
                st.success(_("rating_sent"))
                st.session_state.review_announce = None; st.rerun()
        existing = qdb("SELECT r.*,u.name FROM reviews r JOIN users u ON r.reviewer_id=u.id WHERE r.announcement_id=? ORDER BY r.created_at DESC",
                       (st.session_state.review_announce,))
        if existing:
            avg = sum(r["rating"] for r in existing)/len(existing)
            st.markdown(f"**Moyenne :** {'⭐'*round(avg)} ({avg:.1f}/5, {len(existing)} avis)")
            for r in existing:
                st.markdown(f"- **{r['name']}** — {'⭐'*r['rating']} — *{r['comment']}*")
    else:
        my = qdb("SELECT id FROM announcements WHERE user_id=?", (user["id"],))
        if my:
            ids = [str(a["id"]) for a in my]
            revs = qdb(f"SELECT r.*,u.name FROM reviews r JOIN users u ON r.reviewer_id=u.id WHERE r.announcement_id IN ({','.join(ids)}) ORDER BY r.created_at DESC")
            if revs:
                for r in revs:
                    st.markdown(f"{'⭐'*r['rating']} **{r['name']}** — *{r['comment']}*")
            else:
                st.info("Aucun avis reçu.")
        else:
            st.info("Publiez une annonce pour recevoir des avis.")

def contract_page():
    st.markdown("### 📄 " + _("contract"))
    user = st.session_state.user
    if not user: st.warning(_("login_required")); return
    if st.session_state.contract_announce:
        anns = qdb("SELECT * FROM announcements WHERE id=?", (st.session_state.contract_announce,))
        if not anns: st.session_state.contract_announce = None; st.rerun(); return
        ann = anns[0]
        owner = qdb("SELECT * FROM users WHERE id=?", (ann["user_id"],))
        if not owner: st.error("Propriétaire introuvable."); return
        owner = owner[0]
        st.subheader(f"Contrat — {ann['title']}")
        if st.button("← Retour", key="back_cont"):
            st.session_state.contract_announce = None; st.rerun()
        c1,c2 = st.columns(2)
        start = c1.date_input("Début", date.today(), key="cont_start")
        end   = c2.date_input("Fin", date.today() + timedelta(days=7), key="cont_end")
        terms = st.text_area("Conditions particulières", height=100, key="cont_terms")
        if start > end:
            st.error("La date de fin doit être après le début.")
        elif st.button("📥 Générer le contrat", type="primary", use_container_width=True, key="gen_cont"):
            lot = f"AGR-{ann['id']:04d}-{datetime.now().strftime('%Y%m%d')}"
            content = f"""CONTRAT AGRICONNECT DZ
====================================
Référence    : {lot}
Produit/Service : {ann['title']}
Propriétaire : {owner['name']} ({owner['phone']})
Locataire    : {user['name']} ({user['phone']})
Wilaya       : {ann['wilaya']} — {ann['commune']}
Prix         : {ann['price']} {ann['unit'] or ''}
Période      : du {start} au {end}
Conditions   : {terms or 'Standard AgriConnect'}
====================================
Les deux parties s'engagent à respecter les conditions ci-dessus.
Contrat généré automatiquement par AgriConnect DZ.
Date génération : {datetime.now().strftime('%d/%m/%Y %H:%M')}
© 2026 AgriConnect — contact@agriconnect.dz
"""
            st.download_button("📥 Télécharger le contrat",
                               data=content.encode("utf-8"),
                               file_name=f"contrat_{lot}.txt",
                               mime="text/plain",
                               use_container_width=True,
                               key="dl_cont")
            qdb("INSERT INTO contracts (announcement_id,renter_id,owner_id,start_date,end_date,terms,status) VALUES (?,?,?,?,?,?,?)",
                (ann["id"], user["id"], owner["id"], start.isoformat(), end.isoformat(), terms, "active"), fetch=False)
            st.success(_("contract_created"))
    else:
        my_contracts = qdb("SELECT c.*,a.title as at,u.name as on FROM contracts c JOIN announcements a ON c.announcement_id=a.id JOIN users u ON c.owner_id=u.id WHERE c.renter_id=? ORDER BY c.created_at DESC",
                           (user["id"],))
        if my_contracts:
            st.subheader("Mes contrats")
            for c in my_contracts:
                st.markdown(f"- **{c['at']}** avec *{c['on']}* | {c['start_date']} → {c['end_date']} | `{c['status']}`")
        else:
            st.info("Aucun contrat pour le moment.")

def verification_page():
    st.markdown("### 🪪 " + _("verification"))
    user = st.session_state.user
    if not user: st.warning(_("login_required")); return
    st.info(f"Statut : **{'✅ Vérifié' if user['is_verified'] else '⏳ Non vérifié'}**")
    if not user["is_verified"]:
        doc = st.file_uploader("Pièce d'identité / Registre de commerce", type=["jpg","jpeg","png","pdf"], key="verif_doc")
        if doc and st.button("📤 Envoyer", type="primary", key="send_verif"):
            if doc.type == "application/pdf": b64 = base64.b64encode(doc.read()).decode()
            else: b64 = img_to_b64(doc)
            if b64:
                qdb("UPDATE users SET documents=? WHERE id=?", (b64, user["id"]), fetch=False)
                st.success(_("doc_sent"))

def profile_page():
    st.markdown("### 👤 " + _("profile"))
    user = st.session_state.user
    if not user: st.warning(_("login_required")); return
    ci, cs = st.columns([2,1])
    with ci:
        st.markdown(f"""
        <div class="card"><div class="card-body">
            <div style="font-family:'DM Serif Display',serif;font-size:1.4rem;margin-bottom:8px;">{user['name']}</div>
            <p>📱 {user['phone']}</p>
            <p>🏷️ {user['profile_type']}</p>
            <p>📍 {user['wilaya']} — {user.get('commune','')}</p>
            <p>🪪 {'✅ Vérifié' if user['is_verified'] else '❌ Non vérifié'}</p>
            <p>📅 Inscrit le {user.get('created_at','')[:10]}</p>
        </div></div>""", unsafe_allow_html=True)
    with cs:
        na = qdb("SELECT COUNT(*) as n FROM announcements WHERE user_id=?", (user["id"],))[0]["n"]
        nm = qdb("SELECT COUNT(*) as n FROM messages WHERE sender_id=?", (user["id"],))[0]["n"]
        nu = qdb("SELECT COUNT(*) as n FROM announcements WHERE user_id=? AND is_urgent=1", (user["id"],))[0]["n"]
        for n, l in [(na,"Annonces"),(nm,"Messages"),(nu,"🚨 Urgences")]:
            st.markdown(f'<div class="stat-card" style="margin-bottom:8px;"><div class="num">{n}</div><div class="lbl">{l}</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Mes annonces")
    my = qdb("SELECT * FROM announcements WHERE user_id=? ORDER BY created_at DESC", (user["id"],))
    if my:
        for a in my:
            ct, cd = st.columns([5,1])
            urgent_icon = "🚨 " if a["is_urgent"] else ""
            ct.markdown(f"{urgent_icon}**{a['title']}** — {a['price']} {a['unit']} | *{a['wilaya']}*")
            with cd:
                if st.button("🗑️", key=f"del_{a['id']}", help="Supprimer"):
                    qdb("DELETE FROM announcements WHERE id=? AND user_id=?", (a["id"], user["id"]), fetch=False)
                    st.rerun()
    else:
        st.info("Aucune annonce publiée.")
    st.markdown("---")
    if not user["is_verified"]:
        if st.button("🪪 Demander la vérification", type="primary", key="req_verif"):
            st.session_state.page = "verification"; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    if not st.session_state.db_initialized:
        init_db()
        st.session_state.db_initialized = True

    with st.sidebar:
        st.markdown("### 🌐 Langue")
        lang = st.selectbox("", ["fr","ar","en"], index=["fr","ar","en"].index(st.session_state.lang), label_visibility="collapsed", key="sidebar_lang")
        if lang != st.session_state.lang:
            st.session_state.lang = lang; st.rerun()
        st.markdown("---")
        if st.session_state.user:
            u = st.session_state.user
            st.markdown(f"**👤 {u['name']}** {'✅' if u['is_verified'] else '⏳'}")
            st.caption(f"{u['profile_type']} — {u['wilaya']}")
            if st.button(_("logout"), key="sidebar_logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.ai_messages = []
                st.session_state.page = "home"; st.rerun()
        else:
            if st.button(_("login"), key="sidebar_login", use_container_width=True, type="primary"):
                st.session_state.page = "login"; st.rerun()
            if st.button(_("register"), key="sidebar_register", use_container_width=True):
                st.session_state.page = "register"; st.rerun()
        st.markdown("---")
        urg = qdb("SELECT COUNT(*) as n FROM announcements WHERE is_urgent=1")[0]["n"]
        if urg > 0:
            st.markdown(f'<div style="background:#fde8e8;border:1px solid #fca5a5;border-radius:8px;padding:8px 10px;font-size:0.82rem;margin-bottom:8px;"><strong>🚨 {urg} vente(s) urgente(s)</strong><br><span style="color:#9b1c1c;">Voir les alertes →</span></div>', unsafe_allow_html=True)
            if st.button("Voir les urgences", key="sidebar_urg", use_container_width=True):
                st.session_state.page = "alertes"; st.rerun()
        st.markdown('<div style="background:#eef4e8;border-radius:8px;padding:10px;text-align:center;font-size:0.78rem;color:#3d5a2e;">📢 Espace publicitaire<br>contact@agriconnect.dz</div>', unsafe_allow_html=True)

    if st.session_state.user:
        render_navbar()
    else:
        c1,c2,c3 = st.columns(3)
        for col, pg, lbl, key in [(c1,"home",_("home"),"nav_home"),(c2,"login",_("login"),"nav_login"),(c3,"register",_("register"),"nav_reg")]:
            with col:
                if st.button(lbl, key=key, use_container_width=True, type="primary" if st.session_state.page==pg else "secondary"):
                    st.session_state.page = pg; st.rerun()

    PAGES = {
        "home": home_page, "login": login_page, "register": register_page,
        "market": market_page, "job": job_page, "transport": transport_page,
        "grazing": grazing_page, "pollination": pollination_page,
        "fertilizer": fertilizer_page, "equipment": equipment_page,
        "anem": anem_page, "messages": messages_page, "reviews": reviews_page,
        "contract": contract_page, "verification": verification_page,
        "profile": profile_page,
        "assistant_ia": assistant_ia_page,
        "prix_marche": prix_marche_page,
        "alertes": alertes_page,
        "tracabilite": tracabilite_page,
        "calendrier": calendrier_page,
    }
    PAGES.get(st.session_state.page, home_page)()

    st.markdown('<div class="footer">© 2026 AgriConnect DZ — contact@agriconnect.dz | Plateforme agricole nationale</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
