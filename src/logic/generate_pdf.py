import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from io import BytesIO
from PIL import Image  
from logic.calculate_stats import calculate_statistics  

def generate_pdf(snapshots, statistics_data, file_name):
    
    with PdfPages(file_name) as pdf:
        images_per_row = 1
        images_per_column = 2 

        num_snapshots = len(snapshots)
        total_pages = (num_snapshots // (images_per_row * images_per_column)) + 1

        for page in range(total_pages):
            fig, axs = plt.subplots(images_per_column, images_per_row, figsize=(8, 10))
            axs = axs.flatten()
            plt.subplots_adjust(top=0.88, bottom=0.12, left=0.1, right=0.9, hspace=0.25)

            if page == 0:
                plt.figtext(0.5, 0.95, 'Snapshot Collection', fontsize=20, ha='center', va='top', fontweight='bold')

            for i in range(images_per_row * images_per_column):
                index = page * images_per_row * images_per_column + i
                if index < num_snapshots:
                    # Convert the snapshot buffer to an image
                    img_buffer = snapshots[index]
                    img = Image.open(img_buffer)
                    axs[i].imshow(img)
                    axs[i].axis('off')
                    axs[i].set_title(f'Snapshot {index + 1}', fontsize=10)

                    print(f"Snapshot {index + 1} statistics: {statistics_data[index]}")

                    # Create statistics table below each plot
                    stats = statistics_data[index]
                    table_data = [
                        ["Statistic", "Value"],
                        ["Mean", f"{stats['mean']:.6f}"],
                        ["Std Dev", f"{stats['std']:.6f}"],
                        ["Min", f"{stats['min']:.6f}"],
                        ["Max", f"{stats['max']:.6f}"]
                    ]
                    
                    axs[i].table(cellText=table_data, colWidths=[0.2, 0.2], cellLoc='center',
                                 loc='bottom', bbox=[0.0, -0.35, 1, 0.3]) 
                else:
                    axs[i].axis('off')  # Hide any empty subplot areas

            pdf.savefig(fig)
            plt.close(fig)


    print(f"PDF saved as {file_name}")
