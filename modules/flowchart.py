# ─────────────────────────────────────────────────────────────────────────────
# Génération du logigramme
# ─────────────────────────────────────────────────────────────────────────────

def hierarchy_pos(G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
    '''
    Helper function to create a vertical tree layout for flowcharts.
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
            nextx = left + dx / 2
            for child in children:
                pos = _hierarchy_pos(G, child, nextx - dx/2, nextx + dx/2, vert_loc - vert_gap, nextx, pos, root)
                nextx += dx
            pos[root] = (xcenter, vert_loc)
        return pos

    return _hierarchy_pos(G, root, 0, width, vert_loc, xcenter, pos)


def create_flowchart(nodes, edges, node_types):
    """Retourne une figure Matplotlib représentant le logigramme."""
    G = nx.DiGraph()
    for nid, lbl in nodes.items():
        G.add_node(nid, label=lbl, type=node_types.get(nid, "process"))
    for src, tgt in edges:
        G.add_edge(src, tgt)

    fig, ax = plt.subplots(figsize=(12, 10))
    pos = hierarchy_pos(G)  # ✅ No pygraphviz needed
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
