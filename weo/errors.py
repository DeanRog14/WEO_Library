class WEO_ParsingError(Exception):
    def __init__(self, iso_code):
        super().__init__(f"Invalid ISO code provided: {iso_code}")
