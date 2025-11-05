import copy


# Assumption 1:
# The problem statement mentions:
# "Only once the value type of the key is determined should the parser return the key-value pair.
# "String values **on the other hand** can be partially returned"
# I am assuming that partial string values can be returned but not partial (nested) objects.
# So I will be waiting for the nested object to be closed by '}' before exposing its value
#
# Assumption 2:
# The problem could be solved with recursion but I am assuming it is possible to have more than 1000
# nested objects which could cause the program to hit the python recursion limit.
# I therefore chose to use a stack instead of using recursion
#
# Assumption 3:
# I did not include JSON validation and error handling as I am assuming that we consume a valid partial JSON each time


# Complexity
# The time complexity is linear with the size of the buffer consumed as we usually only process each character once.
# The only exception is when searching for nested object boundaries where we can process commas and whitespaces twice (this overhead is constant)
# The memory complexity is linar with the number of consecutive nested object as we have to save the parsing context of all parent objects.

# Formatting
# I used the Black Formatter with default configurations


class StreamingJsonParser:

    __STRING_DELIMITER = '"'
    __OBJECT_START = "{"
    __OBJECT_END = "}"
    __COMMA = ","

    class __ParsingContext:
        current_key: str
        current_key_buffer: list[str]
        current_object_value_buffer: dict
        current_string_value_buffer: list[str]
        is_parsing_key: bool
        is_parsing_value: bool

        def __init__(self) -> None:
            self.current_key = None
            self.current_key_buffer = list()
            self.current_object_value_buffer = dict()
            self.current_string_value_buffer = list()
            self.is_parsing_key = False
            self.is_parsing_value = False

    __context_stack = list()
    __current_context: __ParsingContext

    def __init__(self) -> None:
        self.__context_stack = list()
        self.__current_context = StreamingJsonParser.__ParsingContext()
        return

    def consume(self, buffer: str) -> None:
        """
        Add the content of the buffer (a partial JSON string) to a dict

        Args:
            buffer (str): A partial (chunked) representation of a valid JSON object containing only string and object values
        """

        # this offset can be moved by helper methods consuming the buffer
        character_offset: int = 0
        buffer_length: int = len(buffer)

        while character_offset < buffer_length:
            # the current key is not fully built yet
            if self.__current_context.current_key is None:

                # the key is null at the start or just after building a new value
                # in the latter case we check if we reached the end of a nested object
                if not self.__current_context.is_parsing_key:
                    object_end_index = self.__find_index_for_next_object_end(
                        buffer, character_offset
                    )
                    if self.__context_stack and object_end_index != -1:
                        self.__pop_context()
                        character_offset = object_end_index + 1
                        continue

                # build the key
                character_offset = self.__build_current_key(buffer, character_offset)
            else:

                if not self.__current_context.is_parsing_value:
                    # we just finished parsing the key but haven't received anything to determine the type of the value yet
                    object_start_index = self.__find_index_for_next_object_start(
                        buffer, character_offset
                    )
                    if object_start_index != -1:
                        self.__push_context()
                        character_offset = object_start_index + 1
                        continue

                # build the value
                character_offset = self.__build_current_value(buffer, character_offset)

        return

    def __find_index_for_next_object_start(
        self, buffer: str, character_offset: int
    ) -> int:
        return self.__find_index_for_char(buffer, character_offset, self.__OBJECT_START)

    def __find_index_for_next_object_end(
        self, buffer: str, character_offset: int
    ) -> int:
        return self.__find_index_for_char(buffer, character_offset, self.__OBJECT_END)

    def __find_index_for_char(
        self, buffer: str, character_offset: int, target_char: str
    ) -> int:
        for i in range(character_offset, len(buffer)):
            current_char: str = buffer[i]

            if current_char == target_char:
                return i

            if current_char == self.__STRING_DELIMITER:
                return -1

        return -1

    def __push_context(self) -> None:
        self.__context_stack.append(self.__current_context)
        self.__current_context = StreamingJsonParser.__ParsingContext()
        return

    def __pop_context(self) -> None:
        complete_object = self.__current_context.current_object_value_buffer
        self.__current_context = self.__context_stack.pop()
        self.__current_context.current_object_value_buffer[
            self.__current_context.current_key
        ] = complete_object
        self.__current_context.current_key = None
        return

    def __build_current_key(self, buffer: str, character_offset: int) -> int:
        for i in range(character_offset, len(buffer)):
            current_char: str = buffer[i]

            if (
                not self.__current_context.is_parsing_key
                and current_char != self.__STRING_DELIMITER
            ):
                # ignore characters before the key starts
                continue

            if current_char == self.__STRING_DELIMITER:
                if not self.__current_context.is_parsing_key:
                    # we are building a new key
                    # skip the delimiter and set the flag as we enter the key
                    self.__current_context.is_parsing_key = True
                    continue

                else:
                    # we finished parsing the current key
                    self.__current_context.current_key = "".join(
                        self.__current_context.current_key_buffer
                    )
                    self.__current_context.current_key_buffer = list()
                    self.__current_context.is_parsing_key = False
                    # return index of next character to parse
                    return i + 1

            # simply add the value in the key buffer
            self.__current_context.current_key_buffer.append(current_char)

        # we processed the whole buffer, return its length
        return len(buffer)

    def __build_current_value(self, buffer: str, character_offset: int) -> int:
        for i in range(character_offset, len(buffer)):
            current_char: str = buffer[i]
            if (
                not self.__current_context.is_parsing_value
                and current_char != self.__STRING_DELIMITER
            ):
                # ignore':' and whitespace when starting to parse string value
                # but if we see a '}' or ',' it means there was a null value
                if current_char == self.__OBJECT_END or current_char == self.__COMMA:
                    # there was a null, set value to None in dict and proceed
                    self.__store_value_and_reset_context(None)

                    # do not skip parsing the potential '}'
                    return i

                continue

            if current_char == self.__STRING_DELIMITER:
                if not self.__current_context.is_parsing_value:
                    # we are building a new string value
                    # skip the delimiter
                    self.__current_context.is_parsing_value = True
                    continue

                else:
                    # we finished parsing the current string value
                    complete_value: str = "".join(
                        self.__current_context.current_string_value_buffer
                    )

                    # flush key value pair in the dict and reset
                    self.__store_value_and_reset_context(complete_value)
                    # return index of next character to parse
                    return i + 1

            # simply add the value in the value buffer
            self.__current_context.current_string_value_buffer.append(current_char)

        if self.__current_context.is_parsing_value:
            # we did not find a string value end delimiter, we should still expose the partial string value in the output dict
            partial_string_value: str = "".join(
                self.__current_context.current_string_value_buffer
            )
            self.__current_context.current_object_value_buffer[
                self.__current_context.current_key
            ] = partial_string_value
        return len(buffer)

    def __store_value_and_reset_context(self, value: str | None | dict) -> None:
        self.__current_context.current_object_value_buffer[
            self.__current_context.current_key
        ] = value
        self.__current_context.current_key = None
        self.__current_context.current_string_value_buffer = list()
        self.__current_context.is_parsing_value = False
        return

    def get(self) -> dict:
        """
        Returns the current state of the parsed object.
        String values can be returned even when partially built.
        Object values are returned once the object is fully built.


        Returns:
            int: The index in the buffer of the next character to parse.
            To be used to move the offset in other method calls.
        """

        # the dict at the bottom of the stack (so head of the list) is the top-level dict
        # or it is the current context if empty
        top_level_parsing_context: StreamingJsonParser.__ParsingContext = (
            self.__current_context
        )
        if self.__context_stack:
            top_level_parsing_context = self.__context_stack[0]

        # returning a copy of the output to prevent accidental modification
        return copy.deepcopy(top_level_parsing_context.current_object_value_buffer)
