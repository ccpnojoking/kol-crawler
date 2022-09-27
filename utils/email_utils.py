import re
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


class EmailClient:

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_html_message(sender_email, receiver_emails, subject, content, image=None):
        message = MIMEMultipart()
        message["from"] = sender_email
        message["to"] = ','.join(receiver_emails)
        message["subject"] = subject
        content = MIMEText(content, 'html', 'utf-8')
        message.attach(content)
        if not image:
            return message
        with open(image['path'], 'rb') as read_send_image:
            image = MIMEImage(read_send_image.read())
        image.add_header('Content-ID', image['cid'])
        message.attach(image)
        return message

    @staticmethod
    def get_smtp_server(domain):
        if domain.lower() == 'outlook.com':
            return 'smtp.office365.com', 587
        if domain.lower() == 'gmail.com':
            return 'smtp.gmail.com', 465
        return None, None

    def send(self, email, password, receivers, message):
        domain = re.findall('@(.*)', email)
        print(domain)
        if not domain:
            return False
        host, port = self.get_smtp_server(domain[0])
        if not all([host, port]):
            return False
        smtp = smtplib.SMTP(host=host, port=port)
        if host == 'smtp.office365.com':
            smtp.starttls()
        smtp.login(email, password)
        response = smtp.sendmail(email, receivers, message.as_string())
        print(response)
        smtp.quit()


def main():
    receiver_emails = [
        'helloccp@126.com',
        'sid@miyutek.com'
    ]
    content = '''
    <html>
    <p style="margin:0;font-family: Verdana, Geneva, sans-serif;">
    不开心就喝水.
    <img src="cid:one_piece_image">
    </p>
    </html>
    '''
    image = {
        'cid': 'one_piece_image',
        'path': '/Users/caibusi/Desktop/projects/kol-crawler/operations/static/images/img.png'
    }
    email = 'nohappy_just_water@outlook.com'
    password = 'helloMDD1995'
    email_client = EmailClient()
    message = email_client.get_html_message(
        sender_email=email,
        receiver_emails=receiver_emails,
        subject='beautiful world',
        content=content,
        image=image
    )
    email_client.send(
        email,
        password,
        receiver_emails,
        message
    )


if __name__ == '__main__':
    main()
