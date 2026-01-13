# ArtStyleTransfer (Feather)

**ArtStyleTransfer** is a  mobile image editing application built with React Native and Expo. It leverages  AI models for semantic image editing, art style transfer, and intelligent prompt assistance.

Experience  yourself ( live apk link ) : https://drive.google.com/file/d/1nICpp2gTIEjmFVx9OHsYsuKafsVAi3dM/view 

## ✨ Key Features

- **🎨 Art Style Transfer**: Transform your photos into masterpieces using curated art styles (powered by SDXL).
- **🧠 Smart Adjust**: Edit images using natural language prompts (e.g., "Make the sky more dramatic", "Remove the bird").
- **👻 Ghost Text & Refine**: 
  - **Real-time Autocomplete**: Get suggestions as you type.
  - **Prompt Refinement**: Enhance your simple prompts into detailed, descriptive instructions using **Google Gemini**.
- **🖼️ Infinite Canvas**: Zoom, pan, and explore your creations with a fluid, infinite UI.
- **💡 Smart Suggestions**: Context-aware editing suggestions based on your image's content.

## 🏗️ Architecture

The project is divided into a mobile client and cloud-based backend services.

### Mobile Client (`/`)
Built with **React Native** and **Expo**.
- **State Management**: React Hooks & Context.
- **AI Integration**: 
  - On-device logic for Ghost suggestions.
  - Google Gemini API for prompt refinement and smart suggestions.
- **Image Processing**: `expo-gl` for real-time filters.

### Backend Services (`/backend`)
Cloud microservices deployed on **Modal**.
- **`photo_art_agent`**: Handling semantic editing and complex workflows.
- **`match_art_style`**: Generating stylized images using SDXL.
> See [`backend/README.md`](backend/README.md) for more details.

### Local Server (`main.py`)
A fast, local Python server (FastAPI) used for testing local LLM capabilities and serving specific local features.

## 🚀 Getting Started

### Prerequisites
- Node.js & npm/yarn
- Expo CLI
- Python 3.10+ (for local backend)
- Android Studio / Xcode (for simulators)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd ArtStyleTransfer
   ```

2. **Install Client Dependencies**
   ```bash
   npm install
   ```

3. **Configure Environment**
   Create a `.env` file in the root directory:
   ```env
   EXPO_PUBLIC_GOOGLE_API_KEY=your_gemini_api_key
   ```

4. **Run the App**
   ```bash
   npm start
   # then press 'a' for Android or 'i' for iOS
   ```

## 🛠️ Development Workflow

- **Frontend**: Edit files in `app/`, `components/`, and `hooks/`.
- **Backend Refine**: The "Refine" feature now uses the Google Gemini API directly (`hooks/useRefinePrompt.js`), removing the strict dependency on the local Python server for this feature.
- **Deployment**: Backend services are deployed to Modal. See `backend/README.md`.

## � Tech Stack

- **Framework**: React Native, Expo SDK 54
- **Language**: JavaScript/JSX, Python
- **AI Models**: 
  - Google Gemini (Flash 1.5/2.5) via API
  - Llama 3.2 (Local/Executorch)
  - SDXL (Cloud)
- **Styling**: Custom Theme system (`constants/Theme.js`)

## 🤝 Contributing

This is a private repository. Please contact the maintainer for access.
