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
import base64

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

.profile-header {
    display: flex;
    align-items: center;
    gap: 25px;
    margin-bottom: 25px;
}

.profile-photo {
    width: 150px;
    height: 150px;
    object-fit: cover;
    border-radius: 50%;
    border: 4px solid #F97316;
}

.profile-info {
    flex: 1;
}


}
</style>
""",
    unsafe_allow_html=True,
)


def load() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


if "d" not in st.session_state:
    st.session_state.d = load()
d = st.session_state.d


# ------------------------------------------------------------------ outils
def e(x) -> str:
    return escape(str(x or ""))


def url(u: str) -> str:
    u = (u or "").strip()
    if not u:
        return ""
    return u if u.startswith(("http://", "https://")) else "https://" + u


def dates(it: dict) -> str:
    return " – ".join(x for x in (it.get("start"), it.get("end")) if x)


def meta_line(it: dict, *extra: str) -> str:
    return " · ".join(x for x in (dates(it), it.get("place"), *extra) if x)


# ------------------------------------------------------------------ pages publiques
def header(d: dict) -> None:
    p, pub = d["profile"], d.get("public", {})
    photo_path = BASE / "photo.jpg"

    photo_html = ""
    
    if photo_path.exists():
        image_base64 = base64.b64encode(photo_path.read_bytes()).decode()
    
        photo_html = f"""
            <img
                src="data:image/jpeg;base64,{image_base64}"
                class="profile-photo"
            >
        """
    
    st.markdown(
        f"""
        <div class="profile-header">
            {photo_html}
            <div class="profile-info">
                <h1>{e(p.get("name", ""))}</h1>
                <p>{e(p.get("headline", ""))}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if p.get("headline"):
        st.markdown(f"**{p['headline']}**")
    info = " · ".join(x for x in (p.get("city"), p.get("availability")) if x)
    if info:
        st.caption(info)
    links = []
    if p.get("linkedin"):
        links.append(("LinkedIn", url(p["linkedin"])))
    if p.get("github"):
        links.append(("GitHub", url(p["github"])))
    if p.get("website"):
        links.append(("Site web", url(p["website"])))
    if pub.get("show_email") and p.get("email"):
        links.append(("E-mail", "mailto:" + p["email"]))
    if links:
        cols = st.columns([1] * len(links) + [max(1, 6 - len(links))])
        for col, (label, href) in zip(cols, links):
            col.link_button(label, href)
    if pub.get("show_phone") and p.get("phone"):
        st.caption(f"Téléphone : {p['phone']}")


def page_about(d: dict) -> None:
    p = d["profile"]
    if p.get("summary"):
        st.markdown(p["summary"])
    if d["education"]:
        st.subheader("Formation actuelle")
        x = d["education"][0]
        st.markdown(f"**{x['degree']}**  \n{x.get('school', '')} · {meta_line(x)}")
    if d["skills"]:
        st.subheader("Domaines")
        for s in d["skills"]:
            st.markdown(f"- **{s['group']}**")


def page_experiences(d: dict) -> None:
    if not d["experiences"]:
        st.info("Aucune expérience pour l'instant.")
    for x in d["experiences"]:
        with st.container(border=True):
            st.markdown(f"**{x.get('role', '')}** · {x.get('org', '')}")
            st.caption(meta_line(x, x.get("kind", "")))
            for b in x.get("bullets", []):
                st.markdown(f"- {b}")


def page_projects(d: dict) -> None:
    if not d["projects"]:
        st.info("Aucun projet pour l'instant.")
    for x in d["projects"]:
        with st.container(border=True):
            st.markdown(f"**{x.get('title', '')}**")
            st.caption(" · ".join(v for v in (x.get("context"), x.get("start")) if v))
            if x.get("description"):
                st.markdown(x["description"])
            for b in x.get("bullets", []):
                st.markdown(f"- {b}")
            if x.get("tools"):
                st.caption(f"Outils : {x['tools']}")
            if x.get("link"):
                st.link_button("Voir le projet", url(x["link"]))


def page_education_skills(d: dict) -> None:
    st.subheader("Formation")
    for x in d["education"]:
        with st.container(border=True):
            st.markdown(f"**{x.get('degree', '')}**  \n{x.get('school', '')}")
            st.caption(meta_line(x))
    st.subheader("Compétences")
    for s in d["skills"]:
        st.markdown(f"**{s['group']}**  \n{s['items']}")
    if d["languages"]:
        st.subheader("Langues")
        st.markdown("  \n".join(f"{l['name']} : {l.get('level', '')}" for l in d["languages"]))


def bullets_html(it: dict) -> str:
    b = it.get("bullets") or []
    return "<ul>" + "".join(f"<li>{e(x)}</li>" for x in b) + "</ul>" if b else ""


def cv_entry(it: dict, title: str, line2: str = "") -> str:
    tools = f'<div class="m">Outils : {e(it["tools"])}</div>' if it.get("tools") else ""
    sub = f"<br>{e(line2)}" if line2 else ""
    return (f'<div class="it"><b>{e(title)}</b>{sub}<div class="m">{e(meta_line(it))}</div>'
            f"{bullets_html(it)}{tools}</div>")


def render_cv(d: dict) -> str:
    p, pub = d["profile"], d.get("public", {})
    contact = [p.get("linkedin"), p.get("city")]
    if pub.get("show_email"):
        contact.insert(0, p.get("email"))
    if pub.get("show_phone"):
        contact.insert(0, p.get("phone"))
    contact_html = "".join(f"<div>{e(c)}</div>" for c in contact if c)

    side = ""
    if p.get("availability"):
        side += f"<h4>Disponibilité</h4><div>{e(p['availability'])}</div>"
    if d["education"]:
        side += "<h4>Formation</h4>" + "".join(
            cv_entry(x, x["degree"], x.get("school", "")) for x in d["education"])
    if d["skills"]:
        side += "<h4>Compétences</h4>" + "".join(
            f'<div class="it"><b>{e(s["group"])}</b><br>{e(s["items"])}</div>' for s in d["skills"])
    if d["languages"]:
        side += "<h4>Langues</h4>" + "".join(
            f"<div>{e(l['name'])} : {e(l.get('level'))}</div>" for l in d["languages"])

    main = ""
    if p.get("summary"):
        main += f"<h4>Profil</h4><p>{e(p['summary'])}</p>"
    if d["experiences"]:
        main += "<h4>Expériences professionnelles</h4>" + "".join(
            cv_entry(x, x["role"], x.get("org", "")) for x in d["experiences"])
    if d["projects"]:
        main += "<h4>Projets</h4>" + "".join(
            cv_entry({**x, "end": "", "place": ""}, x["title"], x.get("context", "")) for x in d["projects"])

    return (f'<div class="cv"><aside><h1>{e(p.get("name"))}</h1>'
            f'<div class="tag">{e(p.get("headline"))}</div>{contact_html}{side}</aside>'
            f"<main>{main}</main></div>")


def page_cv(d: dict) -> None:
    if CV_PDF.exists():
        st.download_button("Télécharger mon CV (PDF)", CV_PDF.read_bytes(),
                           file_name="CV_Bineta_Diouf.pdf", mime="application/pdf", type="primary")
    st.markdown(render_cv(d), unsafe_allow_html=True)


# ------------------------------------------------------------------ édition
FIELDS = {
    "experiences": [("role", "Poste"), ("org", "Organisation"), ("kind", "Type"), ("start", "Début"),
                    ("end", "Fin"), ("place", "Lieu"), ("bullets", "Missions (une par ligne)")],
    "projects": [("title", "Titre"), ("context", "Contexte"), ("start", "Date"), ("tools", "Outils"),
                 ("link", "Lien (facultatif)"), ("description", "Description"),
                 ("bullets", "Réalisations (une par ligne)")],
    "education": [("degree", "Diplôme"), ("school", "Établissement"), ("start", "Début"),
                  ("end", "Fin"), ("place", "Lieu")],
    "skills": [("group", "Rubrique"), ("items", "Compétences (séparées par des virgules)")],
    "languages": [("name", "Langue"), ("level", "Niveau")],
}
LABELS = {"experiences": "Expériences", "projects": "Projets", "education": "Formation",
          "skills": "Compétences", "languages": "Langues"}
TITLE = {"experiences": "role", "projects": "title", "education": "degree",
         "skills": "group", "languages": "name"}
LONG = {"description"}


def _remove(sec: str, i: int) -> None:
    del st.session_state.d[sec][i]


def _move(sec: str, i: int, step: int) -> None:
    a = st.session_state.d[sec]
    j = i + step
    if 0 <= j < len(a):
        a[i], a[j] = a[j], a[i]


def _add(sec: str) -> None:
    item = {"id": uuid.uuid4().hex[:8], **{k: "" for k, _ in FIELDS[sec]}}
    if "bullets" in item:
        item["bullets"] = []
    st.session_state.d[sec].append(item)


def editor(d: dict) -> None:
    st.caption("Vos changements sont visibles tout de suite, mais ils ne sont pas enregistrés en ligne. "
               "Téléchargez data.json en bas du mode édition et remplacez le fichier dans GitHub.")
    tabs = st.tabs(["Profil", *LABELS.values(), "Confidentialité"])
    with tabs[0]:
        p = d["profile"]
        for k, label in [("name", "Nom"), ("headline", "Accroche"), ("email", "E-mail"), ("phone", "Téléphone"),
                         ("linkedin", "Lien LinkedIn"), ("github", "Lien GitHub (facultatif)"),
                         ("website", "Site web (facultatif)"), ("city", "Ville"),
                         ("availability", "Disponibilité")]:
            p[k] = st.text_input(label, p.get(k, ""), key=f"p_{k}")
        p["summary"] = st.text_area("Résumé", p.get("summary", ""), key="p_summary")
    for tab, sec in zip(tabs[1:-1], LABELS):
        with tab:
            for i, it in enumerate(d[sec]):
                with st.expander(it.get(TITLE[sec]) or "Sans titre"):
                    for k, label in FIELDS[sec]:
                        key = f"{sec}_{it['id']}_{k}"
                        if k == "bullets":
                            v = st.text_area(label, "\n".join(it.get(k, [])), key=key)
                            it[k] = [x.strip() for x in v.splitlines() if x.strip()]
                        elif k in LONG:
                            it[k] = st.text_area(label, it.get(k, ""), key=key)
                        else:
                            it[k] = st.text_input(label, it.get(k, ""), key=key)
                    c1, c2, c3 = st.columns(3)
                    c1.button("Monter", key=f"up_{sec}_{it['id']}", on_click=_move, args=(sec, i, -1))
                    c2.button("Descendre", key=f"dn_{sec}_{it['id']}", on_click=_move, args=(sec, i, 1))
                    c3.button("Supprimer", key=f"rm_{sec}_{it['id']}", on_click=_remove, args=(sec, i))
            st.button("Ajouter", key=f"add_{sec}", on_click=_add, args=(sec,))
    with tabs[-1]:
        pub = d.setdefault("public", {})
        pub["show_email"] = st.checkbox("Afficher l'e-mail aux visiteurs", pub.get("show_email", True))
        pub["show_phone"] = st.checkbox("Afficher le téléphone aux visiteurs", pub.get("show_phone", False))
    st.download_button("Télécharger data.json", json.dumps(d, ensure_ascii=False, indent=2),
                       file_name="data.json", mime="application/json", type="primary")


# ------------------------------------------------------------------ accès
def admin_password() -> str:
    try:
        return str(st.secrets.get("ADMIN_PASSWORD", ""))
    except Exception:  # pas de fichier secrets
        return ""


with st.sidebar:
    st.markdown("### Espace propriétaire")
    expected = admin_password()
    if not expected:
        st.caption("Mode édition désactivé : aucun mot de passe configuré.")
        is_admin = False
    else:
        given = st.text_input("Mot de passe", type="password")
        is_admin = bool(given) and hmac.compare_digest(given.encode(), expected.encode())
        if given and not is_admin:
            st.error("Mot de passe incorrect.")

if is_admin:
    with st.expander("Mode édition", expanded=True):
        editor(d)

header(d)
t_about, t_exp, t_proj, t_edu, t_cv = st.tabs(
    ["À propos", "Expériences", "Projets", "Formation et compétences", "CV"])
with t_about:
    page_about(d)
with t_exp:
    page_experiences(d)
with t_proj:
    page_projects(d)
with t_edu:
    page_education_skills(d)
with t_cv:
    page_cv(d)
