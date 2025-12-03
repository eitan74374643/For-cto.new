# VoiceSnap - Voice Message Summarizer

## Overview
VoiceSnap is a mobile application designed to transcribe and summarize voice messages shared from other apps (WhatsApp, Telegram, etc.).

## Technology Stack
- **Framework**: React Native (Expo)
  - Chosen for rapid development, ease of cross-platform support (Android + iOS), and strong ecosystem.
- **Language**: TypeScript
- **State Management**: Zustand
- **Local Storage**: SQLite (via `expo-sqlite`)
- **API Integration**: Axios (to OpenAI/Gemini)

## Architecture

### Backend Recommendation
For the MVP, we are using a **Client-Side Only** approach with direct API calls.
For Production (v1.0), we recommend a **Serverless Backend**:
- **Firebase Functions** or **AWS Lambda**: To hide API keys and handle rate limiting.
- **Middleware**: Receive audio -> Upload to Storage -> Trigger Transcription -> Trigger Summarization -> Return Result.

### Folder Structure
```
/src
  /components     # Reusable UI components
  /screens        # Application screens
  /navigation     # Navigation configuration
  /services       # Logic for API, Storage, Audio
  /store          # Global state management
  /types          # TypeScript definitions
  /utils          # Helper functions
```

## Features Implemented (Scaffolding)
- **Home Screen**: File picker to test audio processing manually.
- **History Screen**: Local database of processed messages.
- **Summary Screen**: View transcription and summary.
- **Services**: 
  - `StorageService`: Saves messages to local SQLite DB.
  - `AIService`: Mock implementation of Transcription and Summarization (ready for API keys).

## Next Steps for MVP v1.0

1. **Share Intent Integration**:
   - Configure `expo-share-intent` or native android/ios config to receive files from other apps.
   - Update `HomeScreen` or `App.tsx` to listen for incoming intents on startup.

2. **API Integration**:
   - Get an OpenAI API Key.
   - Uncomment the code in `src/services/ai.ts`.
   - Implement `transcribeAudio` using OpenAI Whisper API.
   - Implement `summarizeText` using OpenAI GPT-3.5/4.

3. **UI/UX Refinement**:
   - Add Audio Playback controls in `SummaryScreen`.
   - Improve styling with a library like `react-native-paper` or `tamagui`.

4. **Testing**:
   - Test on real devices (Android/iOS) to verify file access permissions and sharing intent reception.

## Complexity & Cost Estimates
- **Complexity**: Medium. The hardest part is handling file permissions and share intents reliably across different Android versions.
- **Cost**:
  - **Whisper API**: ~$0.006 / minute. 1000 mins = $6.
  - **GPT-3.5 Turbo**: Very cheap for short summaries. ~$0.002 / 1k tokens.
  - **Monthly Est (100 active users)**: ~$10-20/month depending on usage.

## Development Commands
- `npm start`: Start the Expo development server.
- `npm run android`: Run on Android emulator.
- `npm run ios`: Run on iOS simulator (requires Mac).
