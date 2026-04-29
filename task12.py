import pandas as pd
import matplotlib.pyplot as plt

# Load CSV results
df = pd.read_csv("results_all.csv")

# Remove extra spaces in column names, if needed
df.columns = df.columns.str.strip()

# Histogram of mean temperatures
plt.figure()
df["mean_temp"].hist(bins=30)
plt.xlabel("Mean temperature (°C)")
plt.ylabel("Number of buildings")
plt.title("Distribution of Mean Temperatures")
plt.savefig("mean_temperature_distribution.png", dpi=300, bbox_inches="tight")
plt.show()

#Histogram of temperature standard deviations 
avg_mean_temp = df["mean_temp"].mean()
avg_std_temp = df["std_temp"].mean()

num_above_18 = (df["pct_above_18"] >= 50).sum()
num_below_15 = (df["pct_below_15"] >= 50).sum()

print("Average mean temperature:", avg_mean_temp)
print("Average temperature standard deviation:", avg_std_temp)
print("Buildings with at least 50% area above 18°C:", num_above_18)
print("Buildings with at least 50% area below 15°C:", num_below_15)