# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from utils.export import export_as_pdf, export_as_png  # export_as_csv inutilisé

# ─────────────────────────────────────────────────────────────────────────────
# Construction du diagramme
# ─────────────────────────────────────────────────────────────────────────────
def create_ishikawa_diagram(problem_statement, categories):
    """Retourne une figure Matplotlib d’un diagramme d’Ishikawa (arêtes de poisson)."""
    fig, ax = plt.subplots(figsize=(14, 8), facecolor="white")
    ax.set_facecolor("white")

    # Épine dorsale
    spine_start_x, main_spine_length = 0.15, 0.65
    spine_end_x, spine_y = spine_start_x + main_spine_length, 0.5
    ax.plot([spine_start_x, spine_end_x], [spine_y, spine_y], color="black", linewidth=3, zorder=1)

    # Flèche à droite
    ax.add_patch(
        mpatches.FancyArrowPatch(
            (spine_end_x - 0.03, spine_y),
            (spine_end_x, spine_y),
            arrowstyle="simple",
            mutation_scale=20,
            linewidth=3,
            color="black",
            zorder=2,
        )
    )

    # Ellipse du problème
    oval_w, oval_h = 0.12, 0.08
    problem_oval = mpatches.Ellipse(
        (spine_end_x + oval_w / 2, spine_y),
        oval_w,
        oval_h,
        facecolor="white",
        edgecolor="black",
        linewidth=1,
        zorder=3,
    )
    ax.add_patch(problem_oval)
    ax.text(
        spine_end_x + oval_w / 2,
        spine_y,
        problem_statement,
        ha="center",
        va="center",
        fontsize=10,
        zorder=4,
    )

    # Catégories fixes
    categories_list = ["Personnes", "Machine", "Méthode", "Matériel", "Mesure", "Environnement"]
    bone_spacing = main_spine_length / len(categories_list)

    # Ligne verticale à droite
    ax.plot(
        [spine_end_x + oval_w + 0.02, spine_end_x + oval_w + 0.02],
        [0.2, 0.8],
        color="black",
        linewidth=1,
        zorder=1,
    )

    # Boucle sur les catégories
    for i, category in enumerate(categories_list):
        x_pos = spine_start_x + bone_spacing * (i + 0.5)
        y_offset = 0.2 if i < 3 else -0.2

        # Arête diagonale
        ax.plot(
            [x_pos, x_pos],
            [spine_y + y_offset, spine_y],
            color="black",
            linewidth=1,
            zorder=2,
        )

        # Boîte catégorie
        box_w, box_h = 0.15, 0.05
        box_x = x_pos - box_w / 2
        box_y = spine_y + y_offset + 0.02 if i < 3 else spine_y + y_offset - 0.07
        ax.add_patch(
            mpatches.Rectangle(
                (box_x, box_y),
                box_w,
                box_h,
                facecolor="white",
                edgecolor="black",
                linewidth=1,
                zorder=3,
            )
        )
        ax.text(box_x + box_w / 2, box_y + box_h / 2, category, ha="center", va="center", fontsize=9, zorder=4)

        # Lignes de causes (max 3)
        for j in range(3):
            line_y = (
                spine_y + y_offset + 0.15 - j * 0.03
                if i < 3
                else spine_y + y_offset - 0.15 + j * 0.03
            )
            ax.plot(
                [x_pos - 0.07, x_pos + 0.07],
                [line_y, line_y],
                color="black",
                linewidth=0.5,
                alpha=0.7,
                zorder=2,
            )

            # Texte cause
            if category in categories and j < len(categories[category]) and categories[category][j].strip():
                ax.text(
                    x_pos - 0.09,
                    line_y,
                    categories[category][j],
                    ha="left",
                    va="center",
                    fontsize=8,
                    zorder=4,
                )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    plt.title("Diagramme d'Ishikawa", fontsize=14, pad=20)
    plt.tight_layout()
    return fig


def count_causes(cat_dict):
    """Compte les causes non vides."""
    return sum(1 for cat in cat_dict for c in cat_dict[cat] if c.strip())


# ─────────────────────────────────────────────────────────────────────────────
# Interface Streamlit
# ─────────────────────────────────────────────────────────────────────────────
def ishikawa_tool():
    st.title("Diagramme d'Ishikawa (arêtes de poisson)")

    st.markdown(
        """
    ## Analyse cause‑effet

    Identifiez et regroupez les causes potentielles d’un problème afin d’en dégager la cause racine.
    """
    )

    # ---------- Données d'exemple ------------------------------------------------
    if "demo_ishikawa_initialized" not in st.session_state:
        st.session_state.demo_ishikawa_initialized = True
        st.session_state.demo_ishikawa_problem = "Délai livré dépassé"
        st.session_state.demo_ishikawa_categories = {
            "Personnes": ["Gestion micro‑managériale", "Secrétaire absente", "Enfants malades"],
            "Machine": ["Machine à café en panne", "Plantages ordinateur", "Connexion Internet faible"],
            "Méthode": ["Processus inefficace", "Priorités floues", "Pas de plan de secours"],
            "Matériel": ["Bureau instable", "Pas de papier", "Pas de crayons"],
            "Mesure": ["Améliorations non suivies", "Pas d’objectifs court terme", "Absence de responsabilité"],
            "Environnement": ["Lumière fluorescente", "Box trop petit", "Bureau trop froid"],
        }

    # ---------- Session state par défaut ----------------------------------------
    st.session_state.setdefault("current_problem", "")
    st.session_state.setdefault("current_categories", {})
    st.session_state.setdefault(
        "custom_categories",
        {
            "Personnes": ["", "", ""],
            "Machine": ["", "", ""],
            "Méthode": ["", "", ""],
            "Matériel": ["", "", ""],
            "Mesure": ["", "", ""],
            "Environnement": ["", "", ""],
        },
    )

    # ---------- Onglets ----------------------------------------------------------
    tab1, tab2, tab3 = st.tabs(["Données", "Visualisation", "Guide méthode"])

    # ───────────────────── Onglet 1 : Données ─────────────────────
    with tab1:
        st.markdown("### Étape 1 : Définir problème et causes")

        data_source = st.radio(
            "Source des données :", ["Données d'exemple", "Saisie manuelle"], horizontal=True
        )

        # ======== DONNÉES D'EXEMPLE (lecture seule) ========
        if data_source == "Données d'exemple":
            st.session_state.current_problem = st.session_state.demo_ishikawa_problem
            st.session_state.current_categories = {
                k: v[:] for k, v in st.session_state.demo_ishikawa_categories.items()
            }

            st.info(f"**Problème :** {st.session_state.current_problem}")

            st.markdown("#### Catégories et causes d’exemple")
            groups = [
                ("Processus", ["Personnes", "Méthode", "Mesure"]),
                ("Ressources", ["Machine", "Matériel", "Environnement"]),
            ]
            for grp_name, grp_cats in groups:
                with st.expander(grp_name, expanded=True):
                    cols = st.columns(len(grp_cats))
                    for i, cat in enumerate(grp_cats):
                        with cols[i]:
                            st.markdown(f"**{cat}**")
                            for cause in st.session_state.current_categories[cat]:
                                st.markdown(f"- {cause}")

        # ======== SAISIE MANUELLE ========
        else:
            st.session_state.current_problem = st.text_area(
                "Énoncé du problème :",
                "Décrivez le problème ici",
                height=80,
            )

            st.session_state.current_categories = st.session_state.custom_categories

            groups = [
                ("Catégories liées au processus", ["Personnes", "Méthode", "Mesure"]),
                ("Catégories liées aux ressources", ["Machine", "Matériel", "Environnement"]),
            ]
            st.markdown("#### Causes par catégorie (max 3 chacune)")
            for grp_name, grp_cats in groups:
                with st.expander(grp_name, expanded=True):
                    for cat in grp_cats:
                        st.markdown(f"**{cat}**")
                        for i in range(3):
                            st.session_state.current_categories[cat][i] = st.text_input(
                                f"{cat} – Cause {i+1}",
                                st.session_state.current_categories[cat][i],
                                key=f"{cat}_{i}",
                            )

            if st.session_state.current_problem != "Décrivez le problème ici":
                st.success("Données saisies. Passez à l'onglet « Visualisation ».")
                st.session_state.custom_categories = st.session_state.current_categories

    # ───────────────────── Onglet 2 : Visualisation ─────────────────────
    with tab2:
        st.markdown("### Étape 2 : Visualiser le diagramme")
        if not st.session_state.current_problem or st.session_state.current_problem == "Décrivez le problème ici":
            st.info("Veuillez renseigner vos données dans l'onglet « Données ».")
        else:
            fig = create_ishikawa_diagram(
                st.session_state.current_problem, st.session_state.current_categories
            )
            st.pyplot(fig)

            with st.expander("Analyse des causes", expanded=True):
                counts = {
                    cat: sum(1 for c in st.session_state.current_categories[cat] if c.strip())
                    for cat in st.session_state.current_categories
                }
                proc_cols = st.columns(3)
                proc_cols[0].metric("Personnes", counts["Personnes"])
                proc_cols[1].metric("Méthode", counts["Méthode"])
                proc_cols[2].metric("Mesure", counts["Mesure"])

                res_cols = st.columns(3)
                res_cols[0].metric("Machine", counts["Machine"])
                res_cols[1].metric("Matériel", counts["Matériel"])
                res_cols[2].metric("Environnement", counts["Environnement"])

                st.markdown(f"**Total causes identifiées :** {count_causes(st.session_state.current_categories)}")

            st.markdown("#### Exporter")
            c1, c2 = st.columns(2)
            with c1:
                png = export_as_png(fig)
                st.download_button("PNG", png, "ishikawa.png", "image/png")
            with c2:
                pdf = export_as_pdf(fig, "Diagramme Ishikawa")
                st.download_button("PDF", pdf, "ishikawa.pdf", "application/pdf")

    # ───────────────────── Onglet 3 : Guide méthode ─────────────────────
    with tab3:
        st.markdown("### Guide Ishikawa")

        with st.expander("Qu’est‑ce qu’un diagramme d’Ishikawa ?", expanded=True):
            st.markdown(
                """
            Un **diagramme d’Ishikawa** (ou diagramme en arêtes de poisson) sert à organiser
            visuellement les causes potentielles d’un problème pour en identifier la cause racine.
            """
            )

        with st.expander("Quand l’utiliser ?", expanded=True):
            st.markdown(
                """
            - **Résolution de problèmes** au sein d’un processus  
            - **Amélioration continue** et gestion de la qualité  
            - **Brainstorming en équipe** afin de répertorier toutes les causes possibles
            """
            )
