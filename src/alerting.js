import nodemailer from "nodemailer";
import dotenv from "dotenv";
dotenv.config();



// ✅ Slack Alert
export const sendSlackAlert = async (message) => {
  await fetch(process.env.SLACK_WEBHOOK_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: message }),
  });
};

// ✅ Email Alert
export const sendEmailAlert = async (subject, message) => {
  const transporter = nodemailer.createTransport({
    service: "gmail",
    auth: {
      user: process.env.ALERT_EMAIL,
      pass: process.env.ALERT_EMAIL_PASSWORD, // <-- App Password
    },
  });

  await transporter.sendMail({
    from: `Alert Bot <${process.env.ALERT_EMAIL}>`,
    to: process.env.ALERT_EMAIL,
    subject,
    text: message,
  });
};

// ✅ Send both together
export const sendAlert = async (msg) => {
  await sendSlackAlert(msg);
  await sendEmailAlert("⚠ Alert Notification", msg);
};

