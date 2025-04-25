# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils.export import export_as_png


# ─────────────────────────────────────────────────────────────────────────────
# Validation des données
# ─────────────────────────────────────────────────────────────────────────────
def validate_histogram_data(df):
    """
    Valide les données fournies pour l'analyse par histogramme.

    Returns
    -------
    tuple(bool, str) : (valide ?, message d'erreur)
    """
    if df is None or df.empty:
        return False, "Aucune donnée fournie."

    if len(df.columns) < 1:
        return False, "Au moins une colonne numérique est requise."

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if not numeric_cols:
        return False, "Au moins une colonne doit contenir des valeurs numériques."

    if len(df) < 5:
        return False, "Au moins 5 valeurs sont nécessaires pour un histogramme pertinent."

    return True, ""


# ─────────────────────────────────────────────────────────────────────────────
# Génération de l'histogramme
# ─────────────────────────────────────────────────────────────────────────────
def generate_histogram(
    data,
    bins=None,
    chart_title="Distribution des données",
    x_label="Valeur",
    y_label="Fréquence",
):
    """
    Génère un histogramme et renvoie la figure Matplotlib.
    """
    if not isinstance(data, (list, np.ndarray, pd.Series)) or len(data) == 0:
        st.error("Entrée invalide : vous devez fournir des données numériques non vides.")
        return None

    stats = {
        "Count": len(data),
        "Mean": np.mean(data),
        "Median": np.median(data),
        "Min": np.min(data),
        "Max": np.max(data),
    }

    if bins is None:
        bins = min(20, max(5, int(len(data) ** 0.5)))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(data, bins=bins, color="#1f77b4", edgecolor="black", alpha=0.7)

    ax.set_title(chart_title, fontsize=14, pad=10)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)

    stats_text = "\n".join(
        [
            f"Nombre de points : {stats['Count']}",
            f"Moyenne : {stats['Mean']:.2f}",
            f"Médiane : {stats['Median']:.2f}",
            f"Étendue : [{stats['Min']:.2f}, {stats['Max']:.2f}]",
        ]
    )

    props = dict(boxstyle="round", facecolor="white", alpha=0.8, edgecolor="#888888")
    ax.text(0.72, 0.95, stats_text, transform=ax.transAxes, bbox=props, fontsize=10, va="top")

    ax.grid(True, linestyle="--", alpha=0.3)
    ax.set_facecolor("#f8f8f8")
    plt.tight_layout()

    return fig


def fig_to_png(fig):
    """Convertit une figure en bytes PNG."""
    return export_as_png(fig)


# ─────────────────────────────────────────────────────────────────────────────
# Outil Streamlit
# ─────────────────────────────────────────────────────────────────────────────
def histogram_tool():
    """Affiche l'outil interactif d'histogramme."""
    st.title("Histogramme")

    with st.expander("À propos des histogrammes", expanded=False):
        st.markdown(
            """
        ## Visualiser la distribution de vos données

        Les histogrammes montrent la fréquence des valeurs au sein d'intervalles (bins) et permettent de :

        - Visualiser la forme et la dispersion des données  
        - Détecter tendances centrales, valeurs aberrantes et motifs  
        - Appuyer la prise de décision basée sur les données
        """
        )

    # Jeu de données d'exemple
    if "demo_histogram_initialized" not in st.session_state:
        st.session_state.demo_histogram_initialized = True
        np.random.seed(42)
        normal_data = np.random.normal(loc=25, scale=4, size=100).round(1)
        outliers = np.array([38.5, 39.2, 12.3, 11.8, 40.1])
        cycle_times = np.concatenate([normal_data, outliers])
        st.session_state.demo_histogram_data = pd.DataFrame({"Temps de cycle (s)": cycle_times})

    tab1, tab2 = st.tabs(["Saisie des données", "Visualisation"])

    # ──────────── Onglet 1 : données ────────────
    with tab1:
        st.markdown("### Étape 1 : Choisissez votre source de données")
        input_method = st.radio(
            "Mode d'entrée des données :",
            ["Données d'exemple", "Saisie manuelle"],
            horizontal=True,
        )

        df = None

        if input_method == "Données d'exemple":
            st.markdown("#### Données d'exemple : temps de cycle d'assemblage (sec)")
            st.dataframe(
                st.session_state.demo_histogram_data.head(10),
                use_container_width=True,
            )
            df = st.session_state.demo_histogram_data.copy()

        else:  # Saisie manuelle
            st.markdown("#### Saisie manuelle")
            data_input = st.text_area(
                "Entrez des valeurs séparées par des virgules :",
                "42, 36, 45, 39, 41, 44, 37, 38, 40, 43",
                height=100,
                help="Ex. : 5, 10, 12.5",
            )

            if data_input:
                try:
                    values = [float(x.strip()) for x in data_input.split(",") if x.strip()]
                    if len(values) < 5:
                        st.error("Veuillez saisir au moins 5 valeurs.")
                    else:
                        df = pd.DataFrame({"Valeur": values})
                        st.success(f"{len(values)} valeurs chargées avec succès.")
                except Exception as e:
                    st.error(f"Erreur : {e}")
                    st.info("Assurez‑vous d'entrer uniquement des nombres séparés par des virgules.")

        # Validation & stockage
        if df is not None and not df.empty:
            valid, error_msg = validate_histogram_data(df)
            if not valid:
                st.error(error_msg)
            else:
                st.session_state.histogram_data = df
                st.info("Données prêtes. Passez à l'onglet « Visualisation ».")

    # ──────────── Onglet 2 : visualisation ────────────
    with tab2:
        if "histogram_data" not in st.session_state:
            st.info("Veuillez d'abord charger des données dans l'onglet « Saisie des données ».")
        else:
            df = st.session_state.histogram_data
            st.markdown("### Étape 2 : Personnalisez votre histogramme")

            numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

            col1, col2 = st.columns(2)
            with col1:
                selected_column = st.selectbox(
                    "Colonne à visualiser :", numeric_cols, index=0
                )

                bin_method = st.radio(
                    "Méthode de calcul des intervalles :",
                    ["Automatique", "Personnalisée"],
                    horizontal=True,
                )

                if bin_method == "Automatique":
                    auto_bins = min(20, max(5, int(len(df[selected_column]) ** 0.5)))
                    st.caption(f"Bacs automatiques : {auto_bins}")
                    num_bins = auto_bins
                else:
                    num_bins = st.slider(
                        "Nombre d'intervalles :",
                        5,
                        30,
                        10,
                        1,
                    )

            with col2:
                chart_title = st.text_input(
                    "Titre du graphique :", f"Distribution de {selected_column}"
                )
                x_label = st.text_input("Label axe X :", selected_column)
                y_label = st.text_input("Label axe Y :", "Fréquence")

            st.markdown("### Votre histogramme")

            try:
                fig = generate_histogram(
                    df[selected_column],
                    bins=num_bins,
                    chart_title=chart_title,
                    x_label=x_label,
                    y_label=y_label,
                )

                if fig:
                    st.pyplot(fig)

                    with st.expander("Statistiques des données", expanded=False):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric("Nombre de valeurs", len(df[selected_column]))
                            st.metric("Moyenne", round(df[selected_column].mean(), 2))
                            st.metric("Médiane", round(df[selected_column].median(), 2))
                        with c2:
                            st.metric("Minimum", round(df[selected_column].min(), 2))
                            st.metric("Maximum", round(df[selected_column].max(), 2))
                            st.metric(
                                "Étendue",
                                round(df[selected_column].max() - df[selected_column].min(), 2),
                            )

                    # Export PNG
                    st.markdown("### Exporter")
                    try:
                        png_data = fig_to_png(fig)
                        st.download_button(
                            "Exporter en PNG",
                            png_data,
                            "histogramme.png",
                            "image/png",
                        )
                    except Exception as e:
                        st.error(f"Erreur export : {e}")

            except Exception as e:
                st.error(f"Erreur lors de la génération de l'histogramme : {e}")

            # Guide interprétation
            with st.expander("Guide d'interprétation", expanded=False):
                st.markdown(
                    """
                ### Lire votre histogramme

                - **En forme de cloche (normale)** : données centrées, queues symétriques  
                - **Asymétrie à droite** : longue queue vers la droite, moyenne > médiane  
                - **Asymétrie à gauche** : longue queue vers la gauche, moyenne < médiane  
                - **Bimodal** : deux pics distincts, peut indiquer deux populations  
                - **Uniforme** : fréquences similaires dans tous les bacs  

                ### Points d'attention

                - **Tendance centrale** : où se concentre la majorité des données ?  
                - **Dispersion** : quelle est l'étendue des valeurs ?  
                - **Valeurs aberrantes** : points éloignés de la distribution principale  

                Ces informations aident à détecter variations et problèmes potentiels dans votre processus.
                """
                )
