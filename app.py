import streamlit as st
import sqlite3
from sqlite3 import Connection
import os

# Chemin vers la base de données SQLite
DB_PATH = os.path.join(os.path.dirname(__file__), 'applications.db')

# Initialisation et obtention de la connexion à la base de données
# On utilise check_same_thread=False pour éviter les erreurs de threads
def get_db_connection() -> Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            cover_letter TEXT
        )
        ''')
    conn.commit()
    return conn

# Ajoute une nouvelle candidature
def add_application(company: str, title: str, description: str, cover_letter: str):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO applications (company, title, description, cover_letter) VALUES (?, ?, ?, ?)',
        (company, title, description, cover_letter)
    )
    conn.commit()
    conn.close()

# Récupère toutes les candidatures
def fetch_all_applications():
    conn = get_db_connection()
    cur = conn.execute('SELECT id, company, title FROM applications ORDER BY id DESC')
    rows = cur.fetchall()
    conn.close()
    return rows

# Récupère une candidature par son id
def fetch_application_by_id(app_id: int):
    conn = get_db_connection()
    cur = conn.execute(
        'SELECT company, title, description, cover_letter FROM applications WHERE id = ?', (app_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row

# Page d'affichage des candidatures
def show_applications():
    st.header("Mes candidatures")
    apps = fetch_all_applications()
    if not apps:
        st.info("Aucune candidature enregistrée pour l'instant.")
        return

    options = {f"{row[1]} - {row[2]}": row[0] for row in apps}
    selected_label = st.selectbox("Choisir une candidature", list(options.keys()))
    selected_id = options[selected_label]

    app = fetch_application_by_id(selected_id)
    if app:
        company, title, description, cover_letter = app
        st.subheader(f"{company} - {title}")
        with st.expander("Description de l'offre", expanded=True):
            st.write(description)
        with st.expander("Lettre de motivation", expanded=True):
            st.write(cover_letter)

# Page de formulaire pour ajouter une candidature
def add_application_form():
    st.header("Ajouter une nouvelle candidature")
    with st.form(key='add_app_form'):
        company = st.text_input("Nom de l'entreprise")
        title = st.text_input("Intitulé du poste")
        description = st.text_area("Description de l'offre")
        cover_letter = st.text_area("Lettre de motivation")
        submitted = st.form_submit_button("Enregistrer")
        if submitted:
            if company.strip() and title.strip():
                add_application(company.strip(), title.strip(), description.strip(), cover_letter.strip())
                st.success("Candidature ajoutée avec succès !")
            else:
                st.error("Veuillez renseigner au moins le nom de l'entreprise et l'intitulé du poste.")

# Fonction principale
def main():
    st.title("Suivi de candidatures")
    menu = ["Voir mes candidatures", "Ajouter une candidature"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Voir mes candidatures":
        show_applications()
    else:
        add_application_form()

if __name__ == '__main__':
    main()