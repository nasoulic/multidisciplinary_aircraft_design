import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def generate_spider_plot(csv_file_path):
    # Read data from the CSV file
    try:
        data = pd.read_csv(csv_file_path, header=None, names=['Category', 'Value'])
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found.")
        return

    # Ensure that the 'Category' column is of type string
    data['Category'] = data['Category'].astype(str)

    # Number of data points (categories)
    num_categories = len(data)

    # Create a list of category names and corresponding values
    categories = data['Category'].tolist()
    values = data['Value'].tolist()

    # Calculate the angle at which each category will be located on the plot
    angles = np.linspace(0, 2 * np.pi, num_categories, endpoint=False).tolist()

    # Close the loop by repeating the first angle and value
    angles += angles[:1]
    values += values[:1]

    # Number of categories
    num_categories = len(categories)

    # Plot the data
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)

    # Plot the values
    ax.fill(angles, values, 'b', alpha=0.1)
    ax.set_yticklabels([])  # Hide radial labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12)

    # Set the title
    plt.title('Annual Operating Costs', size=16, y=1.1)

    # Display the plot
    plt.savefig(csv_file_path.replace(".csv", ".png"), dpi = 300)
    plt.close()