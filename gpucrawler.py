import streamlit as st
import json
import pandas as pd
import re
import os.path
from datetime import datetime

st.set_page_config(page_title="GPU Price Tracker", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #0066cc;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #444;
        margin-bottom: 1rem;
    }
    .price-highlight {
        font-weight: bold;
        color: #119922;
    }
    .product-name {
        font-size: 1.2rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 0.5rem;
    }
    .model-name {
        font-weight: bold;
        color: #0066cc;
    }
    .card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .filter-section {
        background-color: #f0f5ff;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .source-tag {
        background-color: #e0e0e0;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


def clean_price(price_str):
    """Extract numerical price value from string"""
    if not price_str:
        return None

    # Extract digits, decimal point, and commas
    price_match = re.search(r'[\$£€]?([0-9,]+\.[0-9]+|[0-9,]+)', str(price_str))
    if price_match:
        # Remove commas and convert to float
        return float(price_match.group(1).replace(',', ''))
    return None


def load_data():
    """Load data from the JSON file"""
    data_file = "gpu_prices_crawled.json"

    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError:
                st.error(f"Error: Could not parse JSON data from {data_file}")
                return {"ebay": [], "amazon": []}
    else:
        # Generate sample data if file doesn't exist (for testing purposes)
        st.warning(f"Warning: Data file {data_file} not found. Using sample data for demonstration.")
        return {
            "ebay": [
                {"name": "EVGA NVIDIA GeForce RTX 3080 10GB GDDR6X Graphics Card", "price": "$699.99",
                 "url": "https://example.com/1"},
                {"name": "Sapphire AMD Radeon RX 6800 XT 16GB GDDR6 Gaming GPU", "price": "$649.99",
                 "url": "https://example.com/2"}
            ],
            "amazon": [
                {"name": "MSI NVIDIA GeForce RTX 3070 8GB GDDR6 Gaming GPU", "price": "$499.99",
                 "url": "https://example.com/3"},
                {"name": "ASUS TUF Gaming AMD Radeon RX 6700 XT 12GB", "price": "$479.99",
                 "url": "https://example.com/4"}
            ]
        }


def prepare_dataframe(data):
    """Convert JSON data to pandas DataFrame"""
    all_products = []

    # Process eBay data
    for product in data.get("ebay", []):
        all_products.append({
            "name": product.get("name", "Unknown"),
            "price_str": product.get("price", "N/A"),
            "price": clean_price(product.get("price")),
            "url": product.get("url", "#"),
            "specifications": product.get("specifications", {}),
            "source": "eBay"
        })

    # Process Amazon data
    for product in data.get("amazon", []):
        all_products.append({
            "name": product.get("name", "Unknown"),
            "price_str": product.get("price", "N/A"),
            "price": clean_price(product.get("price")),
            "url": product.get("url", "#"),
            "specifications": product.get("specifications", {}),
            "source": "Amazon"
        })

    # Create DataFrame
    df = pd.DataFrame(all_products)

    # Remove rows with no price
    df = df.dropna(subset=["price"])

    return df


def extract_gpu_model(name):
    """Extract GPU model from product name"""
    model_patterns = [
        r'(RTX\s*[0-9]{4}\s*(?:Ti|Super)?)',  # NVIDIA RTX models
        r'(GTX\s*[0-9]{3,4}\s*(?:Ti|Super)?)',  # NVIDIA GTX models
        r'(RX\s*[0-9]{3,4}\s*(?:XT)?)',  # AMD RX models
        r'(Radeon\s*(?:RX)?\s*[0-9]{3,4}\s*(?:XT)?)'  # AMD Radeon models
    ]

    for pattern in model_patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            return match.group(1)

    return "Unknown Model"


def extract_brand(name):
    """Extract GPU brand from product name"""
    brand_patterns = [
        r'\b(NVIDIA|GeForce)\b',
        r'\b(AMD|Radeon)\b',
        r'\b(ASUS|MSI|EVGA|Gigabyte|Sapphire|XFX|Zotac|PNY)\b'
    ]

    for pattern in brand_patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def main():
    st.markdown("<h1 class='main-header'>GPU Price Tracker</h1>", unsafe_allow_html=True)

    # Load the data
    data = load_data()

    # Convert to DataFrame
    df = prepare_dataframe(data)

    # Extract GPU models and brands
    df["model"] = df["name"].apply(extract_gpu_model)
    df["brand"] = df["name"].apply(extract_brand)

    # Display stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='card'><h3>Total Products</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
    with col2:
        ebay_count = len(df[df["source"] == "eBay"])
        st.markdown(f"<div class='card'><h3>eBay Products</h3><h2>{ebay_count}</h2></div>", unsafe_allow_html=True)
    with col3:
        amazon_count = len(df[df["source"] == "Amazon"])
        st.markdown(f"<div class='card'><h3>Amazon Products</h3><h2>{amazon_count}</h2></div>", unsafe_allow_html=True)

    # Filters section
    st.markdown("<h2 class='sub-header'>Filters</h2>", unsafe_allow_html=True)

    st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        # Price range filter
        if not df.empty and df["price"].notna().any():
            min_price = int(df["price"].min())
            max_price = int(df["price"].max())
            price_range = st.slider("Price Range ($)", min_price, max_price, (min_price, max_price))
            df = df[(df["price"] >= price_range[0]) & (df["price"] <= price_range[1])]

        # Name search filter
        name_search = st.text_input("Search by Name")
        if name_search:
            df = df[df["name"].str.contains(name_search, case=False)]

    with col2:
        # Source filter
        sources = ["All"] + sorted(df["source"].unique().tolist())
        selected_source = st.selectbox("Source", sources)
        if selected_source != "All":
            df = df[df["source"] == selected_source]

        # Model filter if we have models extracted
        models = ["All"] + sorted(df["model"].unique().tolist())
        selected_model = st.selectbox("GPU Model", models)
        if selected_model != "All":
            df = df[df["model"] == selected_model]

    # Sort options
    sort_options = ["Price (Low to High)", "Price (High to Low)", "Name (A-Z)"]
    selected_sort = st.selectbox("Sort By", sort_options)

    if selected_sort == "Price (Low to High)":
        df = df.sort_values(by="price")
    elif selected_sort == "Price (High to Low)":
        df = df.sort_values(by="price", ascending=False)
    else:  # Name (A-Z)
        df = df.sort_values(by="name")

    st.markdown("</div>", unsafe_allow_html=True)

    # Display results
    st.markdown("<h2 class='sub-header'>Results</h2>", unsafe_allow_html=True)

    if df.empty:
        st.info("No products found matching your filters.")
    else:
        # Display number of results
        st.write(f"Found {len(df)} products matching your criteria")

        # Display as cards
        for _, row in df.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"""
                    <div class='card'>
                        <div class='product-name'>{row['name']}</div>
                        <p><span class='model-name'>{row['model']}</span> • <span class='price-highlight'>{row['price_str']}</span> • 
                        <span class='source-tag'>{row['source']}</span></p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
                    st.markdown(f"[View Details]({row['url']})")

    # Add timestamp and data source note
    st.markdown("---")
    st.markdown(
        f"<p style='text-align: center; color: gray;'>Data loaded from GPU crawler results. Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
        unsafe_allow_html=True)


if __name__ == "__main__":
    main()