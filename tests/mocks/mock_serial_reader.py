class MockSerialReader:
    """
    A deterministic, line-driven mock replacement for SerialReader.
    Designed for integration tests that want to simulate serial input
    without patching serial.Serial directly.

    Usage:
        reader = MockSerialReader.from_lines([
            "CPS, 10, CPM, 100, uSv/hr, 0.10, SLOW",
            "CPS, 20, CPM, 200, uSv/hr, 0.20, FAST",
        ])

        line = reader.read_line()  # returns first line
        line = reader.read_line()  # returns second line
        line = reader.read_line()  # raises StopIteration
    """

    def __init__(self, lines=None, side_effect=None):
        self._lines = list(lines or [])
        self._index = 0
        self._side_effect = side_effect

    @classmethod
    def from_lines(cls, lines):
        """Convenience constructor for simple line sequences."""
        return cls(lines=lines)

    def read_line(self):
        """
        Mimics SerialReader.read_line():
        - Returns the next line as a string
        - Raises StopIteration when exhausted
        - Supports side_effect exceptions
        """
        # If a side_effect is provided, behave like MagicMock
        if self._side_effect:
            effect = self._side_effect.pop(0)
            if isinstance(effect, Exception):
                raise effect
            return effect

        if self._index >= len(self._lines):
            raise StopIteration("MockSerialReader exhausted")

        line = self._lines[self._index]
        self._index += 1
        return line
