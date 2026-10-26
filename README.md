# TANTO Process Manager (TPM)

A lightweight, standalone auto-restart script for **Battlefield 2142** dedicated servers on Windows. 

TPM monitors your game server (`BF2142_w32ded.exe`). If it crashes, TPM will automatically restart it, ensuring your server stays online 24/7.

## Features
- **Standalone:** Does not require any other panels or web apps.
- **Crash Protection:** Restarts the server if it closes unexpectedly.
- **Restart Limits:** Prevents infinite crash loops (e.g., max 5 restarts per hour).
- **Logging:** Saves game server output and TPM events to the `logs/` folder.
- **Easy Config:** All paths and settings are in a simple `config.yaml`.

## IMPORTANT WARNING
**You MUST create a `config.yaml` file.** 
If TPM cannot find `config.yaml`, it will use default paths (like `C:\Path\To\BF2142_w32ded.exe`) and will **not** be able to find or restart your server. It will just print a warning and do nothing.

## Installation

1. **Install Python 3.10+** on your server.
2. **Clone or download** this repository.
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt