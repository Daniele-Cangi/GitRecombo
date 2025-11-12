import sqlite3

conn = sqlite3.connect('repo_cache.db')
cursor = conn.cursor()

# Vedi tabelle
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tabelle nel database:')
for table in tables:
    print(f'  - {table[0]}')

# Controlla processed_repos
try:
    cursor.execute('PRAGMA table_info(processed_repos)')
    columns = cursor.fetchall()
    print(f'\nColonne nella tabella processed_repos:')
    for col in columns:
        print(f'  - {col[1]}')
    
    cursor.execute('SELECT COUNT(*) FROM processed_repos')
    count_processed = cursor.fetchone()[0]
    print(f'Repository processati: {count_processed}')
    
    cursor.execute('SELECT * FROM processed_repos LIMIT 5')
    print('Primi 5 record processati:')
    for row in cursor.fetchall():
        print(f'  - {row}')
except Exception as e:
    print(f'\nErrore nell\'accesso alla tabella processed_repos: {e}')

# Controlla repositories
try:
    cursor.execute('PRAGMA table_info(repositories)')
    columns = cursor.fetchall()
    print(f'\nColonne nella tabella repositories:')
    for col in columns:
        print(f'  - {col[1]}')
    
    cursor.execute('SELECT COUNT(*) FROM repositories')
    count = cursor.fetchone()[0]
    print(f'Repository nella tabella repositories: {count}')
    
    if count > 0:
        cursor.execute('SELECT * FROM repositories LIMIT 3')
        print('Primi 3 record:')
        for row in cursor.fetchall():
            print(f'  - {row}')
except Exception as e:
    print(f'\nErrore nell\'accesso alla tabella repositories: {e}')

conn.close()