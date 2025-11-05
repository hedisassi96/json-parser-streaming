import unittest
from hedi_sassi_streaming_json_parser import StreamingJsonParser


class TestStreamingJsonParser(unittest.TestCase):

    def test_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo": "bar"}')
        self.assertEqual(parser.get(), {"foo": "bar"})

    def test_partial_quote_key_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"')
        self.assertEqual(parser.get(), {})
        parser.consume('foo": "bar"}')
        self.assertEqual(parser.get(), {"foo": "bar"})

    def test_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo": null, "bar": ')
        self.assertEqual(parser.get(), {"foo": None})
        parser.consume('{"a": nu')
        self.assertEqual(parser.get(), {"foo": None})
        parser.consume('ll, "b": "something"}')
        self.assertEqual(
            parser.get(), {"foo": None, "bar": {"a": None, "b": "something"}}
        )

    def test_empty_value_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo": ""}')
        self.assertEqual(parser.get(), {"foo": ""})

    def test_null_value_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo": null}')
        self.assertEqual(parser.get(), {"foo": None})

    def test_null_value_chunked_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo": nul')
        self.assertEqual(parser.get(), {})
        parser.consume("l")
        self.assertEqual(parser.get(), {})
        parser.consume("}")
        self.assertEqual(parser.get(), {"foo": None})

    def test_empty_key_and_val_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"": ""}')
        self.assertEqual(parser.get(), {"": ""})

    def test_empty_key_empty_object_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"": {')
        self.assertEqual(parser.get(), {})
        parser.consume("}}")
        self.assertEqual(parser.get(), {"": {}})

    def test_chunked_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo":')
        parser.consume('"bar')
        self.assertEqual(parser.get(), {"foo": "bar"})

    def test_partial_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo": "bar')
        self.assertEqual(parser.get(), {"foo": "bar"})

    def test_partial_quote_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo": "')
        self.assertEqual(parser.get(), {"foo": ""})
        parser.consume('bar"')
        self.assertEqual(parser.get(), {"foo": "bar"})

    def test_partial_string_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo": "bar", "country": "')
        self.assertEqual(parser.get(), {"foo": "bar", "country": ""})
        parser.consume("Switz")
        self.assertEqual(parser.get(), {"foo": "bar", "country": "Switz"})
        parser.consume("erland")
        self.assertEqual(parser.get(), {"foo": "bar", "country": "Switzerland"})

    def test_immutable_output_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo": "bar", "country": "Switz')
        value = parser.get()
        self.assertEqual(parser.get(), {"foo": "bar", "country": "Switz"})

        value["foo"] = "adios"
        self.assertEqual(value, {"foo": "adios", "country": "Switz"})

        self.assertEqual(parser.get(), {"foo": "bar", "country": "Switz"})

    def test_split_key_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foob')
        self.assertEqual(parser.get(), {})
        parser.consume('ar": "value"')
        self.assertEqual(parser.get(), {"foobar": "value"})

    def test_sub_objects_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo": {"bar": "foobar"')
        self.assertEqual(parser.get(), {})
        parser.consume("}")
        self.assertEqual(parser.get(), {"foo": {"bar": "foobar"}})
        parser.consume(',"a": {')
        self.assertEqual(parser.get(), {"foo": {"bar": "foobar"}})
        parser.consume('"inner": { "a": "b"}')
        self.assertEqual(parser.get(), {"foo": {"bar": "foobar"}})
        parser.consume("}")
        self.assertEqual(
            parser.get(), {"foo": {"bar": "foobar"}, "a": {"inner": {"a": "b"}}}
        )

    def test_sub_objects_closing_in_chunks(self):
        parser = StreamingJsonParser()
        parser.consume('{"a": {"inner": {"a": "b"')
        self.assertEqual(parser.get(), {})
        parser.consume("}")
        self.assertEqual(parser.get(), {})
        parser.consume("}")
        self.assertEqual(parser.get(), {"a": {"inner": {"a": "b"}}})
        parser.consume("}")
        self.assertEqual(parser.get(), {"a": {"inner": {"a": "b"}}})

    def test_sub_objects_closing_in_chunks(self):
        parser = StreamingJsonParser()
        parser.consume('{"{,{,{,{,{a": {",{inner": {"{a,; ": "}b{,:"')
        self.assertEqual(parser.get(), {})
        parser.consume("}")
        self.assertEqual(parser.get(), {})
        parser.consume("}")
        self.assertEqual(parser.get(), {"{,{,{,{,{a": {",{inner": {"{a,; ": "}b{,:"}}})
        parser.consume("}")
        self.assertEqual(parser.get(), {"{,{,{,{,{a": {",{inner": {"{a,; ": "}b{,:"}}})

    def test_sub_key_values_in_chunks(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo": {"bar')
        self.assertEqual(parser.get(), {})
        parser.consume('": "')
        self.assertEqual(parser.get(), {})
        parser.consume("foobar")
        self.assertEqual(parser.get(), {})
        parser.consume('"}')
        self.assertEqual(parser.get(), {"foo": {"bar": "foobar"}})

    def test_sub_objects_empty_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo": {')
        self.assertEqual(parser.get(), {})
        parser.consume("}")
        self.assertEqual(parser.get(), {"foo": {}})

    # AI-generated tests

    def test_empty_json(self):
        parser = StreamingJsonParser()
        parser.consume('{}')
        self.assertEqual(parser.get(), {})

    def test_deeply_nested_objects(self):
        parser = StreamingJsonParser()
        parser.consume('{"a": {"b": {"c": {"d": {"e": "f"}}}}}')
        expected = {
            "a": {
                "b": {
                    "c": {
                        "d": {
                            "e": "f"
                        }
                    }
                }
            }
        }
        self.assertEqual(parser.get(), expected)

    def test_deeply_nested_objects_chunked(self):
        parser = StreamingJsonParser()
        parser.consume('{"a":')
        self.assertEqual(parser.get(), {})
        parser.consume('{"b":')
        self.assertEqual(parser.get(), {})
        parser.consume('{"c":')
        self.assertEqual(parser.get(), {})
        parser.consume('{"d":')
        self.assertEqual(parser.get(), {})
        parser.consume('{"e":')
        self.assertEqual(parser.get(), {})
        parser.consume('"f"}}}')
        self.assertEqual(parser.get(), {})
        parser.consume('}}')
        expected = {
            "a": {
                "b": {
                    "c": {
                        "d": {
                            "e": "f"
                        }
                    }
                }
            }
        }
        self.assertEqual(parser.get(), expected)
        parser.consume('}}')
        self.assertEqual(parser.get(), expected)

    def test_special_chars_in_strings(self):
        parser = StreamingJsonParser()
        json_string = '{"key with spaces": "value with, commas, and {braces}", "another-key": "value with: colons"}'
        parser.consume(json_string)
        self.assertEqual(parser.get(), {"key with spaces": "value with, commas, and {braces}", "another-key": "value with: colons"})

    def test_very_long_string_value(self):
        parser = StreamingJsonParser()
        long_string = "a" * 10000
        parser.consume(f'{{"long": "{long_string}"}}')
        self.assertEqual(parser.get(), {"long": long_string})

    def test_very_long_string_value_chunked(self):
        parser = StreamingJsonParser()
        long_string = "a" * 10000
        parser.consume('{"long": "')
        self.assertEqual(parser.get(), {"long": ""})
        for i in range(1000):
            parser.consume("a" * 10)
            self.assertEqual(parser.get(), {"long": "a" * ((i + 1) * 10)})
        parser.consume('"}')
        self.assertEqual(parser.get(), {"long": long_string})

    def test_multiple_key_value_pairs(self):
        parser = StreamingJsonParser()
        parser.consume('{"a": "1", "b": "2", "c": "3", "d": "4"}')
        self.assertEqual(parser.get(), {"a": "1", "b": "2", "c": "3", "d": "4"})

    def test_multiple_key_value_pairs_chunked(self):
        parser = StreamingJsonParser()
        parser.consume('{"a": "1",')
        self.assertEqual(parser.get(), {"a": "1"})
        parser.consume(' "b": "2",')
        self.assertEqual(parser.get(), {"a": "1", "b": "2"})
        parser.consume(' "c": "3"')
        self.assertEqual(parser.get(), {"a": "1", "b": "2", "c": "3"})
        parser.consume(', "d": "4"}')
        self.assertEqual(parser.get(), {"a": "1", "b": "2", "c": "3", "d": "4"})

    def test_mixed_values(self):
        parser = StreamingJsonParser()
        parser.consume('{"a": "string", "b": {"c": "nested"}, "d": null, "e": ""}')
        self.assertEqual(parser.get(), {"a": "string", "b": {"c": "nested"}, "d": None, "e": ""})

    def test_chunking_at_boundaries(self):
        parser = StreamingJsonParser()
        parser.consume('{')
        self.assertEqual(parser.get(), {})
        parser.consume('"a"')
        self.assertEqual(parser.get(), {})
        parser.consume(':')
        self.assertEqual(parser.get(), {})
        parser.consume('"b"')
        self.assertEqual(parser.get(), {"a": "b"})
        parser.consume(',')
        self.assertEqual(parser.get(), {"a": "b"})
        parser.consume('"c"')
        self.assertEqual(parser.get(), {"a": "b"})
        parser.consume(':')
        self.assertEqual(parser.get(), {"a": "b"})
        parser.consume('null')
        self.assertEqual(parser.get(), {"a": "b"})
        parser.consume('}')
        self.assertEqual(parser.get(), {"a": "b", "c": None})

    def test_unicode_characters(self):
        parser = StreamingJsonParser()
        parser.consume('{"key_ru": "ключ", "value_ru": "значение"}')
        self.assertEqual(parser.get(), {"key_ru": "ключ", "value_ru": "значение"})

    def test_partial_unicode_characters(self):
        parser = StreamingJsonParser()
        parser.consume('{"key": "прив')
        self.assertEqual(parser.get(), {"key": "прив"})
        parser.consume('ет"}')
        self.assertEqual(parser.get(), {"key": "привет"})

    def test_null_value_in_object(self):
        parser = StreamingJsonParser()
        parser.consume('{"a": null, "b": "not null"}')
        self.assertEqual(parser.get(), {"a": None, "b": "not null"})

    def test_trailing_comma_in_object(self):
        # This is technically invalid JSON, but let's see how the parser handles it.
        # Based on the current implementation, it will likely wait for another key-value pair.
        parser = StreamingJsonParser()
        parser.consume('{"a": "b",}')
        self.assertEqual(parser.get(), {"a": "b"})
        parser.consume('"c": "d"}')
        self.assertEqual(parser.get(), {"a": "b", "c": "d"})

    def test_no_comma_between_kv_pairs(self):
        # This is invalid JSON. The parser will likely merge the second key into the first value.
        parser = StreamingJsonParser()
        parser.consume('{"a": "b" "c": "d"}')
        self.assertEqual(parser.get(), {'a': 'b', 'c': 'd'})

    def test_key_with_no_value(self):
        # This is invalid. The parser should ideally not add the key.
        parser = StreamingJsonParser()
        parser.consume('{"a":')
        self.assertEqual(parser.get(), {})
        parser.consume('}')
        self.assertEqual(parser.get(), {"a": None}) # Implementation dependent, None is a reasonable output

    def test_value_before_key(self):
        # Invalid JSON
        parser = StreamingJsonParser()
        parser.consume('{"a": "b", "c"}')
        self.assertEqual(parser.get(), {"a": "b", "c": None}) # Should ignore "c"


if __name__ == "__main_":
    unittest.main()
