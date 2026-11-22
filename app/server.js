
const express = require("express");
const { MongoClient } = require("mongodb");
const os = require("os");

const app = express();

const PORT = process.env.PORT || 3000;
const MONGO_URL = process.env.MONGO_URL;

let db;

app.use(express.json());
app.use(express.static("public"));

// Connect to MongoDB
async function connectDB() {
    if (!MONGO_URL) {
        throw new Error("MONGO_URL environment variable is missing");
    }

    const client = new MongoClient(MONGO_URL, {
        serverSelectionTimeoutMS: 5000
    });

    await client.connect();
    db = client.db("emidb");

    console.log("Connected to MongoDB successfully");
}

// Get pod name and IP
function getPodInfo() {
    const interfaces = os.networkInterfaces();

    let podIP = process.env.POD_IP;

    if (!podIP) {
        for (const addresses of Object.values(interfaces)) {
            const found = addresses.find(
                address => address.family === "IPv4" && !address.internal
            );

            if (found) {
                podIP = found.address;
                break;
            }
        }
    }

    return {
        name: process.env.HOSTNAME || os.hostname(),
        ip: podIP || "Unknown"
    };
}

// EMI Calculator API
app.post("/api/emi", async (req, res) => {
    try {
        const { P, rate, n } = req.body;

        const principal = Number(P);
        const annualRate = Number(rate);
        const months = Number(n);

        if (
            !Number.isFinite(principal) ||
            !Number.isFinite(annualRate) ||
            !Number.isSafeInteger(months) ||
            principal <= 0 ||
            annualRate <= 0 ||
            months <= 0
        ) {
            return res.status(400).json({
                error: "Please enter positive valid numbers for all fields."
            });
        }

        if (!db) {
            return res.status(503).json({
                error: "Database is unavailable"
            });
        }

        const r = annualRate / 12 / 100;

        const emi =
            principal * r * Math.pow(1 + r, months) /
            (Math.pow(1 + r, months) - 1);

        const totalPayment = emi * months;
        const totalInterest = totalPayment - principal;

        const pod = getPodInfo();

        const calculation = {
            principal,
            rate: annualRate,
            months,
            emi: Number(emi.toFixed(2)),
            servedBy: pod.name,
            servedByIP: pod.ip,
            createdAt: new Date()
        };

        await db.collection("calculations").insertOne(calculation);

        res.json({
            emi: calculation.emi,
            totalPayment: Number(totalPayment.toFixed(2)),
            totalInterest: Number(totalInterest.toFixed(2)),
            servedBy: pod.name,
            servedByIP: pod.ip
        });

    } catch (error) {
        console.error("EMI calculation error:", error);
        res.status(500).json({ error: "Calculation failed" });
    }
});

// Get last 10 calculations
app.get("/api/history", async (req, res) => {
    try {
        const history = await db.collection("calculations")
            .find({})
            .sort({ createdAt: -1, _id: -1 })
            .limit(10)
            .toArray();

        res.json(history);

    } catch (error) {
        console.error("History error:", error);
        res.status(500).json({ error: "Unable to retrieve history" });
    }
});

// Health check
app.get("/health", async (req, res) => {
    try {
        if (!db) {
            return res.status(503).json({ status: "Database unavailable" });
        }

        await db.command({ ping: 1 });

        res.status(200).json({ status: "healthy" });

    } catch (error) {
        res.status(503).json({ status: "unhealthy" });
    }
});

// Start server after database connection
connectDB()
    .then(() => {
        app.listen(PORT, "0.0.0.0", () => {
            console.log(`EMI Calculator running on port ${PORT}`);
        });
    })
    .catch(error => {
        console.error("MongoDB connection failed:", error);
        process.exit(1);
    });
