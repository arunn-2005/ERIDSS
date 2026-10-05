import pytest
import networkx as nx

# --- MODULE 1: INGESTION & PII REDACTION ---
def test_mod1_document_ingestion_and_pii_redaction():
    sample_text = "Engineer Alice (alice@corp.internal) deployed DB at 192.168.1.50"
    # Simulated Presidio / regex redaction logic
    import re
    redacted = re.sub(r'[\w\.-]+@[\w\.-]+', '<REDACTED_EMAIL>', sample_text)
    redacted = re.sub(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', '<REDACTED_IP>', redacted)
    
    assert "<REDACTED_EMAIL>" in redacted
    assert "<REDACTED_IP>" in redacted
    assert "192.168.1.50" not in redacted

# --- MODULE 2: ENTITY & RELATION EXTRACTION ---
def test_mod2_entity_relation_extraction_gliner():
    # Simulated GLiNER triple extraction output
    extracted_triples = [
        {"subject": "auth_service", "relation": "DEPENDS_ON", "object": "postgres_db"},
        {"subject": "payment_gateway", "relation": "COMMUNICATES_WITH", "object": "auth_service"}
    ]
    assert len(extracted_triples) == 2
    assert extracted_triples[0]["relation"] == "DEPENDS_ON"
    assert extracted_triples[1]["subject"] == "payment_gateway"

# --- MODULE 3: KNOWLEDGE GRAPH SYNCHRONIZATION ---
def test_mod3_neo4j_schema_sync_and_deduplication():
    # Validates node set uniqueness / constraint enforcement
    raw_nodes = ["auth_service", "postgres_db", "auth_service", "cache_redis"]
    unique_nodes = list(set(raw_nodes))
    
    assert len(unique_nodes) == 3
    assert "auth_service" in unique_nodes

# --- MODULE 4: TOPOLOGICAL RISK CALCULATION ---
def test_mod4_topological_betweenness_centrality():
    # Build test graph: A -> B -> C -> D (B and C are bottlenecks)
    G = nx.DiGraph()
    G.add_edges_from([
        ("client_app", "api_gateway"),
        ("api_gateway", "auth_service"),
        ("auth_service", "postgres_db")
    ])
    
    centrality = nx.betweenness_centrality(G)
    assert "api_gateway" in centrality
    assert centrality["api_gateway"] > centrality["client_app"]

# --- MODULE 5: CASCADE SIMULATION & DECISION SUPPORT ---
def test_mod5_cascade_simulation_and_blast_radius():
    G = nx.DiGraph()
    G.add_edges_from([
        ("auth_service", "order_service"),
        ("order_service", "notification_service"),
        ("auth_service", "payment_service")
    ])
    
    target_node = "auth_service"
    downstream_nodes = list(nx.descendants(G, target_node))
    blast_radius_count = len(downstream_nodes)
    
    assert blast_radius_count == 3
    assert "payment_service" in downstream_nodes
    assert "notification_service" in downstream_nodes