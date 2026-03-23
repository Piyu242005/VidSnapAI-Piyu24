import re
import glob
import os

def process_css(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Generic cleanups to modern vars
    content = re.sub(r'var\(--bg-card[^)]*\)', 'var(--card-bg)', content)
    content = re.sub(r'var\(--text-light[^)]*\)', 'var(--text-primary)', content)
    content = re.sub(r'var\(--text-muted[^)]*\)', 'var(--text-secondary)', content)
    content = re.sub(r'var\(--border-default[^)]*\)', 'var(--border-color)', content)
    content = re.sub(r'var\(--border-subtle[^)]*\)', 'var(--border-color)', content)
    content = re.sub(r'var\(--accent-glow[^)]*\)', 'var(--shadow)', content)
    
    # Remove gold theme code completely
    content = re.sub(r'\[data-theme="gold"\].*?\{[^}]*\}', '', content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

for filepath in glob.glob('static/css/*.css'):
    process_css(filepath)
    print(f"Processed: {filepath}")
