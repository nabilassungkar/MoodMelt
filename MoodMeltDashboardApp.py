import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from fpdf import FPDF # Library for PDF generation in Python

# --- Define the vibrant fruit-themed color palette ---
colors = {
    'darkPink': '#E91E63', # Strawberry
    'yellow': '#FFEB3B',   # Lemon
    'green': '#8BC34A',    # Lime
    'orange': '#FF9800',   # Orange
    'blue': '#2196F3',     # Blueberry
    'lightYellow': '#FFFDE7', # Creamy base
    'lightGreen': '#DCEDC8',  # Soft green accent
    'lightPink': '#F8BBD0',   # Lighter pink accent
}

# --- Global Styling for Streamlit App ---
st.set_page_config(layout="wide", page_title="MoodMelt Dashboard")

# Glitter/sparkle effect (using radial gradients for visual flair)
# Streamlit doesn't support advanced CSS pseudo-elements directly on its body/container
# So, we'll apply background-image using inline HTML
sparkle_bg = f"""
radial-gradient(circle at 10% 20%, {colors['lightYellow']} 0%, transparent 15%),
radial-gradient(circle at 70% 80%, {colors['lightGreen']} 0%, transparent 10%),
radial-gradient(circle at 30% 90%, {colors['lightPink']} 0%, transparent 12%),
radial-gradient(circle at 80% 10%, {colors['yellow']} 0%, transparent 8%),
radial-gradient(circle at 50% 50%, rgba(255,255,255,0.2) 0%, transparent 100%)
"""

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(https://placehold.co/1920x1080/FFFDE7/FFEB3B?text=Fruit+Glitter+Background);
        background-size: cover;
        background-attachment: fixed;
        font-family: 'Inter', sans-serif;
    }}
    .main .block-container {{
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 24px; /* rounded-3xl approx */
        box-shadow: 0 0 40px rgba(233, 30, 99, 0.6), inset 0 0 20px rgba(255, 235, 59, 0.4);
        border: 4px solid {colors['darkPink']};
        padding: 3rem; /* p-8 approx */
        overflow: hidden; /* Ensure shadow/border are within bounds */
    }}
    h1 {{
        color: {colors['darkPink']};
        text-shadow: 2px 2px 5px {colors['yellow']};
        font-size: 3.5rem; /* text-5xl approx */
        font-weight: 800; /* font-extrabold approx */
        margin-bottom: 1.5rem; /* mb-6 approx */
    }}
    h2 {{
        font-size: 2.25rem; /* text-3xl approx */
        font-weight: 700; /* font-bold approx */
        margin-bottom: 1rem; /* mb-4 approx */
    }}
    h3 {{
        font-size: 1.5rem; /* text-2xl approx */
        font-weight: 600; /* font-semibold approx */
        margin-top: 1.5rem; /* mt-6 approx */
        margin-bottom: 0.75rem; /* mb-3 approx */
    }}
    .stButton>button {{
        background: linear-gradient(45deg, {colors['darkPink']}, {colors['orange']});
        box-shadow: 0 8px 15px rgba(233, 30, 99, 0.4);
        border: 2px solid {colors['yellow']};
        color: white;
        padding: 0.75rem 2rem; /* px-8 py-3 approx */
        border-radius: 9999px; /* rounded-full */
        font-weight: bold;
        font-size: 1.125rem; /* text-lg */
        transition: all 0.3s ease-in-out;
        transform: scale(1);
    }}
    .stButton>button:hover {{
        transform: scale(1.05);
    }}
    .pdf-button>button {{ /* Specific styling for PDF button */
        background: linear-gradient(45deg, {colors['blue']}, {colors['green']}) !important;
        box-shadow: 0 8px 15px rgba(33, 150, 243, 0.4) !important;
        border: 2px solid {colors['yellow']} !important;
    }}

    .stFileUploader > div > button {{
        border: 0;
        background-color: {colors['lightPink']};
        color: {colors['darkPink']};
        font-weight: 600;
    }}
    .stFileUploader > div > button:hover {{
        background-color: {colors['lightPink']}CC; /* slightly darker pink */
    }}
    .stFileUploader > div > input[type="file"] {{
        border: 2px solid {colors['yellow']};
        border-radius: 0.75rem; /* rounded-xl */
        padding: 1rem;
        background-color: rgba(255, 255, 255, 0.7);
        color: #4A4A4A;
        font-size: 1rem;
    }}
    .stFileUploader {{
        border: 2px solid {colors['yellow']};
        border-radius: 0.75rem;
        padding: 1rem;
        background-color: rgba(255, 255, 255, 0.7);
    }}

    /* Decorative sparkle background for the main content area */
    .stApp::before {{
        content: "";
        position: absolute;
        inset: 0;
        z-index: 0;
        pointer-events: none;
        background: {sparkle_bg};
        opacity: 0.7;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Helper Functions ---

# Helper function to normalize column names more robustly
def normalize_column_name(name):
    return name.strip().lower().replace(' ', '').replace('-', '').replace('_', '')

# Function to process the CSV data
@st.cache_data # Add caching to speed up data processing
def process_csv(df):
    if df.empty:
        st.warning("CSV file is empty or contains only headers.")
        return pd.DataFrame()

    # Normalize headers
    normalized_headers = [normalize_column_name(col) for col in df.columns]
    df.columns = normalized_headers

    # Define the expected normalized column names
    expected_columns = ['date', 'platform', 'sentiment', 'location', 'engagements', 'mediatype']

    # Ensure all expected columns exist, fill with None or default if not
    for col in expected_columns:
        if col not in df.columns:
            # st.warning(f"Missing expected column: '{col}'. Filling with default values.") # Removed warning for cleaner logs
            df[col] = None

    processed_data = []
    for index, row in df.iterrows():
        new_row = {}
        for col in expected_columns:
            value = row.get(col) # Use .get() to safely access column values

            if col == 'date':
                new_row[col] = pd.to_datetime(value, errors='coerce') if pd.notna(value) else None
            elif col == 'engagements':
                new_row[col] = pd.to_numeric(value, errors='coerce').fillna(0).astype(int) if pd.notna(value) else 0
            else:
                new_row[col] = str(value).strip() if pd.notna(value) else 'Unknown'

        # Special handling for 'mediatype' if it ends up as 'Unknown'
        if new_row.get('mediatype') == 'Unknown':
             new_row['mediatype'] = 'Unknown Media Type'

        processed_data.append(new_row)

    return pd.DataFrame(processed_data)

# --- Chart Generation Functions ---

def create_sentiment_pie_chart(df):
    sentiment_counts = df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    fig = px.pie(sentiment_counts,
                 values='Count',
                 names='Sentiment',
                 title='Sentiment Breakdown: How\'s the Vibe? 💖',
                 color='Sentiment',
                 color_discrete_map={
                     'Positive': colors['green'],
                     'Neutral': colors['yellow'],
                     'Negative': colors['darkPink'],
                     'Unknown': colors['blue']
                 })
    fig.update_layout(title_font_color=colors['darkPink'], title_font_size=24, title_font_family='Inter, sans-serif')
    fig.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_color='#FFF', textfont_size=16, pull=[0.05, 0, 0.05, 0])
    return fig

def get_sentiment_insights(df):
    sentiment_counts = df['sentiment'].value_counts()
    total = len(df)
    if total == 0: return ['No sentiment data to analyze.']

    sorted_sentiments = sentiment_counts.sort_values(ascending=False)

    insights = []
    if not sorted_sentiments.empty:
        most_common_sentiment = sorted_sentiments.index[0]
        most_common_percent = (sorted_sentiments.iloc[0] / total * 100)
        insights.append(f"**1.** Looks like a good vibe! `{most_common_sentiment}` is the most common sentiment, making up about **{most_common_percent:.1f}%** of the buzz.")

        if len(sorted_sentiments) > 1:
            least_common_sentiment = sorted_sentiments.index[-1]
            least_common_percent = (sorted_sentiments.iloc[-1] / total * 100)
            insights.append(f"**2.** Keep an eye on `{least_common_sentiment}` sentiment, as it's the least frequent, representing only **{least_common_percent:.1f}%**.")
        else:
            insights.append("**2.** Only one sentiment category found. Consider diversifying content to get varied reactions.")

        insights.append("**3.** The spread of sentiments gives you a snapshot of overall perception. Are you seeing more positive apples or sour lemons?")
    else:
        insights.append("No sentiment data available for insights.")
    return insights

def create_engagement_line_chart(df):
    # Ensure 'date' column is datetime and drop rows where it's NaT
    df_clean = df.dropna(subset=['date']).copy()
    df_clean['date'] = pd.to_datetime(df_clean['date'])
    df_clean = df_clean.sort_values('date')
    engagements_by_date = df_clean.groupby(df_clean['date'].dt.date)['engagements'].sum().reset_index()
    engagements_by_date.columns = ['Date', 'Total Engagements']

    fig = px.line(engagements_by_date,
                  x='Date',
                  y='Total Engagements',
                  title='Engagement Trend: Riding the Wave! 🌊',
                  markers=True)
    fig.update_traces(marker_color=colors['blue'], marker_size=8, line_color=colors['blue'], line_width=3)
    fig.update_layout(title_font_color=colors['orange'], title_font_size=24, title_font_family='Inter, sans-serif',
                      xaxis_title_font_color='#4A4A4A', yaxis_title_font_color='#4A4A4A',
                      xaxis_gridcolor='#E0E0E0', yaxis_gridcolor='#E0E0E0')
    return fig

def get_engagement_insights(df):
    df_clean = df.dropna(subset=['date']).copy()
    df_clean['date'] = pd.to_datetime(df_clean['date'])
    df_clean = df_clean.sort_values('date')
    engagements_by_date = df_clean.groupby(df_clean['date'].dt.date)['engagements'].sum()

    if engagements_by_date.empty: return ['No engagement data to analyze.']

    max_engagements = engagements_by_date.max()
    min_engagements = engagements_by_date.min()
    max_date = engagements_by_date.idxmax()
    min_date = engagements_by_date.idxmin()
    total_engagements = engagements_by_date.sum()
    average_engagements = total_engagements / len(engagements_by_date)

    insights = [
        f"**1.** Wow! Your peak engagement happened on **{max_date}** with a juicy **{max_engagements}** engagements! What fresh content did you share then?",
        f"**2.** Keep an eye on **{min_date}**, which saw the lowest engagements at **{min_engagements}**. Time to sprinkle some new ideas?",
        f"**3.** On average, you're gathering about **{average_engagements:.0f}** engagements daily. Consistent growth is key, like a ripening fruit!"
    ]
    return insights

def create_platform_bar_chart(df):
    platform_engagements = df.groupby('platform')['engagements'].sum().reset_index()
    platform_engagements = platform_engagements.sort_values('engagements', ascending=False)
    fig = px.bar(platform_engagements,
                 x='platform',
                 y='engagements',
                 title='Platform Power: Where\'s the Buzz Juiciest? 🚀',
                 color='platform',
                 color_discrete_sequence=[colors['yellow'], colors['darkPink'], colors['green'], colors['orange'], colors['blue']])
    fig.update_layout(title_font_color=colors['blue'], title_font_size=24, title_font_family='Inter, sans-serif',
                      xaxis_title_font_color='#4A4A4A', yaxis_title_font_color='#4A4A4A')
    return fig

def get_platform_insights(df):
    platform_engagements = df.groupby('platform')['engagements'].sum()
    if platform_engagements.empty: return ['No platform engagement data to analyze.']

    sorted_platforms = platform_engagements.sort_values(ascending=False)

    insights = [
        f"**1.** `{sorted_platforms.index[0]}` is your superstar platform, raking in a whopping **{sorted_platforms.iloc[0]}** engagements! Keep that content flowing there!",
        f"**2.** Time to sprinkle some love on `{sorted_platforms.index[-1]}`, which currently has the fewest engagements at **{sorted_platforms.iloc[-1]}**. Can you grow it like a new sprout?",
        "**3.** Observe the engagement spread across platforms. Are certain platforms serving up specific types of interactions better than others?"
    ]
    return insights

def create_media_type_pie_chart(df):
    media_type_counts = df['mediatype'].value_counts().reset_index()
    media_type_counts.columns = ['MediaType', 'Count']
    fig = px.pie(media_type_counts,
                 values='Count',
                 names='MediaType',
                 title='Media Type Mix: What\'s Your Recipe? 🍍',
                 color='MediaType',
                 color_discrete_map={
                     'Image': colors['orange'],
                     'Text': colors['darkPink'],
                     'Video': colors['green'],
                     'Unknown Media Type': colors['yellow']
                 })
    fig.update_layout(title_font_color=colors['green'], title_font_size=24, title_font_family='Inter, sans-serif')
    fig.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_color='#FFF', textfont_size=16, pull=[0.05, 0.05, 0, 0])
    return fig

def get_media_type_insights(df):
    media_type_counts = df['mediatype'].value_counts()
    total = len(df)
    if total == 0: return ['No media type data to analyze.']

    sorted_media_types = media_type_counts.sort_values(ascending=False)

    insights = [
        f"**1.** Your content recipe is heavy on `{sorted_media_types.index[0]}`, making up about **{(sorted_media_types.iloc[0] / total * 100):.1f}%**! It's clearly a crowd-pleaser.",
        f"**2.** Perhaps try adding more `{sorted_media_types.index[-1]}` to your mix, as it's currently the least used type at **{(sorted_media_types.iloc[-1] / total * 100):.1f}%**.",
        "**3.** Understanding your media mix helps optimize your content strategy. Are you using the right fruits for the right occasion?"
    ]
    return insights

def create_location_bar_chart(df):
    location_counts = df['location'].value_counts().reset_index()
    location_counts.columns = ['Location', 'Count']
    location_counts = location_counts.sort_values('Count', ascending=False).head(5) # Top 5
    fig = px.bar(location_counts,
                 x='Location',
                 y='Count',
                 title='Top 5 Locations: Where Are Your Fans Blooming? 🌍',
                 color='Location',
                 color_discrete_sequence=[colors['blue'], colors['orange'], colors['darkPink'], colors['yellow'], colors['green']])
    fig.update_layout(title_font_color=colors['yellow'], title_font_size=24, title_font_family='Inter, sans-serif',
                      xaxis_title_font_color='#4A4A4A', yaxis_title_font_color='#4A4A4A')
    return fig

def get_location_insights(df):
    location_counts = df['location'].value_counts()
    if location_counts.empty: return ['No location data to analyze.']

    sorted_locations = location_counts.sort_values(ascending=False)

    insights = [
        f"**1.** Your biggest fan base is in `{sorted_locations.index[0]}`, with a huge **{sorted_locations.iloc[0]}** mentions! Time for a virtual fruit-picking party there!",
        f"**2.** Consider nurturing connections in `{sorted_locations.index[-1]}` (among the top 5), which has **{sorted_locations.iloc[-1]}** mentions.",
        "**3.** Knowing your top locations helps target your content like a perfectly aimed seed. Where can you make the most impact?"
    ]
    return insights

# --- Overall Business Recommendations & Actionable Steps ---
def get_overall_recommendations(df):
    recommendations = []

    if df.empty:
        return ['Upload your CSV file to get some juicy business recommendations!']

    # 1. Analyze Sentiment for overarching recommendation
    sentiment_counts = df['sentiment'].value_counts()
    total_sentiment_entries = len(df)
    positive_count = sentiment_counts.get('Positive', 0)
    negative_count = sentiment_counts.get('Negative', 0)
    neutral_count = sentiment_counts.get('Neutral', 0)

    if positive_count > negative_count and positive_count > neutral_count:
        recommendations.append('Overall, your **audience is loving your content!** Keep doing what you\'re doing and explore ways to amplify your most successful messages.')
    elif negative_count > positive_count and negative_count > neutral_count:
        recommendations.append('There\'s a significant amount of **negative sentiment**. It\'s crucial to investigate the root causes and address concerns directly to improve brand perception.')
    elif neutral_count > positive_count and neutral_count > negative_count:
        recommendations.append('A lot of **neutral sentiment** suggests your content might not be sparking strong reactions. Experiment with bolder messaging or more engaging formats to drive stronger opinions.')
    elif total_sentiment_entries > 0: # If there's data but no clear majority
        recommendations.append('Sentiment is a mixed bag. Focus on understanding specific comments in each category to find actionable opportunities for improvement or replication of success.')
    else:
        recommendations.append('No clear sentiment data available to draw strong conclusions.')


    # 2. Analyze Engagement Trend for overarching recommendation
    df_clean = df.dropna(subset=['date']).copy()
    df_clean['date'] = pd.to_datetime(df_clean['date'])
    df_clean = df_clean.sort_values('date')
    engagements_by_date = df_clean.groupby(df_clean['date'].dt.date)['engagements'].sum()

    if len(engagements_by_date) > 1:
        first_eng = engagements_by_date.iloc[0]
        last_eng = engagements_by_date.iloc[-1]
        total_engagements = engagements_by_date.sum()

        if total_engagements > 0:
            if last_eng > first_eng * 1.1: # More than 10% growth
                recommendations.append(f"Your **engagement is on a fantastic upward trajectory**! Double down on the strategies that are driving this growth, and consider investing more in these areas.")
            elif last_eng < first_eng * 0.9: # More than 10% drop
                recommendations.append(f"**Engagement is declining**. It's time for a thorough content audit. Analyze what might have changed and what resonated previously to re-engage your audience.")
            else:
                 recommendations.append(f"**Stable engagement** indicates a consistent audience. To drive further growth, explore new content pillars, target audiences, or platforms.")
        else:
            recommendations.append('Engagement data is available but shows no clear trend yet. Continue monitoring daily engagements for patterns.')
    elif len(engagements_by_date) > 0:
        recommendations.append('Limited engagement data available. Upload more dates to observe trends and get more precise recommendations.')
    else:
        recommendations.append('No engagement data found for trend analysis.')


    # 3. Analyze Top Platform for actionable advice
    platform_engagements = df.groupby('platform')['engagements'].sum()
    sorted_platforms = platform_engagements.sort_values(ascending=False)

    if not sorted_platforms.empty and sorted_platforms.index[0] != 'Unknown' and sorted_platforms.iloc[0] > 0:
        recommendations.append(f"**Focus on {sorted_platforms.index[0]}**, your highest-performing platform. Allocate more resources here for maximum impact, but also consider diversifying slowly.")
    elif not sorted_platforms.empty and sorted_platforms.index[0] == 'Unknown':
        recommendations.append('Platform data is missing for some entries. Ensure "Platform" column is correctly filled in your CSV for better insights.')
    else:
        recommendations.append('No platform data found. Please ensure your CSV includes a "Platform" column to identify key channels.')


    # 4. Analyze Top Media Type for actionable advice
    media_type_counts = df['mediatype'].value_counts()
    sorted_media_types = media_type_counts.sort_values(ascending=False)

    if not sorted_media_types.empty and sorted_media_types.index[0] != 'Unknown Media Type' and sorted_media_types.iloc[0] > 0:
        recommendations.append(f"Your **{sorted_media_types.index[0]}** content is a hit! Create more content in this format, and consider repurposing existing popular content into this media type.")
    elif not sorted_media_types.empty and sorted_media_types.index[0] == 'Unknown Media Type':
        recommendations.append('Media Type data is missing for some entries. Fill out the "Media Type" column in your CSV for clearer content insights.')
    else:
        recommendations.append('No media type data found. Please ensure your CSV includes a "Media Type" column to understand content preferences.')


    # 5. Analyze Top Location for actionable advice
    location_counts = df['location'].value_counts()
    sorted_locations = location_counts.sort_values(ascending=False)

    if not sorted_locations.empty and sorted_locations.index[0] != 'Unknown' and sorted_locations.iloc[0] > 0:
        recommendations.append(f"**Target {sorted_locations.index[0]}** with localized campaigns or content. This region is a hot spot for your audience!")
    elif not sorted_locations.empty and sorted_locations.index[0] == 'Unknown':
        recommendations.append('Location data is missing for some entries. Ensure the "Location" column is populated in your CSV to understand geographic reach.')
    else:
        recommendations.append('No location data found. Please ensure your CSV includes a "Location" column to identify where your audience is blooming.')


    return recommendations if recommendations else ['No specific recommendations can be generated yet. Upload your CSV file with complete data to get started!']

# --- PDF Generation Function for Streamlit ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'MoodMelt\'s Media Intelligence Dashboard Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def chapter_title(self, title, color_hex):
        self.set_fill_color(*tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)))
        self.set_text_color(255, 255, 255) # White text for title background
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(4)
        self.set_text_color(0, 0, 0) # Black text for body

    def chapter_body(self, body_text):
        self.set_font('Arial', '', 12)
        # Process markdown bold for PDF
        body_text_lines = body_text.split('\n')
        for line_raw in body_text_lines:
            line = line_raw.strip()
            if not line: # Skip empty lines
                continue
            if line.startswith('- '): # Handle list items
                line = line[2:] # Remove '- '

            parts = line.split('**')
            for i, part in enumerate(parts):
                if i % 2 == 1: # Odd parts are bold
                    self.set_font('Arial', 'B', 12)
                else:
                    self.set_font('Arial', '', 12)
                self.write(8, part) # Write with 8mm line height
            self.ln(8) # Line height for next line
        self.ln(8) # Extra space after block

@st.cache_data # Cache the PDF generation for speed
def generate_pdf_report(processed_df, sentiment_insights, engagement_insights,
                        platform_insights, media_type_insights, location_insights,
                        overall_recommendations):

    pdf = PDF('P', 'mm', 'A4')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15) # Adjust auto page break margin

    # Add introduction
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 8, "This report provides an in-depth analysis of your media data from MoodMelt's Interactive Dashboard. Dive into sentiment, engagement, platform performance, media type mix, and geographical insights.", align='C')
    pdf.ln(10)

    # 2. Data Clean-Up Crew!
    pdf.chapter_title("2. Data Clean-Up Crew!", colors['green'])
    pdf.chapter_body("We've spruced up your data! Dates are now friendly, missing engagements have been filled with a big fat zero, and all column names are squeaky clean. Ready for the juicy insights!")

    # 3. Sentiment Breakdown
    pdf.chapter_title("3. Sentiment Breakdown: How's the Vibe? 💖", colors['darkPink'])
    pdf.chapter_body("\n".join(sentiment_insights)) # Pass insights as a single string for chapter_body to process

    # 4. Engagement Trend
    pdf.chapter_title("4. Engagement Trend: Riding the Wave! 🌊", colors['orange'])
    pdf.chapter_body("\n".join(engagement_insights))

    # 5. Platform Engagements
    pdf.chapter_title("5. Platform Power: Where's the Buzz Juiciest? 🚀", colors['blue'])
    pdf.chapter_body("\n".join(platform_insights))

    # 6. Media Type Mix
    pdf.chapter_title("6. Media Type Mix: What's Your Recipe? 🍍", colors['green'])
    pdf.chapter_body("\n".join(media_type_insights))

    # 7. Top 5 Locations
    pdf.chapter_title("7. Top 5 Locations: Where Are Your Fans Blooming? 🌍", colors['yellow'])
    pdf.chapter_body("\n".join(location_insights))

    # 8. Overall Business Recommendations
    pdf.chapter_title("8. Overall Business Recommendations: Your Next Steps! 🎯", colors['darkPink'])
    pdf.chapter_body("\n".join(overall_recommendations))


    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# --- Streamlit App Layout ---
st.title("MoodMelt's Interactive Media Intelligence Dashboard! 🍓🍋🍍")
st.write("Ready to slice through your data? Upload your CSV and let's uncover some fruity insights!")

st.markdown(
    f"""
    <div style="
        margin-bottom: 3rem; /* mb-12 */
        padding: 1.5rem; /* p-6 */
        border-radius: 1rem; /* rounded-2xl */
        border: 2px solid {colors['orange']};
        background-color: rgba(255, 255, 255, 0.7);
    ">
        <h2 style="color: {colors['orange']};">1. Your Data Delight!</h2>
        <p style="margin-bottom: 1rem; color: #4A4A4A;">
            Choose your CSV file. Make sure it has these columns:
            <span style="font-weight: bold; color: {colors['darkPink']};">Date, Platform, Sentiment, Location, Engagements, Media Type</span>.
        </p>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("", type=["csv"])

st.markdown("</div>", unsafe_allow_html=True) # Close the div

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    with st.spinner("Processing your juicy data... Please wait! 🍍"): # Added spinner
        processed_df = process_csv(df)

    if not processed_df.empty:
        st.markdown(
            f"""
            <div style="
                margin-bottom: 3rem;
                padding: 1.5rem;
                border-radius: 1rem;
                border: 2px solid {colors['green']};
                background-color: rgba(255, 255, 255, 0.7);
            ">
                <h2 style="color: {colors['green']};">2. Data Clean-Up Crew!</h2>
                <p style="color: #4A4A4A;">
                    We've spruced up your data! Dates are now friendly, missing engagements have been filled with a big fat zero, and all column names are squeaky clean. Ready for the juicy insights!
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Generate and display charts and insights
        # Chart 1: Sentiment Breakdown
        st.markdown(f"""
            <div style="
                margin-bottom: 3rem; padding: 1.5rem; border-radius: 1rem;
                border: 2px solid {colors['darkPink']}; background-color: rgba(255, 255, 255, 0.7);
            ">
                <h2 style="color: {colors['darkPink']};">3. Sentiment Breakdown: How's the Vibe? 💖</h2>
            </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(create_sentiment_pie_chart(processed_df), use_container_width=True)
        st.markdown(f'<h3 style="color: {colors["darkPink"]};">Juicy Insights:</h3>', unsafe_allow_html=True)
        for insight in get_sentiment_insights(processed_df):
            st.markdown(f'- {insight}')
        st.markdown("---") # Separator

        # Chart 2: Engagement Trend
        st.markdown(f"""
            <div style="
                margin-bottom: 3rem; padding: 1.5rem; border-radius: 1rem;
                border: 2px solid {colors['orange']}; background-color: rgba(255, 255, 255, 0.7);
            ">
                <h2 style="color: {colors['orange']};">4. Engagement Trend: Riding the Wave! 🌊</h2>
            </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(create_engagement_line_chart(processed_df), use_container_width=True)
        st.markdown(f'<h3 style="color: {colors["orange"]};">Juicy Insights:</h3>', unsafe_allow_html=True)
        for insight in get_engagement_insights(processed_df):
            st.markdown(f'- {insight}')
        st.markdown("---")

        # Chart 3: Platform Engagements
        st.markdown(f"""
            <div style="
                margin-bottom: 3rem; padding: 1.5rem; border-radius: 1rem;
                border: 2px solid {colors['blue']}; background-color: rgba(255, 255, 255, 0.7);
            ">
                <h2 style="color: {colors['blue']};">5. Platform Power: Where's the Buzz Juiciest? 🚀</h2>
            </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(create_platform_bar_chart(processed_df), use_container_width=True)
        st.markdown(f'<h3 style="color: {colors["blue"]};">Juicy Insights:</h3>', unsafe_allow_html=True)
        for insight in get_platform_insights(processed_df):
            st.markdown(f'- {insight}')
        st.markdown("---")

        # Chart 4: Media Type Mix
        st.markdown(f"""
            <div style="
                margin-bottom: 3rem; padding: 1.5rem; border-radius: 1rem;
                border: 2px solid {colors['green']}; background-color: rgba(255, 255, 255, 0.7);
            ">
                <h2 style="color: {colors['green']};">6. Media Type Mix: What's Your Recipe? 🍍</h2>
            </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(create_media_type_pie_chart(processed_df), use_container_width=True)
        st.markdown(f'<h3 style="color: {colors["green"]};">Juicy Insights:</h3>', unsafe_allow_html=True)
        for insight in get_media_type_insights(processed_df):
            st.markdown(f'- {insight}')
        st.markdown("---")

        # Chart 5: Top 5 Locations
        st.markdown(f"""
            <div style="
                margin-bottom: 3rem; padding: 1.5rem; border-radius: 1rem;
                border: 2px solid {colors['yellow']}; background-color: rgba(255, 255, 255, 0.7);
            ">
                <h2 style="color: {colors['yellow']};">7. Top 5 Locations: Where Are Your Fans Blooming? 🌍</h2>
            </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(create_location_bar_chart(processed_df), use_container_width=True)
        st.markdown(f'<h3 style="color: {colors["yellow"]};">Juicy Insights:</h3>', unsafe_allow_html=True)
        for insight in get_location_insights(processed_df):
            st.markdown(f'- {insight}')
        st.markdown("---")

        # Overall Business Recommendations
        st.markdown(f"""
            <div style="
                margin-bottom: 3rem; padding: 1.5rem; border-radius: 1rem;
                border: 2px solid {colors['darkPink']}; background-color: rgba(255, 255, 255, 0.7);
            ">
                <h2 style="color: {colors['darkPink']};">8. Overall Business Recommendations: Your Next Steps! 🎯</h2>
            </div>
        """, unsafe_allow_html=True)
        for rec in get_overall_recommendations(processed_df):
            st.markdown(f'- {rec}')
        st.markdown("---")

        # Download PDF button
        pdf_report = generate_pdf_report(
            processed_df,
            get_sentiment_insights(processed_df),
            get_engagement_insights(processed_df),
            get_platform_insights(processed_df),
            get_media_type_insights(processed_df),
            get_location_insights(processed_df),
            get_overall_recommendations(processed_df)
        )
        st.download_button(
            label="Download Insights as PDF! 📥",
            data=pdf_report,
            file_name="moodmelt_dashboard_report.pdf",
            mime="application/pdf",
            key="download_pdf_button",
            help="Download a PDF report of your analysis and recommendations.",
            # Add custom class for styling the button
            # Need to apply styling via a separate markdown as st.download_button doesn't take 'class'
            # The CSS above handles '.pdf-button>button'
        )
        st.markdown(
            f"""
            <style>
            #download_pdf_button {{
                margin-top: 3rem; /* mt-12 */
                display: block; /* Make it block to take full width or center */
                margin-left: auto;
                margin-right: auto;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown(f'<p style="text-align: center; font-size: 1.125rem; margin-top: 2rem; color: {colors["darkPink"]};">That\'s it! Your MoodMelt dashboard is brimming with insights. Keep crushing it! 🎉</p>', unsafe_allow_html=True)

