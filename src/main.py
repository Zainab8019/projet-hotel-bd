import sqlite3
import streamlit as st
import os
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Gestion Hôtelière", layout="wide")

# Connexion à la base SQLite avec création automatique du dossier
def create_connection():
    """Crée une connexion à la base SQLite et le dossier data si nécessaire"""
    os.makedirs('data', exist_ok=True)  # Crée le dossier s'il n'existe pas
    db_path = os.path.join('data', 'hotel.db')
    conn = sqlite3.connect(db_path)
    # Pour accéder aux colonnes par nom
    conn.row_factory = sqlite3.Row  
    return conn

# Initialisation de la base de données
def init_db():
    conn = create_connection()
    cursor = conn.cursor()

    # Création des tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Hotel (
        Id_Hotel INTEGER PRIMARY KEY AUTOINCREMENT,
        Ville TEXT NOT NULL,
        Pays TEXT NOT NULL,
        Code_postal INTEGER NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Type_Chambre (
        Id_Type INTEGER PRIMARY KEY AUTOINCREMENT,
        Type TEXT NOT NULL,
        Tarif REAL NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Chambre (
        Numero INTEGER PRIMARY KEY,
        Etage INTEGER NOT NULL,
        Fumeur INTEGER NOT NULL,
        Id_Hotel INTEGER NOT NULL,
        Id_Type INTEGER NOT NULL,
        FOREIGN KEY (Id_Hotel) REFERENCES Hotel(Id_Hotel),
        FOREIGN KEY (Id_Type) REFERENCES Type_Chambre(Id_Type)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Client (
        Id_Client INTEGER PRIMARY KEY AUTOINCREMENT,
        Adresse TEXT NOT NULL,
        Ville TEXT NOT NULL,
        Code_postal INTEGER NOT NULL,
        Email TEXT NOT NULL,
        Telephone TEXT NOT NULL,
        Nom TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reservation (
        Id_Reservation INTEGER PRIMARY KEY AUTOINCREMENT,
        Date_arrivee TEXT NOT NULL,
        Date_depart TEXT NOT NULL,
        Id_Client INTEGER NOT NULL,
        FOREIGN KEY (Id_Client) REFERENCES Client(Id_Client)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reservation_Chambre (
        Id_Reservation INTEGER,
        Numero_chambre INTEGER,
        PRIMARY KEY (Id_Reservation, Numero_chambre),
        FOREIGN KEY (Id_Reservation) REFERENCES Reservation(Id_Reservation),
        FOREIGN KEY (Numero_chambre) REFERENCES Chambre(Numero)
    )''')

    # Nouvelle table pour les prestations/services
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Prestation (
        Id_Prestation INTEGER PRIMARY KEY AUTOINCREMENT,
        Nom TEXT NOT NULL,
        Description TEXT,
        Prix REAL NOT NULL,
        Id_Hotel INTEGER NOT NULL,
        FOREIGN KEY (Id_Hotel) REFERENCES Hotel(Id_Hotel)
    )''')

    # Table pour lier les prestations aux réservations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reservation_Prestation (
        Id_Reservation INTEGER,
        Id_Prestation INTEGER,
        Quantite INTEGER DEFAULT 1,
        PRIMARY KEY (Id_Reservation, Id_Prestation),
        FOREIGN KEY (Id_Reservation) REFERENCES Reservation(Id_Reservation),
        FOREIGN KEY (Id_Prestation) REFERENCES Prestation(Id_Prestation)
    )''')

    # Table pour les évaluations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Evaluation (
        Id_Evaluation INTEGER PRIMARY KEY AUTOINCREMENT,
        Note INTEGER NOT NULL CHECK (Note BETWEEN 1 AND 5),
        Commentaire TEXT,
        Date_evaluation TEXT DEFAULT CURRENT_DATE,
        Id_Client INTEGER NOT NULL,
        Id_Hotel INTEGER NOT NULL,
        FOREIGN KEY (Id_Client) REFERENCES Client(Id_Client),
        FOREIGN KEY (Id_Hotel) REFERENCES Hotel(Id_Hotel)
    )''')

    # Insertion des données de base si les tables sont vides
    if not cursor.execute("SELECT COUNT(*) FROM Hotel").fetchone()[0]:
        # Insertion des données d'exemple
        cursor.executemany('INSERT INTO Hotel VALUES (?, ?, ?, ?)', [
            (1, 'Paris', 'France', 75001),
            (2, 'Lyon', 'France', 69002)
        ])

        cursor.executemany('INSERT INTO Type_Chambre VALUES (?, ?, ?)', [
            (1, 'Simple', 80),
            (2, 'Double', 120)
        ])

        cursor.executemany('INSERT INTO Chambre VALUES (?, ?, ?, ?, ?)', [
            (101, 1, 0, 1, 1),
            (201, 2, 0, 1, 1),
            (202, 2, 0, 1, 1),
            (305, 3, 0, 2, 1),
            (307, 3, 1, 1, 2),
            (410, 4, 0, 2, 2),
            (502, 5, 1, 1, 2),
            (104, 1, 1, 2, 2)
        ])

        cursor.executemany('INSERT INTO Client VALUES (?, ?, ?, ?, ?, ?, ?)', [
            (1, '12 Rue de Paris', 'Paris', 75001, 'jean.dupont@email.fr', '0612345678', 'Jean Dupont'),
            (2, '5 Avenue Victor Hugo', 'Lyon', 69002, 'marie.leroy@email.fr', '0623456789', 'Marie Leroy'),
            (3, '8 Boulevard Saint-Michel', 'Marseille', 13005, 'paul.moreau@email.fr', '0634567890', 'Paul Moreau'),
            (4, '27 Rue Nationale', 'Lille', 59800, 'lucie.martin@email.fr', '0645678901', 'Lucie Martin'),
            (5, '3 Rue des Fleurs', 'Nice', 6000, 'emma.giraud@email.fr', '0656789012', 'Emma Giraud')
        ])

        # Ajout de prestations/services
        cursor.executemany('INSERT INTO Prestation VALUES (?, ?, ?, ?, ?)', [
            (1, 'Petit déjeuner', 'Buffet petit déjeuner complet', 15.0, 1),
            (2, 'Parking', 'Place de parking sécurisée', 10.0, 1),
            (3, 'SPA', 'Accès au spa pendant 1 heure', 40.0, 1),
            (4, 'Petit déjeuner', 'Petit déjeuner continental', 12.0, 2),
            (5, 'Service en chambre', 'Service de restauration en chambre', 25.0, 2)
        ])

        # Ajout d'évaluations
        cursor.executemany('INSERT INTO Evaluation VALUES (?, ?, ?, ?, ?, ?)', [
            (1, 4, 'Très bon séjour, personnel accueillant', '2023-01-15', 1, 1),
            (2, 5, 'Excellent service, chambre spacieuse', '2023-02-20', 2, 1),
            (3, 3, 'Correct mais un peu bruyant', '2023-03-10', 3, 2)
        ])

    conn.commit()
    conn.close()

def rows_to_dict_list(rows):
    """Convertit une liste de sqlite3.Row en liste de dictionnaires classiques (pour éviter erreurs pickling dans Streamlit)"""
    return [dict(row) for row in rows]

# Fonction principale
def main():
    st.title("Bienvenue chez notre Hôtel")

    menu = ["Accueil", "Réservations", "Clients",
            "Chambres Disponibles", "Ajouter Client",
            "Ajouter Réservation", "Prestations", "Évaluations"]
    choice = st.sidebar.selectbox("Menu", menu)

    conn = create_connection()

    if choice == "Accueil":
        st.subheader("Tableau de Bord")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Clients", conn.execute("SELECT COUNT(*) FROM Client").fetchone()[0])

        with col2:
            st.metric("Réservations Actives", conn.execute("""
                SELECT COUNT(*) FROM Reservation 
                WHERE Date_arrivee <= date('now') 
                AND Date_depart >= date('now')
            """).fetchone()[0])

        with col3:
            st.metric("Chambres Occupées", conn.execute("""
                SELECT COUNT(DISTINCT Numero_chambre) 
                FROM Reservation_Chambre rc
                JOIN Reservation r ON rc.Id_Reservation = r.Id_Reservation
                WHERE r.Date_arrivee <= date('now') 
                AND r.Date_depart >= date('now')
            """).fetchone()[0])

        # Afficher la note moyenne des hôtels
        st.subheader("Évaluations des hôtels")
        evaluations = conn.execute('''
            SELECT h.Ville, AVG(e.Note) as Note_moyenne, COUNT(e.Id_Evaluation) as Nombre_evaluations
            FROM Hotel h
            LEFT JOIN Evaluation e ON h.Id_Hotel = e.Id_Hotel
            GROUP BY h.Id_Hotel
        ''').fetchall()

        for eval in evaluations:
            if eval['Note_moyenne']:
                st.write(f"**{eval['Ville']}** - Note moyenne: {eval['Note_moyenne']:.1f}/5 ({eval['Nombre_evaluations']} avis)")
            else:
                st.write(f"**{eval['Ville']}** - Pas encore d'évaluation")

    elif choice == "Réservations":
        st.subheader("Liste des Réservations")
        reservations = conn.execute('''
        SELECT r.Id_Reservation, c.Nom AS Client, h.Ville, 
               r.Date_arrivee, r.Date_depart, ch.Numero AS Chambre,
               SUM(p.Prix * rp.Quantite) as Total_prestations
        FROM Reservation r
        JOIN Client c ON r.Id_Client = c.Id_Client
        JOIN Reservation_Chambre rc ON r.Id_Reservation = rc.Id_Reservation
        JOIN Chambre ch ON rc.Numero_chambre = ch.Numero
        JOIN Hotel h ON ch.Id_Hotel = h.Id_Hotel
        LEFT JOIN Reservation_Prestation rp ON r.Id_Reservation = rp.Id_Reservation
        LEFT JOIN Prestation p ON rp.Id_Prestation = p.Id_Prestation
        GROUP BY r.Id_Reservation
        ORDER BY r.Date_arrivee DESC
        ''').fetchall()

        if not reservations:
            st.warning("Aucune réservation trouvée")
        else:
            st.success(f"{len(reservations)} réservations trouvées")
            for res in reservations:
                with st.expander(f"Réservation #{res['Id_Reservation']} - {res['Client']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Hôtel:** {res['Ville']}")
                        st.write(f"**Chambre:** {res['Chambre']}")
                    with col2:
                        st.write(f"**Arrivée:** {res['Date_arrivee']}")
                        st.write(f"**Départ:** {res['Date_depart']}")
                    
                    # Afficher les prestations associées
                    prestations = conn.execute('''
                        SELECT p.Nom, p.Prix, rp.Quantite
                        FROM Reservation_Prestation rp
                        JOIN Prestation p ON rp.Id_Prestation = p.Id_Prestation
                        WHERE rp.Id_Reservation = ?
                    ''', (res['Id_Reservation'],)).fetchall()
                    
                    if prestations:
                        st.write("**Prestations:**")
                        for presta in prestations:
                            st.write(f"- {presta['Nom']} ({presta['Prix']}€ x {presta['Quantite']})")
                        st.write(f"**Total prestations:** {res['Total_prestations'] or 0:.2f}€")

    elif choice == "Clients":
        st.subheader("Liste des Clients")
        clients = conn.execute("SELECT * FROM Client ORDER BY Nom").fetchall()

        for client in clients:
            with st.expander(f"{client['Nom']}"):
                st.write(f"**Adresse:** {client['Adresse']}, {client['Code_postal']} {client['Ville']}")
                st.write(f"**Email:** {client['Email']}")
                st.write(f"**Téléphone:** {client['Telephone']}")
                
                # Afficher les évaluations du client
                evaluations = conn.execute('''
                    SELECT e.Note, e.Commentaire, e.Date_evaluation, h.Ville
                    FROM Evaluation e
                    JOIN Hotel h ON e.Id_Hotel = h.Id_Hotel
                    WHERE e.Id_Client = ?
                    ORDER BY e.Date_evaluation DESC
                ''', (client['Id_Client'],)).fetchall()
                
                if evaluations:
                    st.write("**Évaluations:**")
                    for eval in evaluations:
                        st.write(f"- {eval['Ville']}: {eval['Note']}/5 le {eval['Date_evaluation']}")
                        if eval['Commentaire']:
                            st.write(f"  *\"{eval['Commentaire']}\"*")

    elif choice == "Chambres Disponibles":
        st.subheader("Recherche de chambres disponibles")
        col1, col2 = st.columns(2)
        with col1:
            date_debut = st.date_input("Date d'arrivée", datetime.now())
        with col2:
            date_fin = st.date_input("Date de départ", datetime.now())

        if st.button("Rechercher"):
            chambres_dispo = conn.execute('''
            SELECT c.Numero, c.Etage, tc.Type, tc.Tarif, h.Ville, c.Fumeur
            FROM Chambre c
            JOIN Type_Chambre tc ON c.Id_Type = tc.Id_Type
            JOIN Hotel h ON c.Id_Hotel = h.Id_Hotel
            WHERE c.Numero NOT IN (
                SELECT rc.Numero_chambre
                FROM Reservation r
                JOIN Reservation_Chambre rc ON r.Id_Reservation = rc.Id_Reservation
                WHERE (r.Date_arrivee <= ? AND r.Date_depart >= ?)
            )
            ORDER BY c.Etage, c.Numero
            ''', (date_fin, date_debut)).fetchall()

            if chambres_dispo:
                st.success(f"{len(chambres_dispo)} chambres disponibles")
                for chambre in chambres_dispo:
                    with st.expander(f"Chambre {chambre['Numero']} - Étage {chambre['Etage']} ({chambre['Type']})"):
                        st.write(f"**Hôtel:** {chambre['Ville']}")
                        st.write(f"**Type:** {chambre['Type']}")
                        st.write(f"**Tarif:** {chambre['Tarif']}€/nuit")
                        st.write(f"**Fumeur:** {'Oui' if chambre['Fumeur'] else 'Non'}")
                        
                        # Afficher les prestations disponibles pour cet hôtel
                        prestations = conn.execute('''
                            SELECT * FROM Prestation 
                            WHERE Id_Hotel = ?
                        ''', (chambre['Id_Hotel'],)).fetchall()
                        
                        if prestations:
                            st.write("**Prestations disponibles:**")
                            for presta in prestations:
                                st.write(f"- {presta['Nom']}: {presta['Prix']}€")
            else:
                st.warning("Aucune chambre disponible pour ces dates")

    elif choice == "Ajouter Client":
        st.subheader("Ajouter un nouveau client")
        with st.form("nouveau_client", clear_on_submit=True):
            nom = st.text_input("Nom complet*")
            adresse = st.text_input("Adresse*")
            ville = st.text_input("Ville*")
            cp = st.number_input("Code postal*", min_value=0, format="%d")
            email = st.text_input("Email*")
            tel = st.text_input("Téléphone*")

            if st.form_submit_button("Enregistrer"):
                if nom and adresse and ville and email and tel:
                    conn.execute('''
                    INSERT INTO Client (Nom, Adresse, Ville, Code_postal, Email, Telephone)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (nom, adresse, ville, cp, email, tel))
                    conn.commit()
                    st.success("Client ajouté avec succès!")
                else:
                    st.error("Veuillez remplir tous les champs obligatoires (*)")

    elif choice == "Ajouter Réservation":
        st.subheader("Nouvelle réservation")

        clients = conn.execute("SELECT Id_Client, Nom FROM Client ORDER BY Nom").fetchall()
        clients_list = rows_to_dict_list(clients)

        hotels = conn.execute("SELECT Id_Hotel, Ville FROM Hotel").fetchall()
        hotels_list = rows_to_dict_list(hotels)

        types_chambre = conn.execute("SELECT Id_Type, Type FROM Type_Chambre").fetchall()
        types_list = rows_to_dict_list(types_chambre)

        if not clients_list:
            st.warning("Veuillez d'abord ajouter des clients.")
            return

        with st.form("form_reservation", clear_on_submit=True):
            client_options = {client['Nom']: client['Id_Client'] for client in clients_list}
            client_nom = st.selectbox("Client", list(client_options.keys()))
            client_id = client_options[client_nom]

            hotel_options = {hotel['Ville']: hotel['Id_Hotel'] for hotel in hotels_list}
            hotel_ville = st.selectbox("Ville de l'hôtel", list(hotel_options.keys()))
            hotel_id = hotel_options[hotel_ville]

            date_arrivee = st.date_input("Date d'arrivée")
            date_depart = st.date_input("Date de départ")

            type_options = {t['Type']: t['Id_Type'] for t in types_list}
            type_chambre = st.selectbox("Type de chambre", list(type_options.keys()))
            type_id = type_options[type_chambre]

            # Récupérer les chambres disponibles selon filtre
            chambres_dispo = conn.execute('''
                SELECT Numero FROM Chambre
                WHERE Id_Hotel = ? AND Id_Type = ? AND Numero NOT IN (
                    SELECT rc.Numero_chambre FROM Reservation r
                    JOIN Reservation_Chambre rc ON r.Id_Reservation = rc.Id_Reservation
                    WHERE (r.Date_arrivee <= ? AND r.Date_depart >= ?)
                )
            ''', (hotel_id, type_id, date_depart, date_arrivee)).fetchall()

            chambres_list = [row['Numero'] for row in chambres_dispo]

            if not chambres_list:
                st.warning("Aucune chambre disponible pour ce choix de dates, ville et type.")
            else:
                chambre_numero = st.selectbox("Numéro de chambre", chambres_list)
                
                # Sélection des prestations
                prestations = conn.execute('''
                    SELECT * FROM Prestation WHERE Id_Hotel = ?
                ''', (hotel_id,)).fetchall()
                
                prestations_selection = {}
                if prestations:
                    st.write("**Prestations supplémentaires:**")
                    for presta in prestations:
                        qty = st.number_input(
                            f"{presta['Nom']} ({presta['Prix']}€)",
                            min_value=0,
                            max_value=10,
                            key=f"presta_{presta['Id_Prestation']}"
                        )
                        if qty > 0:
                            prestations_selection[presta['Id_Prestation']] = qty

                if st.form_submit_button("Réserver"):
                    if date_arrivee >= date_depart:
                        st.error("La date de départ doit être après la date d'arrivée.")
                    else:
                        # Insertion réservation
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO Reservation (Date_arrivee, Date_depart, Id_Client)
                            VALUES (?, ?, ?)
                        ''', (date_arrivee.isoformat(), date_depart.isoformat(), client_id))
                        id_reservation = cursor.lastrowid

                        # Insertion liaison chambre-réservation
                        cursor.execute('''
                            INSERT INTO Reservation_Chambre (Id_Reservation, Numero_chambre)
                            VALUES (?, ?)
                        ''', (id_reservation, chambre_numero))

                        # Insertion des prestations
                        for presta_id, qty in prestations_selection.items():
                            cursor.execute('''
                                INSERT INTO Reservation_Prestation (Id_Reservation, Id_Prestation, Quantite)
                                VALUES (?, ?, ?)
                            ''', (id_reservation, presta_id, qty))

                        conn.commit()
                        st.success(f"Réservation créée avec succès pour {client_nom} en chambre {chambre_numero} du {date_arrivee} au {date_depart}")

    elif choice == "Prestations":
        st.subheader("Gestion des Prestations")
        
        tab1, tab2 = st.tabs(["Liste des Prestations", "Ajouter une Prestation"])
        
        with tab1:
            prestations = conn.execute('''
                SELECT p.*, h.Ville 
                FROM Prestation p
                JOIN Hotel h ON p.Id_Hotel = h.Id_Hotel
                ORDER BY h.Ville, p.Nom
            ''').fetchall()
            
            if not prestations:
                st.warning("Aucune prestation disponible")
            else:
                for presta in prestations:
                    with st.expander(f"{presta['Nom']} - {presta['Ville']}"):
                        st.write(f"**Description:** {presta['Description']}")
                        st.write(f"**Prix:** {presta['Prix']}€")
                        
                        # Statistiques d'utilisation
                        usage = conn.execute('''
                            SELECT COUNT(*) as Nb_utilisations, SUM(Quantite) as Total_quantite
                            FROM Reservation_Prestation
                            WHERE Id_Prestation = ?
                        ''', (presta['Id_Prestation'],)).fetchone()
                        st.write(f"**Utilisations:** {usage['Nb_utilisations']} fois ({usage['Total_quantite']} au total)")
        
        with tab2:
            with st.form("nouvelle_prestation"):
                hotels = conn.execute("SELECT Id_Hotel, Ville FROM Hotel").fetchall()
                hotel_options = {hotel['Ville']: hotel['Id_Hotel'] for hotel in hotels}
                
                nom = st.text_input("Nom de la prestation*")
                description = st.text_area("Description")
                prix = st.number_input("Prix*", min_value=0.0, step=0.5, format="%.2f")
                hotel = st.selectbox("Hôtel*", list(hotel_options.keys()))
                
                if st.form_submit_button("Ajouter"):
                    if nom and prix:
                        conn.execute('''
                            INSERT INTO Prestation (Nom, Description, Prix, Id_Hotel)
                            VALUES (?, ?, ?, ?)
                        ''', (nom, description, prix, hotel_options[hotel]))
                        conn.commit()
                        st.success("Prestation ajoutée avec succès!")
                    else:
                        st.error("Veuillez remplir les champs obligatoires (*)")

    elif choice == "Évaluations":
        st.subheader("Évaluations des Clients")
        
        tab1, tab2 = st.tabs(["Liste des Évaluations", "Ajouter une Évaluation"])
        
        with tab1:
            evaluations = conn.execute('''
                SELECT e.*, c.Nom as Client, h.Ville
                FROM Evaluation e
                JOIN Client c ON e.Id_Client = c.Id_Client
                JOIN Hotel h ON e.Id_Hotel = h.Id_Hotel
                ORDER BY e.Date_evaluation DESC
            ''').fetchall()
            
            if not evaluations:
                st.warning("Aucune évaluation disponible")
            else:
                for eval in evaluations:
                    with st.expander(f"{eval['Client']} - {eval['Ville']} ({eval['Note']}/5)"):
                        st.write(f"**Date:** {eval['Date_evaluation']}")
                        st.write(f"**Note:** {eval['Note']}/5")
                        if eval['Commentaire']:
                            st.write(f"**Commentaire:** {eval['Commentaire']}")
        
        with tab2:
            with st.form("nouvelle_evaluation"):
                clients = conn.execute("SELECT Id_Client, Nom FROM Client ORDER BY Nom").fetchall()
                client_options = {client['Nom']: client['Id_Client'] for client in clients}
                
                hotels = conn.execute("SELECT Id_Hotel, Ville FROM Hotel").fetchall()
                hotel_options = {hotel['Ville']: hotel['Id_Hotel'] for hotel in hotels}
                
                client = st.selectbox("Client*", list(client_options.keys()))
                hotel = st.selectbox("Hôtel*", list(hotel_options.keys()))
                note = st.slider("Note*", 1, 5, 3)
                commentaire = st.text_area("Commentaire")
                
                if st.form_submit_button("Envoyer"):
                    conn.execute('''
                        INSERT INTO Evaluation (Note, Commentaire, Id_Client, Id_Hotel)
                        VALUES (?, ?, ?, ?)
                    ''', (note, commentaire, client_options[client], hotel_options[hotel]))
                    conn.commit()
                    st.success("Évaluation enregistrée avec succès!")

    conn.close()

if __name__ == "__main__":
    init_db()
    main()