# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
from utils.export import export_as_pdf, export_as_png


# ─────────────────────────────────────────────────────────
# Génération du diagramme QQOQCCP
# ─────────────────────────────────────────────────────────
def create_qqoqccp_diagram(title, answers):
    fig, ax = plt.subplots(figsize=(14, 12))
    ax.axis("off")

    questions = {
        "Quoi ?":     {"color": "lightblue",   "y": 0.90},
        "Qui ?":      {"color": "lightgreen",  "y": 0.75},
        "Où ?":       {"color": "lightyellow", "y": 0.60},
        "Quand ?":    {"color": "lightpink",   "y": 0.45},
        "Comment ?":  {"color": "lightgray",   "y": 0.30},
        "Combien ?":  {"color": "wheat",       "y": 0.15},
        "Pourquoi ?": {"color": "lavender",    "y": 0.00},
    }

    ax.text(0.5, 1.0, title, ha="center", va="bottom", fontsize=16, fontweight="bold")
    width, height = 0.9, 0.12

    import textwrap
    wrap = lambda txt, w: textwrap.fill(txt, width=w)

    for q, prop in questions.items():
        y = prop["y"]
        ax.add_patch(
            plt.Rectangle((0.05, y), width, height, facecolor=prop["color"], edgecolor="black", alpha=0.7)
        )
        ax.text(0.08, y + height / 2, q, ha="left", va="center", fontsize=12, fontweight="bold")

        ans = answers.get(q, "")
        if len(ans) > 80:
            ans_wrapped, fsize = wrap(ans, 60), 9
        elif len(ans) > 50:
            ans_wrapped, fsize = wrap(ans, 45), 10
        else:
            ans_wrapped, fsize = ans, 11

        lines = ans_wrapped.count("\n") + 1
        ax.text(
            0.5,
            y + height / 2 - (lines - 1) * 0.005,
            ans_wrapped,
            ha="left",
            va="center",
            fontsize=fsize,
            linespacing=0.9,
        )

    plt.tight_layout(pad=1.2)
    return fig


def get_question_help_text(question):
    aides = {
        "Quoi ?": "Que se passe‑t‑il ? Quel est le sujet ou le problème ?",
        "Qui ?": "Qui est impliqué ? Qui est concerné ? Qui est responsable ?",
        "Où ?": "Où cela se produit‑il ? Lieu d’origine / d’impact ?",
        "Quand ?": "Quand cela se produit‑il ? Depuis quand ? Fréquence ?",
        "Comment ?": "Comment cela se produit‑il ? Méthodes, processus…",
        "Combien ?": "Combien cela coûte‑t‑il ? Ressources, quantité…",
        "Pourquoi ?": "Pourquoi cela arrive‑t‑il ? Cause racine ?",
    }
    return aides.get(question, "")


# ─────────────────────────────────────────────────────────
# Interface Streamlit
# ─────────────────────────────────────────────────────────
def qqoqccp_tool():
    st.title("Analyse QQOQCCP (5W2H)")

    st.markdown(
        """
    ## Méthode complète de questionnement QQOQCCP

    Cette approche (parfois appelée 5W2H) permet de décrire et d’analyser en profondeur une situation
    grâce à 7 questions : **Quoi, Qui, Où, Quand, Comment, Combien, Pourquoi**.
    """
    )

    # ---------- Données d'exemple ----------
    if "demo_qqoqccp_initialized" not in st.session_state:
        st.session_state.demo_qqoqccp_initialized = True
        st.session_state.demo_qqoqccp_title = "Analyse du retard du projet X"
        st.session_state.demo_qqoqccp_answers = {
            "Quoi ?": "Retard important de livraison du projet X",
            "Qui ?": "Équipe dev, chef de projet, fournisseurs",
            "Où ?": "Usine principale et sites fournisseurs",
            "Quand ?": "Depuis trois mois, accentué les deux dernières semaines",
            "Comment ?": "Jalons manqués et livraisons incomplètes",
            "Combien ?": "30 % de dérive planning, +50 k€",
            "Pourquoi ?": "Pénurie composants, communication faible, dérive périmètre",
        }

    questions = ["Quoi ?", "Qui ?", "Où ?", "Quand ?", "Comment ?", "Combien ?", "Pourquoi ?"]

    tab1, tab2, tab3 = st.tabs(["Données", "Visualisation", "Guide"])

    # ───────── Tab 1 : Données ─────────
    with tab1:
        st.markdown("### Étape 1 : Saisir les informations")

        st.session_state.qqoqccp_title = st.text_input(
            "Titre de l’analyse :",
            st.session_state.demo_qqoqccp_title,
            help="Modifiable selon vos besoins",
        )

        answers = {}
        blocs = [("Quoi ?", "Qui ?"), ("Où ?", "Quand ?"), ("Comment ?", "Combien ?")]

        for left_q, right_q in blocs:
            with st.expander(f"{left_q[:-1]} & {right_q[:-1]}", expanded=True):
                c1, c2 = st.columns(2)
                with c1:
                    answers[left_q] = st.text_area(
                        left_q,
                        st.session_state.demo_qqoqccp_answers.get(left_q, ""),
                        height=100,
                        help=get_question_help_text(left_q),
                        key=f"a_{left_q}",
                    )
                with c2:
                    answers[right_q] = st.text_area(
                        right_q,
                        st.session_state.demo_qqoqccp_answers.get(right_q, ""),
                        height=100,
                        help=get_question_help_text(right_q),
                        key=f"a_{right_q}",
                    )

        with st.expander("Pourquoi", expanded=True):
            q = "Pourquoi ?"
            answers[q] = st.text_area(
                q,
                st.session_state.demo_qqoqccp_answers.get(q, ""),
                height=120,
                help=get_question_help_text(q),
                key=f"a_{q}",
            )

        st.session_state.qqoqccp_answers = answers
        st.success("Données enregistrées. Passez à « Visualisation ».")

    # ───────── Tab 2 : Visualisation ─────────
    with tab2:
        st.markdown("### Étape 2 : Visualiser le diagramme")

        if not {"qqoqccp_title", "qqoqccp_answers"} <= st.session_state.keys():
            st.info("Veuillez d’abord saisir vos données.")
        else:
            fig = create_qqoqccp_diagram(
                st.session_state.qqoqccp_title, st.session_state.qqoqccp_answers
            )
            st.pyplot(fig)

            with st.expander("Résumé", expanded=True):
                for q in questions:
                    st.markdown(f"**{q}**")
                    st.markdown(st.session_state.qqoqccp_answers.get(q, ""))
                    st.markdown("---")

                done = sum(
                    bool(st.session_state.qqoqccp_answers.get(q, "").strip()) for q in questions
                )
                rate = int(done / len(questions) * 100)
                c1, c2 = st.columns(2)
                c1.metric("Répondu", f"{done}/{len(questions)}")
                c2.metric("Complétude", f"{rate}%")
                if rate < 100:
                    st.warning("Analyse incomplète : répondez à toutes les questions.")

            st.markdown("#### Exporter")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "Télécharger PNG",
                    export_as_png(fig),
                    "qqoqccp.png",
                    "image/png",
                )
            with col2:
                st.download_button(
                    "Télécharger PDF",
                    export_as_pdf(fig, st.session_state.qqoqccp_title),
                    "qqoqccp.pdf",
                    "application/pdf",
                )

    # ───────── Tab 3 : Guide ─────────
    with tab3:
        st.markdown("### Guide rapide QQOQCCP")

        with st.expander("Comprendre l’outil", expanded=True):
            st.markdown(
                """
            Les 7 questions permettent de couvrir tous les aspects d’un problème ou projet :
            **quoi, qui, où, quand, comment, combien, pourquoi**.
            """
            )

        with st.expander("Quand l’utiliser ?", expanded=True):
            st.markdown(
                """
            - Analyse de problème  
            - Planification de projet  
            - Documentation de processus  
            - Recherche de causes racines  
            - Plan de communication
            """
            )
