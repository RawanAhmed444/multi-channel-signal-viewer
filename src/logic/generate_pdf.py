import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from logic.calculate_stats import calculate_statistics  # Make sure to import this correctly

def generate_pdf(snapshots, statistics_data, file_name):
    """Generate a PDF with snapshots and their corresponding statistics."""

    with PdfPages(file_name) as pdf:
        images_per_row = 1
        images_per_column = 2  # Adjust this depending on your layout preference

        num_snapshots = len(snapshots)
        total_pages = (num_snapshots // (images_per_row * images_per_column)) + 1

        for page in range(total_pages):
            # Create a new figure for each set of images
            fig, axs = plt.subplots(images_per_column, images_per_row, figsize=(8, 10))
            axs = axs.flatten()

            # Adjust margins for cleaner layout
            plt.subplots_adjust(top=0.92, bottom=0.1, left=0.1, right=0.9, hspace=0.4)

            # Title for the first page
            if page == 0:
                plt.figtext(0.5, 0.98, 'Snapshot Collection', fontsize=20, ha='center', va='top', fontweight='bold')

            for i in range(images_per_row * images_per_column):
                index = page * images_per_row * images_per_column + i
                if index < num_snapshots:
                    # Plot the image
                    img = plt.imread(snapshots[index])
                    axs[i].imshow(img)
                    axs[i].axis('off')
                    axs[i].set_title(f'Snapshot {index + 1}', fontsize=10)

                    # Create statistics table below each plot
                    stats = statistics_data[index]
                    table_data = [
                        ["Statistic", "Value"],
                        ["Mean", f"{stats['mean']:.2f}"],
                        ["Std Dev", f"{stats['std']:.2f}"],
                        ["Duration", f"{stats['duration']:.2f}"],
                        ["Min", f"{stats['min']:.2f}"],
                        ["Max", f"{stats['max']:.2f}"]
                    ]
                    
                    # Add table below the plot
                    axs[i].table(cellText=table_data, colWidths=[0.2, 0.2], cellLoc='center',
                                 loc='bottom', bbox=[0.0, -0.5, 1, 0.4])  # Adjust position with bbox

                else:
                    axs[i].axis('off')  # Hide any empty subplot areas

            pdf.savefig(fig)
            plt.close(fig)

    print(f"PDF saved as {file_name}")