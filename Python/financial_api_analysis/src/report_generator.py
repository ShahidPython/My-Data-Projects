from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from pathlib import Path
import pandas as pd
import logging
from config import settings

logger = logging.getLogger(__name__)

class PDFReportGenerator:
    def __init__(self, summary_stats, chart_paths):
        self.summary_stats = summary_stats
        self.chart_paths = chart_paths
        self.output_path = settings.OUTPUT_REPORTS
        
        # Initialize styles
        self.styles = getSampleStyleSheet()
        self._custom_styles = {}  # Store custom styles separately
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom styles if they don't exist."""
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#2C3E50'),
                spaceAfter=12,
                alignment=TA_CENTER
            ))
        
        if 'SectionHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#34495E'),
                spaceAfter=6,
                spaceBefore=12
            ))
        
        if 'BodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='BodyText',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#2C3E50'),
                spaceAfter=6
            ))
        
        # Store custom style names for reference
        self._custom_styles = {
            'CustomTitle': self.styles['CustomTitle'],
            'SectionHeader': self.styles['SectionHeader'],
            'BodyText': self.styles['BodyText']
        }
    
    def _create_header_footer(self, canvas, doc):
        canvas.saveState()
        
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.HexColor('#2C3E50'))
        canvas.drawString(inch, doc.height + inch + 0.5*inch, 
                         f"{settings.COMPANY_NAME} - {settings.REPORT_TITLE}")
        
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.gray)
        canvas.drawRightString(doc.width + inch, doc.height + inch + 0.5*inch,
                              f"Page {canvas.getPageNumber()}")
        
        canvas.setFont('Helvetica', 7)
        canvas.drawString(inch, 0.5*inch, settings.REPORT_FOOTER_TEXT)
        
        canvas.restoreState()
    
    def _create_executive_summary(self):
        content = []
        
        content.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        if self.summary_stats:
            date_range = self.summary_stats.get('date_range', {})
            symbols = self.summary_stats.get('symbols_analyzed', [])
            
            summary_text = f"""
            This report provides a comprehensive analysis of financial market data covering the period from 
            {date_range.get('start', 'N/A')} to {date_range.get('end', 'N/A')}. The analysis includes 
            {len(symbols)} equity symbols and key macroeconomic indicators. The dataset contains 
            {self.summary_stats.get('total_observations', 0):,} observations with detailed technical indicators 
            calculated for each security.
            """
            
            content.append(Paragraph(summary_text.strip(), self.styles['BodyText']))
            content.append(Spacer(1, 0.25*inch))
        
        return content
    
    def _create_performance_table(self):
        content = []
        
        content.append(Paragraph("Equity Performance Metrics", self.styles['SectionHeader']))
        
        if 'equity_metrics' in self.summary_stats:
            table_data = [['Symbol', 'Latest Close', 'Total Return (%)', 
                          'Avg Volatility (%)', 'Sector']]
            
            for symbol, metrics in self.summary_stats['equity_metrics'].items():
                row = [
                    symbol,
                    f"${metrics.get('latest_close', 0):,.2f}",
                    f"{metrics.get('total_return', 0):+.2f}%",
                    f"{metrics.get('avg_volatility', 0):.2f}%",
                    metrics.get('sector', 'N/A')
                ]
                table_data.append(row)
            
            col_widths = [1*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.5*inch]
            table = Table(table_data, colWidths=col_widths)
            
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            content.append(table)
            content.append(Spacer(1, 0.25*inch))
        
        return content
    
    def _insert_chart_with_caption(self, chart_path, caption):
        content = []
        
        if chart_path and Path(chart_path).exists():
            try:
                img = Image(chart_path, width=6*inch, height=3.5*inch)
                img.hAlign = 'CENTER'
                content.append(img)
                content.append(Spacer(1, 0.1*inch))
                content.append(Paragraph(caption, ParagraphStyle(
                    name='Caption',
                    parent=self.styles['Normal'],
                    fontSize=8,
                    textColor=colors.gray,
                    alignment=TA_CENTER
                )))
                content.append(Spacer(1, 0.25*inch))
            except Exception as e:
                logger.error(f"Error inserting chart {chart_path}: {str(e)}")
                content.append(Paragraph(f"Chart unavailable: {caption}", self.styles['BodyText']))
        
        return content
    
    def _create_analysis_insights(self):
        content = []
        
        content.append(Paragraph("Key Insights & Recommendations", self.styles['SectionHeader']))
        
        insights = [
            "Market volatility shows varying levels across analyzed securities, indicating different risk profiles.",
            "Correlation analysis reveals inter-sector relationships that can inform diversification strategies.",
            "Moving average crossovers provide technical signals for potential entry/exit points.",
            "Macroeconomic indicators show the broader economic context affecting all securities.",
            "Volume analysis confirms price movements with institutional participation levels."
        ]
        
        for insight in insights:
            content.append(Paragraph(f"• {insight}", self.styles['BodyText']))
            content.append(Spacer(1, 0.05*inch))
        
        content.append(Spacer(1, 0.25*inch))
        
        return content
    
    def _create_methodology_section(self):
        content = []
        
        content.append(Paragraph("Methodology", self.styles['SectionHeader']))
        
        methodology_text = """
        <b>Data Sources:</b> Equity data sourced from Yahoo Finance API. Macroeconomic indicators from FRED (Federal Reserve Economic Data).<br/>
        <b>Time Period:</b> Analysis covers one year of historical data with daily resolution for equities.<br/>
        <b>Technical Indicators:</b> Calculated 20-day and 50-day moving averages, daily returns, annualized volatility, and volume ratios.<br/>
        <b>Risk Metrics:</b> Volatility calculated as annualized standard deviation of daily returns.<br/>
        <b>Correlation Analysis:</b> Pearson correlation coefficients computed on daily returns.<br/>
        <b>Report Generation:</b> Automated PDF generation with embedded visualizations and summary statistics.<br/>
        """
        
        content.append(Paragraph(methodology_text, self.styles['BodyText']))
        content.append(Spacer(1, 0.25*inch))
        
        return content
    
    def generate_report(self):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = self.output_path / f"financial_analysis_report_{timestamp}.pdf"
            
            doc = SimpleDocTemplate(str(filename), pagesize=landscape(letter),
                                   topMargin=1*inch, bottomMargin=1*inch,
                                   leftMargin=0.75*inch, rightMargin=0.75*inch)
            
            story = []
            
            story.append(Paragraph(settings.REPORT_TITLE, self.styles['CustomTitle']))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                 ParagraphStyle(name='Subtitle', parent=self.styles['Normal'],
                                               fontSize=10, alignment=TA_CENTER,
                                               textColor=colors.gray)))
            story.append(Spacer(1, 0.3*inch))
            
            story.extend(self._create_executive_summary())
            story.extend(self._create_performance_table())
            
            if 'correlation_heatmap' in self.chart_paths:
                story.extend(self._insert_chart_with_caption(
                    self.chart_paths['correlation_heatmap'],
                    "Figure 1: Equity Returns Correlation Matrix"
                ))
            
            if 'volatility_comparison' in self.chart_paths:
                story.extend(self._insert_chart_with_caption(
                    self.chart_paths['volatility_comparison'],
                    "Figure 2: Annualized Volatility Comparison Across Securities"
                ))
            
            # Add price trend charts
            price_charts = [k for k in self.chart_paths.keys() if k.startswith('price_trend_')]
            for i, chart_key in enumerate(price_charts[:2], 3):  # Limit to 2 charts
                symbol = chart_key.replace('price_trend_', '')
                story.extend(self._insert_chart_with_caption(
                    self.chart_paths[chart_key],
                    f"Figure {i}: {symbol} Price Trend with Moving Averages"
                ))
            
            if 'macro_economic' in self.chart_paths:
                story.extend(self._insert_chart_with_caption(
                    self.chart_paths['macro_economic'],
                    "Figure: Macroeconomic Indicators Trend Analysis"
                ))
            
            story.extend(self._create_analysis_insights())
            story.extend(self._create_methodology_section())
            
            doc.build(story, onFirstPage=self._create_header_footer, 
                     onLaterPages=self._create_header_footer)
            
            logger.info(f"PDF report generated: {filename}")
            return filename
            
        except Exception as e:
            logger.exception(f"Error generating PDF report: {str(e)}")
            return None