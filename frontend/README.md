# Speech Processing Frontend

Desktop application built with Tauri + React + TypeScript for speech-to-text transcription.

## Features

- Drag-and-drop file upload
- Real-time transcription progress
- Multiple model sizes (tiny to large)
- Language selection
- Export to TXT, JSON, SRT formats
- Native desktop performance with minimal bundle size

## Prerequisites

- Node.js 18 or higher
- Rust 1.70 or higher
- npm or yarn

## Installation

```bash
# Install dependencies
npm install

# Copy environment configuration
cp .env.example .env
```

## Configuration

Edit `.env` to configure the backend API URL:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Development

```bash
# Run in development mode (with hot reload)
npm run tauri:dev

# Run web version only (without Tauri)
npm run dev
```

The development app will open automatically. Changes to React components will hot-reload.

## Building

```bash
# Build for your current platform
npm run tauri:build

# Build for specific platforms
npm run tauri:build -- --target universal-apple-darwin  # macOS
npm run tauri:build -- --target x86_64-pc-windows-msvc  # Windows
npm run tauri:build -- --target x86_64-unknown-linux-gnu  # Linux
```

Built applications will be in `src-tauri/target/release/bundle/`

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── FileUploader.tsx    # File upload interface
│   │   └── TranscriptionView.tsx  # Results display
│   ├── services/            # API clients
│   │   ├── api.ts              # Base API client
│   │   └── transcription.ts     # Transcription API calls
│   ├── stores/              # State management
│   │   └── transcription.ts     # Transcription state
│   ├── types/               # TypeScript definitions
│   │   └── api.ts              # API types
│   ├── styles/              # CSS styles
│   │   └── globals.css         # Global styles
│   ├── App.tsx              # Main app component
│   └── main.tsx             # Entry point
├── src-tauri/               # Tauri/Rust code
│   ├── src/
│   │   └── main.rs             # Tauri entry point
│   ├── Cargo.toml              # Rust dependencies
│   └── tauri.conf.json         # Tauri configuration
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Tech Stack

- **Tauri**: Native desktop framework (Rust + WebView)
- **React 18**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Utility-first CSS
- **Zustand**: State management
- **Axios**: HTTP client

## Available Scripts

- `npm run dev` - Start Vite dev server
- `npm run build` - Build web assets
- `npm run preview` - Preview production build
- `npm run tauri` - Run Tauri CLI
- `npm run tauri:dev` - Start Tauri development mode
- `npm run tauri:build` - Build Tauri app for production
- `npm run lint` - Lint code with ESLint
- `npm run format` - Format code with Prettier

## Troubleshooting

### Tauri build fails

Ensure Rust is installed:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup update
```

### Backend connection fails

1. Ensure backend is running at the URL specified in `.env`
2. Check CORS settings in backend
3. Verify firewall allows connections

### Dependencies fail to install

Try clearing the cache:
```bash
rm -rf node_modules package-lock.json
npm install
```

## License

[Specify your license here]
