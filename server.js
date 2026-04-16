import express from "express";
import axios from "axios";
import dotenv from "dotenv";

dotenv.config();

const app = express();
app.use(express.json());

const webhookUrl = process.env.SLACK_WEBHOOK_URL;

// Health check
app.get("/", (req, res) => {
  res.send("🚀 Alert API is running");
});

// Send alert API
app.post("/alert", async (req, res) => {
  try {
    const { message, loss } = req.body;

    if (!message && !loss) {
      return res.status(400).json({
        error: "Provide message or loss"
      });
    }

    let finalMessage = message;

    // If loss is provided → generate message
    if (loss) {
      finalMessage = `🚨 ALERT!
Loss: ${loss}`;
    }

    await axios.post(webhookUrl, {
      text: finalMessage
    });

    res.json({
      success: true,
      message: "Alert sent to Slack"
    });

  } catch (error) {
    console.error(error.message);

    res.status(500).json({
      error: "Failed to send alert"
    });
  }
});

// Start server
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`🔥 Server running on http://localhost:${PORT}`);
});