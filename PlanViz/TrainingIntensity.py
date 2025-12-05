import pandas as pd
import matplotlib.pyplot as plt
import re

# Load plan (or use existing plan_df)
plan_df = pd.read_excel("Add the dataset generated after running training logic and export.")

# --- 1 Define intensity zones mapping ---
intensity_map = {
    "Zone 1": ["Easy Run", "Jog", "Warm-Up", "Recovery", "Walk"],
    "Zone 2": ["Long Run", "Time Run"],
    "Zone 3": ["Tempo Run", "Brisk Run"],
    "Zone 4": ["Threshold", "10k Pace", "Repetition"],
    "Zone 5": ["Intervals", "Sprints", "Fast", "Mile Pace", "5k Pace"]
}

# --- Define intervals mapping ---
intervals = {
    5: {"novice":[(400,4),(600,4)],
       "intermediate":[(400,4),(600,4),(600,6)],
       "advanced":[(600,4),(800,4)]},
    10:{"novice":[(400,4),(600,4),(800,4)],
        "intermediate":[(400,4),(600,6),(800,6)],
        "advanced":[(600,4),(800,6),(1000,6)]},
    21:{"novice":[(400,4),(600,4),(800,6)],
        "intermediate":[(400,4),(600,6),(800,8),(1000,6)],
        "advanced":[(400,4),(600,6),(800,8),(1000,10)]},
    42:{"novice":[(400,4),(600,6),(800,8),(1000,8)],
        "intermediate":[(400,4),(600,6),(800,8),(1000,10)],
        "advanced":[(400,4),(600,6),(800,8),(1000,10)]}
}

# --- 3 Function to identify zone from workout description ---
def classify_zone(activity, race_distance, level):
    if pd.isna(activity) or activity == "Rest" or "Strength" in activity:
        return None

    # Regex to extract the interval distance (e.g., 800m, 400m)
    # This will match intervals like "4x800m", "3x1000m", etc.
    interval_match = re.search(r'(\d+)[xX](\d+)\s?[mM]', activity)

    if interval_match:
        reps = int(interval_match.group(1))  # Number of repetitions (e.g., 4 in "4x800m")
        interval_distance = int(interval_match.group(2))  # Interval distance (e.g., 800m)


        # Check if this interval distance matches any of the distances for the given race and level
        for dist, reps_in_plan in intervals[race_distance].get(level, []):
            #print(f"Checking interval: {dist} meters (reps: {reps_in_plan})")
            if dist == interval_distance:  # Match only based on distance
                # If the interval distance is greater than 600m, classify as Zone 5
                if dist > 600:
                    #print(f"Classifying as Zone 5: {dist} meters")
                    return "Zone 5"
                else:
                    #print(f"Classifying as Zone 4: {dist} meters")
                    return "Zone 4"

    for zone, keywords in intensity_map.items():
        if any(k.lower() in activity.lower() for k in keywords):
            return zone

    return "Unclassified"

# --- 4 Melt the plan into one column per workout day ---
plan_melted = plan_df.melt(id_vars=["Week"], var_name="Day", value_name="Workout")

# --- 5 Apply zone classification ---


# Example placeholders for race_distance and level (you would replace this logic with your own)
plan_melted['Race Distance'] = 5  # Placeholder for race distance (e.g., 5k, 10k)
plan_melted['Level'] = 'intermediate'  # Placeholder for training level (e.g., 'novice', 'intermediate', 'advanced')

plan_melted["Zone"] = plan_melted.apply(lambda row: classify_zone(row["Workout"], row["Race Distance"], row["Level"]), axis=1)

# --- 6 Filter out Rest/ST ---
plan_melted = plan_melted.dropna(subset=["Zone"])

# --- 7 Calculate overall zone distribution ---
zone_counts = plan_melted["Zone"].value_counts().sort_index()

# --- 8 Display summary ---
print(zone_counts)

# --- 9 Pie Chart for Zone Distribution ---
zone_percent = zone_counts / zone_counts.sum() * 100  # Calculate percentage distribution
plt.figure(figsize=(7,7))
plt.pie(zone_percent, labels=zone_percent.index, autopct='%1.1f%%', startangle=140)
plt.title("Training Intensity Distribution (Polarization Model)")
plt.show()
