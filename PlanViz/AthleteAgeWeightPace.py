import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd 

# Calculate median pace for each athlete from df_runs
if not df_runs.empty:
    athlete_paces = df_runs.groupby('athlete_id')['pace_min_per_km'].median().reset_index()
    athlete_paces.rename(columns={'pace_min_per_km': 'median_pace_min_per_km'}, inplace=True)

    # Ensure athlete_id columns are of string type for consistent merging
    df_profiles['athlete_id'] = df_profiles['athlete_id'].astype(str)
    athlete_paces['athlete_id'] = athlete_paces['athlete_id'].astype(str)

    # Merge median paces into df_profiles
    df_profiles_with_pace = pd.merge(df_profiles, athlete_paces, on='athlete_id', how='left')
else:
    print("⚠️ No valid runs found to calculate athlete paces. Skipping 3D plot.")
    # Create an empty DataFrame to prevent errors if no runs are found
    df_profiles_with_pace = pd.DataFrame(columns=['age', 'weight', 'median_pace_min_per_km'])

# Now use df_profiles_with_pace for plotting
if not df_profiles_with_pace.empty and 'median_pace_min_per_km' in df_profiles_with_pace.columns:
    fig = plt.figure(figsize=(9,7))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(df_profiles_with_pace['age'], df_profiles_with_pace['weight'], df_profiles_with_pace['median_pace_min_per_km'], c='b', alpha=0.6)
    ax.set_xlabel('Age (years)')
    ax.set_ylabel('Weight (kg)')
    ax.set_zlabel('Pace (min/km)')
    plt.title("Age–Weight–Pace Relationship in Personalized Plans")
    plt.show()
else:
    print("Skipping 3D plot due to insufficient data or missing pace information after merge.")
