import streamlit as st
import requests
import math
from datetime import datetime
import json
import os

# Configuration de la page
st.set_page_config(page_title="FPD Pro - Expert Predictor", page_icon="📊", layout="centered")

# Clé API Football-Data.org
API_TOKEN = "bb42361060ff481499fe8538f511115a"
headers = {"X-Auth-Token": API_TOKEN}

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
    st.header("⚽ Analyse Football & Confrontations Directes")
    DICT_COMPETS = {
        "Ligue des Champions (Europe)": "CL", "Coupe du Monde (FIFA)": "WC",
        "Championnat d'Europe (Euro)": "EC", "Premier League (Angleterre)": "PL",
        "Ligue 1 (France)": "FL1", "La Liga (Espagne)": "PD", "Serie A (Italie)": "SA",
        "Bundesliga (Allemagne)": "BL1", "Eredivisie (Pays-Bas)": "DED", "Primeira Liga (Portugal)": "PPL",
        "➕ [MODE MANUEL] Match Amical / Autre Coupe": "MANUAL"
    }
    compet_choisie = st.selectbox("Sélectionne une compétition ou un mode", list(DICT_COMPETS.keys()))
    code_compet = DICT_COMPETS[compet_choisie]

    @st.cache_data(ttl=1800)
    def charger_matchs(code):
        if code == "MANUAL": return []
        url = f"https://api.football-data.org/v4/competitions/{code}/matches?status=SCHEDULED"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200: return response.json().get("matches", [])
        except: pass
        return []

    matchs = charger_matchs(code_compet)
    if code_compet == "MANUAL" or not matchs:
        mode_manuel = True
        col_input1, col_input2 = st.columns(2)
        nom_a_api = col_input1.text_input("Nom de l'Équipe à Domicile", "Équipe A")
        nom_b_api = col_input2.text_input("Nom de l'Équipe à l'Extérieur", "Équipe B")
    else:
        mode_manuel = False
        liste_options_matchs = []
        dict_matchs = {}
        for m in matchs[:20]:
            date_utc = m.get("utcDate", "")
            try:
                date_obj = datetime.strptime(date_utc, "%Y-%m-%dT%H:%M:%SZ")
                date_str = date_obj.strftime("%d/%m %H:%M")
            except: date_str = ""
            label = f"[{date_str}] {m['homeTeam']['name']} vs {m['awayTeam']['name']}"
            liste_options_matchs.append(label)
            dict_matchs[label] = m
        match_selectionne = st.selectbox("Sélectionne le match à analyser", liste_options_matchs)
        match_data = dict_matchs[match_selectionne]
        nom_a_api = match_data["homeTeam"]["name"]
        nom_b_api = match_data["awayTeam"]["name"]

    st.markdown("---")
    st.subheader("📊 Paramètres & Données des Équipes")
    col1, col2 = st.columns(2)

    @st.cache_data(ttl=7200)
    def recuperer_stats_et_classement(code_league, team_name):
        if code_league == "MANUAL": return 7, 5, 2, 2, 0
        url = f"https://api.football-data.org/v4/competitions/{code_league}/standings"
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                standings = res.json().get("standings", [])
                if standings:
                    table = standings[0].get("table", [])
                    for row in table:
                        if row["team"]["name"] == team_name:
                            matchs_joues = row["playedGames"] if row["playedGames"] > 0 else 1
                            ratio = 5 / matchs_joues
                            return max(1, round(row["goalsFor"] * ratio)), max(1, round(row["goalsAgainst"] * ratio)), max(0, min(5, round(row["won"] * ratio))), max(0, min(5, round(row["draw"] * ratio))), row["position"]
        except: pass
        return 7, 5, 2, 2, 0

    if not mode_manuel:
        bm_a_auto, be_a_auto, v_a_auto, n_a_auto, rang_a = recuperer_stats_et_classement(code_compet, nom_a_api)
        bm_b_auto, be_b_auto, v_b_auto, n_b_auto, rang_b = recuperer_stats_et_classement(code_compet, nom_b_api)
    else:
        bm_a_auto, be_a_auto, v_a_auto, n_a_auto, rang_a = 7, 5, 2, 1, 0
        bm_b_auto, be_b_auto, v_b_auto, n_b_auto, rang_b = 6, 6, 1, 2, 0

    with col1:
        st.subheader(f"🛡️ {nom_a_api}")
        if rang_a > 0: st.markdown(f"🏆 Classement : **{rang_a}e**")
        style_a = st.selectbox(f"Style Tactique ({nom_a_api})", ["Équilibré", "Ultra-Offensif", "Autobus / Bloc Bas"], key="sa")
        buts_marques_a = st.number_input("Buts marqués (5 derniers matchs)", value=int(bm_a_auto), min_value=0, key="bma")
        buts_encaisses_a = st.number_input("Buts encaissés (5 derniers matchs)", value=int(be_a_auto), min_value=0, key="bea")
        v_a_input = st.number_input("Victoires (5 derniers)", value=int(v_a_auto), min_value=0, max_value=5, key="va")
        n_a_input = st.number_input("Nuls (5 derniers)", value=int(n_a_auto), min_value=0, max_value=5, key="na")

    with col2:
        st.subheader(f"⚔️ {nom_b_api}")
        if rang_b > 0: st.markdown(f"🏆 Classement : **{rang_b}e**")
        style_b = st.selectbox(f"Style Tactique ({nom_b_api})", ["Équilibré", "Ultra-Offensif", "Autobus / Bloc Bas"], key="sb")
        buts_marques_b = st.number_input("Buts marqués (5 derniers matchs)", value=int(bm_b_auto), min_value=0, key="bmb")
        buts_encaisses_b = st.number_input("Buts encaissés (5 derniers matchs)", value=int(be_b_auto), min_value=0, key="beb")
        v_b_input = st.number_input("Victoires (5 derniers)", value=int(v_b_auto), min_value=0, max_value=5, key="vb")
        n_b_input = st.number_input("Nuls (5 derniers)", value=int(n_b_auto), min_value=0, max_value=5, key="nb")

    st.markdown("---")
    st.subheader("🔄 3. Historique Confrontations Directes (H2H)")
    cx_h2h1, cx_h2h2, cx_h2h3 = st.columns(3)
    h2h_v_a = cx_h2h1.number_input(f"Duels gagnés par {nom_a_api}", min_value=0, value=1)
    h2h_nuls = cx_h2h2.number_input("Matchs nuls entre eux", min_value=0, value=2)
    h2h_v_b = cx_h2h3.number_input(f"Duels gagnés par {nom_b_api}", min_value=0, value=1)
    
    total_duels = h2h_v_a + h2h_nuls + h2h_v_b
    if total_duels > 0:
        if h2h_v_a > h2h_v_b: st.info(f"👑 **Ascendant Psychologique** : {nom_a_api} est plus décisif.")
        elif h2h_v_b > h2h_v_a: st.info(f"👑 **Ascendant Psychologique** : {nom_b_api} est plus décisif.")

    st.markdown("---")
    st.subheader("💰 Cotes Réelles Bet261")
    cx1, cx2, cx3 = st.columns(3)
    cote_a = cx1.number_input(f"Cote {nom_a_api}", min_value=1.0, value=2.00, step=0.05)
    cote_nul = cx2.number_input("Cote Nul", min_value=1.0, value=3.20, step=0.05)
    cote_b = cx3.number_input(f"Cote {nom_b_api}", min_value=1.0, value=3.50, step=0.05)

    if st.button("📊 LANCER L'ANALYSE FOOTBALL", use_container_width=True):
        d_a_input = max(0, 5 - v_a_input - n_a_input)
        d_b_input = max(0, 5 - v_b_input - n_b_input)
        att_a, def_a = buts_marques_a / 5, buts_encaisses_a / 5
        att_b, def_b = buts_marques_b / 5, buts_encaisses_b / 5
        att_a *= (1.0 + (v_a_input * 0.05) - (d_a_input * 0.05))
        att_b *= (1.0 + (v_b_input * 0.05) - (d_b_input * 0.05))
        
        if rang_a > 0 and rang_b > 0:
            ecart = rang_b - rang_a
            if ecart > 4: att_a *= 1.08; def_b *= 1.05
            elif ecart < -4: att_b *= 1.08; def_a *= 1.05
        
        if style_b == "Autobus / Bloc Bas": att_a *= 0.70; def_b *= 0.80
        if style_a == "Autobus / Bloc Bas": att_b *= 0.70; def_a *= 0.80
        if style_a == "Ultra-Offensif": att_a *= 1.25; def_a *= 1.20
        if style_b == "Ultra-Offensif": att_b *= 1.25; def_b *= 1.20
            
        bonus_domicile = 1.05 if code_compet in ["WC", "EC", "MANUAL"] else 1.15
        buts_attendus_a = ((att_a + def_b) / 2) * bonus_domicile
        buts_attendus_b = (att_b + def_a) / 2
        
        prob_a = [math.exp(-buts_attendus_a) * (buts_attendus_a**i) / math.factorial(i) for i in range(7)]
        prob_b = [math.exp(-buts_attendus_b) * (buts_attendus_b**i) / math.factorial(i) for i in range(7)]
        
        v_a, nul, v_b = 0, 0, 0
        for i in range(7):
            for j in range(7):
                p_score = prob_a[i] * prob_b[j]
                if i > j: v_a += p_score
                elif i == j: nul += p_score
                else: v_b += p_score

        total = v_a + nul + v_b
        p_v_a, p_nul, p_v_b = (v_a / total) * 100, (nul / total) * 100, (v_b / total) * 100
        
        if total_duels > 0:
            if (h2h_nuls / total_duels) > 0.40: p_nul += 7.5
            if h2h_v_a > h2h_v_b: p_v_a += 5.0
            elif h2h_v_b > h2h_v_a: p_v_b += 5.0

        total_ajuste = p_v_a + p_nul + p_v_b
        p_v_a, p_nul, p_v_b = (p_v_a/total_ajuste)*100, (p_nul/total_ajuste)*100, (p_v_b/total_ajuste)*100

        st.subheader("📈 Pourcentages Calculés Finalisés")
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Victoire {nom_a_api}", f"{p_v_a:.1f}%")
        c2.metric("Match Nul", f"{p_nul:.1f}%")
        c3.metric(f"Victoire {nom_b_api}", f"{p_v_b:.1f}%")
        
        st.subheader("🛡️ Option Sécurité FPD Pro (Mise : 5%)")
        cadre_vert = ""
        if p_v_a > 58: cadre_vert = f"Double Chance 1X ({nom_a_api} ou Nul)"
        elif p_v_b > 58: cadre_vert = f"Double Chance X2 ({nom_b_api} ou Nul)"
        elif (buts_attendus_a + buts_attendus_b) > 2.7: cadre_vert = "Plus de 1,5 buts dans le match"
        else: cadre_vert = "Moins de 3,5 buts dans le match"
        st.success(f"💪 **Cadre Vert** : {cadre_vert}")
        
        st.session_state.historique_paris.append({
            "Sport": "Football ⚽", "Match / Duel": f"{nom_a_api} vs {nom_b_api}",
            "Cadre Vert": cadre_vert, "Cotes": f"{cote_a:.2f} | {cote_nul:.2f} | {cote_b:.2f}"
        })

        sauvegarder_historique(st.session_state.historique_paris)
        
# ==============================================================================
# MODULE TENNIS ULTRA AUTOMATISÉ (TOURNOIS + SURFACES ACCORDÉES)
# ==============================================================================
elif sport == "Tennis 🎾":
    st.header("🎾 Module Tennis Connecté aux Tournois")
    
    st.subheader("🏆 1. Sélection du Tournoi")
    tournoi_selectionne = st.selectbox("Où se joue le match ?", list(DICTIONNAIRE_TOURNOIS.keys()))
    
    # Extraction automatique de la surface d'après le tournoi choisi
    surface = DICTIONNAIRE_TOURNOIS[tournoi_selectionne]
    st.info(f"🏟️ Type de court détecté : **{surface}**")

    st.subheader("👤 2. Profil des Joueurs")
    tx1, tx2 = st.columns(2)
    joueur_1 = tx1.text_input("Nom du Joueur 1", "Flavio Cobolli")
    joueur_2 = tx2.text_input("Nom du Joueur 2", "Felix Auger Aliassime")

    nom_recherche = f"{joueur_1} {joueur_2}".replace(" ", "+")
    st.markdown(f"🔗 [⚡ CLIQUE ICI : Voir les formes récentes de ces joueurs sur Flashscore](https://www.google.com/search?q=flashscore+tennis+{nom_recherche}+h2h)")

    # Détermination croisée (Tournoi automatique -> Surface -> Spécialité Joueur)
    auto_pref_j1 = verifier_excellence(joueur_1, surface)
    auto_pref_j2 = verifier_excellence(joueur_2, surface)

    st.markdown("---")
    st.subheader("📊 3. Forme Récente & Terrain")
    col_t1, col_t2 = st.columns(2)
    
    victoires_j1 = col_t1.number_input(f"Victoires de {joueur_1} (sur les 10 derniers)", min_value=0, max_value=10, value=6)
    pref_j1 = col_t1.toggle(f"{joueur_1} excelle sur ce terrain", value=auto_pref_j1)
    if auto_pref_j1: col_t1.caption("✨ *Boost de surface activé automatiquement !*")
    
    victoires_j2 = col_t2.number_input(f"Victoires de {joueur_2} (sur les 10 derniers)", min_value=0, max_value=10, value=6)
    pref_j2 = col_t2.toggle(f"{joueur_2} excelle sur ce terrain", value=auto_pref_j2)
    if auto_pref_j2: col_t2.caption("✨ *Boost de surface activé automatiquement !*")

    st.markdown("---")
    st.subheader("💰 4. Cotes Réelles Bet261")
    cx_t1, cx_t2 = st.columns(2)
    cote_j1 = cx_t1.number_input(f"Cote {joueur_1}", min_value=1.01, value=1.80, step=0.05)
    cote_j2 = cx_t2.number_input(f"Cote {joueur_2}", min_value=1.01, value=2.00, step=0.05)

    if st.button("📊 LANCER L'ANALYSE TENNIS", use_container_width=True):
        score_j1 = victoires_j1 * 10
        score_j2 = victoires_j2 * 10
        if pref_j1: score_j1 += 15
        if pref_j2: score_j2 += 15
            
        total_scores = score_j1 + score_j2
        if total_scores == 0: total_scores = 1
        
        prob_j1 = (score_j1 / total_scores) * 100
        prob_j2 = (score_j2 / total_scores) * 100
        
        implied_j1 = (1 / cote_j1) * 100
        implied_j2 = (1 / cote_j2) * 100
        total_implied = implied_j1 + implied_j2
        prob_j1_finale = (prob_j1 * 0.6) + ((implied_j1 / total_implied * 100) * 0.4)
        prob_j2_finale = (prob_j2 * 0.6) + ((implied_j2 / total_implied * 100) * 0.4)

        st.subheader("📈 Pourcentages de Victoire")
        res_col1, res_col2 = st.columns(2)
        res_col1.metric(f"Probabilité {joueur_1}", f"{prob_j1_finale:.1f}%")
        res_col2.metric(f"Probabilité {joueur_2}", f"{prob_j2_finale:.1f}%")

        cadre_tennis = ""
        if prob_j1_finale > 62: cadre_tennis = f"Victoire Sèche de {joueur_1}"
        elif prob_j2_finale > 62: cadre_tennis = f"Victoire Sèche de {joueur_2}"
        else: cadre_tennis = "Le favori prend au moins 1 Set"
            
        st.subheader("🛡️ Option Sécurité Tennis (Mise : 5%)")
        st.success(f"🟩 **Cadre Vert** : {cadre_tennis}")
        
        st.session_state.historique_paris.append({
            "Sport": f"Tennis 🎾 ({tournoi_selectionne.split()[1]})", "Match / Duel": f"{joueur_1} vs {joueur_2}",
            "Cadre Vert": cadre_tennis, "Cotes": f"{cote_j1:.2f} | {cote_j2:.2f}"
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
        
