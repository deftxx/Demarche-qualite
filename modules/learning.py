# -*- coding: utf‑8 -*-
import streamlit as st
import random
from assets.quality_fundamentals import quality_fundamentals_content

# Fonction de traduction locale
def _(text):
    if 'translate' in st.session_state:
        return st.session_state.translate(text)
    return text

def display_learning_module(module_name: str) -> None:
    """Affiche le module sélectionné."""
    if module_name == _("Ressources d’apprentissage"):
        st.title(_("Fondamentaux du gestion de la qualité"))

        # Contenu principal
        quality_fundamentals_content()

        # Quiz
        display_knowledge_check()

def display_knowledge_check() -> None:
    """Quiz de vérification des connaissances"""
    st.markdown("---")

    with st.expander(_("Vérification des connaissances"), expanded=False):
        st.markdown(_("""\
        Testez votre compréhension des concepts qualité avec ce quiz.
        Sélectionnez vos réponses puis cliquez sur « Soumettre » pour voir votre score.
        """))

        # Initialisation de l’état du quiz
        if 'quiz_questions' not in st.session_state:
            st.session_state.quiz_questions = generate_questions()
            st.session_state.quiz_submitted = False
            st.session_state.quiz_score = 0
            st.session_state.quiz_answers = {}

        # Formulaire du quiz
        quiz_form = st.form("quiz_form")
        with quiz_form:
            for i, question in enumerate(st.session_state.quiz_questions):
                st.markdown(f"**{_('Question')} {i + 1}** : {question['question']}")

                key = f"answer_{i}"
                if key not in st.session_state.quiz_answers:
                    st.session_state.quiz_answers[key] = ""

                st.session_state.quiz_answers[key] = st.radio(
                    _("Sélectionnez votre réponse :"),
                    question['options'],
                    key=key
                )
                st.markdown("---")

            submitted = st.form_submit_button(_("Soumettre"))

            if submitted:
                st.session_state.quiz_submitted = True

        if st.session_state.quiz_submitted:
            score = 0
            for i, question in enumerate(st.session_state.quiz_questions):
                key = f"answer_{i}"
                if st.session_state.quiz_answers[key] == question['correct_answer']:
                    score += 1
            st.session_state.quiz_score = score

            st.success(f"{_('Votre score')} : {score}/{len(st.session_state.quiz_questions)}")

            # Détail des réponses
            st.markdown(f"### {_('Vos résultats')}")
            for i, question in enumerate(st.session_state.quiz_questions):
                key = f"answer_{i}"
                user_ans = st.session_state.quiz_answers[key]
                if user_ans == question['correct_answer']:
                    st.markdown(f"✅ **{_('Question')} {i + 1}** : {question['question']}")
                    st.markdown(f"{_('Votre réponse')} : **{user_ans}** ({_('Correct')})")
                else:
                    st.markdown(f"❌ **{_('Question')} {i + 1}** : {question['question']}")
                    st.markdown(f"{_('Votre réponse')} : **{user_ans}**")
                    st.markdown(f"{_('Bonne réponse')} : **{question['correct_answer']}**")

                if 'explanation' in question:
                    st.info(question['explanation'])
                st.markdown("---")

            if st.button(_("Nouveau quiz")):
                st.session_state.quiz_questions = generate_questions()
                st.session_state.quiz_submitted = False
                st.session_state.quiz_score = 0
                st.session_state.quiz_answers = {}
                st.rerun()

def generate_questions():
    """Crée un jeu de questions aléatoires."""
    all_questions = [
        {
            'question': "Quel est l’objectif principal du principe de Pareto ?",
            'options': [
                "Garantir que 80 % des efforts produisent 20 % des résultats",
                "Identifier que 80 % des problèmes proviennent de 20 % des causes",
                "Assurer que 80 % des défauts sont découverts en test",
                "Prouver que 20 % des clients génèrent 80 % des réclamations"
            ],
            'correct_answer': "Identifier que 80 % des problèmes proviennent de 20 % des causes",
            'explanation': "Le principe de Pareto (règle 80/20) stipule qu’environ 80 % des effets proviennent de 20 % des causes."
        },
        {
            'question': "Quel type de problème possède des relations cause‑effet claires et des résultats prévisibles ?",
            'options': [
                "Problèmes complexes",
                "Problèmes compliqués",
                "Problèmes simples",
                "Problèmes chaotiques"
            ],
            'correct_answer': "Problèmes simples",
            'explanation': "Les problèmes simples ont des relations cause‑effet évidentes et des solutions standard."
        },
        {
            'question': "Quel est le but principal d’un diagramme d’Ishikawa ?",
            'options': [
                "Suivre les échéances d’un projet",
                "Identifier les causes potentielles d’un problème",
                "Cartographier les points de contact du parcours client",
                "Documenter le flux de production"
            ],
            'correct_answer': "Identifier les causes potentielles d’un problème",
            'explanation': "Le diagramme d’Ishikawa permet de lister et classer les causes possibles par grandes familles."
        },
        {
            'question': "Lequel des éléments suivants fait partie d’une analyse SWOT ?",
            'options': [
                "Synergies",
                "Faiblesses",
                "Décomposition du travail",
                "Échéances"
            ],
            'correct_answer': "Faiblesses",
            'explanation': "SWOT analyse les Forces, Faiblesses, Opportunités et Menaces."
        },
        {
            'question': "La technique des « 5 Why » sert principalement à identifier :",
            'options': [
                "Cinq perspectives différentes d’un problème",
                "Les causes racines des problèmes",
                "Cinq solutions potentielles",
                "Cinq membres à affecter à un problème"
            ],
            'correct_answer': "Les causes racines des problèmes",
            'explanation': "En posant « Pourquoi ? » cinq fois, on remonte jusqu’à la cause profonde."
        },
        {
            'question': "Sur un diagramme de Pareto, sur quoi faut‑il se concentrer en premier ?",
            'options': [
                "Les barres les plus hautes",
                "Les barres les plus basses",
                "La partie centrale",
                "La courbe cumulative"
            ],
            'correct_answer': "Les barres les plus hautes",
            'explanation': "Les barres les plus hautes représentent les causes majeures à traiter en priorité."
        },
        {
            'question': "Dans un histogramme, une distribution en cloche (normale) indique que :",
            'options': [
                "Les données sont asymétriques vers la droite",
                "Les données sont centrées avec des queues symétriques",
                "Il existe deux groupes distincts",
                "Le processus est hors contrôle"
            ],
            'correct_answer': "Les données sont centrées avec des queues symétriques",
            'explanation': "La distribution normale reflète un processus stable avec la plupart des valeurs autour de la moyenne."
        },
        {
            'question': "Un coefficient de corrélation fortement positif (proche de +1) signifie :",
            'options': [
                "Quand une variable augmente, l’autre diminue",
                "Les deux variables sont sans relation",
                "Quand une variable augmente, l’autre augmente généralement",
                "La relation est aléatoire"
            ],
            'correct_answer': "Quand une variable augmente, l’autre augmente généralement",
            'explanation': "Un coefficient proche de +1 indique une relation linéaire positive forte."
        },
        {
            'question': "Comment définir un « problème compliqué » en gestion de la qualité ?",
            'options': [
                "Problème sans solution claire nécessitant l’essai/erreur",
                "Problème à variables multiples nécessitant de l’expertise mais avec relations cause‑effet déterminables",
                "Problème simple rendu inutilement complexe",
                "Problème impossible à résoudre avec la technologie actuelle"
            ],
            'correct_answer': "Problème à variables multiples nécessitant de l’expertise mais avec relations cause‑effet déterminables",
            'explanation': "Les problèmes compliqués demandent des analyses poussées mais restent déterministes."
        }
    ]

    # Sélection aléatoire de 5 questions
    return random.sample(all_questions, 5) if len(all_questions) > 5 else all_questions
