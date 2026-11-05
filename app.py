"""Profil en ligne : aperçu public du CV + mode édition protégé par mot de passe.

Les visiteurs voient seulement l'aperçu. Le mode édition (barre latérale) permet de
modifier le contenu puis de télécharger un nouveau data.json, à remplacer dans GitHub.
"""
import hmac
import json
import uuid
from html import escape
from pathlib import Path

import streamlit as st

DATA = Path(__file__).parent / "data.json"
NAVY, NAVY_INK = "#193141", "#eef4f7"

st.set_page_config(page_title="Bineta Diouf · Profil", layout="wide")

st.markdown(
    f"""
<style>
.block-container {{ max-width: 1000px; padding-top: 2rem; }}
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
    unsafe_allow_html=True,
)


def load() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


if "d" not in st.session_state:
    st.session_state.d = load()
d = st.session_state.d


def e(x) -> str:
    return escape(str(x or ""))


def dates(it: dict) -> str:
    return " – ".join(x for x in (it.get("start"), it.get("end")) if x)


def bullets(it: dict) -> str:
    b = it.get("bullets") or []
    return "<ul>" + "".join(f"<li>{e(x)}</li>" for x in b) + "</ul>" if b else ""


def entry(it: dict, title: str, line2: str = "") -> str:
    meta = " · ".join(x for x in (dates(it), it.get("place")) if x)
    tools = f'<div class="m">Outils : {e(it["tools"])}</div>' if it.get("tools") else ""
    sub = f"<br>{e(line2)}" if line2 else ""
    return f'<div class="it"><b>{e(title)}</b>{sub}<div class="m">{e(meta)}</div>{bullets(it)}{tools}</div>'


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
            entry(x, x["degree"], x.get("school", "")) for x in d["education"]
        )
    if d["skills"]:
        side += "<h4>Compétences</h4>" + "".join(
            f'<div class="it"><b>{e(s["group"])}</b><br>{e(s["items"])}</div>' for s in d["skills"]
        )
    if d["languages"]:
        side += "<h4>Langues</h4>" + "".join(
            f"<div>{e(l['name'])} : {e(l.get('level'))}</div>" for l in d["languages"]
        )

    main = ""
    if p.get("summary"):
        main += f"<h4>Profil</h4><p>{e(p['summary'])}</p>"
    if d["experiences"]:
        main += "<h4>Expériences professionnelles</h4>" + "".join(
            entry(x, x["role"], x.get("org", "")) for x in d["experiences"]
        )
    if d["projects"]:
        main += "<h4>Projets</h4>" + "".join(
            entry({**x, "end": ""}, x["title"], x.get("context", "")) for x in d["projects"]
        )

    return (
        f'<div class="cv"><aside><h1>{e(p.get("name"))}</h1>'
        f'<div class="tag">{e(p.get("headline"))}</div>{contact_html}{side}</aside>'
        f"<main>{main}</main></div>"
    )


# ---------------------------------------------------------------- édition
FIELDS = {
    "experiences": [("role", "Poste"), ("org", "Organisation"), ("kind", "Type"), ("start", "Début"),
                    ("end", "Fin"), ("place", "Lieu"), ("bullets", "Missions (une par ligne)")],
    "projects": [("title", "Titre"), ("context", "Contexte"), ("start", "Date"), ("tools", "Outils"),
                 ("link", "Lien"), ("bullets", "Réalisations (une par ligne)")],
    "education": [("degree", "Diplôme"), ("school", "Établissement"), ("start", "Début"),
                  ("end", "Fin"), ("place", "Lieu")],
    "skills": [("group", "Rubrique"), ("items", "Compétences (séparées par des virgules)")],
    "languages": [("name", "Langue"), ("level", "Niveau")],
}
LABELS = {"experiences": "Expériences", "projects": "Projets", "education": "Formation",
          "skills": "Compétences", "languages": "Langues"}
TITLE = {"experiences": "role", "projects": "title", "education": "degree", "skills": "group", "languages": "name"}


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
    st.subheader("Mode édition")
    st.caption("Vos changements sont visibles tout de suite ici, mais ils ne sont pas enregistrés en ligne. "
               "Téléchargez data.json en bas de page et remplacez le fichier dans GitHub.")
    tabs = st.tabs(["Profil", *LABELS.values(), "Confidentialité"])
    with tabs[0]:
        p = d["profile"]
        for k, label in [("name", "Nom"), ("headline", "Accroche"), ("email", "E-mail"), ("phone", "Téléphone"),
                         ("linkedin", "LinkedIn"), ("city", "Ville"), ("availability", "Disponibilité")]:
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


# ---------------------------------------------------------------- accès
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
    editor(d)
    st.divider()
st.markdown(render_cv(d), unsafe_allow_html=True)
