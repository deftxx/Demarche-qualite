# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils.export import export_as_png, export_as_pdf


# ─────────────────────────────────────────────────────────────────────────────
# Validation des données
# ─────────────────────────────────────────────────────────────────────────────
def validate_pareto_data(df):
    """
    Valide les données téléchargées pour l'analyse de Pareto.

    Args:
        df (pandas.DataFrame): Le DataFrame à valider.

    Returns:
        tuple: (is_valid, message_erreur)
    """
    if df is None or df.empty:
        return False, "Aucune donnée fournie."

    if len(df.columns) < 2:
        return False, "Au moins deux colonnes sont requises : l'une pour les catégories et l'autre pour les valeurs."

    # Vérifie que la deuxième colonne est bien numérique
    try:
        pd.to_numeric(df.iloc[:, 1])
    except Exception:
        return False, "La deuxième colonne doit contenir des valeurs numériques."

    if len(df) < 2:
        return False, "Au moins deux points de données sont nécessaires pour un diagramme de Pareto pertinent."

    return True, ""


# ─────────────────────────────────────────────────────────────────────────────
# Création du diagramme
# ─────────────────────────────────────────────────────────────────────────────
def create_pareto_chart(
    df,
    category_col,
    value_col,
    chart_title="Analyse de Pareto",
    x_label="Catégories",
    y_label="Fréquence",
    show_percent_line=True,
    bar_color="#1f77b4",
    line_color="#ff7f0e",
):
    """
    Génère un diagramme de Pareto à partir d'un DataFrame.

    Returns:
        matplotlib.figure.Figure, pandas.DataFrame (données triées)
    """
    # Force la colonne de valeurs en numérique
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

    # Trie décroissant
    df_sorted = df.sort_values(by=value_col, ascending=False).copy()

    # Pourcentages cumulés
    df_sorted["cumulative"] = df_sorted[value_col].cumsum()
    df_sorted["percentage"] = 100 * df_sorted[value_col] / df_sorted[value_col].sum()
    df_sorted["cumulative_percentage"] = 100 * df_sorted["cumulative"] / df_sorted[value_col].sum()

    fig, ax1 = plt.subplots(figsize=(12, 8))
    ax1.set_facecolor("#f8f8f8")
    fig.patch.set_facecolor("white")

    bars = ax1.bar(
        df_sorted[category_col],
        df_sorted[value_col],
        color=bar_color,
        edgecolor="black",
        alpha=0.8,
        width=0.6,
    )

    # Valeurs au‑dessus des barres
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, height + 0.1, f"{height:.0f}", ha="center", va="bottom", fontsize=9)

    ax1.set_xlabel(x_label, fontsize=12, fontweight="bold")
    ax1.set_ylabel(y_label, fontsize=12, fontweight="bold", color=bar_color)
    ax1.tick_params(axis="y", labelcolor=bar_color)

    if len(df_sorted) > 5:
        plt.xticks(rotation=45, ha="right")

    ax1.tick_params(axis="both", which="major", labelsize=10)

    # Axe secondaire pour le % cumulé
    ax2 = ax1.twinx()
    ax2.plot(
        df_sorted[category_col],
        df_sorted["cumulative_percentage"],
        color=line_color,
        marker="o",
        linestyle="-",
        linewidth=2.5,
        markersize=7,
        label="Pourcentage cumulé",
    )

    for i, pct in enumerate(df_sorted["cumulative_percentage"]):
        ax2.annotate(
            f"{pct:.1f} %",
            (i, pct),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=9,
            color=line_color,
        )

    ax2.set_ylabel("Pourcentage cumulé", fontsize=12, fontweight="bold", color=line_color)
    ax2.tick_params(axis="y", labelcolor=line_color)
    ax2.set_ylim(0, 110)

    if show_percent_line:
        ax2.axhline(y=80, color="red", linestyle="--", alpha=0.7, linewidth=1.5, label="Seuil 80 %")
        lignes, libelles = ax2.get_legend_handles_labels()
        ax2.legend(lignes, libelles, loc="upper left", bbox_to_anchor=(0.01, 0.99))

    ax1.grid(axis="y", linestyle="--", alpha=0.3)
    plt.title(chart_title, fontsize=16, fontweight="bold", pad=15)
    plt.tight_layout()

    return fig, df_sorted


# ─────────────────────────────────────────────────────────────────────────────
# Outil Streamlit
# ─────────────────────────────────────────────────────────────────────────────
def pareto_tool():
    """Affiche l'outil interactif de diagramme de Pareto"""
    st.title("Diagramme de Pareto")

    with st.expander("À propos du diagramme de Pareto", expanded=False):
        st.markdown(
            """
        ## Identifier les quelques causes vitales avec l'analyse de Pareto

        Le principe de Pareto (règle 80/20) suggère qu'environ 80 % des effets proviennent de 20 % des causes.
        Un diagramme de Pareto associe un histogramme à une courbe cumulative pour vous aider à :

        - Visualiser les facteurs les plus significatifs dans un jeu de données
        - Comprendre l'impact cumulatif de la résolution de ces facteurs
        - Orienter vos efforts d'amélioration pour un impact maximal
        """
        )

    # Données d'exemple (réclamations clients) — initialisation unique
    if "demo_pareto_initialized" not in st.session_state:
        st.session_state.demo_pareto_initialized = True
        st.session_state.demo_pareto_data = pd.DataFrame(
            {
                "Type de réclamation": [
                    "Livraison retardée",
                    "Produit défectueux",
                    "Article incorrect",
                    "Pièces manquantes",
                    "Documentation insuffisante",
                    "Problèmes d'emballage",
                    "Erreur de facturation",
                ],
                "Fréquence": [187, 124, 73, 42, 35, 28, 19],
            }
        )

    tab1, tab2 = st.tabs(["Saisie des données", "Visualisation"])

    # ────────────────
    # Onglet 1 : Données
    # ────────────────
    with tab1:
        st.markdown("### Étape 1 : Choisissez votre source de données")

        input_method = st.radio(
            "Sélectionnez le mode d'entrée des données :",
            ["Données d'exemple", "Saisie manuelle"],
            horizontal=True,
            help="Choisissez entre le jeu de données préchargé ou entrez vos propres données.",
        )

        df = None

        if input_method == "Données d'exemple":
            st.markdown("#### Données d'exemple : Réclamations clients")
            st.markdown("Ce jeu de données montre la répartition des réclamations clients par type.")
            st.dataframe(st.session_state.demo_pareto_data, use_container_width=True)
            df = st.session_state.demo_pareto_data.copy()

        else:  # Saisie manuelle
            st.markdown("#### Saisie manuelle")
            st.markdown("Indiquez vos catégories et les valeurs correspondantes :")

            if "manual_pareto_data" not in st.session_state:
                st.session_state.manual_pareto_data = pd.DataFrame(
                    {"Catégorie": ["Exemple A", "Exemple B", "Exemple C"], "Valeur": [10, 5, 3]}
                )

            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("Ajouter une ligne", key="add_row_pareto"):
                    new_row = pd.DataFrame({"Catégorie": ["Nouvelle catégorie"], "Valeur": [0]})
                    st.session_state.manual_pareto_data = pd.concat(
                        [st.session_state.manual_pareto_data, new_row], ignore_index=True
                    )

            with col2:
                if (
                    st.button("Supprimer la dernière ligne", key="remove_row_pareto")
                    and len(st.session_state.manual_pareto_data) > 1
                ):
                    st.session_state.manual_pareto_data = st.session_state.manual_pareto_data.iloc[:-1]

            with col3:
                st.caption("Saisissez au moins 2 catégories et leurs valeurs.")

            st.markdown("#### Vos données :")
            data_editor = st.data_editor(
                st.session_state.manual_pareto_data,
                use_container_width=True,
                hide_index=True,
                num_rows="fixed",
                column_config={
                    "Catégorie": st.column_config.TextColumn(
                        "Nom de la catégorie", help="Nom de chaque catégorie", width="medium"
                    ),
                    "Valeur": st.column_config.NumberColumn(
                        "Valeur", help="Valeur numérique pour chaque catégorie", min_value=0, step=1, format="%d"
                    ),
                },
            )

            if data_editor is not None:
                df = data_editor

        # Validation
        if df is not None and not df.empty:
            valid, error_msg = validate_pareto_data(df)
            if not valid:
                st.error(error_msg)
            else:
                st.session_state.pareto_data = df
                st.success("Données chargées avec succès. Rendez‑vous dans l'onglet « Visualisation ».")

    # ────────────────
    # Onglet 2 : Visualisation
    # ────────────────
    with tab2:
        if "pareto_data" not in st.session_state:
            st.info("Veuillez d'abord charger vos données dans l'onglet « Saisie des données ».")
        else:
            df = st.session_state.pareto_data
            st.markdown("### Étape 2 : Personnalisez votre diagramme")

            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    category_column = st.selectbox(
                        "Sélectionnez la colonne des catégories :",
                        df.columns.tolist(),
                        index=0,
                        help="Colonne contenant les données catégorielles (ex. : types de défaut).",
                    )

                    value_column = st.selectbox(
                        "Sélectionnez la colonne des valeurs :",
                        df.columns.tolist(),
                        index=min(1, len(df.columns) - 1),
                        help="Colonne contenant les valeurs numériques (ex. : fréquences).",
                    )

                    show_reference = st.checkbox(
                        "Afficher la ligne seuil 80 %", value=True, help="Affiche la ligne de contribution cumulative 80 %"
                    )

                with col2:
                    chart_title = st.text_input("Titre du graphique :", "Analyse de Pareto")
                    x_label = st.text_input("Label axe X :", category_column)
                    y_label = st.text_input("Label axe Y :", "Fréquence")

            st.markdown("### Votre diagramme de Pareto")

            try:
                fig, df_sorted = create_pareto_chart(
                    df,
                    category_column,
                    value_column,
                    chart_title=chart_title,
                    x_label=x_label,
                    y_label=y_label,
                    show_percent_line=show_reference,
                )
                st.pyplot(fig)

                # ───────── Résultats analyse Pareto ─────────
                with st.expander("Résultats de l'analyse de Pareto", expanded=True):
                    vital_few = df_sorted[df_sorted["cumulative_percentage"] <= 80]
                    if len(vital_few) == 0:
                        vital_few = df_sorted.iloc[[0]]

                    st.markdown(f"### Les quelques causes vitales ({len(vital_few)} sur {len(df_sorted)} catégories)")

                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("Nombre de catégories vitales", f"{len(vital_few)}")
                    with m2:
                        st.metric("Contribution cumulative", f"{vital_few['cumulative_percentage'].max():.1f} %")
                    with m3:
                        st.metric(
                            "Ratio de catégories",
                            f"{len(vital_few)}/{len(df_sorted)}",
                            f"{(len(vital_few)/len(df_sorted)*100):.1f} %",
                        )

                    st.markdown("#### Détail")
                    vital_display = vital_few[[category_column, value_column, "percentage", "cumulative_percentage"]].copy()
                    vital_display["percentage"] = vital_display["percentage"].round(1).astype(str) + " %"
                    vital_display["cumulative_percentage"] = vital_display["cumulative_percentage"].round(1).astype(str) + " %"
                    vital_display.columns = [category_column, value_column, "Pourcentage", "Cumul %"]
                    st.dataframe(vital_display, use_container_width=True)

                    st.info(
                        f"**Enseignement clé** : en se concentrant sur seulement {len(vital_few)} catégories "
                        f"({(len(vital_few)/len(df_sorted)*100):.1f} % du total), vous traitez "
                        f"{vital_few['cumulative_percentage'].max():.1f} % des problèmes."
                    )

                # Jeu de données complet
                with st.expander("Afficher le jeu de données complet", expanded=False):
                    full = df_sorted[[category_column, value_column, "percentage", "cumulative_percentage"]].copy()
                    full["percentage"] = full["percentage"].round(1).astype(str) + " %"
                    full["cumulative_percentage"] = full["cumulative_percentage"].round(1).astype(str) + " %"
                    full.columns = [category_column, value_column, "Pourcentage", "Cumul %"]
                    st.dataframe(full, use_container_width=True)

                # ───────── Export ─────────
                st.markdown("### Exporter")
                c1, c2 = st.columns(2)
                with c1:
                    try:
                        png_data = export_as_png(fig)
                        st.download_button("Exporter en PNG", png_data, "diagramme_pareto.png", "image/png")
                    except Exception as e:
                        st.error(f"Erreur export PNG : {e}")
                with c2:
                    try:
                        pdf_data = export_as_pdf(fig, chart_title)
                        st.download_button("Exporter en PDF", pdf_data, "diagramme_pareto.pdf", "application/pdf")
                    except Exception as e:
                        st.error(f"Erreur export PDF : {e}")

            except Exception as e:
                st.error(f"Erreur lors de la génération du diagramme : {e}")

            # ───────── Guide d'interprétation ─────────
            with st.expander("Guide d'interprétation", expanded=False):
                st.markdown(
                    """
                ### Comment lire votre diagramme ?

                - **Barres** : contribution individuelle de chaque catégorie (ordre décroissant)  
                - **Ligne** : contribution cumulative en pourcentage  
                - **Seuil 80 %** : ligne rouge en tirets — indique où s'arrête la « loi des 80/20 »

                ### Utilisation pratique

                1. **Repérez les causes vitales** (avant la ligne 80 %)  
                2. **Concentrez vos actions** sur ces catégories prioritaires  
                3. **Mesurez de nouveau** après amélioration pour vérifier l'impact
                """
                )
