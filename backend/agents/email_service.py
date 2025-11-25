import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os


def send_email(
    recipient_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None
) -> tuple[bool, str]:
    """
    Send an email using SMTP.
    
    Args:
        recipient_email: Recipient's email address
        subject: Email subject
        body: Plain text email body
        html_body: Optional HTML version of the email body
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Get SMTP configuration from environment variables
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER") or os.getenv("SMTP_USER")
        # Support both SMTP_PASSWORD and SMTP_PASS env var names
        smtp_password = os.getenv("SMTP_PASSWORD") or os.getenv("SMTP_PASS")

        if not smtp_user or not smtp_password:
            return False, "SMTP credentials not configured. Please set SMTP_USER and SMTP_PASS (or SMTP_PASSWORD) environment variables."
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = smtp_user
        message["To"] = recipient_email
        
        # Add plain text part
        text_part = MIMEText(body, "plain")
        message.attach(text_part)
        
        # Add HTML part if provided
        if html_body:
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)
        
        return True, f"Email successfully sent to {recipient_email}"
        
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"


def clean_workshop_data(raw_data: str) -> str:
    """
    Clean workshop data by removing error messages and formatting nicely.
    
    Args:
        raw_data: Raw workshop information string
        
    Returns:
        Cleaned and formatted workshop information
    """
    import re
    
    
    lines = raw_data.split('\n')
    cleaned_lines = []
    skip_until_blank = False
    
    for line in lines:
        
        if '❌' in line or 'Database access error' in line or 'psycopg2.errors' in line:
            skip_until_blank = True
            continue
        if skip_until_blank:
            if line.strip() == '' or line.startswith('🌐'):
                skip_until_blank = False
            continue
        
        
        if any(x in line for x in ['[SQL:', 'LINE 1:', 'HINT:', 'sqlalche.me', '(Background on']):
            continue
            
        cleaned_lines.append(line)
    
    cleaned_text = '\n'.join(cleaned_lines)
    
    
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    return cleaned_text.strip()


def parse_workshops_from_text(text: str) -> list[dict]:
    """
    Parse workshop information from text into structured data.
    Only include direct workshop URLs, filter out Yelp links.
    """
    import re
    import ast
    workshops = []
    dict_matches = re.findall(r'\{[^}]+\}', text)
    for dstr in dict_matches:
        try:
            d = ast.literal_eval(dstr)
            url = d.get('url', '')
            # Filter out Yelp links
            if url and ('yelp.com' in url or 'm.yelp.com' in url):
                url = ''
            ws = {
                'name': d.get('title', ''),
                'url': url,
                'description': d.get('content', '')
            }
            if ws['name'] or ws['description']:
                workshops.append(ws)
        except Exception:
            continue
    return workshops


def create_workshop_recommendation_html(
    customer_name: str,
    workshops_info: str
) -> str:
    """
    Create an HTML version of the workshop recommendation email.
    Show up to 3 workshops with homepage links (no Yelp).
    """
    cleaned_info = clean_workshop_data(workshops_info)
    workshops = [ws for ws in parse_workshops_from_text(workshops_info) if ws.get('url')]
    workshops = workshops[:3]
    workshop_cards = ""
    if workshops:
        for i, ws in enumerate(workshops, 1):
            description = ws.get('description', 'No description available')
            url = ws.get('url', '')
            url_link = f'<p><a href="{url}" style="color: #4CAF50; text-decoration: underline;">Homepage →</a></p>' if url else ''
            workshop_cards += f"""
            <div style='background-color: white; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #4CAF50; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                <p style='color: #666; line-height: 1.6;'>{description}</p>
                {url_link}
            </div>
            """
    else:
        cleaned_html = cleaned_info.replace('\n', '<br>')
        workshop_cards = f"""
        <div style='background-color: white; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #4CAF50;'>
            {cleaned_html}
        </div>
        """
    html = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 0; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; padding: 30px 20px; text-align: center; }}
                .header h2 {{ margin: 0; font-size: 24px; }}
                .content {{ padding: 30px 20px; background-color: #f9f9f9; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #999; background-color: #f5f5f5; border-top: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class='container'>
                <div class='header'>
                    <h2>🚗 Your Workshop Recommendations</h2>
                </div>
                <div class='content'>
                    <p style='font-size: 16px;'>Hello <strong>{customer_name}</strong>,</p>
                    <p>Thank you for using our workshop search service. Here are up to 3 recommended workshops with homepage links:</p>
                    {workshop_cards}
                    <p style='margin-top: 30px;'>If you have any questions or need further assistance, please don't hesitate to contact us.</p>
                    <p style='margin-top: 20px;'>Best regards,<br><strong>Your Vehicle Service Team</strong></p>
                </div>
                <div class='footer'>
                    <p>This is an automated message from your Vehicle Service Assistant.</p>
                    <p>© 2025 Vehicle Service. All rights reserved.</p>
                </div>
            </div>
        </body>
    </html>
    """
    return html


def format_workshop_recommendation_email(
    customer_name: str,
    workshops_info: str
) -> tuple[str, str]:
    """
    Format an email with workshop recommendations.
    Show up to 3 workshops with homepage links (no Yelp).
    """
    cleaned_info = clean_workshop_data(workshops_info)
    workshops = [ws for ws in parse_workshops_from_text(workshops_info) if ws.get('url')]
    workshops = workshops[:3]
    lines = [f"Hello {customer_name},", "", "Thank you for using our workshop search service. Here are up to 3 recommended workshops with homepage links:", ""]
    if workshops:
        for i, ws in enumerate(workshops, 1):
            description = ws.get('description', 'No description available')
            url = ws.get('url', '')
            url_line = f"Homepage: {url}" if url else ""
            lines.append(f"{i}.\n{description}\n{url_line}\n")
    else:
        lines.append(cleaned_info)
    lines.append("If you have any questions or need further assistance, please don't hesitate to contact us.")
    lines.append("Best regards,\nYour Vehicle Service Team")
    subject = "Your Workshop Recommendations"
    body = "\n".join(lines)
    return subject, body
