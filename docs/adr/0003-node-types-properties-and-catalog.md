# 0003. Node types, property definitions and the catalog file

Status: accepted
Date: 2026-10-17

## Context
Kumar wants configurable, "fluid" default properties per node, user-added properties, and pre-defined nodes and properties kept in a local settings file.

## Decision
- A **catalog** YAML file in the repo defines node types (default property definitions and allowed child types) and property definitions (key, data type, default, required flag, allowed values). It is loaded and validated once at startup (`infrastructure/catalog_file.py`); an invalid file stops the app.
- **Defaults are resolved on read.** A node stores only the values set on it; effective properties are the type's defaults overlaid with those values. Defaults are never copied into nodes.
- **Custom properties** sit beside default ones in the node's property map and are validated by their own definition.
- Workspace owners may add workspace-level property definitions, stored in DynamoDB (ADR-0002). Node types come from the catalog file only in v1.
- Data types: string, number, boolean, date, enum, list, object.

## Consequences
- Changing a default in the catalog changes every node that has not overridden it, with no migration.
- Removing or retyping a property in the catalog can leave stored values that no longer validate; catalog changes need a compatibility check before deploy.
- Action: add PyYAML to `pyproject.toml`.
- Settles scope open questions 5 (who can define types) and 6 (defaults follow catalog changes).
