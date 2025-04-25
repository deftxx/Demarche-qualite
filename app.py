# -*- coding: utf‑8 -*-
import streamlit as st
import os
from modules.learning import display_learning_module
from modules.pareto import pareto_tool
from modules.five_whys import five_whys_tool
# -*- coding: utf‑8 -*-
import streamlit as st
import os
from modules.learning import display_learning_module
from modules.pareto import pareto_tool
from modules.five_whys import five_whys_tool
from modules.histogram import histogram_tool
from modules.ishikawa import ishikawa_tool
from modules.flowchart import flowchart_tool
from modules.swot import swot_tool
from modules.qqoqccp import qqoqccp_tool
from modules.correlation import correlation_tool
from utils.translation import initialize_translation

# ✅ MUST BE FIRST Streamlit command
st.set_page_config(
    page_title="Outils Qualité",
    page_icon="📊",
    layout="centered",
    menu_items={
        'About': """
        © 2025 Étudiant M1 Mécanique, Université de Lorraine

        Technologies utilisées : Python, Streamlit, Plotly, Pandas
        """
    }
)

# 🔒 Hide GitHub "View Source" link, Streamlit Profile link, and Footer
# Correct CSS to hide only GitHub/Profile links
st.markdown(
    """
    <style>
    a[href*="github.com"] {display: none;}
    a[href*="streamlit.io"] {display: none;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)




# 🌐 Initialize translation
initialize_translation()

# Translation shortcut
_ = st.session_state.translate

st.sidebar.markdown("---")

st.sidebar.info(
    _("Projet réalisé par les étudiants M1 Mécanique : Adim Hachim, Bamoh Abdellah, "
      "Nerhaioui Mohamed, Laaraich Hamza, dans le cadre du cours "
      "**Démarche Qualité de Résolution de Problèmes**.")
)
st.sidebar.markdown("---")

# Main navigation
app_mode = st.sidebar.selectbox(
    _("Sélectionner la section"),
    [_("Accueil"), _("Ressources d’apprentissage"), _("Outils Qualité")]
)

# Tool categories
tool_categories = {
    _("Outils de base"): [_("Diagramme de Pareto"),
                         _("Histogramme"),
                         _("Analyse de corrélation (Correlation)"),
                         _("Analyse 5 Why"),
                         _("Diagramme d'Ishikawa")],
    _("Cartographie des processus"): [_("Organigramme (Flowchart)")],
    _("Outils avancés"): [_("Analyse SWOT"), _("Analyse QQOQCCP")]
}

tool_type = ""

# Tool sub-navigation
if app_mode == _("Outils Qualité"):
    tool_category = st.sidebar.selectbox(
        _("Sélectionner la catégorie d’outil"),
        list(tool_categories.keys()),
        key="tool_category"
    )

    if 'previous_tool' not in st.session_state:
        st.session_state.previous_tool = ""

    tool_type = st.sidebar.selectbox(
        _("Sélectionner l’outil"),
        tool_categories[tool_category],
        key="tool_selection"
    )

    if st.session_state.previous_tool != tool_type:
        for key in list(st.session_state.keys()):
            if key.endswith("_tab_index"):
                del st.session_state[key]
        st.session_state.previous_tool = tool_type

# Main content rendering
if app_mode == _("Accueil"):
    st.title(_("Outils Qualité"))

    st.markdown(_("Cette application vous aide à apprendre et appliquer des outils de gestion de la qualité et de résolution de problèmes."))

    with st.expander(_("Fonctionnalités"), expanded=False):
        st.markdown(_("""\
        - **Outils qualité sélectionnés** : collection d’outils essentiels pour l’analyse et l’amélioration
        - **Interface interactive** : prise en main facile avec visualisations
        - **Exemples pré‑chargés** : jeux de données d’exemple pour chaque outil
        - **Design professionnel** : visuels épurés adaptés aux rapports
        - **Options d’export** : enregistrez vos analyses dans divers formats
        """))

    with st.expander(_("Prise en main"), expanded=False):
        st.markdown(_("""\
        1. Rendez‑vous dans **Ressources d’apprentissage** pour découvrir les concepts clés
        2. Explorez la section **Outils Qualité** pour accéder aux outils interactifs
        3. Chaque outil propose un jeu de données d’exemple
        4. Créez vos propres analyses via la saisie manuelle
        5. Exportez vos résultats pour vos présentations et rapports
        """))

    with st.expander(_("Outils vedettes"), expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(_("Outils de base"))
            features_text = f"""
            - **{_('Diagramme de Pareto')}** : {_('Identifier les causes vitales')}
            - **{_('Analyse 5 Why')}** : {_('Découvrir les causes profondes')}
            - **{_('Histogramme')}** : {_('Visualiser la distribution des données')}
            - **{_('Analyse de corrélation (Correlation)')}** : {_('Analyser les relations entre variables')}
            - **{_('Diagramme d Ishikawa')}** : {_('Cartographier les relations cause‑effet')}
            """
            st.markdown(features_text)

            st.subheader(_("Cartographie des processus"))
            process_text = f"""
            - **{_('Organigramme (Flowchart)')}** : {_('Documenter les flux de processus')}
            """
            st.markdown(process_text)

        with col2:
            st.subheader(_("Outils avancés"))
            advanced_text = f"""
            - **{_('Analyse SWOT')}** : {_('Évaluer forces, faiblesses, opportunités et menaces')}
            - **{_('Analyse QQOQCCP')}** : {_('Cadre d analyse complet d un problème')}
            """
            st.markdown(advanced_text)

elif app_mode == _("Ressources d’apprentissage"):
    display_learning_module(_("Ressources d’apprentissage"))

elif app_mode == _("Outils Qualité"):
    tool_type_lower = tool_type.lower()

    if "pareto" in tool_type_lower:
        pareto_tool()
    elif "5 why" in tool_type_lower:
        five_whys_tool()
    elif "histo" in tool_type_lower:
        histogram_tool()
    elif "correl" in tool_type_lower:
        correlation_tool()
    elif "ishikawa" in tool_type_lower:
        ishikawa_tool()
    elif "flow" in tool_type_lower:
        flowchart_tool()
    elif "swot" in tool_type_lower:
        swot_tool()
    elif "qqoqccp" in tool_type_lower or "5w2h" in tool_type_lower:
        qqoqccp_tool()

# Sidebar navigation guide
if app_mode == _("Outils Qualité"):
    st.sidebar.markdown("---")
    st.sidebar.info(
        f"📌 **{_('Guide de navigation')}**\n\n"
        f"{_('Utilisez ce menu pour naviguer entre les différents outils :')}\n"
        f"- 📊 **{_('Outils de base')}** : {_('Diagramme de Pareto, Histogramme, Corrélation, etc.')}\n"
        f"- 📝 **{_('Cartographie des processus')}** : {_('Visualisation des workflows')}\n"
        f"- 🔍 **{_('Outils avancés')}** : {_('Analyses à large spectre')}\n\n"
        f"{_('Chaque outil inclut un exemple de données pour démarrer rapidement.')}"
    )

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    _("Cette application est conçue pour enseigner et appliquer les outils de gestion de la qualité. "
      "Utilisez la navigation ci‑dessus pour explorer le contenu pédagogique et les outils interactifs.")
)
