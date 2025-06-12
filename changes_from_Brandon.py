"""
Functions for generating MongoDB delete mutation files.
"""
import os
from typing import Dict, Any, List

from scripts.mongo_mutations.utils.file_utils import save_json_file
from scripts.mongo_mutations.utils.insert_mutation_generator import _extract_scalar_type, _camel_to_lower
from scripts.mongo_mutations.utils.update_mutation_generator import _generate_field_name_variations, _generate_field_mapping_condition


def _build_ifnull_chain(variations: List[str], prefix: str) -> Dict[str, Any]:
    """
    Build nested $ifNull expressions for field name variations.

    Args:
        variations: List of field name variations
        prefix: Variable prefix (e.g., "$$filter")

    Returns:
        MongoDB $ifNull expression
    """
    if len(variations) == 1:
        return f"{prefix}.{variations[0]}"
    else:
        return {
            "$ifNull": [
                f"{prefix}.{variations[0]}",
                _build_ifnull_chain(variations[1:], prefix)
            ]
        }


def generate_delete_by_pk_mutation(collection_info: Dict[str, Any], output_dir: str) -> str:
    """
    Generate a delete_by_pk mutation file.

    Args:
        collection_info: Collection information dictionary
        output_dir: Directory to save the mutation file

    Returns:
        Path to the generated file
    """
    collection_name = collection_info["collection_name"]

    # Create a result type name
    result_type_name = f"Delete{collection_name}"

    # Create the mutation
    mutation = {
        "name": f"delete{collection_name}ById",
        "description": f"Delete a {collection_name} document by ID",
        "resultType": {
            "object": result_type_name
        },
        "arguments": {
            "id": {
                "type": {
                    "scalar": "objectId"
                }
            }
        },
        "objectTypes": {
            result_type_name: {
                "fields": {
                    "ok": {
                        "type": {
                            "scalar": "int"
                        }
                    },
                    "n": {
                        "type": {
                            "scalar": "int"
                        }
                    }
                }
            }
        },
        "command": {
            "delete": collection_name,
            "deletes": [
                {
                    "q": {
                        "_id": "{{ id }}"
                    },
                    "limit": 0
                }
            ]
        }
    }

    filepath = os.path.join(output_dir, f"delete_{collection_name.lower()}_by_id.json")
    save_json_file(filepath, mutation)
    return filepath


def generate_delete_many_mutation(collection_info: Dict[str, Any], output_dir: str) -> str:
    """
    Generate a delete_many mutation file.

    Args:
        collection_info: Collection information dictionary
        output_dir: Directory to save the mutation file

    Returns:
        Path to the generated file
    """
    collection_name = collection_info["collection_name"]
    fields = collection_info["fields"]

    # Create a result type name
    result_type_name = f"DeleteMany{collection_name}"
    filter_type_name = f"Delete{collection_name}ManyFilter"

    # Generate field types for filter object (including _id)
    filter_field_types = {}
    for field_name, field_info in fields.items():
        # Extract the type information
        type_info = field_info["type"]
        scalar_type = _extract_scalar_type(type_info)

        if scalar_type:
            if isinstance(type_info, str):
                filter_field_types[_camel_to_lower(field_name)] = {
                    "type": type_info
                }
            else:
                filter_field_types[_camel_to_lower(field_name)] = {
                    "type": {
                        "nullable": {
                            "scalar": scalar_type
                        }
                    }
                }

    # Add special case for ids array
    filter_field_types["ids"] = {
        "type": {
            "nullable": {
                "arrayOf": {
                    "scalar": "objectId"
                }
            }
        }
    }

    # Create the mutation
    mutation = {
        "name": f"deleteMany{collection_name}",
        "description": f"Delete multiple {collection_name} documents",
        "resultType": {
            "object": result_type_name
        },
        "arguments": {
            "filter": {
                "type": {
                    "object": filter_type_name
                }
            }
        },
        "objectTypes": {
            result_type_name: {
                "fields": {
                    "ok": {
                        "type": {
                            "scalar": "int"
                        }
                    },
                    "n": {
                        "type": {
                            "scalar": "int"
                        }
                    }
                }
            },
            filter_type_name: {
                "fields": filter_field_types
            }
        },
        "command": {
            "delete": collection_name,
            "deletes": [
                {
                    "q": "{{ filter }}"
                }
            ],
        }
    }

    filepath = os.path.join(output_dir, f"delete_many_{collection_name.lower()}.json")
    save_json_file(filepath, mutation)
    return filepath


def generate_flexible_delete_mutation(collection_info: Dict[str, Any], output_dir: str) -> str:
    """
    Generate a flexible delete mutation file with filter and field name mapping.

    Args:
        collection_info: Collection information dictionary
        output_dir: Directory to save the mutation file

    Returns:
        Path to the generated file
    """
    collection_name = collection_info["collection_name"]
    fields = collection_info["fields"]

    # Create type names
    result_type_name = f"Delete{collection_name}Result"
    filter_type_name = f"Delete{collection_name}Filter"

    # Generate filter fields (all fields as nullable)
    filter_fields = {}
    for field_name, field_info in fields.items():
        # Extract the type information
        type_info = field_info["type"]
        scalar_type = _extract_scalar_type(type_info)
        
        if scalar_type:
            if isinstance(type_info, str):
                filter_fields[_camel_to_lower(field_name)] = {
                    "type": type_info
                }
            else:
                filter_fields[field_name] = {
                    "type": {
                        "nullable": {
                            "scalar": scalar_type
                        }
                    }
                }

    # Generate filter mapping conditions for field name variations
    filter_conditions = []
    for field_name, field_info in fields.items():
        # Generate field name variations
        variations = _generate_field_name_variations(field_name)

        # Create condition for this field
        field_condition = {
            "$cond": {
                "if": {
                    "$ne": [
                        {
                            "$ifNull": [
                                _build_ifnull_chain(variations, "$$filter"),
                                None
                            ]
                        },
                        None
                    ]
                },
                "then": {
                    "$eq": [
                        f"${field_name}",
                        _build_ifnull_chain(variations, "$$filter")
                    ]
                },
                "else": True
            }
        }
        filter_conditions.append(field_condition)

    # Create the mutation with pipeline
    mutation = {
        "name": f"delete{collection_name}",
        "description": f"Delete {collection_name} documents with flexible field name mapping",
        "resultType": {
            "object": result_type_name
        },
        "arguments": {
            "filter": {
                "type": {
                    "object": filter_type_name
                }
            }
        },
        "objectTypes": {
            result_type_name: {
                "fields": {
                    "ok": {
                        "type": {
                            "scalar": "int"
                        }
                    },
                    "n": {
                        "type": {
                            "scalar": "int"
                        }
                    }
                }
            },
            filter_type_name: {
                "fields": filter_fields
            }
        },
        "command": {
            "delete": collection_name,
            "deletes": [
                {
                    "q": {
                        "$expr": {
                            "$and": filter_conditions
                        }
                    },
                    "limit": 0
                }
            ],
            "let": {
                "filter": "{{ filter }}"
            }
        }
    }

    filepath = os.path.join(output_dir, f"delete_{collection_name.lower()}.json")
    save_json_file(filepath, mutation)
    return filepath
