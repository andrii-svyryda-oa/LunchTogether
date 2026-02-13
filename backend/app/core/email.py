import logging
from email.message import EmailMessage

import aiosmtplib

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Async email service using SMTP."""

    async def send_email(self, to: str, subject: str, html_body: str) -> None:
        """Send an HTML email. Silently logs errors in development mode."""
        message = EmailMessage()
        message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
        message["To"] = to
        message["Subject"] = subject
        message.set_content(html_body, subtype="html")

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_user or None,
                password=settings.smtp_password or None,
                start_tls=settings.smtp_use_tls,
            )
            logger.info("Email sent to %s: %s", to, subject)
        except Exception:
            logger.exception("Failed to send email to %s: %s", to, subject)
            if not settings.is_development:
                raise

    async def send_invitation_email(
        self,
        to_email: str,
        inviter_name: str,
        group_name: str,
        token: str,
    ) -> None:
        """Send a group invitation email."""
        accept_url = f"{settings.frontend_url}/invitations/accept?token={token}"
        subject = f"You've been invited to join \"{group_name}\" on LunchTogether"

        html_body = f"""\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0; padding:0; background-color:#faf8f5; font-family:'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#faf8f5; padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:520px; background-color:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.08);">
          <!-- Header -->
          <tr>
            <td style="background-color:#f97316; padding:32px 40px; text-align:center;">
              <span style="font-size:28px;">🍽️</span>
              <h1 style="margin:8px 0 0; color:#ffffff; font-size:22px; font-weight:700; letter-spacing:-0.02em;">
                LunchTogether
              </h1>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:36px 40px 20px;">
              <h2 style="margin:0 0 8px; color:#1c1917; font-size:20px; font-weight:600;">
                You're invited! 🎉
              </h2>
              <p style="margin:0 0 24px; color:#57534e; font-size:15px; line-height:1.6;">
                <strong style="color:#1c1917;">{inviter_name}</strong> has invited you to join
                the group <strong style="color:#1c1917;">"{group_name}"</strong> on LunchTogether.
              </p>
              <!-- CTA Button -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding:8px 0 24px;">
                    <a href="{accept_url}"
                       style="display:inline-block; background-color:#f97316; color:#ffffff; font-size:15px; font-weight:600; text-decoration:none; padding:12px 32px; border-radius:10px; box-shadow:0 2px 8px rgba(249,115,22,0.25);">
                      Accept Invitation
                    </a>
                  </td>
                </tr>
              </table>
              <p style="margin:0 0 16px; color:#78716c; font-size:13px; line-height:1.5;">
                If the button doesn't work, copy and paste this link into your browser:
              </p>
              <p style="margin:0 0 24px; word-break:break-all; color:#f97316; font-size:13px;">
                {accept_url}
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="padding:20px 40px 28px; border-top:1px solid #f0ebe4;">
              <p style="margin:0; color:#a8a29e; font-size:12px; text-align:center;">
                You received this email because someone invited you to LunchTogether.<br>
                If you didn't expect this, you can safely ignore it.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

        await self.send_email(to_email, subject, html_body)

