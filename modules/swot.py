# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from utils.export import export_as_pdf, export_as_png


# ─────────────────────────────────────────────────────────────────────────────
# Construction du diagramme SWOT
# ─────────────────────────────────────────────────────────────────────────────
def create_swot_diagram(title, strengths, weaknesses, opportunities, threats):
    """Retourne une figure Matplotlib représentant la matrice SWOT."""
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.axis("off")

    quads = [
        {"nom": "Forces", "x": 0.25, "y": 0.75, "couleur": "lightgreen", "items": strengths},
        {"nom": "Faiblesses", "x": 0.75, "y": 0.75, "couleur": "salmon", "items": weaknesses},
        {"nom": "Opportunités", "x": 0.25, "y": 0.25, "couleur": "lightblue", "items": opportunities},
        {"nom": "Menaces", "x": 0.75, "y": 0.25, "couleur": "lightyellow", "items": threats},
    ]

    for q in quads:
        w, h = 0.45, 0.45
        ax.add_patch(
            plt.Rectangle((q["x"] - w / 2, q["y"] - h / 2), w, h, facecolor=q["couleur"], edgecolor="black", alpha=0.7)
        )
        ax.text(q["x"], q["y"] + h / 2 - 0.05, q["nom"], ha="center", va="center", fontsize=14, fontweight="bold")
        texte = "\n".join([f"• {it}" for it in q["items"] if it.strip()])
        ax.text(q["x"], q["y"], texte, ha="center", va="center", fontsize=10)

    ax.axvline(0.5, 0.05, 0.95, color="black")
    ax.axhline(0.5, 0.05, 0.95, color="black")

    ax.text(0.5, 0.98, "Facteurs internes", ha="center", va="center", fontsize=12)
    ax.text(0.5, 0.02, "Facteurs externes", ha="center", va="center", fontsize=12)
    ax.text(0.02, 0.5, "Aide", ha="center", va="center", fontsize=12, rotation=90)
    ax.text(0.98, 0.5, "Nuisible", ha="center", va="center", fontsize=12, rotation=270)

    plt.suptitle(title, fontsize=16, y=1.05)
    plt.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Interface Streamlit
# ─────────────────────────────────────────────────────────────────────────────
def swot_tool():
    st.title("Outil d’analyse SWOT")

    st.markdown(
        """
    ## Planification stratégique avec la matrice SWOT

    La méthode **SWOT** évalue la position concurrentielle d’une organisation en identifiant :
    - ses **Forces** et **Faiblesses** internes,
    - les **Opportunités** et **Menaces** externes.
    """
    )

    # ---------- Données d'exemple ------------------------------------------------
    if "demo_swot_initialized" not in st.session_state:
        st.session_state.demo_swot_initialized = True
        st.session_state.demo_swot_title = "Analyse SWOT – Start‑up Tech"
        st.session_state.demo_swot_strengths = [
            "Produit innovant",
            "Équipe de développement talentueuse",
            "Technologie propriétaire",
            "Processus agile",
            "Soutien financier solide",
        ]
        st.session_state.demo_swot_weaknesses = [
            "Présence marché limitée",
            "Petite base clients",
            "Tensions de trésorerie",
            "Faible notoriété",
            "Budget marketing restreint",
        ]
        st.session_state.demo_swot_opportunities = [
            "Demande croissante",
            "Nouveaux marchés émergents",
            "Partenariats stratégiques potentiels",
            "Intégrations technologiques",
            "Faiblesses des concurrents",
        ]
        st.session_state.demo_swot_threats = [
            "Concurrence intense",
            "Évolutions technologiques rapides",
            "Ralentissements économiques",
            "Contraintes réglementaires",
            "Produits imitables",
        ]

    # Onglets
    tab1, tab2, tab3 = st.tabs(["Données", "Visualisation", "Guide d’interprétation"])

    # ──────────────────── Onglet 1 : Données ────────────────────
    with tab1:
        st.markdown("### Étape 1 : Saisir les données SWOT")

        st.session_state.swot_title = st.text_input(
            "Titre de l’analyse :",
            value=st.session_state.demo_swot_title,
            help="Apparaît en haut du diagramme",
        )

        st.markdown("#### Facteurs internes")
        col1, col2 = st.columns(2)

        # --- Forces ---
        strengths = []
        with col1:
            st.markdown("**Forces (positif)**")
            for i in range(len(st.session_state.demo_swot_strengths)):
                c1, c2 = st.columns([5, 1])
                with c1:
                    val = st.text_input(
                        f"Forces {i+1}", value=st.session_state.demo_swot_strengths[i], key=f"strength_{i}"
                    )
                    if val:
                        strengths.append(val)
                with c2:
                    if st.button("🗑️", key=f"del_strength_{i}"):
                        st.session_state.demo_swot_strengths.pop(i); st.rerun()
            if st.button("Ajouter une force", key="add_strength"):
                st.session_state.demo_swot_strengths.append(""); st.rerun()

        # --- Faiblesses ---
        weaknesses = []
        with col2:
            st.markdown("**Faiblesses (négatif)**")
            for i in range(len(st.session_state.demo_swot_weaknesses)):
                c1, c2 = st.columns([5, 1])
                with c1:
                    val = st.text_input(
                        f"Faiblesses {i+1}", value=st.session_state.demo_swot_weaknesses[i], key=f"weak_{i}"
                    )
                    if val:
                        weaknesses.append(val)
                with c2:
                    if st.button("🗑️", key=f"del_weak_{i}"):
                        st.session_state.demo_swot_weaknesses.pop(i); st.rerun()
            if st.button("Ajouter une faiblesse", key="add_weak"):
                st.session_state.demo_swot_weaknesses.append(""); st.rerun()

        st.markdown("#### Facteurs externes")
        col3, col4 = st.columns(2)

        # --- Opportunités ---
        opportunities = []
        with col3:
            st.markdown("**Opportunités (positif)**")
            for i in range(len(st.session_state.demo_swot_opportunities)):
                c1, c2 = st.columns([5, 1])
                with c1:
                    val = st.text_input(
                        f"Opportunités {i+1}", value=st.session_state.demo_swot_opportunities[i], key=f"opp_{i}"
                    )
                    if val:
                        opportunities.append(val)
                with c2:
                    if st.button("🗑️", key=f"del_opp_{i}"):
                        st.session_state.demo_swot_opportunities.pop(i); st.rerun()
            if st.button("Ajouter une opportunité", key="add_opp"):
                st.session_state.demo_swot_opportunities.append(""); st.rerun()

        # --- Menaces ---
        threats = []
        with col4:
            st.markdown("**Menaces (négatif)**")
            for i in range(len(st.session_state.demo_swot_threats)):
                c1, c2 = st.columns([5, 1])
                with c1:
                    val = st.text_input(
                        f"Menaces {i+1}", value=st.session_state.demo_swot_threats[i], key=f"threat_{i}"
                    )
                    if val:
                        threats.append(val)
                with c2:
                    if st.button("🗑️", key=f"del_threat_{i}"):
                        st.session_state.demo_swot_threats.pop(i); st.rerun()
            if st.button("Ajouter une menace", key="add_threat"):
                st.session_state.demo_swot_threats.append(""); st.rerun()

        # Sauvegarde
        st.session_state.swot_strengths = strengths
        st.session_state.swot_weaknesses = weaknesses
        st.session_state.swot_opportunities = opportunities
        st.session_state.swot_threats = threats

        st.success("Données enregistrées. Passez à l’onglet « Visualisation ».")

    # ──────────────────── Onglet 2 : Visualisation ────────────────────
    with tab2:
        st.markdown("### Étape 2 : Visualisation de la matrice")
        required_keys = [
            "swot_title",
            "swot_strengths",
            "swot_weaknesses",
            "swot_opportunities",
            "swot_threats",
        ]
        if not all(k in st.session_state for k in required_keys):
            st.info("Veuillez d’abord saisir vos données dans l’onglet « Données ».")
        else:
            with st.expander("Paramètres d’affichage", expanded=False):
                st.caption("Couleurs par défaut (non modifiables ici)")

            fig = create_swot_diagram(
                st.session_state.swot_title,
                st.session_state.swot_strengths,
                st.session_state.swot_weaknesses,
                st.session_state.swot_opportunities,
                st.session_state.swot_threats,
            )
            st.pyplot(fig)

            with st.expander("Résumé de la matrice", expanded=True):
                col_s, col_w = st.columns(2)
                with col_s:
                    st.markdown("##### Forces")
                    for i, s in enumerate(st.session_state.swot_strengths):
                        st.markdown(f"{i+1}. {s}")
                with col_w:
                    st.markdown("##### Faiblesses")
                    for i, w in enumerate(st.session_state.swot_weaknesses):
                        st.markdown(f"{i+1}. {w}")

                col_o, col_t = st.columns(2)
                with col_o:
                    st.markdown("##### Opportunités")
                    for i, o in enumerate(st.session_state.swot_opportunities):
                        st.markdown(f"{i+1}. {o}")
                with col_t:
                    st.markdown("##### Menaces")
                    for i, t in enumerate(st.session_state.swot_threats):
                        st.markdown(f"{i+1}. {t}")

                # Statistiques
                s1, s2, s3, s4 = st.columns(4)
                s1.metric("Forces", len(st.session_state.swot_strengths))
                s2.metric("Faiblesses", len(st.session_state.swot_weaknesses))
                s3.metric("Opportunités", len(st.session_state.swot_opportunities))
                s4.metric("Menaces", len(st.session_state.swot_threats))

                int_bal = len(st.session_state.swot_strengths) - len(st.session_state.swot_weaknesses)
                ext_bal = len(st.session_state.swot_opportunities) - len(st.session_state.swot_threats)
                b1, b2 = st.columns(2)
                b1.metric("Équilibre interne (F–Fa)", f"{int_bal:+d}")
                b2.metric("Équilibre externe (O–M)", f"{ext_bal:+d}")

            st.markdown("#### Exporter")
            c1, c2 = st.columns(2)
            with c1:
                png = export_as_png(fig)
                st.download_button("PNG", png, "swot.png", "image/png")
            with c2:
                pdf = export_as_pdf(fig, st.session_state.swot_title)
                st.download_button("PDF", pdf, "swot.pdf", "application/pdf")

    # ──────────────────── Onglet 3 : Guide ────────────────────
    with tab3:
        st.markdown("### Guide d’interprétation SWOT")

        with st.expander("Comprendre la matrice SWOT", expanded=True):
            st.markdown(
                """
            - **Forces** : atouts internes qui vous avantagent  
            - **Faiblesses** : handicaps internes à surmonter  
            - **Opportunités** : facteurs externes favorables  
            - **Menaces** : facteurs externes défavorables
            """
            )

        with st.expander("Approches stratégiques", expanded=True):
            st.markdown(
                """
            **Combinaisons classiques** :

            - **FO (Forces + Opportunités)** : exploiter vos atouts pour saisir les opportunités  
            - **FM (Forces + Menaces)** : utiliser vos forces pour contrer les menaces  
            - **FOp (Faiblesses + Opportunités)** : corriger les faiblesses grâce aux opportunités externes  
            - **FMn (Faiblesses + Menaces)** : stratégies défensives pour limiter la vulnérabilité
            """
            )

        with st.expander("Passer à l’action", expanded=True):
            st.markdown(
                """
            1. **Prioriser** les éléments selon leur impact  
            2. **Croiser** forces/opportunités et faiblesses/menaces  
            3. **Définir des objectifs** SMART  
            4. **Élaborer des plans d’action** détaillés  
            5. **Suivre et ajuster** régulièrement l’analyse SWOT
            """
            )
