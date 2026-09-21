import networkx as nx

def calculate_topological_metrics(nodes: list, edges: list) -> dict:
    """
    Builds an in-memory directed graph using NetworkX and calculates 
    centrality metrics for each entity node.
    """
    # 1. Initialize a Directed Graph
    G = nx.DiGraph()

    # 2. Add entity nodes to the graph
    for node in nodes:
        G.add_node(
            str(node["id"]), 
            name=node.get("name", ""), 
            type=node.get("type", "Entity")
        )

    # 3. Add directional edges between entities
    for edge in edges:
        G.add_edge(
            str(edge["source_id"]), 
            str(edge["target_id"]), 
            label=edge.get("relation_type", "")
        )

    # 4. Calculate Degree Centrality
    degree_cent = nx.degree_centrality(G) if len(G) > 0 else {}

    # 5. Calculate Betweenness Centrality
    betweenness_cent = nx.betweenness_centrality(G) if len(G) > 0 else {}

    # 6. Assemble node-by-node topological metrics dictionary
    metrics = {}
    for node_id in G.nodes():
        metrics[node_id] = {
            "degree_centrality": round(degree_cent.get(node_id, 0.0), 4),
            "betweenness_centrality": round(betweenness_cent.get(node_id, 0.0), 4),
            "in_degree": G.in_degree(node_id),      # Total incoming relationships
            "out_degree": G.out_degree(node_id)     # Total outgoing relationships
        }

    return metrics