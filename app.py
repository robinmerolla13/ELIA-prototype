import streamlit as st

# Configuration page
st.set_page_config(
    page_title="ÉLIA – Assistant administratif",
    page_icon="💬",
    layout="centered"
)

# ------------ UI STYLE ------------
st.markdown("""
    <style>
        .title {
            text-align: center;
            font-size: 48px;
            font-weight: bold;
            background: linear-gradient(90deg, #A4C7FF, #E6A3FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            text-align: center;
            color: #888;
            font-size: 20px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ------------ LOGO + TITRE ------------
st.markdown("<div class='title'>ÉLIA</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Ton assistante administrative bienveillante</div>", unsafe_allow_html=True)

st.write("---")

# ------------ INITIALISATION CHAT ------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour 👋 Je suis ÉLIA. Dis-moi simplement ce dont tu as besoin : APL, bourse, carte vitale, CAF… Je suis là pour t’aider ✨"}
    ]

# ------------ AFFICHAGE DES MESSAGES ------------
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])
    else:
        st.chat_message("user").write(msg["content"])


# ------------ IA SIMULÉE (RÉPONSES) ------------
def elia_response(text):
    txt = text.lower()

    if "apl" in txt or "logement" in txt:
        return (
            "🏠 **Demande d'APL : c'est parti !**\n\n"
            "J’ai besoin de quelques infos pour t’aider :\n"
            "1️⃣ Tu habites en résidence CROUS ou en location privée ?\n"
            "2️⃣ As-tu déjà un compte CAF ?\n"
            "3️⃣ As-tu ton bail ou contrat de location ?\n\n"
            "Dès que tu me réponds, je t’explique la procédure étape par étape ✨"
        )

    if "bourse" in txt or "dse" in txt:
        return (
            "🎓 **Demande de bourse étudiante (DSE)**\n\n"
            "Voici comment ça marche :\n"
            "1️⃣ Tu dois créer ton Dossier Social Étudiant sur 👉 etudiant.gouv.fr\n"
            "2️⃣ Prépare : avis fiscal de tes parents, pièces d'identité, certificat de scolarité.\n"
            "3️⃣ Une fois le dossier complet, tu recevras une notification du CROUS.\n"
            "Tu veux que je t’aide à vérifier les documents ? 📄"
        )

    if "carte vitale" in txt:
        return (
            "🟩 **Carte Vitale pour étudiant**\n\n"
            "Pour obtenir ta carte vitale, il te faudra :\n"
            "- ton RIB\n"
            "- une pièce d'identité\n"
            "- une photo d’identité\n\n"
            "Je peux aussi t’envoyer le lien officiel si tu veux !"
        )

    if "caf" in txt:
        return (
            "📑 **CAF – démarches principales**\n\n"
            "Tu peux faire avec moi :\n"
            "- APL\n"
            "- Déclaration de changement de situation\n"
            "- Création de compte CAF\n\n"
            "Que veux-tu faire exactement ? 😊"
        )

    return "Très bien ! Peux-tu préciser ta demande ? Je suis là pour toi 😊"


# ------------ INPUT UTILISATEUR ------------
user_input = st.chat_input("Écris ton message à ÉLIA…")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    response = elia_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()