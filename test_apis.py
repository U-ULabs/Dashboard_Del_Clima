import sys
sys.path.insert(0, '/home/kali/project_export')

from data_sources import meteoblue, meteosource

print("Testing Meteoblue...")
df_mb = meteoblue.fetch_meteoblue()
print(f"Meteoblue rows: {len(df_mb)}")
print(df_mb.head())
print()

print("Testing Meteosource...")
df_ms = meteosource.fetch_meteosource()
print(f"Meteosource rows: {len(df_ms)}")
print(df_ms.head())
