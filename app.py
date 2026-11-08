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
