import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def generate_pdf(snapshots, statistics_data, file_name):
    with PdfPages(file_name) as pdf:
        images_per_row = 1
        images_per_column = 2

        num_snapshots = len(snapshots)
        total_pages = (num_snapshots // (images_per_row * images_per_column)) + 1

        for page in range(total_pages):
            fig, axs = plt.subplots(images_per_column, images_per_row, figsize=(13, 13))
            axs = axs.flatten()

            plt.subplots_adjust(top=0.6, bottom=0.1, left=0.1, right=0.9, hspace=0.5, wspace=0.3)
            if page == 0:
                plt.figtext(0.5, 0.95, 'Snapshot Collection', fontsize=24, ha='center', va='center', fontweight='bold')

            for i in range(images_per_row * images_per_column):
                index = page * images_per_column * images_per_row + i
                if index < num_snapshots:
                    image = plt.imread(snapshots[index])
                    axs[i].imshow(image)
                    axs[i].axis('off')
                    axs[i].set_title(f'Snapshot {index + 1}', fontsize=12)

                    # Add statistics as a table below the snapshot ( this still needs updates)
                    stats = statistics_data[index]
                    stats_text = (f"Mean: {stats['mean']:.2f}\n"
                                  f"Std: {stats['std']:.2f}\n"
                                  f"Min: {stats['min']:.2f}\n"
                                  f"Max: {stats['max']:.2f}\n"
                                  f"Duration: {stats['duration']} points")
                    plt.figtext(0.5, 0.05, stats_text, fontsize=10, ha='center', va='center')
                else:
                    axs[i].axis('off')

            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)
