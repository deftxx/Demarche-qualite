# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from io import StringIO
from utils.export import export_as_pdf, export_as_png


# ─────────────────────────────────────────────────────────────────────────────
# Validation des données
# ─────────────────────────────────────────────────────────────────────────────
def validate_correlation_data(df: pd.DataFrame):
    """Vérifie que la table comporte au moins deux colonnes numériques non vides."""
    if df.empty:
        return False, "Le jeu de données est vide."
    if len(df.select_dtypes(include=np.number).columns) < 2:
        return (
            False,
            "Le jeu de données doit contenir au moins deux colonnes numériques pour l'analyse de corrélation.",
        )
    return True, ""


# ─────────────────────────────────────────────────────────────────────────────
# Création du nuage de points
# ─────────────────────────────────────────────────────────────────────────────
def create_correlation_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    add_trendline: bool = True,
    chart_title: str = "Analyse de corrélation",
    x_label: str | None = None,
    y_label: str | None = None,
    marker_size: int = 60,
    marker_color: str = "#1f77b4",
    line_color: str = "#ff7f0e",
    show_grid: bool = True,
    show_stats_box: bool = True,
):
    """Retourne une figure Matplotlib avec nuage de points + stats."""
    fig, ax = plt.subplots(figsize=(12, 8))

    x_data, y_data = df[x_col], df[y_col]
    ax.scatter(
        x_data,
        y_data,
        alpha=0.7,
        color=marker_color,
        s=marker_size,
        edgecolors="white",
        linewidth=0.5,
    )

    corr = x_data.corr(y_data)
    r_squared = corr**2
    slope = intercept = 0

    if add_trendline:
        slope, intercept = np.polyfit(x_data, y_data, 1)
        p = np.poly1d([slope, intercept])
        x_trend = np.linspace(x_data.min(), x_data.max(), 100)
        ax.plot(x_trend, p(x_trend), "--", color=line_color, linewidth=2, label=f"y = {slope:.3f}x + {intercept:.3f}")
        ax.legend(loc="best", frameon=True, framealpha=0.8)

    ax.set_xlabel(x_label or x_col, fontsize=12)
    ax.set_ylabel(y_label or y_col, fontsize=12)

    direction = "positive" if corr > 0 else "négative" if corr < 0 else "nulle"
    strength = "faible" if abs(corr) < 0.3 else "modérée" if abs(corr) < 0.7 else "forte"
    ax.set_title(f"{chart_title}\nCorrélation {strength} {direction} (r = {corr:.3f})", fontsize=14)

    if show_grid:
        ax.grid(True, linestyle="--", alpha=0.3)

    if show_stats_box:
        stats_text = (
            f"r : {corr:.3f}\n"
            f"R² : {r_squared:.3f}\n"
            f"N : {len(x_data)}"
            + (f"\nRégression : y = {slope:.3f}x + {intercept:.3f}" if add_trendline else "")
        )
        bbox = dict(boxstyle="round", facecolor="white", alpha=0.7)
        ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=11, va="top", bbox=bbox)

    ax.tick_params(axis="both", which="major", labelsize=10)
    plt.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Outil Streamlit principal
# ─────────────────────────────────────────────────────────────────────────────
def correlation_tool():
    """Outil interactif d'analyse de corrélation."""
    st.title("Analyse de corrélation")

    st.markdown(
        """
    ## Étudier la relation entre deux variables

    L'analyse de corrélation permet de mesurer la force et la direction du lien linéaire entre deux variables continues.
    """
    )

    # ------------------- Données d'exemple -----------------------------------
    if "demo_correlation_initialized" not in st.session_state:
        st.session_state.demo_correlation_initialized = True
        np.random.seed(42)
        temp = np.linspace(20, 35, 50) + np.random.normal(0, 0.3, 50)
        defects = 2 + 0.5 * (temp - 20) + np.random.normal(0, 1, 50)
        humidity = 60 - 1 * (temp - 20) + np.random.normal(0, 2, 50)
        speed = 100 + 2 * (temp - 20) + np.random.normal(0, 5, 50)
        st.session_state.demo_correlation_data = pd.DataFrame(
            {
                "Température (°C)": temp.round(1),
                "Taux de défauts (%)": defects.round(1),
                "Humidité (%)": humidity.round(1),
                "Vitesse de prod. (u/h)": speed.round(1),
            }
        )

    # ------------------- Session state --------------------------------------
    st.session_state.setdefault("correlation_data", None)
    st.session_state.setdefault("correlation_x_column", None)
    st.session_state.setdefault("correlation_y_column", None)
    st.session_state.setdefault(
        "correlation_settings",
        {
            "add_trendline": True,
            "chart_title": "Analyse de corrélation",
            "x_label": None,
            "y_label": None,
            "marker_size": 60,
            "marker_color": "#1f77b4",
            "line_color": "#ff7f0e",
            "show_grid": True,
            "show_stats_box": True,
        },
    )

    # ------------------- Onglets --------------------------------------------
    tab1, tab2, tab3 = st.tabs(["Données", "Visualisation", "Guide méthode"])

    # ────────────────────────────────────────
    # Onglet 1 : Données
    # ────────────────────────────────────────
    with tab1:
        st.markdown("### Étape 1 : Choisissez vos données")

        input_method = st.radio(
            "Méthode d'entrée :",
            ["Données d'exemple", "Saisie manuelle"],
            horizontal=True,
        )

        df = None

        # ---------- Jeu d'exemple ----------
        if input_method == "Données d'exemple":
            st.markdown("#### Données d'exemple : variables process")
            with st.expander("Voir les données", expanded=True):
                st.dataframe(st.session_state.demo_correlation_data.head(10), use_container_width=True)
                st.markdown("##### Matrice de corrélation")
                st.dataframe(
                    st.session_state.demo_correlation_data.corr()
                    .round(3)
                    .style.background_gradient(cmap="coolwarm", axis=None, vmin=-1, vmax=1),
                    use_container_width=True,
                )

            relation = st.selectbox(
                "Relation à analyser :",
                [
                    "Température → Taux de défauts (positive)",
                    "Température → Humidité (négative)",
                    "Température → Vitesse de prod. (positive)",
                    "Variables personnalisées",
                ],
            )

            mapping = {
                "Température → Taux de défauts (positive)": ("Température (°C)", "Taux de défauts (%)"),
                "Température → Humidité (négative)": ("Température (°C)", "Humidité (%)"),
                "Température → Vitesse de prod. (positive)": ("Température (°C)", "Vitesse de prod. (u/h)"),
            }

            if relation in mapping:
                st.session_state.correlation_x_column, st.session_state.correlation_y_column = mapping[relation]
                st.session_state.correlation_settings["chart_title"] = f"{mapping[relation][0]} vs {mapping[relation][1]}"
                st.session_state.correlation_settings["x_label"] = mapping[relation][0]
                st.session_state.correlation_settings["y_label"] = mapping[relation][1]

            df = st.session_state.demo_correlation_data.copy()

        # ---------- Saisie manuelle ----------
        else:
            st.markdown("#### Saisie manuelle (format CSV)")
            exemple_defaut = (
                "Température,Défauts\n"
                "20.5,10.2\n22.1,11.5\n23.4,12.1\n25.0,13.8\n26.3,14.6\n27.8,16.2\n29.4,17.5\n30.2,18.9"
            )
            data_input = st.text_area("Collez vos données CSV :", exemple_defaut, height=200)
            if data_input:
                try:
                    df = pd.read_csv(StringIO(data_input))
                    st.success("Données lues avec succès !")
                    with st.expander("Aperçu", expanded=True):
                        st.dataframe(df, use_container_width=True)
                        num_df = df.select_dtypes(include=np.number)
                        if num_df.shape[1] > 1:
                            st.markdown("##### Matrice de corrélation")
                            st.dataframe(
                                num_df.corr()
                                .round(3)
                                .style.background_gradient(cmap="coolwarm", axis=None, vmin=-1, vmax=1),
                                use_container_width=True,
                            )
                except Exception as e:
                    st.error(f"Erreur de lecture : {e}")

        # ---------- Validation ----------
        if df is not None:
            ok, msg = validate_correlation_data(df)
            if not ok:
                st.error(msg)
                st.session_state.correlation_data = None
            else:
                st.session_state.correlation_data = df
                numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

                # Variables personnalisées si nécessaire
                if (
                    input_method == "Saisie manuelle"
                    or (input_method == "Données d'exemple" and relation == "Variables personnalisées")
                ):
                    st.markdown("#### Sélection des variables")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.session_state.correlation_x_column = st.selectbox(
                            "Variable X :", numeric_cols, index=0
                        )
                    with col2:
                        st.session_state.correlation_y_column = st.selectbox(
                            "Variable Y :", numeric_cols, index=min(1, len(numeric_cols) - 1)
                        )
                    st.session_state.correlation_settings["chart_title"] = (
                        f"{st.session_state.correlation_x_column} vs {st.session_state.correlation_y_column}"
                    )
                    st.session_state.correlation_settings["x_label"] = st.session_state.correlation_x_column
                    st.session_state.correlation_settings["y_label"] = st.session_state.correlation_y_column

                if st.session_state.correlation_x_column and st.session_state.correlation_y_column:
                    st.success("Variables sélectionnées. Rendez‑vous dans l'onglet « Visualisation ».")

    # ────────────────────────────────────────
    # Onglet 2 : Visualisation
    # ────────────────────────────────────────
    with tab2:
        st.markdown("### Étape 2 : Visualisation")

        if st.session_state.correlation_data is None:
            st.info("Veuillez d'abord choisir vos données dans l'onglet « Données ».")
        elif not (st.session_state.correlation_x_column and st.session_state.correlation_y_column):
            st.info("Veuillez sélectionner les variables X et Y dans l'onglet « Données ».")
        else:
            df = st.session_state.correlation_data
            x_col = st.session_state.correlation_x_column
            y_col = st.session_state.correlation_y_column

            with st.expander("Personnalisation du graphique", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.session_state.correlation_settings["chart_title"] = st.text_input(
                        "Titre du graphique :", st.session_state.correlation_settings["chart_title"]
                    )
                    st.session_state.correlation_settings["x_label"] = st.text_input(
                        "Label X :", st.session_state.correlation_settings["x_label"] or x_col
                    )
                    st.session_state.correlation_settings["y_label"] = st.text_input(
                        "Label Y :", st.session_state.correlation_settings["y_label"] or y_col
                    )
                    st.session_state.correlation_settings["add_trendline"] = st.checkbox(
                        "Afficher la droite de régression", st.session_state.correlation_settings["add_trendline"]
                    )
                with col2:
                    st.session_state.correlation_settings["marker_size"] = st.slider(
                        "Taille des points :", 20, 100, st.session_state.correlation_settings["marker_size"], 5
                    )
                    st.session_state.correlation_settings["marker_color"] = st.color_picker(
                        "Couleur des points :", st.session_state.correlation_settings["marker_color"]
                    )
                    st.session_state.correlation_settings["line_color"] = st.color_picker(
                        "Couleur de la régression :", st.session_state.correlation_settings["line_color"]
                    )
                    st.session_state.correlation_settings["show_grid"] = st.checkbox(
                        "Afficher la grille", st.session_state.correlation_settings["show_grid"]
                    )
                    st.session_state.correlation_settings["show_stats_box"] = st.checkbox(
                        "Afficher le panneau de stats", st.session_state.correlation_settings["show_stats_box"]
                    )

            fig = create_correlation_scatter(
                df,
                x_col,
                y_col,
                **st.session_state.correlation_settings,
            )
            st.pyplot(fig)

            # --------- Résumé ---------
            corr = df[x_col].corr(df[y_col])
            r_sq = corr**2
            strength = "faible" if abs(corr) < 0.3 else "modérée" if abs(corr) < 0.7 else "forte"
            direction = "positive" if corr > 0 else "négative" if corr < 0 else "nulle"

            with st.expander("Résumé de l'analyse", expanded=True):
                c1, c2, c3 = st.columns(3)
                c1.metric("Coefficient r", f"{corr:.3f}")
                c2.metric("R²", f"{r_sq:.3f}")
                c3.markdown(f"**Relation** : {strength.capitalize()} {direction}")

                if st.session_state.correlation_settings["add_trendline"]:
                    slope, intercept = np.polyfit(df[x_col], df[y_col], 1)
                    st.markdown(
                        f"**Équation** : y = {slope:.3f}x + {intercept:.3f}\n\n"
                        f"À chaque augmentation de 1 unité de **{x_col}**, "
                        f"**{y_col}** {'augmente' if slope > 0 else 'diminue'} en moyenne de {abs(slope):.3f}."
                    )

                st.info(
                    f"La corrélation **{strength}** {direction} indique qu'environ {r_sq*100:.1f} % "
                    f"de la variation de **{y_col}** est expliquée par **{x_col}**."
                )

            # --------- Export ---------
            st.markdown("#### Exporter")
            col_png, col_pdf = st.columns(2)
            with col_png:
                png = export_as_png(fig)
                st.download_button("Télécharger PNG", png, "correlation.png", "image/png")
            with col_pdf:
                pdf = export_as_pdf(fig, st.session_state.correlation_settings["chart_title"])
                st.download_button("Télécharger PDF", pdf, "correlation.pdf", "application/pdf")

    # ────────────────────────────────────────
    # Onglet 3 : Guide méthode
    # ────────────────────────────────────────
    with tab3:
        st.markdown("### Guide d'analyse de corrélation")

        with st.expander("Qu'est‑ce que l'analyse de corrélation ?", expanded=True):
            st.markdown(
                """
            L'analyse de corrélation mesure la **force** et la **direction** d'une relation linéaire entre deux variables
            continues. Le coefficient de corrélation de **Pearson (r)** varie de **-1** (corrélation négative parfaite)
            à **+1** (corrélation positive parfaite). Une valeur de **0** indique l'absence de relation linéaire.
            """
            )

        with st.expander("Interpréter les coefficients", expanded=True):
            st.markdown(
                """
            | Valeur de r | Interprétation |
            |-------------|----------------|
            | 0,00 – 0,19 | Relation très faible |
            | 0,20 – 0,29 | Relation faible |
            | 0,30 – 0,49 | Relation modérée |
            | 0,50 – 0,69 | Relation forte |
            | 0,70 – 1,00 | Relation très forte |

            **R²** (carré de r) indique la proportion de la variance expliquée :  
            - R² = 0,25 ⇒ 25 % de la variation expliquée  
            - R² = 0,64 ⇒ 64 % de la variation expliquée
            """
            )
