# InspireWorks IVR Demo System

A multi-level Interactive Voice Response (IVR) system built with **Plivo Voice API** and **Flask**.

## 📋 Overview

This application demonstrates Plivo's Voice API capabilities by implementing:

1. **Outbound Call Initiation** - Trigger calls to any phone number via web UI
2. **Multi-level IVR Menu** - Two-level menu system with branching logic
3. **Language Selection** - Support for English and Spanish
4. **Audio Playback** - Play pre-recorded audio messages
5. **Call Forwarding** - Connect callers to live associates

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        IVR CALL FLOW                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   [Web UI] ──POST /make-call──▶ [Flask App] ──API──▶ [Plivo]       │
│                                                          │          │
│                                                          ▼          │
│                                              [Outbound Call to User]│
│                                                          │          │
│                                                          ▼          │
│                                               ┌─────────────────┐   │
│                                               │   LEVEL 1       │   │
│                                               │ Language Select │   │
│                                               │ 1=EN  2=ES      │   │
│                                               └────────┬────────┘   │
│                                                        │            │
│                                          ┌─────────────┴─────────┐  │
│                                          ▼                       ▼  │
│                                   ┌────────────┐          ┌────────────┐
│                                   │  LEVEL 2   │          │  LEVEL 2   │
│                                   │  English   │          │  Spanish   │
│                                   └─────┬──────┘          └─────┬──────┘
│                                         │                       │       │
│                                   ┌─────┴─────┐           ┌─────┴─────┐ │
│                                   ▼           ▼           ▼           ▼ │
│                               Press 1     Press 2     Press 1     Press 2
│                               Play Audio  Connect     Play Audio  Connect
│                                           to Agent                to Agent
└─────────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
inspireworks-ivr/
├── app.py              # Main Flask application with all IVR endpoints
├── .env                # Environment variables (credentials)
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Web UI to trigger outbound calls
└── README.md           # This file
```

## 🔧 Prerequisites

- Python 3.8+
- Plivo Account with Auth ID and Auth Token
- Plivo Phone Number (for caller ID)
- ngrok (for exposing local server to internet)

## 🚀 Setup Instructions

### 1. Clone/Download the Project

```bash
cd inspireworks-ivr
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate on Mac/Linux:
source venv/bin/activate

# Activate on Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Edit the `.env` file with your Plivo credentials:

```env
PLIVO_AUTH_ID=YOUR_AUTH_ID_HERE
PLIVO_AUTH_TOKEN=YOUR_AUTH_TOKEN_HERE
PLIVO_PHONE_NUMBER=+14692463990
ASSOCIATE_NUMBER=+918031274121
```

### 5. Start the Flask Server

```bash
python app.py
```

You should see:
```
============================================================
  InspireWorks IVR Demo System
============================================================
  Plivo Phone Number: +14692463990
  Associate Number:   +918031274121
============================================================
  Starting server on http://localhost:5000
  Use ngrok to expose: ngrok http 5000
============================================================
```

### 6. Expose with ngrok

In a **new terminal window**:

```bash
ngrok http 5000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

### 7. Test the Application

1. Open your browser: `http://localhost:5000`
2. Enter your phone number (with country code)
3. Click "Initiate Outbound Call"
4. Answer the call and interact with the IVR:
   - Press 1 for English, Press 2 for Spanish
   - Press 1 to hear audio, Press 2 to connect to associate

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI for triggering calls |
| `/make-call` | POST | Initiate outbound call |
| `/ivr/welcome` | GET | Level 1 - Language selection |
| `/ivr/language-handler` | POST | Handle language input |
| `/ivr/main-menu/<lang>` | GET | Level 2 - Main menu |
| `/ivr/menu-handler/<lang>` | POST | Handle menu selection |
| `/health` | GET | Health check |

## 🧪 Testing Scenarios

### Test 1: English → Audio Playback
1. Call is received
2. Press `1` (English)
3. Press `1` (Play audio)
4. Audio plays, call ends

### Test 2: Spanish → Connect to Associate
1. Call is received
2. Press `2` (Spanish)
3. Press `2` (Connect to associate)
4. Call forwards to associate number

### Test 3: Invalid Input Handling
1. Call is received
2. Press `5` (invalid)
3. "Invalid option" message plays
4. Menu repeats

### Test 4: No Input Timeout
1. Call is received
2. Don't press anything for 10 seconds
3. "No input received" message plays
4. Call ends gracefully

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| "Plivo API error" | Check Auth ID and Token in `.env` |
| "Call not received" | Ensure ngrok is running and URL is correct |
| "Invalid phone number" | Use format `+[country code][number]` |
| "Audio not playing" | Check if audio URL is accessible |

## 📊 Evaluation Criteria Coverage

| Criteria | Implementation |
|----------|----------------|
| ✅ API Integration | Plivo REST API for outbound calls |
| ✅ Outbound Calls | `/make-call` endpoint |
| ✅ Multi-level IVR | Level 1 (language) → Level 2 (action) |
| ✅ DTMF Handling | GetDigits with valid_digits parameter |
| ✅ Branching Logic | Language-based routing |
| ✅ Audio Playback | Play element with public MP3 |
| ✅ Call Forwarding | Dial element to associate |
| ✅ Error Handling | Invalid input and timeout handling |
| ✅ Frontend | Web UI for call triggering |

## 📝 Notes

- Audio files are hosted publicly on AWS S3 (Plivo's demo files)
- Associate number is configured in `.env`
- ngrok URL changes on restart (free tier) - update if needed
- For production, deploy to a cloud server with static URL

## 👤 Author

Built for Plivo Forward Deployed Engineer (FDE) Technical Assignment

## 📄 License

MIT License