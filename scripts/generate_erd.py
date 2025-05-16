import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

def create_box(ax, x, y, width, height, title, attributes):
    # Create the main box
    box = patches.Rectangle((x, y), width, height, 
                          facecolor='#E6E6FF',  
                          edgecolor='black',
                          linewidth=1)
    ax.add_patch(box)
    
   
    ax.plot([x, x + width], [y + height - 0.5, y + height - 0.5], 
            color='black', linewidth=1)
    
   
    ax.text(x + width/2, y + height - 0.25, title,
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=10,
            fontweight='bold')
    
   
    for i, (attr_name, attr_type) in enumerate(attributes):
        y_pos = y + height - 1 - i * 0.4
        if attr_type in ['PK', 'FK']:
            ax.text(x + 0.2, y_pos, f'{attr_name}', fontsize=9)
            ax.text(x + width - 0.3, y_pos, attr_type, fontsize=8, 
                   style='italic', color='#666666')
        else:
            ax.text(x + 0.2, y_pos, f'{attr_name}', fontsize=9)

def create_erd():
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Define boxes data
    countries_data = [
        ('country_id', 'PK'),
        ('country_name', ''),
        ('country_code', 'UK')
    ]
    
    trust_data = [
        ('trust_id', 'PK'),
        ('country_id', 'FK'),
        ('trust_score (0-10)', ''),
        ('response_count', '')
    ]
    
    freedom_data = [
        ('freedom_id', 'PK'),
        ('country_id', 'FK'),
        ('freedom_score (0-60)', ''),
        ('year', '')
    ]
    
    # Create boxes
    create_box(ax, 2, 4, 3, 2.5, 'COUNTRIES', countries_data)
    create_box(ax, 8, 4, 3, 3, 'TRUST_LEVELS', trust_data)
    create_box(ax, 5, 1, 3, 3, 'FREEDOM_SCORES', freedom_data)
    
    # Draw relationships
    # Countries to Trust (1:1)
    ax.plot([5, 8], [5.25, 5.25], color='black', linewidth=1)
    ax.plot([5, 5.2], [5.25, 5.45], color='black', linewidth=1)  # Left side mark
    ax.plot([7.8, 8], [5.25, 5.45], color='black', linewidth=1)  # Right side mark
    
    # Countries to Freedom (1:N)
    ax.plot([3.5, 3.5], [4, 2.5], color='black', linewidth=1)
    ax.plot([3.5, 5], [2.5, 2.5], color='black', linewidth=1)
    ax.plot([3.3, 3.5], [4, 3.8], color='black', linewidth=1)  # Top mark
    # Crow's foot notation
    ax.plot([4.8, 5], [2.3, 2.5], color='black', linewidth=1)
    ax.plot([4.8, 5], [2.7, 2.5], color='black', linewidth=1)
    ax.plot([4.6, 5], [2.5, 2.5], color='black', linewidth=1)
    
    # Set limits and aspect
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_aspect('equal')
    
    # Remove axes
    ax.axis('off')
    
    # Add title
    plt.title('EU Trust & Freedom Database - Entity Relationship Diagram', 
              pad=20, fontsize=12)
    
    # Save the diagram
    output_dir = Path(__file__).parent.parent / 'static' / 'diagrams'
    output_dir.mkdir(exist_ok=True)
    plt.savefig(output_dir / 'database_erd.png',
                bbox_inches='tight',
                dpi=300,
                facecolor='white')
    plt.close()

if __name__ == '__main__':
    create_erd() 