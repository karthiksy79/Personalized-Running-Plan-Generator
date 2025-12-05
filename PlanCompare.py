import pandas as pd
import numpy as nphat
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

# --- 1️⃣ Load your comparison Excel file ---
file_path = "Add a dataset from this folder corresponding to distance and experience."
df = pd.read_excel(file_path)

print(f"✅ Loaded {file_path} with {len(df)} weeks")

# --- 2️⃣ Auto-detect plans based on the columns ---
# Extract plan names by looking at the part before ' Weekly Mileage (km)' in the column name
plans = sorted({col.split(' Weekly')[0] for col in df.columns if "Weekly Mileage" in col})
print(f"📘 Detected Plans: {plans}")

# --- 3️⃣ Function to compute comparison metrics ---
def compute_metrics(ai_col, ref_col, label):
    merged = df[[ai_col, ref_col]].dropna()
    mae = np.mean(np.abs(merged[ai_col] - merged[ref_col]))
    rmse = np.sqrt(np.mean((merged[ai_col] - merged[ref_col])**2))
    corr, _ = pearsonr(merged[ai_col], merged[ref_col])
    return {"Reference Plan": label, "MAE (km)": round(mae, 2),
            "RMSE (km)": round(rmse, 2), "Correlation (r)": round(corr, 3)}

# --- 4️⃣ Compare "Flag Off" vs others for Weekly Mileage ---
ai_col = "Flag Off Weekly Mileage (km)"
results = []
for plan in plans:
    if plan == "Flag Off":  # Skip self (Flag Off plan)
        continue
    ref_col = f"{plan} Weekly Mileage (km)"

    # Check if the reference column exists in the DataFrame before processing
    if ref_col in df.columns:
        results.append(compute_metrics(ai_col, ref_col, plan))
    else:
        print(f"❌ Column '{ref_col}' not found in DataFrame")

metrics_df = pd.DataFrame(results)
display(metrics_df)

# --- 5️⃣ Visualization: Weekly Mileage Comparison (Flag Off vs all other plans) ---
plt.figure(figsize=(10, 6))
# Plot "Flag Off" plan first
plt.plot(df["Week"], df["Flag Off Weekly Mileage (km)"], marker='o', label="Flag Off", color='black', linewidth=2)

# Plot all other plans
for plan in plans:
    if plan == "Flag Off":  # Skip self (Flag Off plan)
        continue
    plt.plot(df["Week"], df[f"{plan} Weekly Mileage (km)"], marker='o', label=plan)

plt.title("Weekly Mileage Comparison: Flag Off vs Other Plans")
plt.xlabel("Week")
plt.ylabel("Weekly Mileage (km)")
plt.grid(True)
plt.legend()
plt.tight_layout()  # Ensures no overlap in the plot layout
plt.show()  # Ensure the plot displays before moving to the next output

# --- 6️⃣ Visualization: Long Run Progression (Flag Off vs all other plans) ---
plt.figure(figsize=(10, 6))
# Plot "Flag Off" plan first
plt.plot(df["Week"], df["Flag Off Long Run"], marker='s', label="Flag Off", color='black', linewidth=2)

# Plot all other plans
for plan in plans:
    if plan == "Flag Off":  # Skip self (Flag Off plan)
        continue
    plt.plot(df["Week"], df[f"{plan} Long Run"], marker='s', label=plan)

plt.title("Long Run Distance Progression: Flag Off vs Other Plans")
plt.xlabel("Week")
plt.ylabel("Long Run (km)")
plt.grid(True)
plt.legend()
plt.tight_layout()  # Ensure plot doesn't overlap with labels
plt.show()  # Display the plot

# --- 7️⃣ Visualization: Run Frequency (Load Distribution) (Flag Off vs all other plans) ---
plt.figure(figsize=(10, 6))
# Plot "Flag Off" plan first
plt.plot(df["Week"], df["Flag Off Run Count"], marker='^', label="Flag Off", color='black', linewidth=2)

# Plot all other plans
for plan in plans:
    if plan == "Flag Off":  # Skip self (Flag Off plan)
        continue
    plt.plot(df["Week"], df[f"{plan} Run Count"], marker='^', label=plan)

plt.title("Weekly Run Count Comparison: Flag Off vs Other Plans")
plt.xlabel("Week")
plt.ylabel("Run Count")
plt.grid(True)
plt.legend()
plt.tight_layout()  # Adjust layout to avoid overlap
plt.show()  # Display the plot

# --- 8️⃣ Interpret key findings ---
for _, row in metrics_df.iterrows():
    print(f"\n📊 {row['Reference Plan']} vs Flag Off:")
    print(f"→ Mean Absolute Error: {row['MAE (km)']} km")
    print(f"→ RMSE: {row['RMSE (km)']} km")
    print(f"→ Correlation: {row['Correlation (r)']}")
    if row['Correlation (r)'] > 0.8:
        print("✅ Very similar load pattern — well-aligned with reference.")
    elif row['Correlation (r)'] > 0.6:
        print("🟨 Moderately similar — progression trend comparable.")
    else:
        print("❌ Divergent pattern — unique periodization structure.")
