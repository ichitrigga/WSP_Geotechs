from pathlib import Path
import pandas as pd
import numpy as np

results = []

for file in Path("models").glob("*.csv"):

    df = pd.read_csv(file)

    conditions = [
        (df["AU"] < 0.25) & (df["AG"] < 25),
        (df["AU"] < 0.25) & (df["AG"].between(25, 45, inclusive="left")),
        (df["AU"] < 0.25) & (df["AG"] >= 45),

        (df["AU"].between(0.25, 0.7, inclusive="left")) & (df["AG"] < 25),
        (df["AU"].between(0.25, 0.7, inclusive="left")) & (df["AG"].between(25, 45, inclusive="left")),
        (df["AU"].between(0.25, 0.7, inclusive="left")) & (df["AG"] >= 45),

        (df["AU"] >= 0.7) & (df["AG"] < 25),
        (df["AU"] >= 0.7) & (df["AG"].between(25, 45, inclusive="left")),
        (df["AU"] >= 0.7) & (df["AG"] >= 45),
    ]

    labels = [
        "lau_lag","lau_mag","lau_hag",
        "mau_lag","mau_mag","mau_hag",
        "hau_lag","hau_mag","hau_hag"
    ]

    df["mat_bin"] = np.select(conditions, labels)

    # Sum tonnes by bin
    summary = (
        df.groupby("mat_bin")["TONNES"]
        .sum()
        .reset_index()
    )

    summary["model"] = file.stem

    results.append(summary)

# Combine all models
final = pd.concat(results, ignore_index=True)

# Wide format
pivot = (
    final.pivot_table(
        index="model",
        columns="mat_bin",
        values="TONNES",
        aggfunc="sum",
        fill_value=0
    )
    .reset_index()
)

pivot.to_csv("mat_bin_summary.csv", index=False)

print(pivot)