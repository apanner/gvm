# Nuke Installation Automation for Linux

This project provides automated installation scripts for Nuke on Linux systems (tested on Ubuntu 24.04).

## Features

- **Fully Automated GUI Installer** - Complete automation of all installation steps
- **Single File Selection** - Just select the Nuke .run file, script auto-detects other files
- **Sudo Password Management** - Secure password handling for all sudo operations
- **Auto License Generation** - Automatically creates license file with system info
- **Auto Alias Creation** - Creates 'nukex' command to easily start Nuke
- **Real-time Progress Logging** - See all installation steps in real-time
- **Standalone bash script** - Command-line alternative for automation

## Requirements

- Linux system (Ubuntu 24.04 or compatible)
- Python 3 with tkinter (for GUI)
- sudo privileges
- Required files:
  - Nuke `.run` installer file
  - FLT7 `.tgz` archive
  - `rlm.foundry` file
  - `foundry.set` file
  - `xf_foundry.lic` license file (or template to edit)

## Installation Methods

### Method 1: GUI Installer (Recommended)

1. Make the script executable:
```bash
chmod +x nuke_installer_gui.py
```

2. Run the GUI installer (from terminal to see console logs):
```bash
python3 nuke_installer_gui.py
```

**Tip**: Run from terminal to see real-time console output with colored logs:
- ✅ Green = Success messages
- ⚠️ Yellow = Warnings
- ❌ Red = Errors
- Regular = Info messages

3. Follow the GUI steps:
   - **Set Sudo Password**: Enter your sudo password and click "Set Password"
   - **Select Nuke File**: Browse and select the Nuke .run file (or select the folder containing all files)
   - **Auto-detect Files**: Click "Auto-detect Files" to find FLT7, rlm.foundry, and foundry.set
   - **Verify System Info**: Check that hostname and MAC address are detected correctly
   - **Configure Options**: Set installation path (default: `/opt`) and Nuke version
   - **Start Installation**: Click "Start Full Installation" - all steps execute automatically!
   - **Manual Step**: When prompted, shut down the license server via web browser
   - **Done**: Use `nukex` command to start Nuke anytime!

### Method 2: Standalone Bash Script

1. Make the script executable:
```bash
chmod +x install_nuke_standalone.sh
```

2. Run the script:
```bash
./install_nuke_standalone.sh
```

3. Follow the prompts to provide file paths and configuration

## License File Configuration

The license file (`xf_foundry.lic`) needs to contain your system information:

1. **Hostname**: Get it using `hostname` command
2. **MAC Address**: Get it using `ip link show` or the GUI's "Get MAC Address" button
3. **Port**: Usually `4101`

Example license file format:
```
HOST_NAME MAC_ADDRESS 4101
```

For example:
```
CXMA04 00f635v57202 4101
```

**Note**: The MAC address should be without colons (remove `:` characters).

## Running Nuke After Installation

After installation, a `nukex` function is automatically added to your `~/.bashrc`. Simply run:

```bash
nukex
```

This will:
1. Start the license server
2. Launch Nuke automatically

**Note**: If you just installed, you may need to restart your terminal or run:
```bash
source ~/.bashrc
```

Alternatively, you can use the provided script:
```bash
chmod +x start_nuke.sh
./start_nuke.sh
```

Or manually run:
```bash
sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM
sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s start -t RLM
sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM
cd /opt/Nuke14.0v2/
./Nuke14.0 &
```

## Installation Steps (Automated)

The script automates these steps:

1. **Install Nuke** - Runs the Nuke installer
2. **Install FLT7 License Server** - Extracts and installs the license server
3. **Shutdown License Server** - Prompts you to manually shut down via web interface
4. **Copy Crack Files** - Replaces license files with provided files
5. **Copy License File** - Installs your license file
6. **Start License Server** - Starts the license server with new configuration

## Troubleshooting

### GUI doesn't start
- Make sure Python 3 and tkinter are installed:
  ```bash
  sudo apt-get install python3-tk
  ```

### Permission denied
- Make sure scripts are executable:
  ```bash
  chmod +x *.sh *.py
  ```

### License server won't start
- Check if the license file is correctly formatted
- Verify MAC address and hostname are correct
- Check license server logs:
  ```bash
  sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM
  ```

### Can't find Nuke after installation
- Check the installation path (default: `/opt`)
- Look for Nuke directory:
  ```bash
  ls -la /opt/Nuke*
  ```

## Files

- `nuke_installer_gui.py` - GUI-based installer (Python/tkinter)
- `install_nuke_standalone.sh` - Standalone bash script installer
- `start_nuke.sh` - Quick script to start license server and Nuke
- `plan.md` - Original manual installation instructions

## Notes

- The installation process requires manual intervention at step 11-12 (shutting down the license server via web interface)
- You need sudo privileges for the installation
- The license server must be started every time before running Nuke
- Tested on Ubuntu 24.04, should work on other Linux distributions

## Support

If you encounter issues:
1. Check the installation log in the GUI
2. Verify all file paths are correct
3. Ensure you have the correct version of all required files
4. Check system requirements and dependencies

