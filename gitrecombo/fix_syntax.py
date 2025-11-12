with open('desktop_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the broken text_color line
content = content.replace('text_color="MODERN_COLORS["bg_primary",', 'text_color=MODERN_COLORS["bg_primary"],')

with open('desktop_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Syntax error fixed - ready to launch!')