"""
Oh I shouldn't do this.
"""


class Templater:
    def __init__(self, filename: str):
        self.filename = filename

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.file:
            return
        try:
            self.file.write("</body></html>")
            self.file.close()
        except:
            pass

    def document(self):
        """
        This is a document.
        """
        self.file = open(self.filename, "w", encoding="utf-8")
        self.file.write(
            """
        <html><style>.grey {
          padding: 20px;
          background-color: WhiteSmoke;
        }</style><body>"""
        )
