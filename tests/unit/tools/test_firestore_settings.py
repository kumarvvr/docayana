import firestore_settings as settings


def test_creds_env_var_uses_the_project_prefix() -> None:
    assert settings.CREDS_ENV_VAR.startswith("DOCAYANA_")


def test_collections_are_named_and_unique() -> None:
    names = [name.strip() for name in settings.COLLECTIONS]

    assert names
    assert all(names)
    assert len(set(names)) == len(names)


def test_collection_names_are_valid_firestore_ids() -> None:
    assert not any("/" in name or name in {".", ".."} for name in settings.COLLECTIONS)


def test_marker_doc_id_is_a_valid_firestore_id() -> None:
    marker = settings.MARKER_DOC_ID

    assert marker not in {"", ".", ".."}
    assert "/" not in marker
    # Ids matching __.*__ are reserved by Firestore.
    assert not (marker.startswith("__") and marker.endswith("__"))
