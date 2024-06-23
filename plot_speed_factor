# Below is the code you could consider to add to the main.py

# Step 4: Plot Speed Factors with Durations
def plot_speed_factors_with_durations(speed_factors, default_durations, target_durations, min_speed_factor):
    fig, ax1 = plt.subplots(figsize=(12, 8))

    ax1.set_xlabel('Segment Index')
    ax1.set_ylabel('Speed Factor', color='tab:blue')
    ax1.bar(range(len(speed_factors)), speed_factors, color='blue', alpha=0.6, label='Speed Factor')
    ax1.axhline(y=min_speed_factor, color='red', linestyle='--', label='Minimum Speed Factor')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Duration (s)', color='tab:green')
    ax2.plot(range(len(default_durations)), default_durations, color='green', marker='o', linestyle='-', label='Default Duration')
    ax2.plot(range(len(target_durations)), target_durations, color='orange', marker='o', linestyle='-', label='Target Duration')
    ax2.tick_params(axis='y', labelcolor='tab:green')

    fig.tight_layout()
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))
    plt.title('Speed Factors and Durations of Each Segment')
    plt.show()

# Set up minimum speed factor if you do not want AI voice to go lower than its default speed
min_speed_factor = 1  # Define minimum speed factor

# Ensure speed factor is not below minimum
if speed_factor < min_speed_factor:
    speed_factor = min_speed_factor
