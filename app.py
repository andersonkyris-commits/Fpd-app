import streamlit as st
import requests
import math
from datetime import datetime
import time
import json
import os
import requests
import streamlit as st

TENNIS_API_KEY = st.secrets["TENNIS_API_KEY"]

tennis_headers = {
    "Authorization": TENNIS_API_KEY
}

@st.cache_data(ttl=3600)
def recuperer_tous_les_rankings():
    time.sleep(0.5)  # petit buffer anti spam

    tous_les_rankings = []
    cursor = None

    while True:
        url = "https://api.balldontlie.io/atp/v1/rankings"

        if cursor:
            url += f"?cursor={cursor}"

        st.write("Cursor actuel :", cursor)
       
        response = requests.get(url, headers=tennis_headers)

        if response.status_code == 429:
            break

        if response.status_code != 200:
            break

        data = response.json()
        tous_les_rankings.extend(data.get("data", []))

        cursor = data.get("meta", {}).get("next_cursor")

        if not cursor:
            break

    return tous_les_rankings
    
def charger_rankings_safe():
    if "rankings" in st.session_state:
        return st.session_state.rankings

    data = recuperer_tous_les_rankings()
    st.session_state.rankings = data
    return data

def recuperer_rang_atp(nom_joueur, rankings):

    if not nom_joueur:
        return None

    nom = nom_joueur.lower().strip()

    for joueur in rankings:
        if nom in joueur["player"]["full_name"].lower():
            return joueur["rank"]

    return None

@st.cache_data(ttl=3600)
def recuperer_tournois():

    tous_les_tournois = []
    cursor = None

    while True:

        url = "https://api.balldontlie.io/atp/v1/tournaments"

        if cursor:
            url += f"?cursor={cursor}"

        response = requests.get(
            url,
            headers=tennis_headers
        )

        if response.status_code != 200:
            st.warning(f"Erreur API Tournois : {response.status_code}")
            break

        data = response.json()

        tous_les_tournois.extend(
            data.get("data", [])
        )

        cursor = (
            data.get("meta", {})
                .get("next_cursor")
        )

        if not cursor:
            break

    return tous_les_tournois

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
    st.header("🎾 Analyse Tennis V7.4 (Tournois API)")
    
    try:
        r = requests.get(
            "https://api.balldontlie.io/atp/v1/rankings",
            headers=tennis_headers
        )

        st.write("Status Rankings :", r.status_code)

    except Exception as e:
        st.write("Erreur :", e)

    tournois = recuperer_tournois()
    
    if not tournois:
        st.warning("Aucun tournoi disponible")
        st.stop()

    options_tournois = {
        t["name"]: t for t in tournois
    }

    tournoi_nom = st.selectbox(
        "🏆 Tournoi ATP",
        list(options_tournois.keys()),
        key="tournoi_atp"
    )

    tournoi = options_tournois[tournoi_nom]

    surface = tournoi.get("surface") or "Hard"
    categorie = tournoi.get("category") or "Inconnue"

    st.info(f"🏟 Surface : {surface}")
    st.info(f"🏆 Catégorie : {categorie}")

    # =========================
    # JOUEURS
    # =========================
    col_j1, col_j2 = st.columns(2)

    joueur_1 = col_j1.text_input("Nom du Joueur 1")
    joueur_2 = col_j2.text_input("Nom du Joueur 2")

    rankings = []

    if joueur_1 or joueur_2:
        rankings = charger_rankings_safe()
        st.write("Rankings chargés :", len(rankings))
        
    rang_j1 = None
    rang_j2 = None

    if rankings:
        rang_j1 = recuperer_rang_atp(joueur_1, rankings)
        rang_j2 = recuperer_rang_atp(joueur_2, rankings)

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
        
        if rang_j1:
            score1 += max(0, 150 - rang_j1)

        if rang_j2:
            score2 += max(0, 150 - rang_j2)

        # =========================
        # RANKING ATP RÉEL
        # =========================

        if rang_j1 is None:
            rang_j1 = 2000
        if rang_j2 is None:
            rang_j2 = 2000

        rank_diff = rang_j2 - rang_j1

        score1 += max(0, (rang_j2 - rang_j1) * 0.2)
        score2 += max(0, (rang_j1 - rang_j2) * 0.2)

        # =========================
        # BONUS SURFACE (LOGIQUE RÉELLE)
        # =========================
        surface_map = {
            "Hard": "Dur",
            "Clay": "Terre Battue",
            "Grass": "Gazon"
        }

        surface = surface_map.get(surface, "Dur")

        surface_bonus = {
            "Dur": 0.5,
            "Terre Battue": 0.7,
            "Gazon": 0.6
        }

        score1 *= (1 + surface_bonus.get(surface, 0.5))
        score2 *= (1 + surface_bonus.get(surface, 0.5))

        # =========================
        # POIDS TOURNOI (NOUVEAU)
        # =========================
        poids_tournoi = {
            "Grand Slam": 1.5,
            "Masters 1000": 1.3,
            "ATP 500": 1.1,
            "ATP 250": 1.0
        }

        facteur_tournoi = poids_tournoi.get(categorie, 1.0)

        score1 *= facteur_tournoi
        score2 *= facteur_tournoi
        
        # =========================
        # ÉCART RANG (OPTIONNEL MAIS PROPRE)
        # =========================
        if rang_j1 and rang_j2:
            ecart_rang = rang_j2 - rang_j1
            score1 += ecart_rang * 1.5
            score2 -= ecart_rang * 1.5

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
        
