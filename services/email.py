import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import settings

async def build_welcome_email(username: str, to_email: str) ->MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["From"] = settings().EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = "Welcome to InkCode"
    msg["Reply"] = settings().EMAIL_FROM
    plain_text = f"""
        Hi {username},

        Welcome to InkCode.
        
        We're delighted to have you join our community.
        
        Your account has been successfully created and you're all set to begin your journey with us.
        
        Whether you're here to share your ideas, publish your work, or discover perspectives from other writers, we're excited to be a part of that experience.
        
        To get started, you can explore InkCode here:
        
        https://inkcode-production.up.railway.app/docs
        
        If you have any questions or need assistance, simply reply to this email and our team will be happy to help.
        
        Thank you for choosing InkCode.
        
        Warm regards,
        
        The InkCode Team
    """

    html = f"""
        <!DOCTYPE html>

        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to InkCode</title>
        </head>

        <body style="margin:0;padding:0;background:#f5f7fb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">

            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f5f7fb;padding:40px 20px;">
            <tr>
            <td align="center">

            <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;">

            <tr>
            <td style="padding:48px 48px 24px 48px;">

            <h1 style="margin:0;font-size:32px;font-weight:700;color:#111827;">
            Welcome to InkCode
            </h1>

            </td>
            </tr>

            <tr>
            <td style="padding:0 48px;">

            <p style="margin:0 0 24px 0;font-size:16px;line-height:28px;color:#374151;">
            Hi <strong>{username}</strong>,
            </p>

            <p style="margin:0 0 24px 0;font-size:16px;line-height:28px;color:#374151;">
            We're delighted to welcome you to InkCode.
            </p>

            <p style="margin:0 0 24px 0;font-size:16px;line-height:28px;color:#374151;">
            Your account has been successfully created, and you're now ready to start exploring, writing, and connecting with the community.
            </p>

            <p style="margin:0 0 32px 0;font-size:16px;line-height:28px;color:#374151;">
            We're excited to have you with us and look forward to seeing what you'll create.
            </p>

            </td>
            </tr>

            <tr>
            <td align="center" style="padding:0 48px 40px 48px;">

            <a href="https://inkcode-production.up.railway.app/docs"
            style="background:#2563eb;
                   color:#ffffff;
                   text-decoration:none;
                   padding:14px 32px;
                   border-radius:8px;
                   font-size:15px;
                   font-weight:600;
                   display:inline-block;">
            Get Started </a>

            </td>
            </tr>

            <tr>
            <td style="padding:32px 48px;border-top:1px solid #e5e7eb;">

            <p style="margin:0;font-size:15px;line-height:26px;color:#6b7280;">
            Thank you for choosing InkCode.
            </p>

            <p style="margin:8px 0 0 0;font-size:15px;line-height:26px;color:#6b7280;">
            The InkCode Team
            </p>

            </td>
            </tr>

            </table>

            </td>
            </tr>
            </table>

        </body>
        </html>

    """
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html, "html"))
    return msg



async def build_opt_email(to_email:str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "OPT"
    msg["From"] = settings().EMAIL_FROM
    msg["To"] = to_email
    msg["Reply"] = settings().EMAIL_FROM
    plain_text = f"""
        Hello,

        Welcome back to InkCode 👋

        Your login OTP is: "otp"
        This code is valid for a short time and can be used only once. If this wasn’t you, please ignore this message.
        Need help? Reach us at {settings().EMAIL_FROM}

        Regards,
        InkCode
    """

    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>InkCode Login OTP</title>
        </head>

        <body style="margin:0;padding:0;background:#f5f7fb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">

            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f5f7fb;padding:40px 20px;">
                <tr>
                    <td align="center">

                        <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;">

                            <tr>
                                <td style="padding:48px 48px 24px 48px;">
                                    <h1 style="margin:0;font-size:32px;font-weight:700;color:#111827;">
                                        Welcome Back 👋
                                    </h1>
                                </td>
                            </tr>

                            <tr>
                                <td style="padding:0 48px;">

                                    <p style="margin:0 0 24px 0;font-size:16px;line-height:28px;color:#374151;">
                                        Hello,
                                    </p>

                                    <p style="margin:0 0 24px 0;font-size:16px;line-height:28px;color:#374151;">
                                        We received a login request for your InkCode account.
                                    </p>

                                    <p style="margin:0 0 16px 0;font-size:16px;line-height:28px;color:#374151;">
                                        Use the following One-Time Password (OTP) to complete your login:
                                    </p>

                                </td>
                            </tr>

                            <tr>
                                <td align="center" style="padding:0 48px 32px 48px;">

                                    <div style="
                                        background:#eff6ff;
                                        border:1px solid #bfdbfe;
                                        border-radius:10px;
                                        padding:20px 32px;
                                        display:inline-block;
                                        font-size:32px;
                                        font-weight:700;
                                        letter-spacing:8px;
                                        color:#2563eb;">
                                        "OPT"///////////////////////////////////////////////
                                    </div>

                                </td>
                            </tr>

                            <tr>
                                <td style="padding:0 48px 32px 48px;">

                                    <p style="margin:0 0 16px 0;font-size:15px;line-height:26px;color:#6b7280;">
                                        This code is valid for a short time and can be used only once.
                                    </p>

                                    <p style="margin:0;font-size:15px;line-height:26px;color:#6b7280;">
                                        If this wasn't you, please ignore this email. No action will be taken without successful verification.
                                    </p>

                                </td>
                            </tr>

                            <tr>
                                <td style="padding:32px 48px;border-top:1px solid #e5e7eb;">

                                    <p style="margin:0;font-size:15px;line-height:26px;color:#6b7280;">
                                        Need help? Contact us at
                                        <a href="mailto:{settings().EMAIL_FROM}"
                                        style="color:#2563eb;text-decoration:none;">
                                            {settings().EMAIL_FROM}
                                        </a>
                                    </p>

                                    <p style="margin:12px 0 0 0;font-size:15px;line-height:26px;color:#6b7280;">
                                        Regards,<br>
                                        <strong>InkCode</strong>
                                    </p>

                                </td>
                            </tr>

                        </table>

                    </td>
                </tr>
            </table>

        </body>
        </html>
    """
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html, "html"))
    return msg



async def send_welcome_email(msg: MIMEMultipart, username: str, to_email: str, ):
    try:
        await aiosmtplib.send(
            msg,
            hostname=settings().EMAIL_HOST,
            port=settings().EMAIL_PORT,
            start_tls=True,
            username=settings().EMAIL_USERNAME,
            password=settings().EMAIL_PASSWORD,
            recipients=[to_email]
        )
    except Exception as e:
        print(f"Error: {e}")

