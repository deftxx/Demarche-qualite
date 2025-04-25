import pandas as pd
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def export_as_csv(df):
    """
    Export DataFrame as CSV
    
    Args:
        df (pandas.DataFrame): DataFrame to export
        
    Returns:
        str: CSV data as string
    """
    return df.to_csv(index=False)

def export_as_png(fig):
    """
    Export matplotlib figure as PNG
    
    Args:
        fig (matplotlib.figure.Figure): Figure to export
        
    Returns:
        bytes: PNG data as bytes
    """
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)
    return buf.getvalue()

def export_as_pdf(fig, title="Chart"):
    """
    Export matplotlib figure as PDF
    
    Args:
        fig (matplotlib.figure.Figure): Figure to export
        title (str): Title for the PDF
        
    Returns:
        bytes: PDF data as bytes
    """
    # Save figure to a temporary buffer
    img_buf = BytesIO()
    fig.savefig(img_buf, format='png', dpi=300, bbox_inches='tight')
    img_buf.seek(0)
    
    # Create PDF
    pdf_buf = BytesIO()
    c = canvas.Canvas(pdf_buf, pagesize=letter)
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, title)
    
    # Add timestamp
    import datetime
    now = datetime.datetime.now()
    c.setFont("Helvetica", 10)
    c.drawString(50, 730, f"Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Add image to PDF
    from reportlab.lib.utils import ImageReader
    img = ImageReader(img_buf)
    img_width, img_height = img.getSize()
    
    # Scale to fit on page (letter size is 8.5 x 11 inches or 612 x 792 points)
    max_width = 512  # Leave margins
    max_height = 600  # Leave margins
    
    width_ratio = max_width / img_width
    height_ratio = max_height / img_height
    scale_ratio = min(width_ratio, height_ratio)
    
    new_width = img_width * scale_ratio
    new_height = img_height * scale_ratio
    
    # Center the image on the page
    x_pos = (612 - new_width) / 2
    y_pos = 700 - new_height  # Position below the title
    
    c.drawImage(img, x_pos, y_pos, width=new_width, height=new_height)
    
    # Finalize PDF
    c.showPage()
    c.save()
    
    pdf_buf.seek(0)
    return pdf_buf.getvalue()
