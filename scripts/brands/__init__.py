"""
Brand-specific ingestion modules.

Structure (current and planned):

- scripts.brands.lululemon: Lululemon PDP/category ingest wrappers.
- scripts.brands.jcrew:     J.Crew PDP/category ingest wrappers. (future)
- scripts.brands.reiss:     Reiss ingest wrappers. (future)
- scripts.brands.theory:    Theory ingest wrappers. (future)
- scripts.brands.rag_bone:  rag & bone ingest wrappers. (future)

These modules provide a stable import surface so that the rest of the codebase
doesn't have to know where the original CLI scripts live.
"""



