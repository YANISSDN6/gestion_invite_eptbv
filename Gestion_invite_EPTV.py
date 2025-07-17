import os
import streamlit as st
import json
import pandas as pd
from io import BytesIO
from PIL import Image

# FICHIERS
USERS_FILE = "users.json"
INVITES_FILE = "invites.json"

# === UTILISATEURS ===
def load_users():
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            st.error("Erreur de lecture du fichier users.json.")
            return []

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

def check_credentials(username, password):
    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return True
    return False

def add_user(username, password):
    users = load_users()
    if any(u["username"] == username for u in users):
        return False
    users.append({"username": username, "password": password})
    save_users(users)
    return True

# === INIT SESSION ===
if "page" not in st.session_state:
    st.session_state.page = "login"
if "username" not in st.session_state:
    st.session_state.username = ""
if "invites" not in st.session_state:
    try:
        with open(INVITES_FILE, "r", encoding="utf-8") as f:
            st.session_state.invites = json.load(f)
    except FileNotFoundError:
        st.session_state.invites = []

# === PAGE DE CONNEXION ===
def login_page():
    st.title("Connexion à l'application EPTV")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        if check_credentials(username, password):
            st.session_state.username = username
            st.session_state.page = "main"
            st.rerun()
        else:
            st.error("Identifiants incorrects.")

# === PAGE PRINCIPALE ===
def main_page():
    st.sidebar.title(f"Bienvenue, {st.session_state.username}")
    menu = st.sidebar.selectbox("Menu", [
        "Ajouter un invité",
        "Afficher les invités",
        "Rechercher un invité",
        "Supprimer un invité",
        "Exporter en Excel",
        "Ajouter un utilisateur",
        "Se déconnecter"
    ])

    # Image d'accueil
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title("Portail de Gestion des Invités - EPTV")
        st.write("Bienvenue sur l'application de gestion des invités de l'EPTV.")
    with col2:
        try:
            image = Image.open("photo_eptv.png")
            st.image(image, width=300)
        except:
            pass

    if menu == "Ajouter un invité":
        st.header("Ajouter un invité")
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        domaine = st.text_input("Domaine")
        organisation = st.text_input("Organisation")
        date_invitation = st.date_input("Date d'invitation")
        numero = st.text_input("Numéro")
        emission = st.text_input("Émission")
        chaine = st.text_input("Chaîne")
        studio = st.text_input("Studio")

        if st.button("Enregistrer l'invité"):
            invite = {
                "nom": nom,
                "prenom": prenom,
                "domaine": domaine,
                "organisation": organisation,
                "date d'invitation": str(date_invitation),
                "numero": numero,
                "emission": emission,
                "chaine": chaine,
                "studio": studio
            }
            st.session_state.invites.append(invite)
            with open(INVITES_FILE, "w", encoding="utf-8") as f:
                json.dump(st.session_state.invites, f, ensure_ascii=False, indent=4)
            st.success("Invité ajouté avec succès.")

    elif menu == "Afficher les invités":
        st.header("Liste des invités")
        if st.session_state.invites:
            df = pd.DataFrame(st.session_state.invites)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Aucun invité enregistré.")

    elif menu == "Rechercher un invité":
        st.header("Rechercher un invité")
        recherche = st.text_input("Entrez un nom ou prénom")
        if st.button("Chercher") and recherche:
            df = pd.DataFrame(st.session_state.invites)
            resultats = df[
                df["nom"].str.lower().str.contains(recherche.lower()) |
                df["prenom"].str.lower().str.contains(recherche.lower())
            ]
            if not resultats.empty:
                st.dataframe(resultats, use_container_width=True)
            else:
                st.warning("Aucun invité trouvé.")

    elif menu == "Supprimer un invité":
        st.header("Supprimer un invité")
        if st.session_state.invites:
            noms = [f"{i['nom']} ({i['date d\'invitation']})" for i in st.session_state.invites]
            choix = st.selectbox("Choisir un invité", noms)
            if st.button("Supprimer"):
                nom_sel, date_sel = choix.split(" (")
                date_sel = date_sel.rstrip(")")
                st.session_state.invites = [
                    i for i in st.session_state.invites
                    if not (i["nom"] == nom_sel and i["date d'invitation"] == date_sel)
                ]
                with open(INVITES_FILE, "w", encoding="utf-8") as f:
                    json.dump(st.session_state.invites, f, ensure_ascii=False, indent=4)
                st.success(f"L'invité **{nom_sel}** a été supprimé avec succès.")
                st.rerun()
        else:
            st.info("Aucun invité à supprimer.")

    elif menu == "Exporter en Excel":
        st.subheader("Exporter les invités au format Excel")
        if st.session_state.invites:
            df = pd.DataFrame(st.session_state.invites)
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Invités')
            st.download_button(
                label="Télécharger le fichier Excel",
                data=buffer.getvalue(),
                file_name="invites_eptv.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("Aucun invité à exporter.")

    elif menu == "Ajouter un utilisateur":
        st.header("Ajouter un utilisateur")
        new_user = st.text_input("Nom d'utilisateur")
        new_pass = st.text_input("Mot de passe", type="password")
        if st.button("Créer l'utilisateur"):
            if add_user(new_user, new_pass):
                st.success("Utilisateur ajouté avec succès.")
                st.rerun()
            else:
                st.warning("Cet utilisateur existe déjà.")

    elif menu == "Se déconnecter":
        st.session_state.page = "login"
        st.session_state.username = ""
        st.rerun()

# === ROUTAGE ===
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "main":
    main_page()
