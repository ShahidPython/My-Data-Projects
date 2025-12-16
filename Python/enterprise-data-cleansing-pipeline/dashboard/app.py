import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import sys
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from src.orchestration.pipeline_manager import PipelineManager

st.set_page_config(
    page_title="Data Cleaning Dashboard",
    page_icon="🧹",
    layout="wide"
)

st.title("🧹 Enterprise Data Cleaning Dashboard")
st.markdown("Real-time monitoring and control for data cleaning pipeline")

tab1, tab2, tab3, tab4 = st.tabs(["Run Pipeline", "Quality Metrics", "Anomaly Detection", "Configuration"])

with tab1:
    st.header("Run Cleaning Pipeline")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
        config_file = st.selectbox(
            "Configuration",
            ["config/cleaning_rules.json", "config/strict_rules.json"]
        )
    
    with col2:
        email_alerts = st.text_input("Email for alerts (optional)")
        run_button = st.button("🚀 Run Pipeline", type="primary")
    
    if uploaded_file and run_button:
        with st.spinner("Running pipeline..."):
            input_path = f"data/input/{uploaded_file.name}"
            with open(input_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            pipeline = PipelineManager(config_file)
            result = pipeline.execute_pipeline(input_path)
            
            if result['success']:
                st.success("✅ Pipeline completed successfully!")
                
                metrics = result['metrics']
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Quality Score", f"{metrics.get('quality_score', 0)}%")
                with col2:
                    st.metric("Rows Processed", metrics.get('transformation', {}).get('rows_final', 0))
                with col3:
                    st.metric("Duration", f"{metrics.get('execution', {}).get('duration_seconds', 0)}s")
                
                st.download_button(
                    label="Download Cleaned Data",
                    data=open(result['output_paths']['parquet'], 'rb').read(),
                    file_name="cleaned_data.parquet",
                    mime="application/octet-stream"
                )
            else:
                st.error("❌ Pipeline failed")
                st.json(result.get('error', {}))

with tab2:
    st.header("Data Quality Metrics")
    
    if Path("data/output").exists():
        summary_files = list(Path("data/output").glob("*summary.json"))
        
        if summary_files:
            latest_summary = max(summary_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_summary, 'r') as f:
                summary_data = json.load(f)
            
            quality_data = summary_data.get('quality', {})
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Overall Score", f"{quality_data.get('overall_score', 0)}%")
            with col2:
                st.metric("Completeness", f"{quality_data.get('completeness', {}).get('overall', 0)}%")
            with col3:
                st.metric("Validity", f"{quality_data.get('validity', {}).get('overall', 0)}%")
            
            metrics_df = pd.DataFrame({
                'Metric': ['Completeness', 'Uniqueness', 'Validity'],
                'Score': [
                    quality_data.get('completeness', {}).get('overall', 0),
                    quality_data.get('uniqueness', {}).get('overall', 0),
                    quality_data.get('validity', {}).get('overall', 0)
                ]
            })
            
            fig = px.bar(metrics_df, x='Metric', y='Score', title="Quality Metrics",
                        color='Score', color_continuous_scale='RdYlGn',
                        range_y=[0, 100])
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Detailed Column Metrics"):
                for metric_type in ['completeness', 'validity']:
                    if metric_type in quality_data:
                        st.subheader(metric_type.title())
                        col_metrics = quality_data[metric_type].get('by_column', {})
                        col_df = pd.DataFrame(list(col_metrics.items()), columns=['Column', 'Score'])
                        st.dataframe(col_df)
        else:
            st.warning("No quality reports found. Run a pipeline first.")
    else:
        st.warning("Output directory not found.")

with tab3:
    st.header("Anomaly Detection")
    
    if Path("data/output").exists():
        summary_files = list(Path("data/output").glob("*summary.json"))
        
        if summary_files:
            latest_summary = max(summary_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_summary, 'r') as f:
                summary_data = json.load(f)
            
            anomalies = summary_data.get('anomalies', {})
            
            if anomalies:
                anomaly_count = anomalies.get('summary', {}).get('total_anomalies_detected', 0)
                anomaly_rate = anomalies.get('summary', {}).get('anomaly_rate', 0)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Anomalies", anomaly_count)
                with col2:
                    st.metric("Anomaly Rate", f"{anomaly_rate}%")
                
                anomaly_types = []
                counts = []
                
                for key, value in anomalies.items():
                    if key != 'summary' and isinstance(value, dict):
                        if 'count' in value:
                            anomaly_types.append(key.replace('_', ' ').title())
                            counts.append(value['count'])
                
                if anomaly_types:
                    fig = px.pie(names=anomaly_types, values=counts, 
                                title="Anomaly Distribution")
                    st.plotly_chart(fig, use_container_width=True)
                
                with st.expander("View Anomaly Details"):
                    st.json(anomalies)
            else:
                st.info("No anomalies detected in the latest run.")
        else:
            st.warning("No reports found. Run a pipeline first.")
    else:
        st.warning("Output directory not found.")

with tab4:
    st.header("Pipeline Configuration")
    
    config_files = {
        "Cleaning Rules": "config/cleaning_rules.json",
        "Data Schema": "config/data_schema.json",
        "Logging Config": "config/logging_config.yaml"
    }
    
    selected_config = st.selectbox("Select Configuration File", list(config_files.keys()))
    
    config_path = config_files[selected_config]
    
    if Path(config_path).exists():
        with open(config_path, 'r') as f:
            if config_path.endswith('.json'):
                config_data = json.load(f)
                st.json(config_data)
            elif config_path.endswith('.yaml'):
                config_content = f.read()
                st.code(config_content, language='yaml')
    else:
        st.error(f"Configuration file not found: {config_path}")

st.sidebar.markdown("## 📊 Pipeline Status")
if Path("logs").exists():
    log_files = list(Path("logs").glob("*.log"))
    if log_files:
        latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
        st.sidebar.metric("Last Run", datetime.fromtimestamp(latest_log.stat().st_mtime).strftime('%Y-%m-%d %H:%M'))
    else:
        st.sidebar.info("No runs yet")
else:
    st.sidebar.warning("Logs directory not found")

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Actions")
if st.sidebar.button("🔄 Check for Updates"):
    st.rerun()

if st.sidebar.button("📁 Open Output Folder"):
    output_path = Path("data/output").absolute()
    st.sidebar.info(f"Output path: {output_path}")