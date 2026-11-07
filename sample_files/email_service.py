"""Сервис отправки электронной почты."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailService:
    """Сервис для отправки email-уведомлений."""

    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        """Инициализация SMTP-соединения."""
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_welcome(self, to_email: str, username: str) -> bool:
        """Отправить приветственное письмо новому пользователю."""
        subject = f"Добро пожаловать, {username}!"
        body = f"Ваш аккаунт успешно создан."
        return self._send(to_email, subject, body)

    def send_reset_password(self, to_email: str, reset_link: str) -> bool:
        """Отправить письмо со ссылкой для сброса пароля."""
        subject = "Сброс пароля"
        body = f"Перейдите по ссылке для сброса пароля: {reset_link}"
        return self._send(to_email, subject, body)

    def _send(self, to_email: str, subject: str, body: str) -> bool:
        """Внутренний метод отправки письма через SMTP."""
        msg = MIMEMultipart()
        msg["From"] = self.username
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.login(self.username, self.password)
            server.send_message(msg)
        return True
