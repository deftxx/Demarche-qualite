# -*- coding: utf‑8 -*-
import streamlit as st

def quality_fundamentals_content() -> None:
    """Contenu du module Fondamentaux de la qualité"""

    st.markdown("""\
    ## Fondamentaux du gestion de la qualité

    Le gestion de la qualité est une approche systématique visant à garantir que les produits
    et services répondent aux attentes des clients et aux normes de l’organisation.
    Ce module couvre les principaux concepts et principes de base.
    """)

    # Définition de la qualité
    with st.expander("Définition de la qualité", expanded=False):
        st.markdown("""\
        ### Qu’est‑ce que la qualité ?

        La qualité est le degré auquel un produit ou service satisfait ou dépasse les attentes du client.
        Elle comprend plusieurs attributs :

        - **Aptitude à l’usage** : le produit remplit‑il sa fonction ?
        - **Fiabilité** : fonctionne‑t‑il de manière constante ?
        - **Durabilité** : combien de temps dure‑t‑il ?
        - **Conformité aux spécifications** : respecte‑t‑il les exigences de conception ?
        - **Qualité perçue** : quelle image le client a‑t‑il du produit ?
        """)

    # Types de problèmes
    with st.expander("Types de problèmes", expanded=False):
        st.markdown("""\
        ### Comprendre les différents types de problèmes

        Tous les problèmes ne se ressemblent pas. Identifier le type de problème permet de choisir la bonne approche :

        #### Problèmes simples
        - **Caractéristiques** : relations cause‑effet claires, résultats prévisibles
        - **Exemple** : une machine se bloque toujours au même point
        - **Approche** : dépannage direct, procédures standard

        #### Problèmes compliqués
        - **Caractéristiques** : plusieurs variables, besoin d’expertise, relations cause‑effet déterminables
        - **Exemple** : baisse de qualité d’un produit avec causes multiples
        - **Approche** : outils analytiques, expertise, recherche des causes racines

        #### Problèmes complexes
        - **Caractéristiques** : schémas émergents, résultats imprévisibles, facteurs interdépendants
        - **Exemple** : instauration d’une nouvelle culture d’entreprise, adoption d’un nouveau produit par le marché
        - **Approche** : expérimentation itérative, pensée systémique, gestion adaptative
        """)
