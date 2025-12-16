import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import logging
from typing import List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class EmailAlerter:
    def __init__(
        self,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587,
        sender_email: str = "alerts@datapipeline.company.com",
        sender_password: Optional[str] = None
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        
        if not sender_password:
            logger.warning("Sender password not provided. Email alerts disabled.")
    
    def send_alert(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        attachment_path: Optional[str] = None,
        is_html: bool = False
    ) -> bool:
        if not self.sender_password:
            logger.error("Cannot send email: sender password not configured")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"[Data Pipeline Alert] {subject}"
            
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            if attachment_path:
                with open(attachment_path, 'rb') as f:
                    attachment = MIMEApplication(f.read())
                    attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    )
                    msg.attach(attachment)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email alert sent to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    def send_pipeline_success_alert(
        self,
        recipients: List[str],
        pipeline_id: str,
        metrics: dict,
        output_paths: dict
    ):
        subject = f"Pipeline Success: {pipeline_id}"
        
        body = f"""
        Data cleaning pipeline completed successfully.
        
        Pipeline ID: {pipeline_id}
        Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Metrics:
        - Rows Processed: {metrics.get('transformation', {}).get('rows_final', 0)}
        - Quality Score: {metrics.get('quality', {}).get('overall_score', 0)}%
        - Duration: {metrics.get('execution', {}).get('duration_seconds', 0)} seconds
        
        Output Files:
        - Cleaned Data: {output_paths.get('parquet', 'N/A')}
        - Quality Report: {output_paths.get('summary', 'N/A')}
        
        Anomalies Detected: {metrics.get('anomalies', {}).get('summary', {}).get('total_anomalies_detected', 0)}
        """
        
        return self.send_alert(recipients, subject, body)
    
    def send_pipeline_failure_alert(
        self,
        recipients: List[str],
        pipeline_id: str,
        error_info: dict
    ):
        subject = f"Pipeline Failure: {pipeline_id}"
        
        body = f"""
        Data cleaning pipeline failed.
        
        Pipeline ID: {pipeline_id}
        Failure Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Error Details:
        - Type: {error_info.get('classification', {}).get('type', 'Unknown')}
        - Category: {error_info.get('classification', {}).get('category', 'Unknown')}
        - Severity: {error_info.get('classification', {}).get('severity', 'Unknown')}
        - Message: {error_info.get('classification', {}).get('message', 'No error message')}
        
        Action Taken: {error_info.get('action_taken', 'Unknown')}
        
        Error log saved to: {error_info.get('error_file', 'N/A')}
        
        Immediate investigation required.
        """
        
        return self.send_alert(recipients, subject, body)
    
    def send_quality_threshold_alert(
        self,
        recipients: List[str],
        pipeline_id: str,
        quality_score: float,
        threshold: float = 95.0
    ):
        subject = f"Quality Threshold Alert: {pipeline_id}"
        
        body = f"""
        Data quality below threshold.
        
        Pipeline ID: {pipeline_id}
        Alert Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Quality Score: {quality_score}%
        Required Threshold: {threshold}%
        Deviation: {threshold - quality_score}%
        
        The pipeline completed but the data quality is below the acceptable threshold.
        Manual review of the output data is recommended.
        """
        
        return self.send_alert(recipients, subject, body)