# Nuke Installation Workflow - Following plan.md

## Complete Installation Workflow After Clicking "Start Installation"

### Pre-Installation
1. **User selects Nuke installer file** (.run or .tgz)
2. **Auto-detection finds:**
   - FLT7 .tgz file (searches all subdirectories including Crack/FLT7.1v1/)
   - rlm.foundry (from Crack folder)
   - foundry.set (from Crack folder)
   - xf_foundry.lic (from Crack folder)
3. **User clicks "Start Full Installation"**
4. **Sudo password prompt** (secure dialog)

---

### Installation Steps (Following plan.md exactly)

#### **STEPS 1-5: Install Nuke FIRST**

**Step 1-3:** Prepare Nuke installer
- `sudo chmod a+rwx Nuke14.v02.run` (or .tgz)
- `cd /Path/to/your_Nuke_Folder/`
- If .tgz: Extract first, then find .run installer

**Step 4:** Run Nuke installer
- `sudo ./Nuke14.v02.run` or `sudo bash Nuke14.v02.run`
- **User completes installer GUI** → Install to `/opt` folder

**Step 5:** Verify Nuke installed to `/opt` folder

---

#### **STEPS 6-10: Install FLT7 License Server (AFTER Nuke)**

**Step 6:** `cd /Path/to/your_FLT7_Folder/`
- Changes to directory where FLT7 .tgz file is located

**Step 7:** `tar xvzf FLT7.1v1-linux-x86-release-64.tgz`
- Extracts FLT7 archive in the same folder

**Step 8:** `cd FLT7.1v1-linux-x86-release-64RH`
- Finds extracted directory matching pattern
- Changes into extracted directory

**Step 9:** `sudo chmod a+rwx ./install.sh`
- Sets permissions on install.sh

**Step 10:** `sudo ./install.sh` or `sudo bash install.sh`
- Runs FLT7 installer
- Installs to `/usr/local/foundry/` (default location)

---

#### **STEPS 11-12: Manual License Server Shutdown**

**Step 11:** Open browser
- Opens Firefox to: `http://127.0.0.1:4102` or `4101` or `5053`
- Shows "Reprise License Server Administration" page

**Step 12:** User manually shuts down server
- Click "Shutdown" button
- Click "SHUT DOWN SERVER"
- Don't change "ISV" (should be "-all")
- Click OK in dialog to continue

---

#### **STEPS 13-20: Copy Crack Files**

**Step 13-16:** Remove existing files
- `sudo rm /usr/local/foundry/RLM/rlm.foundry`
- `sudo rm /usr/local/foundry/LicensingTools7.1/bin/RLM/rlm.foundry`
- `sudo rm /usr/local/foundry/RLM/foundry.set`
- `sudo rm /usr/local/foundry/LicensingTools7.1/bin/RLM/foundry.set`

**Step 17-18:** Copy rlm.foundry
- `sudo cp /Path/to/Crack_Folder/rlm.foundry /usr/local/foundry/RLM/rlm.foundry`
- `sudo cp /Path/to/Crack_Folder/rlm.foundry /usr/local/foundry/LicensingTools7.1/bin/RLM/rlm.foundry`

**Step 19-20:** Copy foundry.set
- `sudo cp /Path/to/Crack_Folder/foundry.set /usr/local/foundry/RLM/foundry.set`
- `sudo cp /Path/to/Crack_Folder/foundry.set /usr/local/foundry/LicensingTools7.1/bin/RLM/foundry.set`

---

#### **STEPS 21-22: Edit and Copy License File**

**Step 21:** Edit xf_foundry.lic
- Makes copy of license file from Crack folder (as per plan.md note)
- Gets HOST_NAME using `rlmutil rlmhostid host` (or system hostname)
- Gets MAC_ADDRESS using `rlmutil rlmhostid` (or system MAC)
- Replaces "HOST_NAME MAC_ADDRESS PORT" with actual values
- Example: "CXMA04 00f635v57202 4101"
- Saves edited copy

**Step 22:** Copy edited license file
- `sudo cp /Path/to/edited_xf_foundry.lic /usr/local/foundry/RLM/xf_foundry.lic`

---

#### **STEPS 23-25: Start License Server**

**Step 23:** Check status
- `sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM`

**Step 24:** Start server
- `sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s start -t RLM`

**Step 25:** Verify status
- `sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM`

---

#### **BONUS STEPS: Automation**

**Step 28-29:** Create startup script (if enabled)
- Creates script in `/etc/init.d/rlm-foundry-startup`
- Auto-starts license server on system boot

**Step 30-31:** Create nukex alias
- Adds `nukex()` function to `~/.bashrc`
- Function starts license server first, then launches Nuke

**Step 32-33:** Setup passwordless sudo (if enabled)
- Adds user to sudoers with NOPASSWD

---

## Installation Order Summary

1. ✅ **Install Nuke** (Steps 1-5) → `/opt/Nuke14.0v2/`
2. ✅ **Install FLT7** (Steps 6-10) → `/usr/local/foundry/`
3. ⏸️ **Manual: Shutdown license server** (Steps 11-12)
4. ✅ **Copy crack files** (Steps 13-20)
5. ✅ **Edit & copy license file** (Steps 21-22)
6. ✅ **Start license server** (Steps 23-25)
7. ✅ **Create nukex alias** (Bonus)
8. ✅ **Create startup script** (Bonus, if enabled)

---

## After Installation

**To run Nuke:**
```bash
nukex
```

This will:
1. Start license server (steps 23-25)
2. Launch Nuke from `/opt/Nuke14.0v2/`

**Or manually:**
```bash
sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s start -t RLM
cd /opt/Nuke14.0v2/
./Nuke14.0 &
```

