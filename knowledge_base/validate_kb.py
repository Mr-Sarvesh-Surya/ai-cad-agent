#!/usr/bin/env python3
"""
Knowledge Base Validator
Validates all parameter schemas and template registry for internal consistency.
Run: python validate_kb.py
"""

import json
import sys
from pathlib import Path
from typing import Any

ALLOWED_RESOLUTION_METHODS = {"ask_user", "formula", "standards_default", "context_hint"}
ALLOWED_SEVERITIES = {"error", "warning"}
SCHEMAS_DIR = Path("knowledge_base/parameter_schemas")
REGISTRY_FILE = Path("knowledge_base/template_registry.json")

errors: list[str] = []


def error(file: str, message: str) -> None:
    errors.append(f"[{file}] {message}")


def load_json(filepath: Path) -> Any:
    try:
        with filepath.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        error(str(filepath), "File not found")
    except json.JSONDecodeError as exc:
        error(str(filepath), f"Invalid JSON: {exc}")
    except OSError as exc:
        error(str(filepath), f"Failed to read file: {exc}")
    return None


def validate_schema(filepath: Path) -> dict[str, Any] | None:
    print(f"Validating schema: {filepath.name}")
    data = load_json(filepath)
    if data is None:
        return None

    if not isinstance(data.get("component_type"), str) or not data.get("component_type").strip():
        error(filepath.name, "component_type field must exist and be a non-empty string")

    if "schema_version" not in data:
        error(filepath.name, "schema_version field is missing")

    parameters = data.get("parameters")
    if not isinstance(parameters, list) or len(parameters) == 0:
        error(filepath.name, "parameters must be a non-empty list")
        return None

    parameter_names: set[str] = set()
    required_params: set[str] = set()
    optional_params: set[str] = set()

    for idx, param in enumerate(parameters):
        context = f"parameter index {idx}"
        if not isinstance(param, dict):
            error(filepath.name, f"{context} must be an object")
            continue

        for field in ("name", "required", "data_type", "resolution_method"):
            if field not in param:
                error(filepath.name, f"{context} missing required field '{field}'")

        name = param.get("name")
        if isinstance(name, str) and name:
            if name in parameter_names:
                error(filepath.name, f"Duplicate parameter name '{name}'")
            parameter_names.add(name)
        else:
            error(filepath.name, f"{context} has invalid name")

        required = param.get("required")
        if isinstance(name, str) and name:
            if required is True:
                required_params.add(name)
            elif required is False:
                optional_params.add(name)
            else:
                error(filepath.name, f"Parameter '{name}' has invalid required flag")

        resolution_method = param.get("resolution_method")
        if resolution_method not in ALLOWED_RESOLUTION_METHODS:
            error(filepath.name, f"Parameter '{name}' has invalid resolution_method '{resolution_method}'")

        if resolution_method == "formula" and "formula" not in param:
            error(filepath.name, f"Parameter '{name}' uses formula resolution but formula is missing")

        if resolution_method == "standards_default":
            has_default = "default_value" in param
            has_allowed_values = "allowed_values" in param
            if not (has_default or has_allowed_values):
                error(
                    filepath.name,
                    f"Parameter '{name}' uses standards_default but has neither default_value nor allowed_values",
                )

    for idx, param in enumerate(parameters):
        if not isinstance(param, dict):
            continue
        name = param.get("name", f"parameter index {idx}")
        depends_on = param.get("depends_on", [])
        if not isinstance(depends_on, list):
            error(filepath.name, f"Parameter '{name}' has non-list depends_on")
            continue
        for dep in depends_on:
            if dep not in parameter_names:
                error(filepath.name, f"Parameter '{name}' depends_on unknown parameter '{dep}'")

    conflict_rules = data.get("conflict_rules")
    if not isinstance(conflict_rules, list):
        error(filepath.name, "conflict_rules must be a list")
    else:
        for idx, rule in enumerate(conflict_rules):
            context = f"conflict_rules index {idx}"
            if not isinstance(rule, dict):
                error(filepath.name, f"{context} must be an object")
                continue

            for field in ("rule", "condition", "severity", "message"):
                if field not in rule:
                    error(filepath.name, f"{context} missing required field '{field}'")

            severity = rule.get("severity")
            if severity not in ALLOWED_SEVERITIES:
                error(filepath.name, f"{context} has invalid severity '{severity}'")

    component_type = data.get("component_type")
    if isinstance(component_type, str) and component_type:
        return {
            "component_type": component_type,
            "required_params": required_params,
            "optional_params": optional_params,
            "filepath": filepath,
        }

    return None


def validate_registry(all_schemas: dict[str, dict[str, Any]]) -> None:
    print(f"Validating registry: {REGISTRY_FILE.name}")
    registry = load_json(REGISTRY_FILE)
    if registry is None:
        return

    primitives = registry.get("primitives")
    primitive_ids = registry.get("primitive_ids")

    if not isinstance(primitives, list):
        error(REGISTRY_FILE.name, "primitives must be a list")
        return

    if not isinstance(primitive_ids, list):
        error(REGISTRY_FILE.name, "primitive_ids must be a list")
        primitive_ids = []

    primitive_map: dict[str, dict[str, Any]] = {}
    for idx, primitive in enumerate(primitives):
        context = f"primitives index {idx}"
        if not isinstance(primitive, dict):
            error(REGISTRY_FILE.name, f"{context} must be an object")
            continue

        primitive_id = primitive.get("id")
        if not isinstance(primitive_id, str) or not primitive_id:
            error(REGISTRY_FILE.name, f"{context} has invalid id")
            continue

        primitive_map[primitive_id] = primitive

        component_type = primitive.get("component_type")
        if component_type not in all_schemas:
            error(REGISTRY_FILE.name, f"Primitive '{primitive_id}' has no matching schema for component_type '{component_type}'")
            continue

        schema_info = all_schemas[component_type]
        schema_required = schema_info["required_params"]
        schema_optional = schema_info["optional_params"]

        required_params = primitive.get("required_params")
        if not isinstance(required_params, list):
            error(REGISTRY_FILE.name, f"Primitive '{primitive_id}' required_params must be a list")
        else:
            for param in required_params:
                if param not in schema_required:
                    error(
                        REGISTRY_FILE.name,
                        f"Primitive '{primitive_id}' required param '{param}' is not required:true in schema '{component_type}'",
                    )
            for param in schema_required:
                if param not in required_params:
                    error(
                        REGISTRY_FILE.name,
                        f"Primitive '{primitive_id}' missing required param '{param}' from schema '{component_type}'",
                    )

        optional_params = primitive.get("optional_params")
        if not isinstance(optional_params, list):
            error(REGISTRY_FILE.name, f"Primitive '{primitive_id}' optional_params must be a list")
        else:
            for param in optional_params:
                if param not in schema_optional:
                    error(
                        REGISTRY_FILE.name,
                        f"Primitive '{primitive_id}' optional param '{param}' is not required:false in schema '{component_type}'",
                    )
            for param in schema_optional:
                if param not in optional_params:
                    error(
                        REGISTRY_FILE.name,
                        f"Primitive '{primitive_id}' missing optional param '{param}' from schema '{component_type}'",
                    )

    for pid in primitive_ids:
        if pid not in primitive_map:
            error(REGISTRY_FILE.name, f"primitive_ids entry '{pid}' does not exist in primitives")


def main() -> None:
    all_schemas: dict[str, dict[str, Any]] = {}

    if not SCHEMAS_DIR.exists():
        error(str(SCHEMAS_DIR), "Schema directory does not exist")
    else:
        schema_files = sorted(SCHEMAS_DIR.glob("*.json"))
        if not schema_files:
            error(str(SCHEMAS_DIR), "No schema files found")

        for schema_path in schema_files:
            schema_info = validate_schema(schema_path)
            if schema_info is not None:
                component_type = schema_info["component_type"]
                if component_type in all_schemas:
                    error(schema_path.name, f"Duplicate component_type '{component_type}' across schema files")
                else:
                    all_schemas[component_type] = schema_info

    validate_registry(all_schemas)

    print("\nValidation Report")
    print("-----------------")
    print(f"Schemas validated: {len(all_schemas)}")

    if errors:
        print(f"Errors found: {len(errors)}")
        for entry in errors:
            print(f"- {entry}")
        sys.exit(1)

    print("ALL CHECKS PASSED")
    sys.exit(0)


if __name__ == "__main__":
    main()
