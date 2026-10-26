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
   
## Configure:

Copy config.example.yaml to config.yaml.

Open config.yaml and set the real paths for your server.

Example config block:
```yaml
process:
  enabled: true
  exe_path: "C:/Program Files (x86)/Electronic Arts/Battlefield 2142 Server/BF2142_w32ded.exe"
  work_dir: "C:/Program Files (x86)/Electronic Arts/Battlefield 2142 Server"
  args: ["+config", "mods/bf2142/settings/serversettings.con", "+maplist", "mods/bf2142/settings/maplist.con", "+dedicated"]
```

Run:
```bash
python tantopm.py 
```

## How it works

TPM checks if BF2142_w32ded.exe is running every 10 seconds.

If the process is missing, it waits 15 seconds (configurable) and starts it using the arguments provided in config.yaml.

If the server crashes 5 times within an hour, TPM will stop restarting it to prevent spam.

## Note
If you are using TANTO Control Deck (TCD) on the same machine, you can enable the built-in Process Manager in config.yaml instead of running TPM separately.
