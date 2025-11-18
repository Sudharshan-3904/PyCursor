from PyQt6.Qsci import QsciScintilla

for style in ["BoxedFoldStyle", "BoxedTreeFoldStyle", "PlainFoldStyle"]:
    if hasattr(QsciScintilla, style):
        self.setFolding(getattr(QsciScintilla, style))
        break
else:
    self.setFolding(QsciScintilla.NoFoldStyle)
