# **Personalized Running Plan Generator** 🏃‍♂️📈

*A data-driven system for generating adaptive training plans using Strava activity profiles, domain rules, and personalized pace adjustments.*

---

## **✨ Project Overview**

This project builds an **adaptive running training plan generator** for distances:

* **5K**
* **10K**
* **HM (21.1 km)**
* **Marathon (42.2 km)**

Unlike traditional one-size-fits-all plans, this system uses:

#### ✔ Real-world runner data (via Strava API)

#### ✔ Baseline athlete matching (age + weight similarity)

#### ✔ Personalized pace adjustment equation

#### ✔ Experience-aware distances (novice/intermediate/advanced)

#### ✔ Progressive overload, deload weeks, and tapering

#### ✔ Exportable weekly schedule in Excel

#### ✔ Scientific comparisons against established plans

---

## **🧠 Core Methodology**

### **1️⃣ Strava Data Fetch & Preprocessing**

User-authorized Strava activities are fetched, filtered, and cleaned.
Only *valid running workouts* are used.

### **2️⃣ Baseline Athlete Mapping**

The system chooses the most physiologically similar athlete using:

```
score = |w_athlete – w_user| + 0.5 × |age_athlete – age_user|
```

### **3️⃣ Personalized Pace Adjustment**

```
adjusted_pace = baseline_pace × (1 + 0.005 × age_gap) × (1 + 0.003 × weight_gap)
```

Pace is then clamped based on fitness level (novice/intermediate/advanced).

### **4️⃣ Training Plan Generation**

Plans include:

* Easy runs
* Tempo runs with capped progression
* Distance-appropriate intervals (400, 600, 800, 1000 m)
* Long runs (with progression, deloads, tapering)
* Time-based endurance runs
* Strength training modules
* Back-to-back long-run weekends for 21K/42K

### **5️⃣ Export to Excel**

Files are automatically named:

```
training_plan_<distance>k_<level>.xlsx
```

---

## **📊 Visualization & Analytics (PlanViz Folder)**

The **PlanViz** folder includes tools to evaluate and compare training plans.

### Includes:

### 🔸 Weekly Mileage Comparison:

Weekly mileage comparison performed against multiple training plans avalaible on the internet. These popular plans are followed by athletes all over the world and are generic in nature.  

### Following examples are for a 10K-Novice Runner labelled as **GTP**:

#### Weekly Mileage Comparison
<img width="1000" height="600" alt="10knov_VizWM" src="https://github.com/user-attachments/assets/d67f3e2f-339a-4af9-968c-fe69709882b4" />

### 🔸 Long Run Comparison:

The long runs for every week are compared against the training plan generated. The long runs are generally done during the weekend and are progressive in nature. They finally taper in the final few weeks of training.

#### Long Run Comparison
<img width="1000" height="600" alt="10knov_VizLR" src="https://github.com/user-attachments/assets/9b8b5b34-2e53-491e-9347-22a953104cb1" />

### 🔸 Run Count:

Run count shows us the number of training days every week. They help us understand the frequency of runs performed weekly.

#### Run Count Comparison
<img width="1000" height="600" alt="10knov_VizRC" src="https://github.com/user-attachments/assets/4dc8def3-5b40-4d41-ac1d-05d3d95a1e9b" />

### 🔸 Intensity Zone Analysis

Using 5 standard training zones:

* Zone 1: Slow endurance
* Zone 2: Extensive endurance (time runs, long runs)
* Zone 3: Tempo / brisk
* Zone 4: Threshold / Intervals (400–600 m)
* Zone 5: High intensity (800–1000 m intervals)

![5kadv_Zones](https://github.com/user-attachments/assets/b5ad1241-79e4-43f3-a2a7-eb7394fbbd52)


### 🔸 Athlete Clustering

A 3D graph showing how age, weight, and pace interact.

### 🔸 Research-backed Comparisons

Notebook includes comparisons against:

* Seiler's polarized 80/20 research
* Knopp et al. long-run structure
* Haugen et al. elite training analysis
* Personalized recommendation systems literature

---

## ** How to Use This Project**

### **Step 1 — Run OAuth Notebook**

Located in:
`Notebooks`

Download the files in the notebooks folder. Files are named according to their run order. They can be run in Google Colab or on the machine locally.

### **Step 2 — Generate Training Plan**

Open:
`Notebooks/05.TrainingLogic.py`

You will be prompted for:

* Distance (5, 10, 21, 42)
* Fitness level
* Age & weight
* Available run days
* Strength training structure

### **Step 3 — Export the Plan**

The training plan will be exported automatically and named based on the distance and experience.

### **Step 4 — Compare & Visualize**

Open any notebook in the `PlanViz/` folder and run it.
Plans for comparison are available in the folder. It contains the consolidated information of plans which includes their weekly mileage and number of running days.


---

## **🛡 Security & Privacy**

This repository **never includes**:

* OAuth tokens
* User ages, weights
* Raw Strava data

---

## **🤝 Contributing**

Pull requests and ideas are welcome!

---

## **📜 License**

MIT License.

---


