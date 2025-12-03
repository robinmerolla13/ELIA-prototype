# ---------------------------------------------------------
#  app.py — Version stable, lisible et fonctionnelle d’ÉLIA
# ---------------------------------------------------------
import streamlit as st
from pathlib import Path
import json
import datetime

# ---------------- Page config ----------------
st.set_page_config(
    page_title="ÉLIA — Aides étudiantes",
    page_icon="💬",
    layout="wide"
)

# ---------------- CSS (palette blanche + accents doux) ----------------
st.markdown("""
<style>
body {
    background-color: #FFFFFF;
}
.chat-msg-user {
    background:#EFF6FF;
    padding:12px 16px;
    border-radius:10px;
    margin-bottom:8px;
    border:1px solid #dbeafe;
}
.chat-msg-elia {
    background:#FDF2FF;
    padding:12px 16px;
    border-radius:10px;
    margin-bottom:8px;
    border:1px solid #f3d8ff;
}
.plan-box {
    background:white;
    border-radius:12px;
    padding:20px;
    border:1px solid #eee;
    box-shadow:0 4px 16px rgba(0,0,0,0.06);
}
.section-title {
    font-size:26px;
    font-weight:700;
    margin-top:15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
header_cols = st.columns([1,5,3])
with header_cols[0]:
    logo_path = Path("logo.png")
    if logo_path.exists():
        st.image(str(logo_path), width=200)   # logo plus grand
with header_cols[1]:
    st.markdown("<h2 style='margin-top:40px;'>Trouve tes aides étudiantes facilement</h2>", unsafe_allow_html=True)
with header_cols[2]:
    st.markdown("<div style='margin-top:45px; text-align:right;'><a style='margin-right:15px;'>Aides disponibles</a><a style='margin-right:15px;'>Profil</a><a>Contact</a></div>", unsafe_allow_html=True)

st.write("---")

# ---------------- Sidebar profil ----------------
st.sidebar.header("Profil étudiant")

with st.sidebar.form("profil"):
    region = st.selectbox("Région", ["Île-de-France","Auvergne-Rhône-Alpes","Occitanie","Nouvelle-Aquitaine","PACA","Hauts-de-France","Autre"])
    is_boursier = st.radio("Boursier ?", ["Non","Oui"]) == "Oui"
    in_apprenticeship = st.checkbox("En apprentissage / alternance")
    international = st.checkbox("Étudiant international")
    low_income = st.checkbox("Revenus modestes")
    living = st.selectbox("Logement", ["Chez parents","Location privée","CROUS","Colocation"])
    needs_mobility = st.checkbox("Aide mobilité (stage, transport)")
    needs_food = st.checkbox("Aide alimentaire / CROUS")
    needs_psy = st.checkbox("Besoin d’un soutien psychologique")

    saved = st.form_submit_button("Enregistrer")

if saved:
    st.sidebar.success("Profil mis à jour ✔")

profile = {
    "region": region,
    "is_boursier": is_boursier,
    "in_apprenticeship": in_apprenticeship,
    "international": international,
    "low_income": low_income,
    "living": living,
    "needs_mobility": needs_mobility,
    "needs_food": needs_food,
    "needs_psy": needs_psy
}

# ---------------- Database des aides ----------------
AIDES_DB = {
    "apl": {
        "name":"APL - Aide au logement",
        "triggers":["apl","logement","loyer","location"],
        "desc":"Aide financière de la CAF pour réduire ton loyer.",
        "docs":["Bail","Pièce d'identité","RIB"],
        "links":{"CAF":"https://www.caf.fr"},
        "steps":["Simuler sur CAF","Créer compte CAF","Envoyer justificatifs"]
    },
    "mobili": {
        "name":"Mobili-Jeune",
        "triggers":["mobili","mobili jeune","mobilijeune"],
        "desc":"Aide d’Action Logement pour alternants.",
        "docs":["Contrat apprentissage","Attestation employeur"],
        "links":{"Action Logement":"https://www.actionlogement.fr"},
        "steps":["Créer un compte","Remplir demande","Joindre justificatifs"]
    },
    "bourse": {
        "name":"Bourse CROUS",
        "triggers":["bourse","dse","crous"],
        "desc":"Aide financière pour étudiants selon les ressources.",
        "docs":["Avis fiscal","Justificatif scolarité"],
        "links":{"DSE":"https://www.etudiant.gouv.fr"},
        "steps":["Créer DSE","Joindre documents","Soumettre dossier"]
    },
    "impots": {
        "name":"Déclaration d’impôts",
        "triggers":["impot","impôts","déclaration"],
        "desc":"Déclaration des revenus, rattachement parental, conseils étudiants.",
        "docs":["Numéro fiscal","Justificatifs revenus"],
        "links":{"Impôts":"https://www.impots.gouv.fr"},
        "steps":["Vérifier obligation","Créer espace fiscal","Déclarer en ligne"]
    },
    "psy": {
        "name":"Aide psychologique",
        "triggers":["psy","psychologue","santé mentale"],
        "desc":"Consultations psychologiques gratuites ou remboursées.",
        "docs":[],
        "links":{"Santé":"https://www.sante.fr"},
        "steps":["Contacter service universitaire","Prendre rendez-vous"]
    },
    "resto": {
        "name":"Restauration CROUS",
        "triggers":["resto","repas","crous","restau"],
        "desc":"Repas étudiants à prix réduit.",
        "docs":[],
        "links":{"CROUS":"https://www.crous.fr"},
        "steps":["Localiser restaurant U","Obtenir carte étudiante"]
    },
}

def normalize(t):
    return t.lower().replace("é","e").replace("è","e").replace("à","a")

def extract_keywords(q):
    if not q: return []
    for c in "?.,;!/()":
        q = q.replace(c," ")
    return [w for w in normalize(q).split() if w]

def score(aid, kws, profile):
    s = 0
    for t in aid["triggers"]:
        if any(kw in t for kw in kws):
            s += 2

    if profile["in_apprenticeship"] and "alternant" in aid["desc"].lower():
        s += 2
    if profile["is_boursier"] and "bourse" in aid["name"].lower():
        s += 2
    if profile["needs_mobility"] and "mobil" in aid["name"].lower():
        s += 2
    if profile["needs_food"] and "rest" in aid["name"].lower():
        s += 1.5
    if profile["needs_psy"] and "psy" in aid["name"].lower():
        s += 1.5

    return s

def find_aids(q, profile):
    kws = extract_keywords(q)
    scored = []
    for aid_id, aid in AIDES_DB.items():
        s = score(aid, kws, profile)
        if s > 0:
            scored.append((aid_id,s))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [aid for aid, _ in scored[:5]]

# ---------------- Session state ----------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "plan" not in st.session_state:
    st.session_state.plan = None

# ---------------- Chat UI ----------------
st.markdown("<div class='section-title'>💬 Discuter avec ÉLIA</div>", unsafe_allow_html=True)

user_msg = st.text_input("Écris ici :", placeholder="Ex : Comment demander l’APL ?")

if st.button("Envoyer"):
    if user_msg.strip():
        st.session_state.conversation.append({"role":"user", "text":user_msg})

        aids = find_aids(user_msg, profile)
        if aids:
            txt = "Voici ce que je peux te proposer :\n\n"
            for aid_id in aids:
                a = AIDES_DB[aid_id]
                txt += f"**{a['name']}** — {a['desc']}\n\n"
            txt += "Tu veux un plan d’action détaillé ? Dis-moi : *plan APL*, *plan Mobili-Jeune*, etc."
        else:
            txt = "Je n’ai pas trouvé d’aide précise. Tu peux reformuler ?"

        st.session_state.conversation.append({"role":"elia", "text":txt})

    st.experimental_rerun()

# Render conversation
for msg in st.session_state.conversation[-10:]:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-msg-user'><b>Toi :</b> {msg['text']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-msg-elia'><b>ÉLIA :</b> {msg['text']}</div>", unsafe_allow_html=True)

st.write("---")

# ---------------- Génération plan ----------------
st.markdown("<div class='section-title'>🗂️ Plan d’action personnalisé</div>", unsafe_allow_html=True)

# Boutons automatiques
colA, colB = st.columns(2)
with colA:
    for aid_id, aid in AIDES_DB.items():
        if st.button(f"📄 Générer : {aid['name']}"):
            st.session_state.plan = {
                "title": aid["name"],
                "description": aid["desc"],
                "steps": aid["steps"],
                "documents": aid["docs"],
                "links": aid["links"],
                "generated_at": datetime.datetime.now().isoformat()
            }
            st.experimental_rerun()

# Display plan
with colB:
    plan = st.session_state.plan
    if plan:
        st.markdown("<div class='plan-box'>", unsafe_allow_html=True)
        st.markdown(f"### {plan['title']}")
        st.write(plan["description"])

        st.markdown("#### 📌 Étapes")
        for s in plan["steps"]:
            st.write("•", s)

        st.markdown("#### 📄 Documents")
        if plan["documents"]:
            for d in plan["documents"]:
                st.write("•", d)
        else:
            st.write("Aucun document nécessaire.")

        st.markdown("#### 🔗 Liens officiels")
        for lbl, url in plan["links"].items():
            st.write(f"- [{lbl}]({url})")

        txt = json.dumps(plan, indent=2, ensure_ascii=False)
        st.download_button("Télécharger le plan (JSON)", txt.encode("utf-8"), "plan.json", "application/json")

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Aucun plan généré pour le moment.")
