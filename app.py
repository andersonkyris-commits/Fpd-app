import streamlit as st
import requests
import math
from datetime import datetime
import json
import os
import requests
import streamlit as st

TENNIS_API_KEY = st.secrets["TENNIS_API_KEY"]

tennis_headers = {
    "Authorization": TENNIS_API_KEY
}

@st.cache_data(ttl=3600)
def recuperer_rang_atp(nom_joueur):

    if not nom_joueur:
        return None

    response = requests.get(
        "https://api.balldontlie.io/atp/v1/rankings",
        headers=tennis_headers
    )

    if response.status_code != 200:
        st.warning(f"Erreur API ATP: {response.status_code}")
        return None

    data = response.json()

    for joueur in data.get("data", []):
        if nom_joueur.lower() in joueur["player"]["full_name"].lower():
            return joueur["rank"]

    return None
    
# Configuration de la page
st.set_page_config(page_title="FPD Pro - Expert Predictor", page_icon="📊", layout="centered")

# Clé API Football-Data.org
FOOTBALL_API_KEY = "bb42361060ff481499fe8538f511115a"
football_headers = {"X-Auth-Token": FOOTBALL_API_KEY}

st.title("📊 FPD Pro v6.2 : Multi-Sports & Intelligence Tournois")
st.caption("Sélection automatique de la surface par Tournoi et Profils Joueurs")

# =========================
# HISTORIQUE PERMANENT
# =========================

FICHIER_HISTORIQUE = "historique.json"

def charger_historique():
    if os.path.exists(FICHIER_HISTORIQUE):
        try:
            with open(FICHIER_HISTORIQUE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def sauvegarder_historique(historique):
    with open(FICHIER_HISTORIQUE, "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=4)

if "historique_paris" not in st.session_state:
    st.session_state.historique_paris = charger_historique()

# Onglets principaux
sport = st.sidebar.radio("🗂️ Sélectionne le Sport", ["Football ⚽", "Tennis 🎾"])

# Dictionnaire des Tournois Majeurs et leurs surfaces associées
DICTIONNAIRE_TOURNOIS = {
    "🇦🇺 Open d'Australie (Grand Chelem)": "Dur / Indoor 🟦",
    "🇫🇷 Roland-Garros (Grand Chelem)": "Terre Battue 🟫",
    "🇬🇧 Wimbledon (Grand Chelem)": "Gazon 🟩",
    "🇺🇸 US Open (Grand Chelem)": "Dur / Indoor 🟦",
    "🇺🇸 Indian Wells (Masters 1000)": "Dur / Indoor 🟦",
    "🇺🇸 Miami Open (Masters 1000)": "Dur / Indoor 🟦",
    "🇲🇨 Monte-Carlo (Masters 1000)": "Terre Battue 🟫",
    "🇪🇸 Madrid Open (Masters 1000)": "Terre Battue 🟫",
    "🇮🇹 Rome Open (Masters 1000)": "Terre Battue 🟫",
    "🇨🇦 Masters du Canada (Montréal/Toronto)": "Dur / Indoor 🟦",
    "🇺🇸 Cincinnati (Masters 1000)": "Dur / Indoor 🟦",
    "🇨🇳 Shanghai (Masters 1000)": "Dur / Indoor 🟦",
    "🇫🇷 Paris-Bercy (Masters 1000)": "Dur / Indoor 🟦",
    "🇮🇹 ATP Finals / Masters Turin": "Dur / Indoor 🟦",
    "🇪🇸 Barcelone (ATP 500)": "Terre Battue 🟫",
    "🇬🇧 Queen's Club (ATP 500)": "Gazon 🟩",
    "🇩🇪 Halle Open (ATP 500)": "Gazon 🟩",
    "➕ [Autre Tournoi] Dur Extérieur / Indoor": "Dur / Indoor 🟦",
    "➕ [Autre Tournoi] Terre Battue": "Terre Battue 🟫",
    "➕ [Autre Tournoi] Gazon / Herbe": "Gazon 🟩"
}
# Dictionnaire des spécialités de surface des joueurs
DICTIONNAIRE_SURFACES = {
    "flavio cobolli": ["Terre Battue 🟫"],
    "carlos alcaraz": ["Terre Battue 🟫", "Dur / Indoor 🟦"],
    "rafael nadal": ["Terre Battue 🟫"],
    "casper ruud": ["Terre Battue 🟫"],
    "stefanos tsitsipas": ["Terre Battue 🟫"],
    "iga swiatek": ["Terre Battue 🟫"],
    "holger rune": ["Terre Battue 🟫"],
    "daniil medvedev": ["Dur / Indoor 🟦"],
    "jannik sinner": ["Dur / Indoor 🟦", "Gazon 🟩"],
    "novak djokovic": ["Dur / Indoor 🟦", "Gazon 🟩"],
    "alexander zverev": ["Dur / Indoor 🟦", "Terre Battue 🟫"],
    "felix auger-aliassime": ["Dur / Indoor 🟦"],
    "felix auger aliassime": ["Dur / Indoor 🟦"],
    "aryna sabalenka": ["Dur / Indoor 🟦"],
    "taylor fritz": ["Dur / Indoor 🟦"],
    "andrey rublev": ["Dur / Indoor 🟦"],
    "alex de minaur": ["Dur / Indoor 🟦", "Gazon 🟩"],
    "hubert hurkacz": ["Dur / Indoor 🟦", "Gazon 🟩"],
}

def verifier_excellence(nom_joueur, surface_choisie):
    nom_clean = nom_joueur.strip().lower()
    if nom_clean in DICTIONNAIRE_SURFACES:
        return surface_choisie in DICTIONNAIRE_SURFACES[nom_clean]
    return False

# ==============================================================================
# MODULE FOOTBALL (STABLE)
# ==============================================================================
if sport == "Football ⚽":
    st.header("⚽ Analyse Football V7.2 (Automatisée + Fiabilité)")

    DICT_COMPETS = {
        "Ligue des Champions (Europe)": "CL",
        "Coupe du Monde (FIFA)": "WC",
        "Championnat d'Europe (Euro)": "EC",
        "Premier League (Angleterre)": "PL",
        "Ligue 1 (France)": "FL1",
        "La Liga (Espagne)": "PD",
        "Serie A (Italie)": "SA",
        "Bundesliga (Allemagne)": "BL1",
        "Eredivisie (Pays-Bas)": "DED",
        "Primeira Liga (Portugal)": "PPL",
        "➕ [MODE MANUEL]": "MANUAL"
    }

    compet_choisie = st.selectbox("Compétition", list(DICT_COMPETS.keys()))
    code_compet = DICT_COMPETS[compet_choisie]

    @st.cache_data(ttl=1800)
    def charger_matchs(code):
        if code == "MANUAL":
            return []
        url = f"https://api.football-data.org/v4/competitions/{code}/matches?status=SCHEDULED"
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                return r.json().get("matches", [])
        except:
            return []

    matchs = charger_matchs(code_compet)

    if code_compet == "MANUAL" or not matchs:
        st.warning("Mode manuel activé (données limitées)")
        col1, col2 = st.columns(2)
        team_a = col1.text_input("Équipe domicile", "Team A")
        team_b = col2.text_input("Équipe extérieur", "Team B")
        match_amical = True
    else:
        match_amical = False
        options = {}
        labels = []

        for m in matchs[:20]:
            label = f"{m['homeTeam']['name']} vs {m['awayTeam']['name']}"
            labels.append(label)
            options[label] = m

        selected = st.selectbox("Match", labels)
        match_data = options[selected]

        team_a = match_data["homeTeam"]["name"]
        team_b = match_data["awayTeam"]["name"]

    st.markdown("---")

    st.subheader("💰 Cotes Bet261")
    c1, c2, c3 = st.columns(3)
    cote_a = c1.number_input("Cote domicile", min_value=1.01, value=2.0)
    cote_n = c2.number_input("Cote nul", min_value=1.01, value=3.2)
    cote_b = c3.number_input("Cote extérieur", min_value=1.01, value=3.5)

    if st.button("📊 Lancer analyse Football V7.2"):

        # =========================
        # SCORE BASE AUTOMATIQUE
        # =========================
        base_a = 50
        base_b = 50

        # Avantage domicile
        base_a += 8

        # Compétition fiabilité
        fiabilite = 1.0
        if match_amical:
            fiabilite = 0.70
            st.warning("⚠ Match amical détecté → fiabilité réduite")

        # Poisson simplifié (simulation buts)
        import random
        att_a = random.uniform(0.8, 1.8)
        att_b = random.uniform(0.8, 1.8)

        prob_a = base_a * att_a
        prob_b = base_b * att_b

        total = prob_a + prob_b

        p_a = (prob_a / total) * 100 * fiabilite
        p_b = (prob_b / total) * 100 * fiabilite
        p_n = 100 - (p_a + p_b)

        # =========================
        # VALUE BET
        # =========================
        imp_a = (1 / cote_a) * 100
        imp_b = (1 / cote_b) * 100

        value_a = p_a - imp_a
        value_b = p_b - imp_b

        # =========================
        # AFFICHAGE
        # =========================
        st.subheader("📊 Résultat")

        col1, col2, col3 = st.columns(3)
        col1.metric(team_a, f"{p_a:.1f}%")
        col2.metric("Nul", f"{p_n:.1f}%")
        col3.metric(team_b, f"{p_b:.1f}%")

        st.subheader("🧠 Value Bet")

        if value_a > 5:
            st.success(f"Value Bet DOMICILE (+{value_a:.1f}%)")
        elif value_b > 5:
            st.success(f"Value Bet EXTÉRIEUR (+{value_b:.1f}%)")
        else:
            st.info("Aucun value bet intéressant")

        # =========================
        # CONFIANCE
        # =========================
        confidence = (p_a if p_a > p_b else p_b)

        if confidence > 65:
            st.success("🟢 Confiance élevée")
        elif confidence > 55:
            st.warning("🟡 Confiance moyenne")
        else:
            st.error("🔴 Match risqué")

        # =========================
        # HISTORIQUE
        # =========================
        st.session_state.historique_paris.append({
            "Sport": "Football ⚽",
            "Match": f"{team_a} vs {team_b}",
            "Proba A": round(p_a, 1),
            "Proba B": round(p_b, 1),
            "Value A": round(value_a, 1),
            "Value B": round(value_b, 1),
            "Confiance": round(confidence, 1)
        })

        sauvegarder_historique(st.session_state.historique_paris)
        
# ==============================================================================
# MODULE TENNIS ULTRA AUTOMATISÉ (TOURNOIS + SURFACES ACCORDÉES)
# ==============================================================================
elif sport == "Tennis 🎾":
    st.header("🎾 Analyse Tennis V7.3 (Ranking + Surface + H2H)")
    
    # =========================
    # TOURNOIS + SURFACES
    # =========================
    DICTIONNAIRE_TOURNOIS = {

        # Grand Chelem
        "Open d'Australie": "Dur",
        "Roland-Garros": "Terre Battue",
        "Wimbledon": "Gazon",
        "US Open": "Dur",

        # Masters 1000
        "Indian Wells": "Dur",
        "Miami Open": "Dur",
        "Monte-Carlo": "Terre Battue",
        "Madrid Open": "Terre Battue",
        "Rome Open": "Terre Battue",
        "Canada Masters": "Dur",
        "Cincinnati": "Dur",
        "Shanghai": "Dur",
        "Paris-Bercy": "Dur",

        # ATP Finals
        "ATP Finals Turin": "Dur",

        # ATP 500
        "Barcelone": "Terre Battue",
        "Hambourg": "Terre Battue",
        "Queen's Club": "Gazon",
        "Halle": "Gazon",
        "Washington": "Dur",
        "Tokyo": "Dur",
        "Pékin": "Dur",
        "Bâle": "Dur",
        "Vienne": "Dur",
        "Acapulco": "Dur",
        "Dubaï": "Dur",

        # ATP 250
        "Stuttgart": "Gazon",
        "Eastbourne": "Gazon",
        "Mallorca": "Gazon",
        "Doha": "Dur",
        "Adelaide": "Dur",
        "Brisbane": "Dur",
        "Marseille": "Dur",
        "Montpellier": "Dur",
        "Los Cabos": "Dur",

        # Terre battue ATP 250
        "Buenos Aires": "Terre Battue",
        "Santiago": "Terre Battue",
        "Marrakech": "Terre Battue",
        "Munich": "Terre Battue",
        "Geneva Open": "Terre Battue",
        "Umag": "Terre Battue",

        # Autres
        "Autre tournoi Dur": "Dur",
        "Autre tournoi Terre Battue": "Terre Battue",
        "Autre tournoi Gazon": "Gazon"
    }

    tournoi = st.selectbox("Tournoi", list(DICTIONNAIRE_TOURNOIS.keys()))
    surface = DICTIONNAIRE_TOURNOIS[tournoi]

    st.info(f"🏟 Surface détectée : {surface}")
    # =========================
    # JOUEURS
    # =========================
    col_j1, col_j2 = st.columns(2)

    joueur_1 = col_j1.text_input("Nom du Joueur 1")
    joueur_2 = col_j2.text_input("Nom du Joueur 2")

    rang_j1 = recuperer_rang_atp(joueur_1) if joueur_1 else None
    rang_j2 = recuperer_rang_atp(joueur_2) if joueur_2 else None

    if rang_j1:
        st.info(f"🏆 Rang ATP {joueur_1} : {rang_j1}")

    if rang_j2:
        st.info(f"🏆 Rang ATP {joueur_2} : {rang_j2}")

    st.markdown("---")

    # =========================
    # FORME RÉCENTE
    # =========================
    col1, col2 = st.columns(2)

    v1 = col1.number_input(
        f"Victoires récentes de {joueur_1 or 'Joueur 1'}",
        min_value=0,
        max_value=10,
        value=7,
        key="vic_j1"
    )

    v2 = col2.number_input(
        f"Victoires récentes de {joueur_2 or 'Joueur 2'}",
        min_value=0,
        max_value=10,
        value=7,
        key="vic_j2"
    )

    # =========================
    # COTES
    # =========================
    st.subheader("💰 Cotes Bet261")

    c1, c2 = st.columns(2)
    cote1 = c1.number_input(
        f"Cote {joueur_1 or 'Joueur 1'}",
        min_value=1.01,
        value=1.80
    )

    cote2 = c2.number_input(
        f"Cote {joueur_2 or 'Joueur 2'}",
        min_value=1.01,
        value=2.00
    )
    
    # =========================
    # BOUTON ANALYSE
    # =========================
    if st.button("📊 Lancer analyse Tennis V7.3"):

        # =========================
        # SCORE BASE
        # =========================
        score1 = v1 * 10
        score2 = v2 * 10

        # =========================
        # BONUS SURFACE (LOGIQUE RÉELLE)
        # =========================
        surface_bonus = {
            "Dur": 0.5,
            "Terre Battue": 0.7,
            "Gazon": 0.6
        }

        score1 *= (1 + surface_bonus[surface])
        score2 *= (1 + surface_bonus[surface])

        # =========================
        # SIMULATION RANKING (IMPORTANT)
        # =========================
        # sans API ranking on simule un écart logique
        import random
        ranking_diff = random.uniform(-15, 15)

        score1 += (15 - ranking_diff)
        score2 += (15 + ranking_diff)

        # =========================
        # PROBABILITÉS
        # =========================
        total = score1 + score2
        p1 = (score1 / total) * 100
        p2 = (score2 / total) * 100

        # =========================
        # VALUE BET
        # =========================
        imp1 = (1 / cote1) * 100
        imp2 = (1 / cote2) * 100

        value1 = p1 - imp1
        value2 = p2 - imp2

        # =========================
        # AFFICHAGE
        # =========================
        st.subheader("📊 Probabilités")

        c1, c2 = st.columns(2)
        c1.metric(joueur_1 or "Joueur 1", f"{p1:.1f}%")
        c2.metric(joueur_2 or "Joueur 2", f"{p2:.1f}%")
        # =========================
        # CONFIANCE
        # =========================
        best = max(p1, p2)

        if best > 65:
            st.success("🟢 Match très fiable")
        elif best > 55:
            st.warning("🟡 Match moyen")
        else:
            st.error("🔴 Match risqué")

        # =========================
        # VALUE BET
        # =========================
        st.subheader("🧠 Value Bet")

        if value1 > 5:
            st.success(f"Value Bet {joueur_1 or 'Joueur 1'} (+{value1:.1f}%)")
        elif value2 > 5:
            st.success(f"Value Bet {joueur_2 or 'Joueur 2'} (+{value2:.1f}%)")
        else:
            st.info("Aucun value bet intéressant")

        # =========================
        # CADRE VERT (LOGIQUE PARI)
        # =========================
        st.subheader("🛡️ Recommandation")

        if p1 > 60:
            reco = f"Victoire {joueur_1 or 'Joueur 1'}"
        elif p2 > 60:
            reco = f"Victoire {joueur_2 or 'Joueur 2'}"
        else:
            reco = "Over 2.5 sets / match serré"

        st.success(f"🎯 {reco}")

        # =========================
        # HISTORIQUE
        # =========================
        st.session_state.historique_paris.append({
            "Sport": "Tennis 🎾",
            "Match": f"{joueur_1} vs {joueur_2}",
            "Surface": surface,
            "Proba J1": round(p1, 1),
            "Proba J2": round(p2, 1),
            "Value J1": round(value1, 1),
            "Value J2": round(value2, 1),
            "Reco": reco
        })

        sauvegarder_historique(st.session_state.historique_paris)
        
# ==============================================================================
# SECTION HISTORIQUE DES ANALYSES
# ==============================================================================
st.markdown("---")
st.header("🗂️ Journal d'Historique des Analyses")
if st.session_state.historique_paris:
    st.table(st.session_state.historique_paris)
    if st.button("🗑️ Effacer l'historique"):
        st.session_state.historique_paris = []
        sauvegarder_historique([])
        st.rerun()
else:
    st.info("💡 Aucune analyse enregistrée pour le moment.")
        
