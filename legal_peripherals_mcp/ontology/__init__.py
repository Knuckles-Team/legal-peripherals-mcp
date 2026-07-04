"""Legal Peripherals legal ontology contribution (CONCEPT:AU-KG.ontology.package-federation-migration).

Data-only subpackage: it carries ``legal.ttl`` (the ``owl:Ontology``
``http://knuckles.team/kg/legal`` module) which the agent-utilities hub federates
in via the ``agent_utilities.ontology_providers`` entry-point. The hub loader
globs every ``*.ttl`` in this directory. It holds no business logic and no heavy
imports so the hub can resolve it cheaply.
"""
