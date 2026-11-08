"""Portfolio en ligne : profil, expériences, projets, formation, compétences et CV.

Les visiteurs voient le portfolio. Le mode édition (barre latérale) est protégé par un mot de passe :
il permet de modifier le contenu puis de télécharger un nouveau data.json, à remplacer dans GitHub.
Pour proposer le CV en téléchargement, ajoutez un fichier cv.pdf à côté de app.py.
"""
import hmac
import json
import uuid
from html import escape
from pathlib import Path

import streamlit as st

BASE = Path(__file__).parent
DATA = BASE / "data.json"
CV_PDF = BASE / "cv.pdf"
NAVY, NAVY_INK = "#193141", "#eef4f7"

st.set_page_config(page_title="Bineta Diouf · Portfolio", layout="wide")

st.markdown(
    f"""
<style>
/* Mise en page générale du portfolio */
.block-container {{ max-width: 1000px; padding-top: 2rem; }}

/* Couleurs du site : orange et blanc */
:root {{
    --primary-color: #F97316;
}}

/* Titre principal et sous-titres */
.stApp h1, .stApp h2, .stApp h3 {{
    color: #C2410C;
}}

/* Boutons Streamlit */
.stButton button, .stDownloadButton button, .stLinkButton a {{
    border-color: #F97316 !important;
    border-radius: 8px !important;
}}
.stButton button[kind="primary"],
.stDownloadButton button[kind="primary"] {{
    background-color: #F97316 !important;
    color: #FFFFFF !important;
}}
.stButton button:hover, .stDownloadButton button:hover,
.stLinkButton a:hover {{
    border-color: #C2410C !important;
    color: #C2410C !important;
}}

/* Onglets du portfolio : seul l'onglet actif est orange */
.stTabs [data-baseweb="tab"] {{
    color: #344054;
}}
.stTabs [data-baseweb="tab"][aria-selected="true"] {{
    color: #EA580C !important;
}}
.stTabs [data-baseweb="tab-highlight"] {{
    background-color: #F97316 !important;
}}

/* Liens */
.stApp a {{
    color: #EA580C !important;
}}

/* Cases à cocher et curseurs */
.stCheckbox label, .stRadio label {{
    accent-color: #F97316;
}}

/* Cartes des expériences et projets */
[data-testid="stVerticalBlockBorderWrapper"] {{
    border-color: #FED7AA !important;
}}

/* CV : on conserve volontairement ses couleurs d'origine */
.cv {{ display: grid; grid-template-columns: 1fr 2fr; border: 1px solid #d8e0e5;
      border-radius: 4px; overflow: hidden; box-shadow: 0 8px 30px rgba(0,0,0,.10); }}
.cv aside {{ background: {NAVY}; color: {NAVY_INK}; padding: 26px 20px; }}
.cv main {{ background: #fff; color: #1c2b35; padding: 26px 24px; }}
.cv h1 {{ font-size: 26px; line-height: 1.1; margin: 0 0 8px; color: {NAVY_INK}; }}
.cv .tag {{ font-size: 15px; opacity: .9; margin-bottom: 18px; }}
.cv h4 {{ margin: 20px 0 6px; font-size: 12px; letter-spacing: .1em; text-transform: uppercase; }}
.cv aside h4 {{ border-bottom: 1px solid rgba(255,255,255,.25); padding-bottom: 4px; color: {NAVY_INK}; }}
.cv main h4 {{ border-bottom: 2px solid {NAVY}; padding-bottom: 4px; color: #1c2b35; }}
.cv .it {{ font-size: 13px; margin-bottom: 12px; overflow-wrap: anywhere; }}
.cv .m {{ font-size: 12px; opacity: .75; }}
.cv ul {{ margin: 4px 0 0; padding-left: 16px; }}
.cv p, .cv div {{ font-size: 13px; }}
@media (max-width: 700px) {{ .cv {{ grid-template-columns: 1fr; }} }}
</style>
""",
