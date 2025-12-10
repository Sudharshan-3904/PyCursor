import os

file_path = r"e:\Tester\PyCursor\core\app_main.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# We want to keep lines 0-329 (Line 1 to 330)
# And lines from 559 onwards (Line 560 to end)
# Line 329 (index 328) is "        return\n"
# Line 330 (index 329) is "\n"
# Line 331 (index 330) is "        menu_bar = self.menuBar()\n"
# ...
# Line 559 (index 558) is "        menu_bar.setCornerWidget(corner_widget, Qt.Corner.TopRightCorner)\n"
# Line 560 (index 559) is "    \n"

new_lines = lines[:330] + lines[559:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Cleanup done")
