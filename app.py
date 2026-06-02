import streamlit as st
import math

# Configuration de la page
st.set_page_config(page_title="FPD Pro - Football PronosticData", page_icon="⚽", layout="centered")

# Titre de l'application
st.title("⚽ FPD Pro : Football PronosticData v3.1")
st.subheader("Analyse stratégique : Championnats, Coupes & Matchs Amicaux")

st.markdown("---")

# 1. PARAMÈTRES DU MATCH
st.header("📋 1. Contexte du Match")
type_match = st.selectbox("Type de compétition / Contexte", [
    "Match de Championnat (Saison régulière)", 
    "Match de Coupe : Phase avancée (Stats disponibles)", 
    "Match d'Ouverture / 1er Match de Poule (Zéro stat)",
    "Match Amical (Pré-saison / Match de préparation)"
])

st.markdown("---")

# 2. ENTRÉE DES DONNÉES ÉQUIPES
col1, col2 = st.columns(2)

with col1:
    st.header("🛡️ Équipe A")
    nom_a = st.text_input("Nom de l'équipe A", "Équipe A")
    style_a = st.selectbox(f"Style Tactique de {nom_a}", ["Équilibré", "Ultra-Offensif", "Autobus / Bloc Bas"], key="sa")
    
    if type_match == "Match d'Ouverture / 1er Match de Poule (Zéro stat)":
        niveau_a = st.slider(f"Niveau global de {nom_a} (10 = Élite)", 1, 10, 7, key="na")
        buts_marques_a, buts_encaisses_a = 0, 0
    else:
        buts_marques_a = st.number_input("Buts marqués (5 derniers matchs)", min_value=0, value=10, key="bma")
        buts_encaisses_a = st.number_input("Buts encaissés (5 derniers matchs)", min_value=0, value=5, key="bea")

with col2:
    st.header("⚔️ Équipe B")
    nom_b = st.text_input("Nom de l'équipe B", "Équipe B")
    style_b = st.selectbox(f"Style Tactique de {nom_b}", ["Équilibré", "Ultra-Offensif", "Autobus / Bloc Bas"], key="sb")
    
    if type_match == "Match d'Ouverture / 1er Match de Poule (Zéro stat)":
        niveau_b = st.slider(f"Niveau global de {nom_b} (10 = Élite)", 1, 10, 5, key="nb")
        buts_marques_b, buts_encaisses_b = 0, 0
    else:
        buts_marques_b = st.number_input("Buts marqués (5 derniers matchs)", min_value=0, value=6, key="bmb")
        buts_encaisses_b = st.number_input("Buts encaissés (5 derniers matchs)", min_value=0, value=4, key="beb")

st.markdown("---")

# 3. INTERFACE DES COTES BET261
st.header("💰 2. Cotes Bet261 (Optionnel)")
cx1, cx2, cx3 = st.columns(3)
cote_a = cx1.number_input(f"Cote {nom_a}", min_value=1.0, value=2.10, step=0.05)
cote_nul = cx2.number_input("Cote Nul", min_value=1.0, value=3.20, step=0.05)
cote_b = cx3.number_input(f"Cote {nom_b}", min_value=1.0, value=3.40, step=0.05)

st.markdown("---")

# BOUTON DE CALCUL
if st.button("📊 ANALYSER AVEC FPD PRO", use_container_width=True):
    
    if type_match == "Match d'Ouverture / 1er Match de Poule (Zéro stat)":
        total_niveau = niveau_a + niveau_b
        base_buts_match = 2.2 
        buts_attendus_a = ((niveau_a / total_niveau) * base_buts_match) * 0.90
        buts_attendus_b = ((niveau_b / total_niveau) * base_buts_match) * 0.90
    else:
        att_a, def_a = buts_marques_a / 5, buts_encaisses_a / 5
        att_b, def_b = buts_marques_b / 5, buts_encaisses_b / 5
        
        # Modificateurs tactiques
        if style_b == "Autobus / Bloc Bas":
            att_a *= 0.70; def_b *= 0.80
        if style_a == "Autobus / Bloc Bas":
            att_b *= 0.70; def_a *= 0.80
        if style_a == "Ultra-Offensif":
            att_a *= 1.25; def_a *= 1.20
        if style_b == "Ultra-Offensif":
            att_b *= 1.25; def_b *= 1.20
            
        # En amical, l'avantage à domicile est réduit de moitié
        bonus_domicile = 1.07 if type_match == "Match Amical (Pré-saison / Match de préparation)" else (1.15 if type_match == "Match de Championnat (Saison régulière)" else 1.0)
        
        buts_attendus_a = ((att_a + def_b) / 2) * bonus_domicile
        buts_attendus_b = (att_b + def_a) / 2
        
        # Ajustement Mathématique Spécial Match Amical
        if type_match == "Match Amical (Pré-saison / Match de préparation)":
            # Les amicales nivellent le score (les gros jouent plus cool, les petits se donnent à fond)
            buts_attendus_a = (buts_attendus_a + 1.2) / 2
            buts_attendus_b = (buts_attendus_b + 1.2) / 2

    # Loi de Poisson
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
    
    # Si c'est un match amical, on pousse artificiellement la probabilité de match nul (tests d'effectifs en fin de match)
    if type_match == "Match Amical (Pré-saison / Match de préparation)":
        p_nul += 5.0
        total_ajuste = p_v_a + p_nul + p_v_b
        p_v_a, p_nul, p_v_b = (p_v_a/total_ajuste)*100, (p_nul/total_ajuste)*100, (p_v_b/total_ajuste)*100

    # AFFICHAGE
    st.header("📈 Probabilités FPD Pro")
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Victoire {nom_a}", f"{p_v_a:.1f}%")
    c2.metric("Match Nul", f"{p_nul:.1f}%")
    c3.metric(f"Victoire {nom_b}", f"{p_v_b:.1f}%")
    
    # VALUE BETS
    st.markdown("---")
    st.header("🔎 Analyse des opportunités Bet261")
    value_a, value_nul, value_b = (p_v_a * cote_a) / 100, (p_nul * cote_nul) / 100, (p_v_b * cote_b) / 100
    
    opportunites = 0
    if value_a > 1.05:
        st.warning(f"⚠️ **VALUE BET sur {nom_a}** (Cote : {cote_a})"); opportunites += 1
    if value_b > 1.05:
        st.warning(f"⚠️ **VALUE BET sur {nom_b}** (Cote : {cote_b})"); opportunites += 1
    if opportunites == 0:
        st.info("💡 Les cotes semblent équilibrées par rapport aux risques.")

    # CONSEILS SÉCURITÉ
    st.markdown("---")
    st.header("🛡️ Conseil Sécurité FPD (Haute Fiabilité)")
    
    if type_match == "Match Amical (Pré-saison / Match de préparation)":
        st.success("🔒 **Option Sécurité Amical (+90%)** : 'Moins de 4,5 buts' ou jouer la 'Chance Double' sur l'équipe favorite. Évitez les mises sèches (1 ou 2) sur les matchs amicaux, les changements massifs à la 60ème minute cassent souvent le rythme du match.")
    elif type_match == "Match d'Ouverture / 1er Match de Poule (Zéro stat)":
        st.success("🔒 **Option Spéciale Ouverture (+90%)** : 'Moins de 3,5 buts'. Le stress du premier match fige souvent le jeu.")
    else:
        if p_v_a > 60: st.success(f"💪 **Option Sécurité** : {nom_a} ou Nul (Chance double).")
        elif p_v_b > 60: st.success(f"💪 **Option Sécurité** : {nom_b} ou Nul (Chance double).")
        elif (buts_attendus_a + buts_attendus_b) > 2.8: st.success("🔥 **Option Buts** : Plus de 1,5 buts dans le match.")
        else: st.success("🔒 **Option Sécurité** : Moins de 3,5 buts dans le match.")

st.markdown("---")
st.caption("FPD Pro v3.1 - Version complète toutes compétitions.")
    
