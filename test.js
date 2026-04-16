import axios from "axios";
import dotenv from "dotenv";
import fs from "fs";
import yaml from "js-yaml";
import csv from "csv-parser";

dotenv.config();

const webhookUrl = process.env.SLACK_WEBHOOK_URL;
const config = yaml.load(fs.readFileSync("config.yaml", "utf8"));

const threshold = config.detection.fixed_threshold;
const filePath = config.input.file;

async function sendSlackAlert(message) {
  await axios.post(webhookUrl, { text: message });
}

async function processCSV() {
  const rows = [];

  return new Promise((resolve, reject) => {
    fs.createReadStream(filePath)
      .pipe(csv())
      .on("data", (row) => rows.push(row))
      .on("end", async () => {
        console.log(`📊 Total rows: ${rows.length}`);

        for (const row of rows) {
          const loss = parseFloat(row[config.input.loss_column]);

          console.log("Checking loss:", loss);

          if (loss > threshold) {
            const msg = `🚨 ALERT!
Service: ${config.labels.service}
Env: ${config.labels.env}
Loss: ${loss} > Threshold: ${threshold}`;

            console.log("🚨 Sending alert...");
            await sendSlackAlert(msg);
          }
        }

        resolve();
      })
      .on("error", reject);
  });
}

console.log("🚀 Running anomaly detection...");
await processCSV();
console.log("✅ Done");