# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from utils.export import export_as_pdf, export_as_png  # export_as_csv non utilisé

# ─────────────────────────────────────────────────────────────────────────────
# Helper: Création d'une position hiérarchique sans pygraphviz
# ─────────────────────────────────────────────────────────────────────────────
def hierarchy_pos(G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
    '''
    Génère une position de graphe en disposition verticale (hiérarchique).
    '''
    pos = {}
    if root is None:
        root = next(iter(nx.topological_sort(G)))

    def _hierarchy_pos(G, root, left, right, vert_loc, xcenter, pos, parent=None):
        children = list(G.successors(root))
        if not isinstance(children, list) or len(children) == 0:
            pos[root] = (xcenter, vert_loc)
        else:
            dx = (right - left) / len(children)
            nextx = left + dx/2
            for child in children:
                pos = _hierarchy_pos(G, child, nextx - dx/2, nextx + dx/2, vert_loc - vert_gap, nextx, pos, root)
                nextx += dx
            pos[root] = (xcenter, vert_loc)
        return pos

    return _hierarchy_pos(G, root, 0, width, vert_loc, xcenter, pos)

# ─────────────────────────────────────────────────────────────────────────────
# Génération du logigramme
# ─────────────────────────────────────────────────────────────────────────────
def create_flowchart(nodes, edges, node_types):
    """Retourne une figure Matplotlib représentant le logigramme."""
    G = nx.DiGraph()
    for nid, lbl in nodes.items():
        G.add_node(nid, label=lbl, type=node_types.get(nid, "process"))
    for src, tgt in edges:
        G.add_edge(src, tgt)

    fig, ax = plt.subplots(figsize=(12, 10))
    pos = hierarchy_pos(G)  # ✅ Utilisation du layout hiérarchique
    labels = nx.get_node_attributes(G, "label")
    types = nx.get_node_attributes(G, "type")

    color_map = {
        "start": "lightgreen",
        "end": "salmon",
        "decision": "lightyellow",
        "process": "lightblue",
        "input": "lightpink",
        "output": "lightgray",
    }
    shape_map = {
        "start": "o",
        "end": "o",
        "decision": "d",
        "process": "s",
        "input": "^",
        "output": "v",
    }

    for t, shape in shape_map.items():
        nodes_t = [n for n in G.nodes() if types.get(n) == t]
        if nodes_t:
            nx.draw_networkx_nodes(
                G,
                pos,
                nodelist=nodes_t,
                node_color=[color_map[t]] * len(nodes_t),
                node_shape=shape,
                node_size=3000,
                ax=ax,
            )

    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=15, ax=ax)
    nx.draw_networkx_labels(G, pos, labels, font_size=9, font_weight="bold", ax=ax)

    plt.title("Logigramme (Flowchart)", fontsize=16)
    plt.axis("off")
    plt.tight_layout()
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# Interface utilisateur Streamlit pour le Flowchart
# ─────────────────────────────────────────────────────────────────────────────
def flowchart_tool():
    st.title("Outil Logigramme (Flowchart)")

    st.markdown(
        """
    ## Documenter un processus avec un logigramme

    Les logigrammes permettent de visualiser les étapes séquentielles d’un processus
    afin de mieux le comprendre, l’analyser et l’améliorer.

    **Instructions :**  
    1. Définissez les nœuds (étapes) du logigramme  
    2. Reliez‑les pour créer le flux  
    3. Visualisez et exportez votre logigramme
    """
    )

    # ------------------- Données d'exemple -----------------------------------
    if "demo_flowchart_initialized" not in st.session_state:
        st.session_state.demo_flowchart_initialized = True
        st.session_state.demo_flowchart_nodes = {
            "start": "Début du processus",
            "input": "Réception de commande",
            "process1": "Vérifier les détails",
            "decision1": "Commande valide ?",
            "process2": "Traiter le paiement",
            "decision2": "Paiement accepté ?",
            "process3": "Préparer l’expédition",
            "process4": "Mettre à jour le stock",
            "output": "Expédier la commande",
            "process5": "Notifier le client",
            "end": "Fin du processus",
        }
        st.session_state.demo_flowchart_node_types = {
            "start": "start",
            "input": "input",
            "process1": "process",
            "decision1": "decision",
            "process2": "process",
            "decision2": "decision",
            "process3": "process",
            "process4": "process",
            "output": "output",
            "process5": "process",
            "end": "end",
        }
        st.session_state.demo_flowchart_edges = [
            ("start", "input"),
            ("input", "process1"),
            ("process1", "decision1"),
            ("decision1", "process2"),  # Oui
            ("decision1", "end"),       # Non
            ("process2", "decision2"),
            ("decision2", "process3"),  # Oui
            ("decision2", "end"),       # Non
            ("process3", "process4"),
            ("process4", "output"),
            ("output", "process5"),
            ("process5", "end"),
        ]

    st.markdown("### Éditeur de logigramme")

    # ---------- Nœuds ----------
    st.subheader("Nœuds")
    if "flowchart_nodes" not in st.session_state:
        st.session_state.flowchart_nodes = st.session_state.demo_flowchart_nodes.copy()
        st.session_state.flowchart_node_types = st.session_state.demo_flowchart_node_types.copy()

    node_df = pd.DataFrame(
        [
            {"ID": nid, "Libellé": lbl, "Type": st.session_state.flowchart_node_types.get(nid, "process")}
            for nid, lbl in st.session_state.flowchart_nodes.items()
        ]
    )

    edited_nodes = st.data_editor(
        node_df,
        key="node_editor",
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Type": st.column_config.SelectboxColumn(
                "Type",
                options=["start", "end", "process", "decision", "input", "output"],
                required=True,
            )
        },
    )

    nodes, node_types = {}, {}
    for _, row in edited_nodes.iterrows():
        nid = row["ID"]
        if nid and not pd.isna(nid):
            nodes[nid] = row["Libellé"]
            node_types[nid] = row["Type"]

    # ---------- Connexions ----------
    st.subheader("Connexions")
    if "flowchart_edges" not in st.session_state:
        st.session_state.flowchart_edges = st.session_state.demo_flowchart_edges.copy()

    edge_df = pd.DataFrame([{"De": s, "À": t} for s, t in st.session_state.flowchart_edges])
    edited_edges = st.data_editor(edge_df, key="edge_editor", use_container_width=True, num_rows="dynamic")

    edges = []
    for _, row in edited_edges.iterrows():
        src, tgt = row["De"], row["À"]
        if src and tgt and not pd.isna(src) and not pd.isna(tgt):
            edges.append((src, tgt))

    # Sauvegarde dans la session
    st.session_state.flowchart_nodes = nodes
    st.session_state.flowchart_node_types = node_types
    st.session_state.flowchart_edges = edges

    # ---------- Visualisation ----------
    if nodes and edges:
        st.subheader("Visualisation du logigramme")
        fig = create_flowchart(nodes, edges, node_types)
        st.pyplot(fig)

        st.markdown("---")
        st.subheader("Exporter")

        col1, col2 = st.columns(2)
        with col1:
            png = export_as_png(fig)
            st.download_button("PNG", png, "logigramme.png", "image/png")
        with col2:
            pdf = export_as_pdf(fig, "Logigramme")
            st.download_button("PDF", pdf, "logigramme.pdf", "application/pdf")

    # ---------- Légende ----------
    st.markdown("---")
    st.subheader("Légende des symboles")

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown(
            """
        - **Début / Fin (ovale)**
        - **Processus (rectangle)**
        - **Décision (losange)**
        """
        )
    with col_r:
        st.markdown(
            """
        - **Entrée (triangle haut)**
        - **Sortie (triangle bas)**
        - **Flèches** : direction du flux
        """
        )

    # ---------- Exemple ----------
    st.markdown("---")
    st.subheader("Exemple d’utilisation")
    st.markdown(
        """
    **Scénario** : traitement d’une commande client.  
    Le logigramme montre la réception, la vérification, le paiement, les décisions
    et l’expédition, permettant d’identifier goulots d’étranglement et points d’amélioration.
    """
    )
