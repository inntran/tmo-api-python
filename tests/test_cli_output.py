"""Tests for CLI output formatting functions."""

import json
import tempfile
from pathlib import Path

import pytest

from tmo_api.cli import (
    flatten_json,
    flatten_name_value_array,
    handle_output,
    is_name_value_array,
    prepare_data_for_flattening,
    write_to_csv,
)


class TestIsNameValueArray:
    """Tests for is_name_value_array function."""

    def test_valid_name_value_array(self):
        data = [
            {"Name": "Field1", "Value": "Value1"},
            {"Name": "Field2", "Value": "Value2"},
        ]
        assert is_name_value_array(data) is True

    def test_empty_list(self):
        assert is_name_value_array([]) is False

    def test_not_a_list(self):
        assert is_name_value_array({"Name": "Field1", "Value": "Value1"}) is False

    def test_list_without_name_key(self):
        data = [{"Field": "Value1"}, {"Field": "Value2"}]
        assert is_name_value_array(data) is False

    def test_list_without_value_key(self):
        data = [{"Name": "Field1"}, {"Name": "Field2"}]
        assert is_name_value_array(data) is False

    def test_list_with_non_dict_items(self):
        data = ["Field1", "Field2"]
        assert is_name_value_array(data) is False


class TestFlattenNameValueArray:
    """Tests for flatten_name_value_array function."""

    def test_basic_flattening(self):
        data = [
            {"Name": "Account Number", "Value": "12345"},
            {"Name": "Account-Status", "Value": "Active"},
        ]
        result = flatten_name_value_array(data)
        assert result == {
            "Account_Number": "12345",
            "Account_Status": "Active",
        }

    def test_with_parent_key(self):
        data = [
            {"Name": "Field1", "Value": "Value1"},
            {"Name": "Field2", "Value": "Value2"},
        ]
        result = flatten_name_value_array(data, parent_key="CustomFields")
        assert result == {
            "CustomFields_Field1": "Value1",
            "CustomFields_Field2": "Value2",
        }

    def test_empty_name_skipped(self):
        data = [
            {"Name": "", "Value": "Value1"},
            {"Name": "Field2", "Value": "Value2"},
        ]
        result = flatten_name_value_array(data)
        assert result == {"Field2": "Value2"}

    def test_special_characters_cleaned(self):
        data = [
            {"Name": "Field.1", "Value": "Value1"},
            {"Name": "Field-2", "Value": "Value2"},
            {"Name": "Field 3", "Value": "Value3"},
        ]
        result = flatten_name_value_array(data)
        assert result == {
            "Field_1": "Value1",
            "Field_2": "Value2",
            "Field_3": "Value3",
        }


class TestFlattenJson:
    """Tests for flatten_json function."""

    def test_simple_dict(self):
        data = {"field1": "value1", "field2": "value2"}
        result = flatten_json(data, max_levels=2)
        assert result == {"field1": "value1", "field2": "value2"}

    def test_nested_dict_one_level(self):
        data = {"field1": {"nested": "value"}}
        result = flatten_json(data, max_levels=2)
        assert result == {"field1_nested": "value"}

    def test_nested_dict_max_levels(self):
        data = {"level1": {"level2": {"level3": "value"}}}
        result = flatten_json(data, max_levels=1)
        # After 1 level of flattening, level2 should be JSON string
        assert "level1_level2" in result
        assert isinstance(result["level1_level2"], str)
        assert "level3" in result["level1_level2"]

    def test_list_with_name_value_pairs(self):
        data = {
            "CustomFields": [
                {"Name": "Field1", "Value": "Value1"},
                {"Name": "Field2", "Value": "Value2"},
            ]
        }
        result = flatten_json(data, max_levels=2)
        assert result == {
            "CustomFields_Field1": "Value1",
            "CustomFields_Field2": "Value2",
        }

    def test_regular_array(self):
        data = {"items": ["item1", "item2"]}
        result = flatten_json(data, max_levels=2)
        assert result == {"items_0": "item1", "items_1": "item2"}

    def test_primitive_value_with_parent_key(self):
        result = flatten_json("value", parent_key="key")
        assert result == {"key": "value"}

    def test_primitive_value_without_parent_key(self):
        result = flatten_json("value")
        assert result == {"value": "value"}


class TestPrepareDataForFlattening:
    """Tests for prepare_data_for_flattening function."""

    def test_list_of_dicts(self):
        data = [{"field1": "value1"}, {"field2": "value2"}]
        result = prepare_data_for_flattening(data)
        assert len(result) == 2
        assert result[0] == {"field1": "value1"}
        assert result[1] == {"field2": "value2"}

    def test_single_dict(self):
        data = {"field1": "value1"}
        result = prepare_data_for_flattening(data)
        assert len(result) == 1
        assert result[0] == {"field1": "value1"}

    def test_filters_raw_data(self):
        data = [{"field1": "value1", "raw_data": {"should": "be removed"}}]
        result = prepare_data_for_flattening(data)
        assert "raw_data" not in result[0]
        assert "field1" in result[0]

    def test_object_with_dict_attribute(self):
        class TestObject:
            def __init__(self):
                self.field1 = "value1"
                self.raw_data = {"should": "be removed"}
                self._private = "excluded"

        obj = TestObject()
        result = prepare_data_for_flattening(obj)
        assert len(result) == 1
        assert result[0] == {"field1": "value1"}

    def test_list_of_objects(self):
        class TestObject:
            def __init__(self, value):
                self.field = value

        data = [TestObject("value1"), TestObject("value2")]
        result = prepare_data_for_flattening(data)
        assert len(result) == 2
        assert result[0] == {"field": "value1"}
        assert result[1] == {"field": "value2"}


class TestWriteToCsv:
    """Tests for write_to_csv function."""

    def test_write_simple_records(self, tmp_path):
        records = [
            {"name": "Alice", "age": "30"},
            {"name": "Bob", "age": "25"},
        ]
        # tmp_path already provides unique directory per test
        output_file = tmp_path / "output.csv"

        write_to_csv(records, str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        assert "name,age" in content or "age,name" in content
        assert "Alice" in content
        assert "Bob" in content

    def test_write_with_missing_fields(self, tmp_path):
        records = [
            {"name": "Alice", "age": "30"},
            {"name": "Bob"},  # Missing age
        ]
        output_file = tmp_path / "output.csv"

        write_to_csv(records, str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        lines = content.strip().split("\n")
        # Should have header + 2 data rows
        assert len(lines) == 3

    def test_write_empty_records(self, tmp_path, capsys):
        output_file = tmp_path / "output.csv"

        write_to_csv([], str(output_file))

        # Should print warning
        captured = capsys.readouterr()
        assert "No records to write" in captured.err


class TestHandleOutput:
    """Tests for handle_output function."""

    def test_stdout_text_output(self, capsys):
        data = [{"field": "value"}]
        handle_output(data, None)

        captured = capsys.readouterr()
        assert "field" in captured.out
        assert "value" in captured.out

    def test_json_file_output(self, tmp_path):
        data = [{"field": "value"}]
        output_file = tmp_path / "output.json"

        handle_output(data, str(output_file))

        assert output_file.exists()
        content = json.loads(output_file.read_text())
        assert content[0]["field"] == "value"

    def test_csv_file_output(self, tmp_path):
        data = [{"field": "value"}]
        output_file = tmp_path / "output.csv"

        handle_output(data, str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        assert "field" in content
        assert "value" in content

    def test_unsupported_format(self, tmp_path):
        data = [{"field": "value"}]
        output_file = tmp_path / "output.txt"

        with pytest.raises(ValueError, match="Unsupported output format"):
            handle_output(data, str(output_file))

    def test_xlsx_file_output(self, tmp_path):
        pytest.importorskip("openpyxl")
        data = [{"field": "value"}]
        output_file = tmp_path / "output.xlsx"

        handle_output(data, str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0


class TestWriteToXlsx:
    """Tests for write_to_xlsx function."""

    def test_requires_openpyxl(self, tmp_path, monkeypatch):
        # Simulate openpyxl not being installed
        import builtins
        import sys

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "openpyxl" or name.startswith("openpyxl."):
                raise ImportError("No module named 'openpyxl'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        from tmo_api.cli import write_to_xlsx

        records = [{"field": "value"}]
        output_file = tmp_path / "output.xlsx"

        with pytest.raises(ImportError, match="openpyxl is required"):
            write_to_xlsx(records, str(output_file))

    def test_write_xlsx_basic(self, tmp_path):
        openpyxl = pytest.importorskip("openpyxl")
        from tmo_api.cli import write_to_xlsx

        records = [
            {"name": "Alice", "age": "30"},
            {"name": "Bob", "age": "25"},
        ]
        output_file = tmp_path / "output.xlsx"

        write_to_xlsx(records, str(output_file))

        assert output_file.exists()

        # Verify content
        wb = openpyxl.load_workbook(output_file)
        ws = wb.active
        assert ws is not None
        # Check header row exists
        assert ws.cell(1, 1).value is not None

    def test_write_xlsx_empty_records(self, tmp_path, capsys):
        pytest.importorskip("openpyxl")
        from tmo_api.cli import write_to_xlsx

        output_file = tmp_path / "output.xlsx"

        write_to_xlsx([], str(output_file))

        captured = capsys.readouterr()
        assert "No records to write" in captured.err
