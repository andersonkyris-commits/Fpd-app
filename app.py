import streamlit as st
import requests
import math
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="FPD Pro - Multi-Sports Predictor", page_icon="📊", layout="centered")

# Clé API Football-Data.org intégrée
API_TOKEN = "bb42361060ff481499fe8538f511115a"
headers = {"X-Auth-Token": API_TOKEN}

st.title("📊 FPD Pro v5.1 : Football & Tennis Predictor")
st.caption("Développé pour l'analyse des cotes réelles")

# Onglets principaux pour choisir le sport
sport = st.sidebar.radio("🗂️ Sélectionne le Sport", ["Football ⚽", "Tennis 🎾"])

# ==============================================================================
# LE MODULE FOOTBALL (CORRIGÉ SANS SÉCURITÉ BLOQUANTE)
# ==============================================================================
if sport == "Football ⚽":
    st.header("⚽ Analyse Football")
    
    # 1. SÉLECTION DE LA COMPÉTITION
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
            if response.status_code == 200:
                return response.json().get("matches", [])
        except: pass
        return []

    matchs = charger_matchs(code_compet)

    if code_compet == "MANUAL" or not matchs:
        if code_compet != "MANUAL":
            st.warning("⚠️ Aucun match trouvé sur l'API. Passage en mode manuel.")
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
    def recuperer_stats_equipe(code_league, team_name):
        if code_league == "MANUAL": return 7, 5, 2, 2
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
                            return max(1, round(row["goalsFor"] * ratio)), max(1, round(row["goalsAgainst"] * ratio)), max(0, min(5, round(row["won"] * ratio))), max(0, min(5, round(row["draw"] * ratio)))
        except: pass
        return 7, 5, 2, 2

    if not mode_manuel:
        st.success(f"🔄 Données en direct récupérées !")
        bm_a_auto, be_a_auto, v_a_auto, n_a_auto = recuperer_stats_equipe(code_compet, nom_a_api)
        bm_b_auto, be_b_auto, v_b_auto, n_b_auto = recuperer_stats_equipe(code_compet, nom_b_api)
    else:
        bm_a_auto, be_a_auto, v_a_auto, n_a_auto = 7, 5, 2, 1
        bm_b_auto, be_b_auto, v_b_auto, n_b_auto = 6, 6, 1, 2

    with col1:
        st.subheader(f"🛡️ {nom_a_api}")
        style_a = st.selectbox(f"Style Tactique ({nom_a_api})", ["Équilibré", "Ultra-Offensif", "Autobus / Bloc Bas"], key="sa")
        buts_marques_a = st.number_input("Buts marqués (sur 5 matchs)", value=int(bm_a_auto), min_value=0, key="bma")
        buts_encaisses_a = st.number_input("Buts encaissés (sur 5 matchs)", value=int(be_a_auto), min_value=0, key="bea")
        v_a_input = st.number_input("Victoires (sur 5 matchs)", value=int(v_a_auto), min_value=0, max_value=5, key="va")
        n_a_input = st.number_input("Nuls (sur 5 matchs)", value=int(n_a_auto), min_value=0, max_value=5, key="na")
        # Calcul souple des défaites
        d_a_input = max(0, 5 - v_a_input - n_a_input)
        st.caption(f"Défaites estimées : {d_a_input}")

    with col2:
        st.subheader(f"⚔️ {nom_b_api}")
        style_b = st.selectbox(f"Style Tactique ({nom_b_api})", ["Équilibré", "Ultra-Offensif", "Autobus / Bloc Bas"], key="sb")
        buts_marques_b = st.number_input("Buts marqués (sur 5 matchs)", value=int(bm_b_auto), min_value=0, key="bmb")
        buts_encaisses_b = st.number_input("Buts encaissés (sur 5 matchs)", value=int(be_b_auto), min_value=0, key="beb")
        v_b_input = st.number_input("Victoires (sur 5 matchs)", value=int(v_b_auto), min_value=0, max_value=5, key="vb")
        n_b_input = st.number_input("Nuls (sur 5 matchs)", value=int(n_b_auto), min_value=0, max_value=5, key="nb")
        # Calcul souple des défaites
        d_b_input = max(0, 5 - v_b_input - n_b_input)
        st.caption(f"Défaites estimées : {d_b_input}")

    st.markdown("---")
    st.subheader("💰 Cotes Réelles Bet261")
    cx1, cx2, cx3 = st.columns(3)
    cote_a = cx1.number_input(f"Cote {nom_a_api}", min_value=1.0, value=2.00, step=0.05)
    cote_nul = cx2.number_input("Cote Nul", min_value=1.0, value=3.20, step=0.05)
    cote_b = cx3.number_input(f"Cote {nom_b_api}", min_value=1.0, value=3.50, step=0.05)

    if st.button("📊 LANCER L'ANALYSE FOOTBALL", use_container_width=True):
        att_a, def_a = buts_marques_a / 5, buts_encaisses_a / 5
        att_b, def_b = buts_marques_b / 5, buts_encaisses_b / 5
        att_a *= (1.0 + (v_a_input * 0.05) - (d_a_input * 0.05))
        att_b *= (1.0 + (v_b_input * 0.05) - (d_b_input * 0.05))
        
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
        p_v_a, p_nul, p_v_b = (v_a / total) * 100, ((nul / total) * 100) + ((n_a_input + n_b_input) * 2.0), (v_b / total) * 100
        total_ajuste = p_v_a + p_nul + p_v_b
        p_v_a, p_nul, p_v_b = (p_v_a/total_ajuste)*100, (p_nul/total_ajuste)*100, (p_v_b/total_ajuste)*100

        st.subheader("📈 Pourcentages Calculés")
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Victoire {nom_a_api}", f"{p_v_a:.1f}%")
        c2.metric("Match Nul", f"{p_nul:.1f}%")
        c3.metric(f"Victoire {nom_b_api}", f"{p_v_b:.1f}%")
        
        st.markdown("---")
        value_a, value_nul, value_b = (p_v_a * cote_a) / 100, (p_nul * cote_nul) / 100, (p_v_b * cote_b) / 100
        if value_a > 1.05: st.warning(f"⚠️ Value Bet sur {nom_a_api} (Cote: {cote_a})")
        if value_nul > 1.05: st.warning(f"⚠️ Value Bet sur Nul (Cote: {cote_nul})")
        if value_b > 1.05: st.warning(f"⚠️ Value Bet sur {nom_b_api} (Cote: {cote_b})")
        
        st.subheader("🛡️ Option Sécurité FPD Pro (Mise : 5%)")
        if p_v_a > 58: st.success(f"💪 **Cadre Vert** : Double Chance 1X ({nom_a_api} ou Nul)")
        elif p_v_b > 58: st.success(f"💪 **Cadre Vert** : Double Chance X2 ({nom_b_api} ou Nul)")
        elif (buts_attendus_a + buts_attendus_b) > 2.7: st.success("🔥 **Cadre Vert** : Plus de 1,5 buts dans le match")
        else: st.success("🔒 **Cadre Vert** : Moins de 3,5 buts dans le match")

# ==============================================================================
# LE MODULE TENNIS
# ==============================================================================
elif sport == "Tennis 🎾":
    st.header("🎾 Analyse Tennis v1.0")
    st.info("💡 Au tennis, pas de match nul ! Le modèle s'appuie sur le ratio de victoires et la surface.")

    st.subheader("👤 1. Profil des Joueurs")
    tx1, tx2 = st.columns(2)
    joueur_1 = tx1.text_input("Nom du Joueur 1", "Joueur A")
    joueur_2 = tx2.text_input("Nom du Joueur 2", "Joueur B")

    st.markdown("---")
    st.subheader("📊 2. Forme Récente & Terrain")
    surface = st.selectbox("Type de Surface de Court", ["Dur / Indoor 🟦", "Terre Battue 🟫", "Gazon 🟩"])
    
    col_t1, col_t2 = st.columns(2)
    victoires_j1 = col_t1.number_input(f"Victoires de {joueur_1} (sur ses 10 derniers matchs)", min_value=0, max_value=10, value=6)
    victoires_j2 = col_t2.number_input(f"Victoires de {joueur_2} (sur ses 10 derniers matchs)", min_value=0, max_value=10, value=6)
    
    pref_j1 = col_t1.toggle(f"{joueur_1} adore cette surface", value=False)
    pref_j2 = col_t2.toggle(f"{joueur_2} adore cette surface", value=False)

    st.markdown("---")
    st.subheader("💰 3. Cotes Réelles Bet261")
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
        implied_j1 = (implied_j1 / total_implied) * 100
        implied_j2 = (implied_j2 / total_implied) * 100
        
        prob_j1_finale = (prob_j1 * 0.6) + (implied_j1 * 0.4)
        prob_j2_finale = (prob_j2 * 0.6) + (implied_j2 * 0.4)

        st.subheader("📈 Pourcentages Probables de Victoire")
        res_col1, res_col2 = st.columns(2)
        res_col1.metric(f"Probabilité {joueur_1}", f"{prob_j1_finale:.1f}%")
        res_col2.metric(f"Probabilité {joueur_2}", f"{prob_j2_finale:.1f}%")

        st.markdown("---")
        st.subheader("🔎 Opportunités Détectées (vs Bet261)")
        val_j1 = (prob_j1_finale * cote_j1) / 100
        val_j2 = (prob_j2_finale * cote_j2) / 100
        
        un_value_trouve = False
        if val_j1 > 1.06:
            st.warning(f"⚠️ **VALUE BET ÉLEVÉ sur {joueur_1}** !")
            un_value_trouve = True
        if val_j2 > 1.06:
            st.warning(f"⚠️ **VALUE BET ÉLEVÉ sur {joueur_2}** !")
            un_value_trouve = True
        if not un_value_trouve:
            st.info("💡 Cotes bien ajustées. Aucun écart spéculatif majeur détecté.")

        st.subheader("🛡️ Option Sécurité Tennis (Mise : 5%)")
        if prob_j1_finale > 62: st.success(f"🟩 **Cadre Vert** : Victoire Sèche de **{joueur_1}**")
        elif prob_j2_finale > 62: st.success(f"🟩 **Cadre Vert** : Victoire Sèche de **{joueur_2}**")
        else: st.success(f"🟩 **Cadre Vert** : 'Le joueur favori prend au moins 1 Set' dans le match.")
        
