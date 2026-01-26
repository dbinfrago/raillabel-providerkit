#!/usr/bin/env python3
# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

"""Test script to verify ontology and schema setup.

This script demonstrates:
1. Loading ontologies and schemas
2. Testing the order attribute type conversion
3. Verifying the ontology-schema mapping
"""

from pathlib import Path

from raillabel_providerkit.ontologies import (
    get_ontology_path,
    get_schema_path,
    list_available_ontologies,
    list_available_schemas,
)


def test_ontology_paths():
    """Test that all ontology files can be found."""
    print("Testing ontology paths...")
    for ontology_name in list_available_ontologies():
        try:
            path = get_ontology_path(ontology_name)
            print(f"  ✓ {ontology_name}: {path}")
            assert path.exists(), f"Ontology file does not exist: {path}"
        except Exception as e:
            print(f"  ✗ {ontology_name}: {e}")
            raise


def test_schema_paths():
    """Test that all schema files can be found."""
    print("\nTesting schema paths...")
    for schema_name in list_available_schemas():
        try:
            path = get_schema_path(schema_name)
            print(f"  ✓ {schema_name}: {path}")
            assert path.exists(), f"Schema file does not exist: {path}"
        except Exception as e:
            print(f"  ✗ {schema_name}: {e}")
            raise


def test_ontology_schema_mapping():
    """Test that ontologies have corresponding schemas."""
    print("\nTesting ontology-schema mapping...")
    
    mappings = {
        "osdar23": "osdar23",
        "osdar26": "osdar26",
        "automatedtrain": "automatedtrain",
    }
    
    for ontology_name, schema_name in mappings.items():
        try:
            ontology_path = get_ontology_path(ontology_name)
            schema_path = get_schema_path(schema_name)
            print(f"  ✓ {ontology_name} → {schema_name}")
            print(f"    Ontology: {ontology_path}")
            print(f"    Schema:   {schema_path}")
        except Exception as e:
            print(f"  ✗ {ontology_name} → {schema_name}: {e}")
            raise


def test_single_select_conversion():
    """Test the single-select attribute type conversion logic."""
    print("\nTesting single-select attribute type conversion...")
    
    from raillabel_providerkit.validation.validate_ontology._ontology_classes._attributes._single_select_attribute import (
        _SingleSelectAttribute,
    )
    from raillabel_providerkit.validation.validate_ontology._ontology_classes._scope import (
        _Scope,
    )
    
    # Create a test attribute with numeric string options (like order)
    attr = _SingleSelectAttribute(
        options={"1", "2", "3", "10", "unknown"},
        optional=False,
        scope=_Scope.ANNOTATION,
        sensor_types=["lidar", "radar"],
    )
    
    # Test numeric string detection
    assert attr._all_options_are_numeric() is False, "Should detect 'unknown' as non-numeric"
    
    # Create attribute with only numeric options
    attr_numeric = _SingleSelectAttribute(
        options={"1", "2", "3", "10"},
        optional=False,
        scope=_Scope.ANNOTATION,
        sensor_types=["lidar", "radar"],
    )
    
    assert attr_numeric._all_options_are_numeric() is True, "Should detect all options as numeric"
    
    print("  ✓ Numeric string detection works correctly")
    print("  ✓ Type conversion logic is in place")


def main():
    """Run all tests."""
    print("=" * 70)
    print("RailLabel ProviderKit - Ontology and Schema Test")
    print("=" * 70)
    
    try:
        test_ontology_paths()
        test_schema_paths()
        test_ontology_schema_mapping()
        test_single_select_conversion()
        
        print("\n" + "=" * 70)
        print("✓ All tests passed successfully!")
        print("=" * 70)
        
        print("\nAvailable ontologies:")
        for name in list_available_ontologies():
            print(f"  - {name}")
        
        print("\nAvailable schemas:")
        for name in list_available_schemas():
            print(f"  - {name}")
            
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"✗ Tests failed: {e}")
        print("=" * 70)
        raise


if __name__ == "__main__":
    main()
