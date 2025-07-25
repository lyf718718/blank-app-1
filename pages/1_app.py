import pandas as pd
import re
from collections import defaultdict

# Load data
df = pd.read_csv('sample_data.csv')

# Load dictionary
dictionaries = {
    'urgency_marketing': {
        'limited', 'limited time', 'limited run', 'limited edition', 'order now',
        'last chance', 'hurry', 'while supplies last', 'before they\'re gone',
        'selling out', 'selling fast', 'act now', 'don\'t wait', 'today only',
        'expires soon', 'final hours', 'almost gone'
    },
    'exclusive_marketing': {
        'exclusive', 'exclusively', 'exclusive offer', 'exclusive deal',
        'members only', 'vip', 'special access', 'invitation only',
        'premium', 'privileged', 'limited access', 'select customers',
        'insider', 'private sale', 'early access'
    }
}

def classify_statement(text, dictionaries):
    """Classify a statement based on marketing tactic dictionaries."""
    if pd.isna(text):
        return {}
    
    text_lower = text.lower()
    results = {}
    
    for tactic, keywords in dictionaries.items():
        matches = []
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matches.append(keyword)
        
        results[tactic] = {
            'present': len(matches) > 0,
            'count': len(matches),
            'matches': matches
        }
    
    return results

# Apply classification
df['classification'] = df['Statement'].apply(lambda x: classify_statement(x, dictionaries))

# Extract results to separate columns
for tactic in dictionaries.keys():
    df[f'{tactic}_present'] = df['classification'].apply(lambda x: x.get(tactic, {}).get('present', False))
    df[f'{tactic}_count'] = df['classification'].apply(lambda x: x.get(tactic, {}).get('count', 0))
    df[f'{tactic}_matches'] = df['classification'].apply(lambda x: ', '.join(x.get(tactic, {}).get('matches', [])))

# Display results
print("Classification Results:")
print("=" * 50)

# Show summary
for tactic in dictionaries.keys():
    total_present = df[f'{tactic}_present'].sum()
    print(f"{tactic}: {total_present}/{len(df)} statements ({total_present/len(df)*100:.1f}%)")

print("\nDetailed Results:")
print("=" * 50)

# Show detailed results
display_cols = ['ID', 'Statement'] + [col for col in df.columns if '_present' in col or '_matches' in col]
result_df = df[display_cols].copy()

for _, row in result_df.iterrows():
    print(f"\nID: {row['ID']}")
    print(f"Statement: {row['Statement']}")
    for tactic in dictionaries.keys():
        if row[f'{tactic}_present']:
            print(f"  ✓ {tactic}: {row[f'{tactic}_matches']}")
        else:
            print(f"  ✗ {tactic}: No matches")

# Save results
output_file = 'classified_data.csv'
df.to_csv(output_file, index=False)
print(f"\nResults saved to: {output_file}")

# Optional: Quick stats
print(f"\nQuick Stats:")
print(f"Total statements: {len(df)}")
print(f"Statements with any tactic: {(df[[f'{t}_present' for t in dictionaries.keys()]].any(axis=1)).sum()}")
