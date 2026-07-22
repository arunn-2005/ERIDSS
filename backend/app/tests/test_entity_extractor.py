from app.services.entity_extractor import extract_entities

text = """
Apple signed a contract with Microsoft.
John Smith will manage Project Phoenix.
The Finance Department approved a budget of $500,000.
The project will start in Chennai on January 15, 2027.
"""

entities = extract_entities(text)

for entity in entities:
    print(f"Entity: {entity['text']}, Label: {entity['label']}")