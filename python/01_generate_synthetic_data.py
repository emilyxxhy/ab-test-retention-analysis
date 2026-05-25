"""
Synthetic Data Generator: AI Chat Feature Impact on Instagram Retention
=========================================================================

This script generates realistic user behavior data for an A/B test analysis.

Assumptions (based on public benchmarks):
- Instagram baseline D1 retention: ~85%
- Instagram baseline L7 retention: ~38-42%
- Instagram baseline L28 retention: ~25-30%
- Realistic retention decay follows power law (not linear)
- AI Chat feature adds ~10% relative retention lift

Public sources:
- App Annie / data.ai benchmarks
- Meta investor relations (SEC filings)
- Academic literature on mobile app retention
"""

import pandas as pd
import numpy as np
from scipy.stats import bernoulli
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

np.random.seed(42)  # For reproducibility

N_USERS = 50000           # Total users in test
TREATMENT_SPLIT = 0.5     # 50/50 split
TEST_DURATION_DAYS = 30   # Run test for 30 days
AI_CHAT_LIFT = 1.10       # 10% relative lift (1.0 = baseline, 1.10 = +10%)

# ============================================================================
# STEP 1: Create User Base with Group Assignment
# ============================================================================

def create_users(n_users, treatment_split):
    """
    Create synthetic user records with random group assignment
    and additional demographic 'fluff' for realism.
    """
    regions = ['North America', 'Europe', 'Asia', 'LATAM', 'Rest of World']
    region_probs = [0.25, 0.25, 0.30, 0.15, 0.05]

    os_types = ['iOS', 'Android']
    os_probs = [0.45, 0.55]  # Rough global split

    users = pd.DataFrame({
        'user_id': range(1, n_users + 1),
        'created_date': pd.Timestamp('2024-01-01'),
        'group': np.random.choice(
            ['control', 'treatment'],
            size=n_users,
            p=[1 - treatment_split, treatment_split]
        ),
        'device_os': np.random.choice(os_types, size=n_users, p=os_probs),
        'region': np.random.choice(regions, size=n_users, p=region_probs)
    })
    return users

# ============================================================================
# STEP 2: Define Realistic Retention Curve
# ============================================================================

def get_baseline_retention_curve(days=30):
    """
    Generate a realistic retention curve based on mobile app benchmarks.
    
    Real apps follow a POWER LAW pattern:
    - Day 1: ~85% (high engagement from new users)
    - Day 7: ~40-45% (significant drop-off)
    - Day 28: ~25-30% (stabilizes around "power users")
    
    This is empirically validated for social/messaging apps.
    
    Formula: retention(t) = A * t^(-b)
    Where:
      - A = initial engagement (0.85)
      - b = decay rate (0.3)
      - t = day number
    """
    day_numbers = np.arange(1, days + 1)
    
    # Power law decay: 85% on Day 1, asymptotically approaches baseline
    retention = 0.85 * np.power(day_numbers, -0.3)
    
    # Bound retention between 15% (minimum power user level) and 85% (Day 1)
    retention = np.clip(retention, 0.15, 0.85)
    
    # Return as dict for easy lookup
    retention_curve = {}
    for day, rate in zip(day_numbers, retention):
        retention_curve[int(day)] = rate
    
    return retention_curve

# ============================================================================
# STEP 3: Generate Login Events
# ============================================================================

def generate_login_events(users, baseline_retention, ai_chat_lift, test_days):
    """
    Generate daily login events for each user based on their group.
    
    Control group: Uses baseline retention curve
    Treatment group: Uses baseline curve * AI_CHAT_LIFT
    
    This creates realistic event data where:
    - Most users are active Day 1-3, then drop off
    - Some users return periodically (power users)
    - Treatment group has slightly higher retention at each day
    - Users perform multiple realistic actions per session (view_reel, etc.)
    """
    events = []
    
    for _, user_row in users.iterrows():
        user_id = user_row['user_id']
        group = user_row['group']
        
        for day in range(1, test_days + 1):
            base_prob = baseline_retention[day]
            
            if group == 'treatment':
                prob_login = min(base_prob * ai_chat_lift, 0.95)
            else:
                prob_login = base_prob
            
            logged_in = bernoulli.rvs(prob_login)
            
            if logged_in == 1:
                # 1. Give them a realistic timestamp (not just midnight)
                base_time = pd.Timestamp('2024-01-01') + pd.Timedelta(days=day - 1)
                login_time = base_time + pd.Timedelta(hours=np.random.randint(6, 23), minutes=np.random.randint(0, 59))
                
                # Every session starts with opening the app
                events.append({
                    'user_id': user_id,
                    'event_timestamp': login_time,
                    'event_type': 'app_open'
                })
                
                # 2. Simulate 1 to 5 random actions during this session
                num_actions = np.random.randint(1, 6)
                
                # Basic actions everyone can do
                possible_actions = ['view_reel', 'like_post', 'send_dm', 'view_story']
                
                # Only treatment users get the AI Chat feature!
                if group == 'treatment':
                    # Give it a high weight so it appears frequently in the data
                    possible_actions.extend(['use_ai_chat', 'use_ai_chat'])
                
                current_time = login_time
                for _ in range(num_actions):
                    # Add 1-5 minutes between actions
                    current_time += pd.Timedelta(minutes=np.random.randint(1, 6))
                    action = np.random.choice(possible_actions)
                    
                    events.append({
                        'user_id': user_id,
                        'event_timestamp': current_time,
                        'event_type': action
                    })
    
    return pd.DataFrame(events)
# ============================================================================
# STEP 4: Calculate Retention Metrics (Validation)
# ============================================================================

def calculate_retention_metrics(events, users, days=7):
    # ADD THIS LINE - extracts date from the timestamp column
    events = events.copy()
    events['event_date'] = events['event_timestamp'].dt.date
    events['event_date'] = pd.to_datetime(events['event_date'])

    # rest of the function stays exactly the same...
    first_events = events.groupby('user_id')['event_date'].min().reset_index()
    first_events.columns = ['user_id', 'first_event_date']

    cohort = first_events.merge(users[['user_id', 'group']], on='user_id')
    cohort['threshold_date'] = cohort['first_event_date'] + pd.Timedelta(days=days)

    events_after_threshold = events[
        events['event_date'] >= events['event_date'].min() + pd.Timedelta(days=days)
    ].copy()

    returned_users_set = set(events_after_threshold['user_id'].unique())
    cohort['returned'] = cohort['user_id'].isin(returned_users_set)

    retention_by_group = cohort.groupby('group').agg({
        'user_id': 'count',
        'returned': 'sum'
    }).reset_index()

    retention_by_group.columns = ['group', 'cohort_size', 'returned_count']
    retention_by_group['retention_pct'] = (
        100 * retention_by_group['returned_count'] / retention_by_group['cohort_size']
    )

    return retention_by_group
# ============================================================================
# STEP 5: Main Execution
# ============================================================================

def main():
    print("=" * 80)
    print("SYNTHETIC DATA GENERATION: AI Chat Retention Analysis")
    print("=" * 80)
    print()
    
    # Step 1: Create users
    print("Step 1: Creating user base...")
    users = create_users(N_USERS, TREATMENT_SPLIT)
    print(f"  ✓ Created {len(users):,} users")
    print(f"  ✓ Control group: {len(users[users['group'] == 'control']):,}")
    print(f"  ✓ Treatment group: {len(users[users['group'] == 'treatment']):,}")
    print()
    
    # Step 2: Get baseline retention curve
    print("Step 2: Computing baseline retention curve...")
    baseline_retention = get_baseline_retention_curve(TEST_DURATION_DAYS)
    print(f"  ✓ Day 1 retention (baseline): {baseline_retention[1]*100:.1f}%")
    print(f"  ✓ Day 7 retention (baseline): {baseline_retention[7]*100:.1f}%")
    print(f"  ✓ Day 30 retention (baseline): {baseline_retention[30]*100:.1f}%")
    print()
    
    # Step 3: Generate login events
    print("Step 3: Generating login events...")
    events = generate_login_events(
        users, 
        baseline_retention, 
        AI_CHAT_LIFT, 
        TEST_DURATION_DAYS
    )
    print(f"  ✓ Generated {len(events):,} login events")
    print(f"  ✓ Users with activity: {events['user_id'].nunique():,}")
    print(f"  ✓ Events per active user (avg): {len(events) / events['user_id'].nunique():.1f}")
    print()
    
    # Step 4: Calculate retention metrics
    print("Step 4: Calculating retention metrics...")
    
    l7_results = calculate_retention_metrics(events, users, days=7)
    print("\n  L7 Retention (7-day):")
    for _, row in l7_results.iterrows():
        print(f"    {row['group'].capitalize():12s}: {row['retention_pct']:5.2f}% "
              f"({int(row['returned_count']):,} / {int(row['cohort_size']):,})")
    
    l28_results = calculate_retention_metrics(events, users, days=28)
    print("\n  L28 Retention (28-day):")
    for _, row in l28_results.iterrows():
        print(f"    {row['group'].capitalize():12s}: {row['retention_pct']:5.2f}% "
              f"({int(row['returned_count']):,} / {int(row['cohort_size']):,})")
    
    print()
    
    # Step 5: Save to CSV
    print("Step 5: Saving to CSV files...")
    
    # Create output directory if needed
    os.makedirs('data', exist_ok=True)
    
    users.to_csv('data/user_cohorts.csv', index=False)
    print(f"  ✓ Saved: data/user_cohorts.csv ({len(users):,} rows)")
    
    events.to_csv('data/user_events_raw.csv', index=False)
    print(f"  ✓ Saved: data/user_events_raw.csv ({len(events):,} rows)")
    
    # Also save retention results
    l7_results.to_csv('data/l7_retention_results.csv', index=False)
    l28_results.to_csv('data/l28_retention_results.csv', index=False)
    print(f"  ✓ Saved: data/l7_retention_results.csv")
    print(f"  ✓ Saved: data/l28_retention_results.csv")
    print()
    
    print("=" * 80)
    print("DONE! Data generation complete.")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Load these CSV files into PostgreSQL")
    print("2. Run SQL aggregations to verify retention calculations")
    print("3. Use scipy.stats to test statistical significance (p-value)")
    print("4. Create Tableau dashboard with results")
    print()

if __name__ == '__main__':
    main()