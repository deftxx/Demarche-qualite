# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
import uuid
import pandas as pd
from utils.export import export_as_png, export_as_pdf, export_as_csv


# ─────────────────────────────────────────────────────────────────────────────
# Création du diagramme
# ─────────────────────────────────────────────────────────────────────────────
def create_5why_diagram(problem, whys, root_cause=None, action=None):
    """Retourne une figure Matplotlib représentant la chaîne 5 Pourquoi."""
    G = nx.DiGraph()
    G.add_node("problem", label=problem, node_type="problem")

    prev_level_nodes = ["problem"]
    for level, level_whys in enumerate(whys):
        current_nodes = []
        for i, why in enumerate(level_whys):
            if why.strip():
                node_id = f"why_{level}_{i}"
                node_type = "root_cause" if level == 4 else "why"
                G.add_node(node_id, label=why, node_type=node_type)
                parent = "problem" if level == 0 else prev_level_nodes[min(i, len(prev_level_nodes) - 1)]
                G.add_edge(parent, node_id)
                current_nodes.append(node_id)
        if current_nodes:
            prev_level_nodes = current_nodes

    if action and action.strip() and prev_level_nodes:
        for node_id in prev_level_nodes:
            act_id = f"action_{node_id}"
            G.add_node(act_id, label=action, node_type="action")
            G.add_edge(node_id, act_id)

    fig, ax = plt.subplots(figsize=(12, 8))
    pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
    labels = nx.get_node_attributes(G, "label")
    types = nx.get_node_attributes(G, "node_type")

    colors, sizes = [], []
    for n in G.nodes():
        t = types.get(n, "why")
        if t == "problem":
            colors.append("#FF9999"); sizes.append(4000)
        elif t == "root_cause":
            colors.append("#FFCC99"); sizes.append(3500)
        elif t == "action":
            colors.append("#99FF99"); sizes.append(3500)
        else:
            colors.append("#ADD8E6"); sizes.append(3000)

    nx.draw(
        G, pos,
        with_labels=True, labels=labels,
        node_size=sizes, node_color=colors,
        font_size=9, font_weight="bold",
        arrows=True, arrowsize=15, ax=ax
    )

    plt.title("Analyse 5 Pourquoi", fontsize=16)
    legend = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#FF9999", markersize=10, label="Problème"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#ADD8E6", markersize=10, label="Pourquoi ?"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#FFCC99", markersize=10, label="Cause racine"),
    ]
    if action and action.strip():
        legend.append(plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#99FF99", markersize=10, label="Action"))
    ax.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.5, -0.05), ncol=4)
    plt.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Outil Streamlit
# ─────────────────────────────────────────────────────────────────────────────
def five_whys_tool():
    """Outil interactif : méthode des 5 Pourquoi en français."""
    st.title("Analyse 5 Pourquoi")

    st.markdown(
        """
    ## Identifier les causes profondes avec la méthode 5 Pourquoi

    La méthode **5 Pourquoi** consiste à poser la question « Pourquoi ? » à plusieurs reprises (souvent cinq)
    afin de remonter à la cause racine d’un problème.
    """
    )

    # ---------- Données d'exemple ------------------------------------------------
    if "demo_5whys_initialized" not in st.session_state:
        st.session_state.demo_5whys_initialized = True
        st.session_state.demo_5whys_problem = "Panne de la ligne de production"
        st.session_state.demo_5whys_root_cause = "Absence de système de notification de maintenance"
        st.session_state.demo_5whys_recommended_action = (
            "Mettre en place un système de notification de maintenance intégré au planning de production"
        )
        st.session_state.demo_5whys_levels = [
            ["La machine a surchauffé"],
            ["La pompe de refroidissement a lâché"],
            ["La maintenance de la pompe a été oubliée"],
            ["Le calendrier de maintenance n’a pas été suivi"],
            ["Pas de système de notification pour les tâches de maintenance"],
        ]

    # ---------- Session state par défaut ----------------------------------------
    st.session_state.setdefault("current_problem", "")
    st.session_state.setdefault("current_root_cause", "")
    st.session_state.setdefault("current_action", "")
    st.session_state.setdefault("why_levels", [[""], [""], [""], [""], [""]])

    # ---------- Onglets ----------------------------------------------------------
    tab1, tab2, tab3 = st.tabs(["Données", "Visualisation", "Guide méthode"])

    # ───────────────────── Onglet 1 : Données ─────────────────────
    with tab1:
        st.markdown("### Étape 1 : Définir le problème")

        data_source = st.radio(
            "Source des données :",
            ["Données d'exemple", "Saisie manuelle"],
            horizontal=True,
        )

        # ======== DONNÉES D'EXEMPLE (lecture seule) ========
        if data_source == "Données d'exemple":
            st.session_state.current_problem = st.session_state.demo_5whys_problem
            st.session_state.current_root_cause = st.session_state.demo_5whys_root_cause
            st.session_state.current_action = st.session_state.demo_5whys_recommended_action
            st.session_state.why_levels = [lvl[:] for lvl in st.session_state.demo_5whys_levels]  # copie profonde

            st.info(f"**Problème :** {st.session_state.current_problem}")

        # ======== SAISIE MANUELLE ========
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.current_problem = st.text_area(
                    "Décrivez le problème :",
                    "Saisissez votre problème ici",
                    height=80,
                )
            with col2:
                st.session_state.current_root_cause = st.text_area(
                    "Cause racine (si connue) :",
                    "Cause racine potentielle",
                    height=80,
                )
            st.session_state.current_action = st.text_area(
                "Action recommandée :",
                "Décrire la mesure corrective",
                height=80,
            )
            if "why_levels" not in st.session_state or data_source == "Saisie manuelle":
                st.session_state.why_levels = [[""], [""], [""], [""], [""]]

        # ---------- Fonctions internes (ajout / retrait de pourquoi) -------------
        def add_why(level):  # noqa: D401
            st.session_state.why_levels[level].append("")

        def remove_why(level, idx):
            if len(st.session_state.why_levels[level]) > 1:
                st.session_state.why_levels[level].pop(idx)

        # ---------- Affichage des niveaux Pourquoi ------------------------------
        st.markdown("### Étape 2 : Chaîne des Pourquoi")

        if data_source == "Données d'exemple":
            for lvl in range(5):
                with st.expander(f"Niveau {lvl+1}", expanded=True):
                    for i, why in enumerate(st.session_state.why_levels[lvl]):
                        if why.strip():
                            st.info(f"**Pourquoi {lvl+1}.{i+1}** : {why}")
        else:
            for lvl in range(5):
                with st.expander(f"Niveau {lvl+1}", expanded=True):
                    st.caption("*Pourquoi l’événement précédent est‑il survenu ?*")
                    for i, why in enumerate(st.session_state.why_levels[lvl]):
                        c1, c2, c3 = st.columns([0.8, 0.1, 0.1])
                        with c1:
                            st.session_state.why_levels[lvl][i] = st.text_area(
                                f"Pourquoi ? (N{lvl+1}-{i+1})",
                                why,
                                key=f"why_{lvl}_{i}",
                                height=80,
                            )
                        with c2:
                            if st.button("➕", key=f"add_{lvl}_{i}"):
                                add_why(lvl); st.rerun()
                        with c3:
                            if st.button("➖", key=f"rem_{lvl}_{i}"):
                                remove_why(lvl, i); st.rerun()
                # aide contexte (non modifiable)
                captions = [
                    "Causes directes",
                    "Facteurs sous‑jacents",
                    "Problèmes systémiques profonds",
                    "Facteurs organisationnels",
                    "Causes fondamentales",
                ]
                st.caption(captions[lvl])

        if data_source == "Saisie manuelle":
            st.success("Données saisies. Passez à l'onglet « Visualisation ».")

    # ───────────────────── Onglet 2 : Visualisation ─────────────────────
    with tab2:
        st.markdown("### Étape 3 : Visualisation 5 Pourquoi")
        if not st.session_state.current_problem or st.session_state.current_problem == "Saisissez votre problème ici":
            st.info("Veuillez d'abord saisir vos données dans l'onglet « Données ».")
        else:
            fig = create_5why_diagram(
                st.session_state.current_problem,
                st.session_state.why_levels,
                st.session_state.current_root_cause,
                st.session_state.current_action,
            )
            st.pyplot(fig)

            with st.expander("Résumé", expanded=True):
                data = [["Problème", st.session_state.current_problem]]
                for lvl in range(5):
                    whys = [w for w in st.session_state.why_levels[lvl] if w.strip()]
                    for idx, w in enumerate(whys):
                        label = f"Niveau {lvl+1}" + (f" (Chemin {idx+1})" if len(whys) > 1 else "")
                        data.append([label, w])
                if st.session_state.current_root_cause.strip():
                    data.append(["Cause racine", st.session_state.current_root_cause])
                if st.session_state.current_action.strip():
                    data.append(["Action recommandée", st.session_state.current_action])

                st.dataframe(pd.DataFrame(data, columns=["Étape", "Description"]), use_container_width=True)

            st.markdown("#### Exporter")
            c1, c2 = st.columns(2)
            with c1:
                png = export_as_png(fig)
                st.download_button("PNG", png, "5why.png", "image/png")
            with c2:
                pdf = export_as_pdf(fig, "Analyse 5 Pourquoi")
                st.download_button("PDF", pdf, "5why.pdf", "application/pdf")

    # ───────────────────── Onglet 3 : Guide méthode ─────────────────────
    with tab3:
        st.markdown("### Guide rapide 5 Pourquoi")

        with st.expander("Principe", expanded=True):
            st.markdown(
                """
            La méthode **5 Pourquoi** consiste à poser la question « Pourquoi ? » de manière itérative
            jusqu’à atteindre la cause racine d’un problème. Elle est particulièrement utile
            pour les problèmes simples à modérément complexes.
            """
            )

        with st.expander("Quand l'utiliser ?", expanded=True):
            st.markdown(
                """
            - Résolution rapide de problèmes opérationnels  
            - Amélioration continue (Lean, Kaizen, Six Sigma)  
            - Analyse en équipe pour stimuler la réflexion collective  
            - Identification de contre‑mesures ciblées
            """
            )
