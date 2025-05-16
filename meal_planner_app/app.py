import streamlit as st
import pandas as pd
import numpy as np
# Required packages: reportlab, arabic-reshaper, python-bidi
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.pdfmetrics import registerFontFamily
import io
import base64
import arabic_reshaper
from bidi.algorithm import get_display
import os
import urllib.request
from datetime import datetime

# Create fonts directory if it doesn't exist
FONTS_DIR = "fonts"
os.makedirs(FONTS_DIR, exist_ok=True)

# Font paths
REGULAR_FONT = os.path.join(FONTS_DIR, "NotoSansArabic-Regular.ttf")
BOLD_FONT = os.path.join(FONTS_DIR, "NotoSansArabic-Bold.ttf")

def download_font(url, path):
    """Download font if it doesn't exist"""
    if not os.path.exists(path):
        try:
            st.info(f"Downloading font to {path}...")
            urllib.request.urlretrieve(url, path)
            st.success("Font downloaded!")
        except Exception as e:
            st.warning(f"Could not download font: {e}")
            return False
    return True

# Font URLs - These should point to actual font files in a production environment
REGULAR_FONT_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansArabic/NotoSansArabic-Regular.ttf"
BOLD_FONT_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansArabic/NotoSansArabic-Bold.ttf"

def register_fonts():
    """Register Arabic fonts for PDF generation"""
    try:
        download_font(REGULAR_FONT_URL, REGULAR_FONT)
        download_font(BOLD_FONT_URL, BOLD_FONT)
        
        pdfmetrics.registerFont(TTFont('Arabic', REGULAR_FONT))
        pdfmetrics.registerFont(TTFont('ArabicBold', BOLD_FONT))
        registerFontFamily('Arabic', normal='Arabic', bold='ArabicBold')
        return True
    except Exception as e:
        st.warning(f"Could not register Arabic fonts: {e}. Using fallback fonts.")
        # Use fallback fonts
        pdfmetrics.registerFont(TTFont('Arabic', 'Helvetica'))
        pdfmetrics.registerFont(TTFont('ArabicBold', 'Helvetica-Bold'))
        registerFontFamily('Arabic', normal='Arabic', bold='ArabicBold')
        return False

def reshape_arabic(text):
    """Properly reshape Arabic text for display"""
    if not text:
        return ""
    try:
        reshaped_text = arabic_reshaper.reshape(str(text))
        return get_display(reshaped_text)
    except:
        return str(text)  # Fallback if reshaping fails

def calculate_macros(meals_data):
    """Calculate total macros from all meals"""
    total_protein = sum(item.get('protein', 0) for meal in meals_data for item in meal.get('items', []))
    total_carbs = sum(item.get('carbs', 0) for meal in meals_data for item in meal.get('items', []))
    total_fat = sum(item.get('fat', 0) for meal in meals_data for item in meal.get('items', []))
    total_calories = (total_protein * 4) + (total_carbs * 4) + (total_fat * 9)
    return total_protein, total_carbs, total_fat, total_calories

def create_meal_plan_pdf(client_name, total_calories, meals_data):
    """Generate PDF meal plan with a layout matching the provided image"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=20, 
        leftMargin=20, 
        topMargin=20, 
        bottomMargin=20
    )
    
    # Create styles
    arabic_style = ParagraphStyle(
        'ArabicStyle',
        fontName='Arabic',
        fontSize=10,
        alignment=1,  # Center
        textColor=colors.white
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        fontName='ArabicBold',
        fontSize=16,
        alignment=1,  # Center
        textColor=colors.goldenrod
    )
    
    footer_style = ParagraphStyle(
        'FooterStyle',
        fontName='ArabicBold',
        fontSize=10,
        alignment=1,  # Center
        textColor=colors.white
    )
    
    # Calculate macros
    total_protein, total_carbs, total_fat, calculated_calories = calculate_macros(meals_data)
    
    # Start building PDF content
    elements = []
    
    # Add header
    header_text = reshape_arabic(f"النظام الرابع : إجمالي السعرات الحرارية: {total_calories} سعر حراري")
    elements.append(Paragraph(header_text, header_style))
    elements.append(Spacer(1, 15))
    
    # Prepare meal headers in Arabic (right-to-left order)
    meal_headers = [
        reshape_arabic("الوجبة الخامسة"),
        reshape_arabic("الوجبة الرابعة"),
        reshape_arabic("الوجبة الثالثة"),
        reshape_arabic("الوجبة الثانية"),
        reshape_arabic("الوجبة الأولى")
    ]
    
    # Initialize data table with headers
    data = [meal_headers]
    
    # Determine maximum number of items in any meal
    max_items = max(len(meal.get('items', [])) for meal in meals_data)
    
    # Add meal items to the table
    for row_idx in range(max_items):
        row = []
        for meal_idx in range(4, -1, -1):  # Reverse order for Arabic RTL
            if meal_idx < len(meals_data) and row_idx < len(meals_data[meal_idx].get('items', [])):
                item = meals_data[meal_idx]['items'][row_idx]
                food_text = item.get('food_text', '')
                if item.get('amount'):
                    food_text = f"{item.get('amount')} جرام {food_text}"
                row.append(reshape_arabic(food_text))
            else:
                row.append("")
        data.append(row)
    
    # Create the table with equal column widths
    table_width = 555  # A4 width minus margins
    col_widths = [table_width/5] * 5
    table = Table(data, colWidths=col_widths)
    
    # Style the table to match the image
    table_style = TableStyle([
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.goldenrod),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'ArabicBold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        
        # Content styling
        ('FONTNAME', (0, 1), (-1, -1), 'Arabic'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.black),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
        
        # Grid styling
        ('GRID', (0, 0), (-1, -1), 1, colors.goldenrod),
        ('BOX', (0, 0), (-1, -1), 1, colors.goldenrod),
        
        # Row heights - flexible based on content
        ('ROWHEIGHTS', (0, 1), (-1, -1), None),
    ])
    
    table.setStyle(table_style)
    elements.append(table)
    elements.append(Spacer(1, 15))
    
    # Add macros summary
    macros_text = reshape_arabic(f"إجمالي البروتين: {total_protein} غ     إجمالي الكربوهيدرات: {total_carbs} غ     إجمالي الدهون: {total_fat} غ")
    elements.append(Paragraph(macros_text, footer_style))
    
    # Add website URL footer
    elements.append(Spacer(1, 10))
    website_text = reshape_arabic("HTTPS://CAP-SHADOW.NETLIFY.APP/")
    elements.append(Paragraph(website_text, footer_style))
    
    # Build the PDF
    doc.build(elements)
    
    # Get PDF as bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

def get_download_link(pdf_bytes, filename="meal_plan.pdf"):
    """Generate a download link for the PDF"""
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" class="download-btn">تحميل خطة الوجبات (PDF)</a>'
    return href

def main():
    st.set_page_config(page_title="مولد خطة الوجبات", layout="wide")
    
    # Register fonts for PDF generation
    register_fonts()
    
    # Custom CSS for Arabic RTL support and styling
    st.markdown("""
    <style>
        body {
            direction: rtl;
            text-align: right;
            font-family: 'Tajawal', sans-serif;
            background-color: #121212;
            color: white;
        }
        .stTextInput, .stNumberInput, .stSelectbox {
            direction: rtl;
            text-align: right;
        }
        h1, h2, h3 {
            text-align: right;
            color: gold;
        }
        .stButton button {
            background-color: gold;
            color: black;
            font-weight: bold;
        }
        .download-btn {
            background-color: gold;
            color: black;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            display: inline-block;
            margin: 10px 0;
        }
        .stApp {
            background-color: #121212;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("مولد خطة الوجبات الغذائية")
    
    # Basic information section
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            client_name = st.text_input("اسم العميل (اختياري)", key="client_name")
            
        with col2:
            total_calories = st.number_input("إجمالي السعرات الحرارية", min_value=1000, max_value=5000, value=1700, step=100)
    
    # Initialize meal structure
    if 'meals_data' not in st.session_state:
        st.session_state.meals_data = [
            {'name': 'الوجبة الأولى', 'items': []},
            {'name': 'الوجبة الثانية', 'items': []},
            {'name': 'الوجبة الثالثة', 'items': []},
            {'name': 'الوجبة الرابعة', 'items': []},
            {'name': 'الوجبة الخامسة', 'items': []}
        ]
    
    # Dynamic items configuration - specify number of items per meal
    st.subheader("تحديد عدد العناصر في كل وجبة")
    
    meal_cols = st.columns(5)
    
    for i, col in enumerate(meal_cols):
        with col:
            meal_name = st.session_state.meals_data[i]['name']
            current_count = len(st.session_state.meals_data[i]['items'])
            count = st.number_input(f"{meal_name}", min_value=0, max_value=10, value=current_count, key=f"count_{i}")
            
            # Update items count
            if count != current_count:
                if count > current_count:
                    # Add new items
                    for _ in range(count - current_count):
                        st.session_state.meals_data[i]['items'].append({
                            'food_text': '',
                            'amount': 0,
                            'protein': 0,
                            'carbs': 0,
                            'fat': 0
                        })
                elif count < current_count:
                    # Remove excess items
                    st.session_state.meals_data[i]['items'] = st.session_state.meals_data[i]['items'][:count]
    
    # Meal content input section
    st.subheader("إدخال محتويات الوجبات")
    
    # Create tabs for each meal
    tab_names = [meal['name'] for meal in st.session_state.meals_data]
    tabs = st.tabs(tab_names)
    
    for i, tab in enumerate(tabs):
        with tab:
            meal_items = st.session_state.meals_data[i]['items']
            
            if not meal_items:
                st.info(f"لم يتم تحديد أي عناصر للوجبة {tab_names[i]}. الرجاء تحديد عدد العناصر أعلاه.")
                continue
                
            for j, item in enumerate(meal_items):
                st.markdown(f"#### العنصر {j+1}")
                
                # Food description and amount
                cols = st.columns([3, 1])
                with cols[0]:
                    meal_items[j]['food_text'] = st.text_input(
                        "وصف الطعام", 
                        value=item.get('food_text', ''),
                        key=f"food_{i}_{j}"
                    )
                with cols[1]:
                    meal_items[j]['amount'] = st.number_input(
                        "الكمية (جرام)", 
                        value=item.get('amount', 0),
                        min_value=0,
                        key=f"amount_{i}_{j}"
                    )
                
                # Macro nutrients
                macro_cols = st.columns(3)
                with macro_cols[0]:
                    meal_items[j]['protein'] = st.number_input(
                        "بروتين (جرام)", 
                        value=item.get('protein', 0),
                        min_value=0,
                        key=f"protein_{i}_{j}"
                    )
                with macro_cols[1]:
                    meal_items[j]['carbs'] = st.number_input(
                        "كربوهيدرات (جرام)", 
                        value=item.get('carbs', 0),
                        min_value=0,
                        key=f"carbs_{i}_{j}"
                    )
                with macro_cols[2]:
                    meal_items[j]['fat'] = st.number_input(
                        "دهون (جرام)", 
                        value=item.get('fat', 0),
                        min_value=0,
                        key=f"fat_{i}_{j}"
                    )
                
                st.markdown("---")
    
    # Calculate and display macros
    total_protein, total_carbs, total_fat, calculated_calories = calculate_macros(st.session_state.meals_data)
    
    st.subheader("ملخص العناصر الغذائية")
    
    macro_cols = st.columns(4)
    with macro_cols[0]:
        st.metric("إجمالي البروتين (غ)", total_protein)
    with macro_cols[1]:
        st.metric("إجمالي الكربوهيدرات (غ)", total_carbs)
    with macro_cols[2]:
        st.metric("إجمالي الدهون (غ)", total_fat)
    with macro_cols[3]:
        st.metric("إجمالي السعرات المحسوبة", calculated_calories)
    
    # Table preview section
    st.subheader("معاينة جدول الوجبات")
    
    # Create a preview of the meal plan table
    preview_cols = st.columns(5)
    for i, col in enumerate(reversed(preview_cols)):  # Reverse for RTL
        with col:
            st.markdown(f"**{st.session_state.meals_data[4-i]['name']}**")  # Also reverse the index
            for item in st.session_state.meals_data[4-i]['items']:
                food_text = item.get('food_text', '')
                amount = item.get('amount')
                if food_text:
                    if amount:
                        st.write(f"• {amount} جرام {food_text}")
                    else:
                        st.write(f"• {food_text}")
    
    # PDF generation section
    st.markdown("---")
    st.subheader("توليد ملف PDF")
    
    if st.button("إنشاء وتحميل PDF", type="primary"):
        with st.spinner("جاري إنشاء PDF..."):
            pdf_bytes = create_meal_plan_pdf(client_name, total_calories, st.session_state.meals_data)
            st.markdown(get_download_link(pdf_bytes, f"meal_plan_{total_calories}.pdf"), unsafe_allow_html=True)
            st.success("تم إنشاء خطة الوجبات بنجاح! انقر على الرابط أعلاه للتحميل.")

if __name__ == "__main__":
    main() 