import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# -------------------
# App Config
# -------------------
st.set_page_config(page_title="UrbanAI – Smart City Intelligence", layout="wide")
st.title("UrbanAI – Smart City Intelligence Platform")
st.header("Upload Smart City Dataset")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

# -------------------
# Colored Metric Function
# -------------------
def colored_metric(col, value, thresholds, label):
    if pd.isna(value):
        metrics_cols[col].metric(label, "N/A")
    else:
        if value >= thresholds[1]:
            metrics_cols[col].metric(label, f"{value}", delta="High 🔴")
        elif value >= thresholds[0]:
            metrics_cols[col].metric(label, f"{value}", delta="Moderate 🟠")
        else:
            metrics_cols[col].metric(label, f"{value}", delta="Low 🟢")

# -------------------
# Main Logic
# -------------------
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.subheader("Dataset Preview")
    st.dataframe(data.head())

    # -------------------
    # Key Metrics
    # -------------------
    st.subheader("Key City Metrics")
    metrics_cols = st.columns(3)

    if "stress_index" in data.columns:
        avg_stress = pd.to_numeric(data["stress_index"], errors='coerce').mean()
        colored_metric(0, avg_stress, [4,7], "Average Traffic Stress")
    
    if "AQI Value" in data.columns:
        aqi_values = pd.to_numeric(data["AQI Value"], errors='coerce')
        max_aqi = aqi_values.max()
        avg_aqi = round(aqi_values.mean(),2)
        colored_metric(1, max_aqi, [150,300], "Maximum AQI")
        colored_metric(1, avg_aqi, [50,100], "Average AQI")
    
    if "energy_consumption" in data.columns:
        avg_energy = pd.to_numeric(data["energy_consumption"], errors='coerce').mean()
        colored_metric(2, avg_energy, [5000,10000], "Average Energy Consumption")

    # -------------------
    # Data Visualization
    # -------------------
    st.subheader("📊 Data Visualization")
    numeric_cols = data.select_dtypes(include=['float64','int64','int32','float32']).columns
    if len(numeric_cols) > 0:
        selected_col = st.selectbox("Select column for histogram", numeric_cols)
        fig, ax = plt.subplots()
        ax.hist(pd.to_numeric(data[selected_col], errors='coerce').dropna(), bins=20, color='skyblue', edgecolor='black')
        ax.set_title(f"Distribution of {selected_col}")
        st.pyplot(fig)

    # -------------------
    # Time Trend Analysis
    # -------------------
    if "date" in data.columns:
        st.subheader("📅 Time Trend Analysis")
        data['date'] = pd.to_datetime(data['date'], errors='coerce')
        trend_cols = [col for col in numeric_cols if col != 'energy_consumption']
        if trend_cols:
            selected_trend_col = st.selectbox("Select column for trend analysis", trend_cols)
            trend_data = data[['date', selected_trend_col]].set_index('date')
            st.line_chart(trend_data)

    # -------------------
    # Feature Correlation Heatmap
    # -------------------
    st.subheader("📊 Feature Correlation Heatmap")
    if len(numeric_cols) > 1:
        fig, ax = plt.subplots(figsize=(8,6))
        sns.heatmap(data[numeric_cols].corr(), annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
        ax.set_title("Correlation Between City Metrics")
        st.pyplot(fig)

    # -------------------
    # AI Smart City Insights
    # -------------------
    st.subheader("💡 AI Smart City Insights")
    insights = []
    risk_factors = {}

    if "stress_index" in data.columns:
        mean_stress = data["stress_index"].mean()
        if mean_stress > 5:
            insights.append("⚠ High driver stress detected in traffic patterns.")
            risk_factors["Traffic Stress"] = mean_stress
    
    if "AQI Value" in data.columns:
        mean_aqi = data["AQI Value"].mean()
        if mean_aqi > 100:
            insights.append("⚠ Air quality is unhealthy in many areas.")
            risk_factors["Air Quality"] = mean_aqi

    if "energy_consumption" in data.columns:
        mean_energy = data["energy_consumption"].mean()
        median_energy = data["energy_consumption"].median()
        if mean_energy > median_energy:
            insights.append("⚠ Energy consumption trend is increasing.")
            risk_factors["Energy Consumption"] = mean_energy

    if insights:
        st.warning("\n".join(insights))
    else:
        st.success("City indicators appear stable.")

    # -------------------
    # Top Risk Factors
    # -------------------
    if risk_factors:
        st.subheader("🔥 Top Risk Factors")
        top_risk = pd.DataFrame(list(risk_factors.items()), columns=["Metric","Value"]).sort_values(by="Value", ascending=False)
        st.table(top_risk)

    # -------------------
    # AI Prediction System
    # -------------------
    st.subheader("🤖 AI Prediction System")
    if st.button("Run AI Analysis"):
        st.write("Analyzing city patterns...")
        if "stress_index" in data.columns:
            avg_stress = data["stress_index"].mean()
            if avg_stress > 7:
                st.error("🚦 Traffic Risk Level: HIGH")
            elif avg_stress > 4:
                st.warning("🚦 Traffic Risk Level: MODERATE")
            else:
                st.success("🚦 Traffic Risk Level: LOW")

        if "AQI Value" in data.columns:
            max_aqi = data["AQI Value"].max()
            if max_aqi > 300:
                st.error("🌫 Pollution Risk: SEVERE")
            elif max_aqi > 150:
                st.warning("🌫 Pollution Risk: MODERATE")
            else:
                st.success("🌫 Pollution Risk: LOW")

        if "energy_consumption" in data.columns:
            avg_energy = data["energy_consumption"].mean()
            if avg_energy > data["energy_consumption"].median():
                st.warning("⚡ Energy demand expected to increase.")
            else:
                st.success("⚡ Energy demand stable.")
else:
    st.info("Please upload a dataset to begin analysis.")