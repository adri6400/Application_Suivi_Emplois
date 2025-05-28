import streamlit as st
import sqlite3
from sqlite3 import Connection
import os

# Chemin vers la base de données SQLite
DB_PATH = os.path.join(os.path.dirname(__file__), 'applications.db')

# Initialisation et obtention de la connexion à la base de données
# On utilise check_same_thread=False pour éviter les erreurs de threads
# On ajoute la colonne "status" avec valeur par défaut 'Postulé'
def get_db_connection() -> Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            cover_letter TEXT,
            status TEXT NOT NULL DEFAULT 'Postulé'
        )
        ''')
    # S'assure que la colonne status existe (au cas où la table pré-existe sans elle)
    existing_cols = [col[1] for col in conn.execute("PRAGMA table_info(applications)")]
    if 'status' not in existing_cols:
        conn.execute("ALTER TABLE applications ADD COLUMN status TEXT NOT NULL DEFAULT 'Postulé'")
    conn.commit()
    return conn

# Ajouter une nouvelle candidature
def add_application(company: str, title: str, description: str, cover_letter: str, status: str):
    conn = get_db_connection()
    conn.execute(
        '''INSERT INTO applications (company, title, description, cover_letter, status)
           VALUES (?, ?, ?, ?, ?)''',
        (company, title, description, cover_letter, status)
    )
    conn.commit()
    conn.close()

# Mettre à jour une candidature existante
def update_application(app_id: int, company: str, title: str, description: str, cover_letter: str, status: str):
    conn = get_db_connection()
    conn.execute(
        '''UPDATE applications
           SET company = ?, title = ?, description = ?, cover_letter = ?, status = ?
           WHERE id = ?''',
        (company, title, description, cover_letter, status, app_id)
    )
    conn.commit()
    conn.close()

# Supprimer une candidature
def delete_application(app_id: int):
    conn = get_db_connection()
    conn.execute('DELETE FROM applications WHERE id = ?', (app_id,))
    conn.commit()
    conn.close()

# Récupère toutes les candidatures
def fetch_all_applications():
    conn = get_db_connection()
    cur = conn.execute('SELECT id, company, title, status FROM applications ORDER BY id DESC')
    rows = cur.fetchall()
    conn.close()
    return rows

# Récupère une candidature par son id
def fetch_application_by_id(app_id: int):
    conn = get_db_connection()
    cur = conn.execute(
        'SELECT company, title, description, cover_letter, status FROM applications WHERE id = ?', (app_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row

# Page d'affichage et modification des candidatures
def show_applications():
    st.header("Mes candidatures")
    apps = fetch_all_applications()
    if not apps:
        st.info("Aucune candidature enregistrée pour l'instant.")
        return

    status_colors = {'Postulé': 'orange', 'Réponse négative': 'red', 'Réponse positive': 'green'}
    options = {}
    for id_, comp, title, stat in apps:
        color = status_colors.get(stat, 'black')
        label = f"{comp} - {title}   "  # point coloré ajouté
        options[label] = id_

    selected_label = st.selectbox(
        "Choisir une candidature", list(options.keys()), format_func=lambda x: x, key='sel'
    )
    selected_id = options[selected_label]

    data = fetch_application_by_id(selected_id)
    if data:
        comp, title, desc, cover, stat = data
        st.subheader(f"{comp} - {title}")
        st.markdown(
            f"**Statut**: <span style='color:{status_colors.get(stat, 'black')}'>{stat}</span>",
            unsafe_allow_html=True
        )
        # Bouton de suppression
        if st.button("Supprimer cette candidature", key='delete_' + str(selected_id)):
            delete_application(selected_id)
            st.success("Candidature supprimée.")
            st.rerun()

        with st.expander("Description de l'offre", expanded=True):
            st.write(desc)
        with st.expander("Lettre de motivation", expanded=True):
            st.write(cover)

        # Formulaire de modification
        with st.expander("Modifier la candidature"):
            with st.form(key='edit_app_form'):
                new_company = st.text_input("Nom de l'entreprise", value=comp)
                new_title = st.text_input("Intitulé du poste", value=title)
                new_desc = st.text_area("Description de l'offre", value=desc)
                new_cover = st.text_area("Lettre de motivation", value=cover)
                new_status = st.selectbox(
                    "Statut",
                    ['Postulé', 'Réponse négative', 'Réponse positive'],
                    index=['Postulé', 'Réponse négative', 'Réponse positive'].index(stat)
                )
                submitted = st.form_submit_button("Enregistrer les modifications")
                if submitted:
                    update_application(
                        selected_id,
                        new_company.strip(), new_title.strip(),
                        new_desc.strip(), new_cover.strip(), new_status
                    )
                    st.success("Candidature mise à jour avec succès !")

# Page de formulaire pour ajouter une candidature
def add_application_form():
    st.header("Ajouter une nouvelle candidature")
    with st.form(key='add_app_form'):
        company = st.text_input("Nom de l'entreprise")
        title = st.text_input("Intitulé du poste")
        description = st.text_area("Description de l'offre")
        cover_letter = st.text_area("Lettre de motivation")
        status = st.selectbox(
            "Statut", ['Postulé', 'Réponse négative', 'Réponse positive'], index=0
        )
        submitted = st.form_submit_button("Enregistrer")
        if submitted:
            if company.strip() and title.strip():
                add_application(
                    company.strip(), title.strip(),
                    description.strip(), cover_letter.strip(), status
                )
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
