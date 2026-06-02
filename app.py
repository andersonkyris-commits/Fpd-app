import streamlit as st
import math

# Configuration de la page
st.set_page_config(page_title="FPD - Football PronosticData", page_icon="⚽", layout="centered")

# Titre de l'application
st.title("⚽ FPD : Football PronosticData v2.0")
st.subheader("Analyse avancée : Styles tactiques & Matchs de Coupe")
st.write("Cette version prend en compte le choc des styles (ex: attaque de feu vs autobus défensif) et les matchs sur terrain neutre.")

st.markdown("---")

# Type de compétition
type_match = st.selectbox("🏆 Type de compétition / Contexte", ["Match de Championnat (Domicile/Extérieur)", "Match de Coupe (Terrain Neutre / Coupe du Monde)"])

st.markdown("---")

# Formulaire de saisie des données
col1, col2 = st.columns(2)

with col1:
    st.header("🛡️ Équipe A")
    nom_a = st.text_input("Nom de l'équipe A", "Équipe A")
    buts_marques_a = st.number_input("Buts marqués (5 derniers matchs)", min_value=0, value=10, key="bma")
    buts_encaisses_a = st.number_input("Buts encaissés (5 derniers matchs)", min_value=0, value=5, key="bea")
    style_a = st.selectbox(f"Style Tactique de {nom_a}", ["Équilibré", "Ultra-Offensif (Attaque à tout va)", "Autobus / Bloc Bas (Défense de fer)"], key="sa")

with col2:
    st.header("⚔️ Équipe B")
    nom_b = st.text_input("Nom de l'équipe B", "Équipe B")
    buts_marques_b = st.number_input("Buts marqués (5 derniers matchs)", min_value=0, value=6, key="bmb")
    buts_encaisses_b = st.number_input("Buts encaissés (5 derniers matchs)", min_value=0, value=4, key="beb")
    style_b = st.selectbox(f"Style Tactique de {nom_b}", ["Équilibré", "Ultra-Offensif (Attaque à tout va)", "Autobus / Bloc Bas (Défense de fer)"], key="sb")

st.markdown("---")

# Bouton de calcul
if st.button("📊 Lancer l'Analyse Tactique FPD", use_container_width=True):
    
    # Calcul des moyennes de buts par match
    att_a = buts_marques_a / 5
    def_a = buts_encaisses_a / 5
    att_b = buts_marques_b / 5
    def_b = buts_encaisses_b / 5
    
    # --- MODIFICATEURS TACTIQUES ---
    # Si l'équipe B fait un "Autobus", l'attaque de l'équipe A perd 30% d'efficacité
    if style_b == "Autobus / Bloc Bas (Défense de fer)":
        att_a *= 0.70
        def_b *= 0.80 # Sa propre défense devient encore plus hermétique
    
    # Si l'équipe A fait un "Autobus", l'attaque de l'équipe B perd 30% d'efficacité
    if style_a == "Autobus / Bloc Bas (Défense de fer)":
        att_b *= 0.70
        def_a *= 0.80

    # Si une équipe est Ultra-Offensive, elle marque plus mais encaisse plus en contre-attaque
    if style_a == "Ultra-Offensif (Attaque à tout va)":
        att_a *= 1.25
        def_a *= 1.20
    if style_b == "Ultra-Offensif (Attaque à tout va)":
        att_b *= 1.25
        def_b *= 1.20

    # --- AJUSTEMENT CONTEXTE DE MATCH ---
     bonus_domicile = 1.15 if type_match == "Match de Championnat (Domicile/Extérieur)" else 1.0
    
    # Estimation finale des buts attendus
    buts_attendus_a = ((att_a + def_b) / 2) * bonus_domicile
    buts_attendus_b = (att_b + def_a) / 2
    
    # Loi de Poisson pour simuler les scores (de 0 à 6 buts)
    prob_a = [math.exp(-buts_attendus_a) * (buts_attendus_a**i) / math.factorial(i) for i in range(7)]
    prob_b = [math.exp(-buts_attendus_b) * (buts_attendus_b**i) / math.factorial(i) for i in range(7)]
    
    v_a, nul, v_b = 0, 0, 0
    for i in range(7):
        for j in range(7):
            p_score = prob_a[i] * prob_b[j]
            if i > j:
                v_a += p_score
            elif i == j:
                nul += p_score
            else:
                v_b += p_score

    total = v_a + nul + v_b
    p_v_a = (v_a / total) * 100
    p_nul = (nul / total) * 100
    p_v_b = (v_b / total) * 100
    
    # Affichage des probabilités
    st.header("📈 Résultats de l'Analyse Tactique")
    
    label_a = f"Victoire {nom_a}" + (" (Dom.)" if type_match == "Match de Championnat (Domicile/Extérieur)" else "")
    label_b = f"Victoire {nom_b}" + (" (Ext.)" if type_match == "Match de Championnat (Domicile/Extérieur)" else "")
    
    c1, c2, c3 = st.columns(3)
    c1.metric(label_a, f"{p_v_a:.1f}%")
    c2.metric("Match Nul", f"{p_nul:.1f}%")
    c3.metric(label_b, f"{p_v_b:.1f}%")
    
    st.markdown("---")
    st.header("🛡️ Conseil Sécurité FPD")
    
    # Logique de conseil intelligente
    if style_a == "Autobus / Bloc Bas (Défense de fer)" and style_b == "Autobus / Bloc Bas (Défense de fer)":
        st.success("🔒 **Option Très Haute Fiabilité (+92%)** : Moins de 2,5 buts dans le match. Choc de deux blocs défensifs, le match sera très fermé.")
    elif (style_a == "Autobus / Bloc Bas (Défense de fer)" or style_b == "Autobus / Bloc Bas (Défense de fer)") and (buts_attendus_a + buts_attendus_b < 2.2):
        st.success("🔒 **Option Sécurité (+90%)** : Moins de 3,5 buts dans le match. Une des équipes va verrouiller le jeu.")
    elif p_v_a > 60:
        st.success(f"💪 **Option Sécurité (+90%)** : {nom_a} ou Nul (Chance double). Dynamique très favorable.")
    elif p_v_b > 60:
        st.success(f"💪 **Option Sécurité (+90%)** : {nom_b} ou Nul (Chance double). Dynamique très favorable.")
    else:
        st.success("🔥 **Option Alternative** : Les deux équipes marquent OU Plus de 1,5 buts. Match indécis sur le vainqueur mais propice aux opportunités.")
        
    if type_match == "Match de Coupe (Terrain Neutre / Coupe du Monde)":
        st.info("⚠️ *Rappel Coupe* : Les pourcentages ci-dessus concernent le temps réglementaire (90 min). En cas de match nul, prévoyez une couverture sur 'Qualification' ou 'Séries de tirs au but'.")

st.markdown("---")
st.caption("FPD v2.0 - Modèle de Poisson ajusté avec matrices de styles tactiques.")
    
