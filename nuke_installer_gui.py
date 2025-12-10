#!/usr/bin/env python3
"""
Nuke Installation GUI - Fully Automated Installer for Linux
This GUI automates the complete Nuke installation process on Linux systems.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
import sys
import threading
import re
import socket
import getpass
from pathlib import Path
import shutil
from datetime import datetime


class NukeInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Nuke Installation Wizard - Fully Automated")
        self.root.geometry("850x750")
        self.root.resizable(True, True)
        
        # Center the window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # File paths
        self.nuke_run_file = tk.StringVar()
        self.install_folder = tk.StringVar()
        self.sudo_password = None
        self.install_path = tk.StringVar(value="/opt")
        self.nuke_version = tk.StringVar(value="14.0v2")
        
        # Detected files
        self.detected_files = {
            'flt7_tgz': None,
            'rlm_foundry': None,
            'foundry_set': None,
            'license_file': None,  # xf_foundry.lic
            'crack_folder': None,  # Path to crack folder
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Nuke Installation Wizard", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Sudo password info
        sudo_frame = ttk.LabelFrame(main_frame, text="System Access", padding="10")
        sudo_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        sudo_frame.columnconfigure(0, weight=1)
        
        info_label = ttk.Label(sudo_frame, 
                              text="⚠ You will be prompted for sudo password when installation starts (secure prompt)",
                              foreground="blue", font=("Arial", 9))
        info_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(1, weight=1)
        
        # Nuke installer file (.run or .tgz)
        ttk.Label(file_frame, text="Nuke Installer File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.nuke_run_file, width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(file_frame, text="Browse", 
                  command=self.browse_nuke_file).grid(row=0, column=2, padx=5)
        ttk.Label(file_frame, text="(.run or .tgz)", 
                 font=("Arial", 7), foreground="gray").grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # Or select folder
        ttk.Label(file_frame, text="OR Select Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.install_folder, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(file_frame, text="Browse Folder", 
                  command=self.browse_folder).grid(row=1, column=2, padx=5)
        
        ttk.Button(file_frame, text="Auto-detect Files", 
                  command=self.auto_detect_files).grid(row=2, column=1, pady=10, sticky=tk.W)
        
        # Detected files display
        detected_frame = ttk.LabelFrame(main_frame, text="Detected Files", padding="10")
        detected_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        detected_frame.columnconfigure(1, weight=1)
        
        self.detected_labels = {}
        row = 0
        
        # FLT7 .tgz
        ttk.Label(detected_frame, text="FLT7 .tgz:").grid(row=row, column=0, sticky=tk.W, pady=2)
        label = ttk.Label(detected_frame, text="Not found", foreground="red")
        label.grid(row=row, column=1, sticky=tk.W, padx=5)
        self.detected_labels['flt7_tgz'] = label
        row += 1
        
        # rlm.foundry
        ttk.Label(detected_frame, text="rlm.foundry:").grid(row=row, column=0, sticky=tk.W, pady=2)
        label = ttk.Label(detected_frame, text="Not found", foreground="red")
        label.grid(row=row, column=1, sticky=tk.W, padx=5)
        self.detected_labels['rlm_foundry'] = label
        ttk.Label(detected_frame, text="(License server binary)", 
                 font=("Arial", 7), foreground="gray").grid(row=row, column=2, sticky=tk.W, padx=5)
        row += 1
        
        # foundry.set
        ttk.Label(detected_frame, text="foundry.set:").grid(row=row, column=0, sticky=tk.W, pady=2)
        label = ttk.Label(detected_frame, text="Not found", foreground="red")
        label.grid(row=row, column=1, sticky=tk.W, padx=5)
        self.detected_labels['foundry_set'] = label
        ttk.Label(detected_frame, text="(RLM settings/config file)", 
                 font=("Arial", 7), foreground="gray").grid(row=row, column=2, sticky=tk.W, padx=5)
        row += 1
        
        # License file
        ttk.Label(detected_frame, text="xf_foundry.lic:").grid(row=row, column=0, sticky=tk.W, pady=2)
        label = ttk.Label(detected_frame, text="Not found", foreground="red")
        label.grid(row=row, column=1, sticky=tk.W, padx=5)
        self.detected_labels['license_file'] = label
        ttk.Label(detected_frame, text="(License file - will be auto-edited)", 
                 font=("Arial", 7), foreground="gray").grid(row=row, column=2, sticky=tk.W, padx=5)
        row += 1
        
        # License file info
        license_frame = ttk.LabelFrame(main_frame, text="License File (Auto-generated)", padding="10")
        license_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        license_frame.columnconfigure(1, weight=1)
        
        ttk.Label(license_frame, text="Hostname:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.hostname_label = ttk.Label(license_frame, text="", font=("Arial", 9, "bold"))
        self.hostname_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(license_frame, text="MAC Address:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.mac_label = ttk.Label(license_frame, text="", font=("Arial", 9, "bold"))
        self.mac_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Button(license_frame, text="Refresh System Info", 
                  command=self.refresh_system_info).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Installation options
        options_frame = ttk.LabelFrame(main_frame, text="Installation Options", padding="10")
        options_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        options_frame.columnconfigure(1, weight=1)
        
        ttk.Label(options_frame, text="Install Path:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(options_frame, textvariable=self.install_path, width=30).grid(
            row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(options_frame, text="Nuke Version:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(options_frame, textvariable=self.nuke_version, width=30).grid(
            row=1, column=1, sticky=tk.W, padx=5)
        
        # Additional options
        self.create_startup_script = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Create startup script in /etc/init.d (auto-start license server on boot)", 
                       variable=self.create_startup_script).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.setup_passwordless_sudo = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Setup passwordless sudo (optional - for convenience)", 
                       variable=self.setup_passwordless_sudo).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Progress/Log section - Terminal style
        log_frame = ttk.LabelFrame(main_frame, text="Installation Log (Terminal Output)", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Create terminal-style console text widget with visible scrollbar
        # ScrolledText automatically includes a scrollbar
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=10,  # Reduced height to ensure scrollbar is visible
            width=75,
            bg='#0d1117',  # Dark background (terminal black - GitHub dark style)
            fg='#c9d1d9',  # Light gray text (better readability)
            insertbackground='#00ff00',  # Green cursor
            font=('Consolas', 9),  # Slightly smaller font
            wrap=tk.WORD,
            relief=tk.SUNKEN,
            borderwidth=2,
            padx=10,
            pady=10,
            state=tk.NORMAL,  # Allow text insertion
            selectbackground='#264f78',  # Selection background
            selectforeground='#ffffff',  # Selection text color
            insertwidth=2,  # Cursor width
            spacing1=1,  # Line spacing
            spacing2=1,
            spacing3=1
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Ensure scrollbar is always visible and functional
        # ScrolledText handles scrollbar automatically, but we can force it to show
        self.log_text.see(tk.END)  # Scroll to bottom initially
        
        # Make it read-only for console-like behavior (but allow selection for copying)
        def make_readonly(event=None):
            # Allow selection and copying, but prevent editing
            if event.keysym in ['BackSpace', 'Delete']:
                return 'break'
            if event.char and event.state == 0:  # Normal typing
                return 'break'
        
        self.log_text.bind('<Key>', make_readonly)
        self.log_text.bind('<Button-1>', lambda e: self.log_text.focus_set())
        
        # Right-click context menu for copy
        context_menu = tk.Menu(self.log_text, tearoff=0)
        context_menu.add_command(label="Copy", command=lambda: self.log_text.event_generate("<<Copy>>"))
        context_menu.add_command(label="Select All", command=lambda: self.log_text.tag_add(tk.SEL, "1.0", tk.END))
        context_menu.add_command(label="Clear", command=self.clear_log)
        
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        self.log_text.bind("<Button-3>", show_context_menu)  # Right-click
        
        # Configure text tags for colored output (terminal colors)
        self.log_text.tag_config("SUCCESS", foreground="#00ff00", font=('Consolas', 10, 'bold'))  # Green
        self.log_text.tag_config("ERROR", foreground="#ff6b6b", font=('Consolas', 10, 'bold'))    # Red
        self.log_text.tag_config("WARNING", foreground="#ffd93d", font=('Consolas', 10))   # Yellow
        self.log_text.tag_config("INFO", foreground="#6bcf7f", font=('Consolas', 10))       # Light green/cyan
        self.log_text.tag_config("COMMAND", foreground="#58a6ff", background="#161b22", font=('Consolas', 10, 'bold'))  # Blue command
        self.log_text.tag_config("TIMESTAMP", foreground="#8b949e")  # Gray timestamp
        
        # Add tooltip/info
        info_label = ttk.Label(log_frame, 
                              text="💡 Right-click to copy text | Scroll to see all output",
                              font=("Arial", 8),
                              foreground="gray")
        info_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=10)
        
        self.install_button = ttk.Button(button_frame, text="Start Full Installation", 
                                        command=self.start_installation, state=tk.NORMAL)
        self.install_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Clear Log", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Exit", 
                  command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # Initialize system info
        self.refresh_system_info()
        
        # Add welcome message to terminal
        self.clear_log()
        self.log("=" * 70, "INFO")
        self.log("Nuke Installation Wizard - Terminal Log", "INFO")
        self.log("=" * 70, "INFO")
        self.log("", "INFO")
        self.log("Ready to start installation. Click 'Start Full Installation' to begin.", "INFO")
        self.log("", "INFO")
        
    def get_sudo_password(self):
        """Prompt for sudo password securely"""
        # Create a secure password dialog
        password_dialog = tk.Toplevel(self.root)
        password_dialog.title("Sudo Password Required")
        password_dialog.geometry("400x150")
        password_dialog.resizable(False, False)
        password_dialog.transient(self.root)
        password_dialog.grab_set()
        
        # Center the dialog
        password_dialog.update_idletasks()
        x = (password_dialog.winfo_screenwidth() // 2) - (password_dialog.winfo_width() // 2)
        y = (password_dialog.winfo_screenheight() // 2) - (password_dialog.winfo_height() // 2)
        password_dialog.geometry(f"+{x}+{y}")
        
        password_var = tk.StringVar()
        result = {'password': None, 'cancelled': False}
        
        # Dialog content
        ttk.Label(password_dialog, text="Enter your sudo password:", 
                 font=("Arial", 10)).pack(pady=10)
        
        password_entry = ttk.Entry(password_dialog, show="*", width=30, 
                                   textvariable=password_var, font=("Arial", 10))
        password_entry.pack(pady=5)
        password_entry.focus()
        
        def on_ok():
            password = password_var.get()
            if password:
                # Verify password
                try:
                    verify_process = subprocess.run(
                        ['sudo', '-S', '-k', 'echo', 'test'],
                        input=password + '\n',
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if verify_process.returncode == 0:
                        result['password'] = password
                        password_dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Invalid password or insufficient privileges")
                        password_entry.delete(0, tk.END)
                        password_entry.focus()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to verify password: {str(e)}")
                    password_entry.delete(0, tk.END)
                    password_entry.focus()
            else:
                messagebox.showwarning("Warning", "Please enter your password")
        
        def on_cancel():
            result['cancelled'] = True
            password_dialog.destroy()
        
        # Buttons
        button_frame = ttk.Frame(password_dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        password_entry.bind('<Return>', lambda e: on_ok())
        password_dialog.bind('<Escape>', lambda e: on_cancel())
        
        # Wait for dialog to close
        password_dialog.wait_window()
        
        if result['cancelled']:
            return None
        
        return result['password']
    
    def refresh_system_info(self):
        """Get system hostname and MAC address"""
        try:
            hostname = socket.gethostname()
            self.hostname_label.config(text=hostname)
        except:
            self.hostname_label.config(text="Unknown")
        
        try:
            result = subprocess.run(['ip', 'link', 'show'], 
                                  capture_output=True, text=True, check=True)
            mac_addresses = re.findall(r'link/ether ([0-9a-f:]{17})', result.stdout)
            if mac_addresses:
                mac = mac_addresses[0].replace(':', '')
                self.mac_label.config(text=mac)
            else:
                self.mac_label.config(text="Not found")
        except:
            self.mac_label.config(text="Not found")
    
    def browse_nuke_file(self):
        """Browse for Nuke installer file (.run or .tgz)"""
        filename = filedialog.askopenfilename(
            title="Select Nuke installer file",
            filetypes=[("Nuke installer", "*.run *.tgz"), ("Run files", "*.run"), ("Archive files", "*.tgz"), ("All files", "*.*")]
        )
        if filename:
            self.nuke_run_file.set(filename)
            # Auto-detect other files in the same directory
            self.auto_detect_files()
    
    def browse_folder(self):
        """Browse for folder containing installation files"""
        folder = filedialog.askdirectory(title="Select folder containing installation files")
        if folder:
            self.install_folder.set(folder)
            # Look for Nuke installer file (.run or .tgz)
            for file in os.listdir(folder):
                if 'nuke' in file.lower() and (file.endswith('.run') or file.endswith('.tgz')):
                    self.nuke_run_file.set(os.path.join(folder, file))
                    break
            self.auto_detect_files()
    
    def auto_detect_files(self):
        """Auto-detect required files, specifically looking for Crack folder"""
        base_dir = None
        if self.nuke_run_file.get():
            base_dir = os.path.dirname(self.nuke_run_file.get())
        elif self.install_folder.get():
            base_dir = self.install_folder.get()
        
        if not base_dir or not os.path.isdir(base_dir):
            return
        
        self.log("Auto-detecting files...", "INFO")
        self.log(f"Searching in: {base_dir}", "INFO")
        
        # First, look for FLT7 in base directory
        for file in os.listdir(base_dir):
            file_path = os.path.join(base_dir, file)
            if os.path.isfile(file_path) and 'flt7' in file.lower() and file.endswith('.tgz'):
                self.detected_files['flt7_tgz'] = file_path
                self.detected_labels['flt7_tgz'].config(text=file, foreground="green")
                self.log(f"Found FLT7: {file}", "SUCCESS")
        
        # Look for Crack folder - common patterns: "Crack", "crack", "Linux/Crack", etc.
        crack_folder = None
        possible_crack_paths = [
            os.path.join(base_dir, 'Crack'),
            os.path.join(base_dir, 'crack'),
            os.path.join(base_dir, 'Linux', 'Crack'),
            os.path.join(base_dir, 'Linux', 'crack'),
            os.path.join(base_dir, 'linux', 'Crack'),
            os.path.join(base_dir, 'linux', 'crack'),
        ]
        
        # Also search recursively for folders named "Crack" or "crack"
        for root, dirs, files in os.walk(base_dir):
            for dir_name in dirs:
                if dir_name.lower() == 'crack':
                    possible_crack_paths.append(os.path.join(root, dir_name))
        
        # Find the first existing crack folder
        for crack_path in possible_crack_paths:
            if os.path.isdir(crack_path):
                crack_folder = crack_path
                self.detected_files['crack_folder'] = crack_folder
                self.log(f"Found Crack folder: {crack_folder}", "SUCCESS")
                break
        
        if not crack_folder:
            self.log("Crack folder not found, searching all subdirectories...", "WARNING")
            # If no crack folder found, search all subdirectories
            crack_folder = base_dir
        
        # Search in crack folder (or base_dir if not found)
        search_dir = crack_folder if crack_folder else base_dir
        
        # Look for files in crack folder
        if os.path.isdir(search_dir):
            for file in os.listdir(search_dir):
                file_path = os.path.join(search_dir, file)
                if os.path.isfile(file_path):
                    # Look for rlm.foundry
                    if file == 'rlm.foundry' or (file.lower().startswith('rlm') and 'foundry' in file.lower() and not file.endswith('.7z') and not file.endswith('.zip')):
                        self.detected_files['rlm_foundry'] = file_path
                        self.detected_labels['rlm_foundry'].config(text=file, foreground="green")
                        self.log(f"Found rlm.foundry: {file_path}", "SUCCESS")
                    # Look for foundry.set
                    elif file == 'foundry.set' or (file.lower().endswith('.set') and 'foundry' in file.lower()):
                        self.detected_files['foundry_set'] = file_path
                        self.detected_labels['foundry_set'].config(text=file, foreground="green")
                        self.log(f"Found foundry.set: {file_path}", "SUCCESS")
                    # Look for license file
                    elif file == 'xf_foundry.lic' or (file.lower().endswith('.lic') and 'foundry' in file.lower()):
                        self.detected_files['license_file'] = file_path
                        self.detected_labels['license_file'].config(text=file, foreground="green")
                        self.log(f"Found license file: {file_path}", "SUCCESS")
        
        # Also search recursively if files not found in crack folder
        if not all([self.detected_files['rlm_foundry'], self.detected_files['foundry_set'], self.detected_files['license_file']]):
            self.log("Searching subdirectories for missing files...", "INFO")
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Look for rlm.foundry
                    if not self.detected_files['rlm_foundry'] and (file == 'rlm.foundry' or (file.lower().startswith('rlm') and 'foundry' in file.lower() and not file.endswith('.7z') and not file.endswith('.zip'))):
                        self.detected_files['rlm_foundry'] = file_path
                        self.detected_labels['rlm_foundry'].config(text=file, foreground="green")
                        self.log(f"Found rlm.foundry: {file_path}", "SUCCESS")
                    # Look for foundry.set
                    if not self.detected_files['foundry_set'] and (file == 'foundry.set' or (file.lower().endswith('.set') and 'foundry' in file.lower())):
                        self.detected_files['foundry_set'] = file_path
                        self.detected_labels['foundry_set'].config(text=file, foreground="green")
                        self.log(f"Found foundry.set: {file_path}", "SUCCESS")
                    # Look for license file
                    if not self.detected_files['license_file'] and (file == 'xf_foundry.lic' or (file.lower().endswith('.lic') and 'foundry' in file.lower())):
                        self.detected_files['license_file'] = file_path
                        self.detected_labels['license_file'].config(text=file, foreground="green")
                        self.log(f"Found license file: {file_path}", "SUCCESS")
        
        # Summary
        found_count = sum(1 for v in self.detected_files.values() if v is not None)
        self.log(f"Auto-detection complete: Found {found_count} files", "SUCCESS" if found_count >= 3 else "WARNING")
    
    def log(self, message, level="INFO"):
        """Add message to log and console with terminal-style formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Terminal-style prompt
        if level == "ERROR":
            prompt = f"[\033[91m{timestamp}\033[0m] [\033[91mERROR\033[0m] "
            log_message = f"[{timestamp}] [ERROR] {message}"
            tag = "ERROR"
        elif level == "WARNING":
            prompt = f"[\033[93m{timestamp}\033[0m] [\033[93mWARN\033[0m]  "
            log_message = f"[{timestamp}] [WARN]  {message}"
            tag = "WARNING"
        elif level == "SUCCESS":
            prompt = f"[\033[92m{timestamp}\033[0m] [\033[92mOK\033[0m]    "
            log_message = f"[{timestamp}] [OK]    {message}"
            tag = "SUCCESS"
        else:
            prompt = f"[\033[36m{timestamp}\033[0m] [\033[36mINFO\033[0m]  "
            log_message = f"[{timestamp}] [INFO]  {message}"
            tag = "INFO"
        
        # Add to GUI log with terminal-style formatting
        start_pos = self.log_text.index(tk.END)
        self.log_text.insert(tk.END, f"{log_message}\n")
        end_pos = self.log_text.index(tk.END + "-1c")
        
        # Apply color tag
        self.log_text.tag_add(tag, start_pos, end_pos)
        
        # Auto-scroll to bottom and ensure scrollbar is visible
        self.log_text.see(tk.END)
        self.log_text.update_idletasks()  # Update to show scrollbar if needed
        self.root.update_idletasks()
        
        # Also print to console with colors
        if level == "ERROR":
            print(f"\033[91m{log_message}\033[0m", file=sys.stderr, flush=True)  # Red
        elif level == "WARNING":
            print(f"\033[93m{log_message}\033[0m", file=sys.stdout, flush=True)  # Yellow
        elif level == "SUCCESS":
            print(f"\033[92m{log_message}\033[0m", file=sys.stdout, flush=True)  # Green
        else:
            print(f"\033[36m{log_message}\033[0m", file=sys.stdout, flush=True)  # Cyan
        
    def clear_log(self):
        """Clear log and add terminal header"""
        self.log_text.delete(1.0, tk.END)
        # Add terminal-style header
        welcome_msg = """╔══════════════════════════════════════════════════════════════════════╗
║              Nuke Installation Wizard - Terminal Log              ║
╚══════════════════════════════════════════════════════════════════════╝

"""
        self.log_text.insert(tk.END, welcome_msg)
        self.log_text.tag_add("INFO", "1.0", tk.END)
        self.log_text.see(tk.END)
    
    def run_sudo_command(self, command, input_text=None, check=True):
        """Run a sudo command with password"""
        if not self.sudo_password:
            raise Exception("Sudo password not set")
        
        # Log the command being executed with terminal style
        cmd_str = ' '.join(command)
        start_pos = self.log_text.index(tk.END)
        self.log_text.insert(tk.END, f"$ sudo {cmd_str}\n")
        end_pos = self.log_text.index(tk.END + "-1c")
        self.log_text.tag_add("COMMAND", start_pos, end_pos)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        cmd = ['sudo', '-S'] + command
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        input_data = self.sudo_password + '\n'
        if input_text:
            input_data += input_text + '\n'
        
        stdout, stderr = process.communicate(input=input_data, timeout=300)
        
        # Log output
        if stdout:
            for line in stdout.strip().split('\n'):
                if line.strip():
                    self.log(f"  → {line}")
        
        if stderr and stderr.strip():
            for line in stderr.strip().split('\n'):
                if line.strip():
                    self.log(f"  ⚠ {line}", "WARNING")
        
        if check and process.returncode != 0:
            error_msg = f"Command failed with exit code {process.returncode}: {stderr or stdout}"
            self.log(error_msg, "ERROR")
            raise Exception(error_msg)
        elif process.returncode == 0:
            self.log(f"Command completed successfully (exit code: {process.returncode})", "SUCCESS")
        
        return stdout, stderr, process.returncode
    
    def validate_inputs(self):
        """Validate that all required files are available"""
        errors = []
        
        if not self.nuke_run_file.get():
            errors.append("Nuke installer file (.run or .tgz) is required")
        elif not os.path.exists(self.nuke_run_file.get()):
            errors.append("Nuke installer file does not exist")
        
        if not self.detected_files['flt7_tgz']:
            errors.append("FLT7 .tgz file not found. Please ensure it's in the same folder.")
        
        if not self.detected_files['rlm_foundry']:
            errors.append("rlm.foundry file not found. Please ensure it's in the same folder.")
        
        if not self.detected_files['foundry_set']:
            errors.append("foundry.set file not found. Please ensure it's in the same folder.")
        
        return errors
    
    def get_system_info_for_license(self):
        """Get hostname and MAC address for license file (used by both create and edit)"""
        hostname = None
        mac_address = None
        
        # Try rlmutil first (as per plan step 21)
        rlmutil_paths = [
            '/usr/local/foundry/LicensingTools7.1/bin/RLM/rlmutil',
            '/usr/local/foundry/RLM/rlmutil',
            'rlmutil'
        ]
        
        rlmutil_found = None
        for path in rlmutil_paths:
            if os.path.exists(path) or path == 'rlmutil':
                try:
                    result = subprocess.run(['which', path] if path == 'rlmutil' else ['test', '-x', path],
                                          capture_output=True, timeout=2)
                    if result.returncode == 0 or os.access(path, os.X_OK):
                        rlmutil_found = path
                        break
                except:
                    continue
        
        if rlmutil_found:
            try:
                # Get hostname
                result = subprocess.run([rlmutil_found, 'rlmhostid', 'host'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    hostname = result.stdout.strip().split()[-1]
                
                # Get MAC address
                result = subprocess.run([rlmutil_found, 'rlmhostid'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    output = result.stdout.strip()
                    mac_match = re.search(r'([0-9a-fA-F]{12})', output)
                    if mac_match:
                        mac_address = mac_match.group(1)
            except:
                pass
        
        # Fallback to system commands
        if not hostname:
            hostname = socket.gethostname()
        
        if not mac_address:
            try:
                result = subprocess.run(['ip', 'link', 'show'], 
                                      capture_output=True, text=True, check=True)
                mac_addresses = re.findall(r'link/ether ([0-9a-f:]{17})', result.stdout)
                if mac_addresses:
                    mac_address = mac_addresses[0].replace(':', '')
            except:
                raise Exception("Could not get MAC address")
        
        mac_address = mac_address.replace(':', '').replace('-', '')
        
        return hostname, mac_address
    
    def create_license_file(self):
        """Create license file with system information using rlmutil (as per plan step 21)"""
        self.log("Getting system information using rlmutil (as per plan step 21)...")
        
        hostname, mac_address = self.get_system_info_for_license()
        port = "4101"  # Default port
        
        # Create license file content
        license_content = f"{hostname} {mac_address} {port}\n"
        
        self.log(f"License file content: {license_content.strip()}", "SUCCESS")
        self.log(f"  HOST_NAME: {hostname}")
        self.log(f"  MAC_ADDRESS: {mac_address}")
        self.log(f"  PORT: {port}")
        
        return license_content
    
    def start_installation(self):
        """Start the installation process"""
        errors = self.validate_inputs()
        if errors:
            messagebox.showerror("Validation Error", 
                               "Please fix the following errors:\n\n" + "\n".join(errors))
            return
        
        # Confirm installation
        response = messagebox.askyesno(
            "Confirm Installation",
            "This will install Nuke and configure the license server.\n\n"
            "All steps will be executed automatically.\n\n"
            "You will be prompted for sudo password when needed.\n\n"
            "Do you want to continue?",
            icon='warning'
        )
        
        if not response:
            return
        
        # Get sudo password securely
        self.log("Prompting for sudo password...")
        password = self.get_sudo_password()
        
        if not password:
            self.log("Installation cancelled - no password provided", "WARNING")
            return
        
        self.sudo_password = password
        self.log("Sudo password verified successfully", "SUCCESS")
        
        # Disable install button
        self.install_button.config(state=tk.DISABLED)
        self.clear_log()
        
        # Start installation in separate thread
        thread = threading.Thread(target=self.run_installation, daemon=True)
        thread.start()
    
    def run_installation(self):
        """Run the complete installation process"""
        try:
            print("\n" + "=" * 70, flush=True)
            print("NUKE INSTALLATION PROCESS STARTED", flush=True)
            print("=" * 70 + "\n", flush=True)
            
            self.log("=" * 70)
            self.log("Starting Nuke Installation Process")
            self.log("=" * 70)
            self.log("")
            
            nuke_run = self.nuke_run_file.get()
            flt7_tgz = self.detected_files['flt7_tgz']
            rlm_foundry = self.detected_files['rlm_foundry']
            foundry_set = self.detected_files['foundry_set']
            install_path = self.install_path.get()
            nuke_version = self.nuke_version.get()
            
            # Step 1-5: Install Nuke FIRST (extract if .tgz, then install)
            print("\n[STEP 1-5] Installing Nuke (FIRST)...", flush=True)
            self.log("[STEP 1-5] Installing Nuke (FIRST)...")
            nuke_dir = os.path.dirname(nuke_run)
            nuke_file = os.path.basename(nuke_run)
            
            self.log(f"Changing to directory: {nuke_dir}")
            os.chdir(nuke_dir)
            
            # Check if it's a .tgz file (needs extraction first)
            if nuke_file.endswith('.tgz'):
                self.log(f"Detected Nuke .tgz archive: {nuke_file}")
                self.log("Extracting Nuke archive...")
                
                # Extract the .tgz file
                try:
                    result = subprocess.run(['tar', 'xvzf', nuke_file], 
                                         capture_output=True, text=True, check=True)
                    if result.stdout:
                        for line in result.stdout.strip().split('\n'):
                            if line.strip():
                                self.log(f"  → {line}")
                    self.log(f"Successfully extracted {nuke_file}", "SUCCESS")
                except subprocess.CalledProcessError as e:
                    self.log(f"Error extracting archive: {e.stderr}", "ERROR")
                    raise
                
                # Find extracted directory or installer
                extracted_nuke = None
                for item in os.listdir('.'):
                    if os.path.isdir(item) and 'nuke' in item.lower():
                        extracted_nuke = item
                        break
                    elif os.path.isfile(item) and item.endswith('.run') and 'nuke' in item.lower():
                        extracted_nuke = item
                        break
                
                if not extracted_nuke:
                    raise Exception("Could not find extracted Nuke directory or installer")
                
                self.log(f"Found extracted Nuke: {extracted_nuke}")
                
                # If it's a directory, look for installer inside
                if os.path.isdir(extracted_nuke):
                    os.chdir(extracted_nuke)
                    # Look for .run installer in the extracted directory
                    for file in os.listdir('.'):
                        if file.endswith('.run') and 'nuke' in file.lower():
                            nuke_file = file
                            self.log(f"Found installer in extracted directory: {nuke_file}")
                            break
                else:
                    # It's a .run file, use it
                    nuke_file = extracted_nuke
            
            # Now install Nuke (either from .run file or extracted)
            self.log(f"Setting permissions on {nuke_file}...")
            self.run_sudo_command(['chmod', 'a+rwx', nuke_file])
            
            self.log(f"Running Nuke installer: {nuke_file}")
            self.log("NOTE: The installer GUI will open. Please install to /opt folder.")
            self.log("Waiting for installer to complete...")
            print("NOTE: Nuke installer GUI will open. Complete the installation in the GUI.", flush=True)
            
            # Run installer (this will open GUI, user needs to complete it)
            try:
                process = subprocess.Popen(
                    ['sudo', '-S', './' + nuke_file],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate(input=self.sudo_password + '\n', timeout=600)
                
                if stdout:
                    for line in stdout.strip().split('\n'):
                        if line.strip():
                            self.log(f"  → {line}")
                
                if stderr:
                    for line in stderr.strip().split('\n'):
                        if line.strip():
                            self.log(f"  ⚠ {line}", "WARNING")
                
                if process.returncode != 0:
                    self.log(f"Nuke installer exited with code {process.returncode}", "WARNING")
                else:
                    self.log("Nuke installer completed successfully", "SUCCESS")
            except subprocess.TimeoutExpired:
                self.log("Nuke installer timeout - assuming installation completed", "WARNING")
                process.kill()
            except Exception as e:
                self.log(f"Error running Nuke installer: {str(e)}", "ERROR")
                raise
            
            self.log("Nuke installation completed successfully!", "SUCCESS")
            self.log("")
            
            # Step 6-12: Install FLT7 License Server (AFTER Nuke)
            print("\n[STEP 6-12] Installing FLT7 License Server (AFTER Nuke)...", flush=True)
            self.log("[STEP 6-12] Installing FLT7 License Server (AFTER Nuke)...")
            
            # Step 5-12: Install FLT7 License Server
            print("\n[STEP 5-12] Installing FLT7 License Server...", flush=True)
            self.log("[STEP 5-12] Installing FLT7 License Server...")
            flt7_dir = os.path.dirname(flt7_tgz)
            os.chdir(flt7_dir)
            
            flt7_archive = os.path.basename(flt7_tgz)
            self.log(f"Extracting {flt7_archive}...")
            try:
                result = subprocess.run(['tar', 'xvzf', flt7_archive], 
                                     capture_output=True, text=True, check=True)
                if result.stdout:
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            self.log(f"  → {line}")
                self.log(f"Successfully extracted {flt7_archive}", "SUCCESS")
            except subprocess.CalledProcessError as e:
                self.log(f"Error extracting archive: {e.stderr}", "ERROR")
                raise
            
            # Find extracted directory
            extracted_dir = None
            for item in os.listdir('.'):
                if os.path.isdir(item) and 'flt7' in item.lower():
                    extracted_dir = item
                    break
            
            if not extracted_dir:
                raise Exception("Could not find extracted FLT7 directory")
            
            self.log(f"Found extracted directory: {extracted_dir}")
            os.chdir(extracted_dir)
            
            self.log("Setting permissions on install.sh...")
            self.run_sudo_command(['chmod', 'a+rwx', './install.sh'])
            
            self.log("Running FLT7 installer...")
            self.run_sudo_command(['./install.sh'], check=False)
            
            self.log("FLT7 installation completed.")
            self.log("")
            
            # Step 11-12: Shutdown license server via web interface
            self.log("[STEP 11-12] License Server Shutdown Required")
            self.log("Opening browser to shutdown license server...")
            
            # Try to open browser
            urls = ['http://127.0.0.1:4102', 'http://127.0.0.1:5053', 'http://127.0.0.1:4101']
            for url in urls:
                try:
                    subprocess.Popen(['xdg-open', url])
                    break
                except:
                    pass
            
            messagebox.showinfo(
                "Manual Step Required",
                "Please:\n"
                "1. Open Firefox (disable VPN if using one)\n"
                "2. Navigate to one of: http://127.0.0.1:4102, 4101, or 5053\n"
                "3. Click 'Shutdown' button\n"
                "4. Click 'SHUT DOWN SERVER'\n"
                "5. Click OK in this dialog to continue"
            )
            
            # Step 13-22: Copy crack files and license
            self.log("[STEP 13-22] Copying crack files and license...")
            
            # Remove existing files
            self.log("Removing existing license files...")
            self.run_sudo_command(['rm', '-f', '/usr/local/foundry/RLM/rlm.foundry'], check=False)
            self.run_sudo_command(['rm', '-f', '/usr/local/foundry/LicensingTools7.1/bin/RLM/rlm.foundry'], check=False)
            self.run_sudo_command(['rm', '-f', '/usr/local/foundry/RLM/foundry.set'], check=False)
            self.run_sudo_command(['rm', '-f', '/usr/local/foundry/LicensingTools7.1/bin/RLM/foundry.set'], check=False)
            
            # Copy crack files
            self.log("Copying rlm.foundry...")
            self.run_sudo_command(['cp', rlm_foundry, '/usr/local/foundry/RLM/rlm.foundry'])
            self.run_sudo_command(['cp', rlm_foundry, '/usr/local/foundry/LicensingTools7.1/bin/RLM/rlm.foundry'])
            
            self.log("Copying foundry.set...")
            self.run_sudo_command(['cp', foundry_set, '/usr/local/foundry/RLM/foundry.set'])
            self.run_sudo_command(['cp', foundry_set, '/usr/local/foundry/LicensingTools7.1/bin/RLM/foundry.set'])
            
            # Create and copy license file
            self.log("Creating license file...")
            license_content = self.create_license_file()
            license_file_path = os.path.join(os.path.expanduser('~'), 'xf_foundry.lic')
            with open(license_file_path, 'w') as f:
                f.write(license_content)
            
            self.log("Copying license file...")
            self.run_sudo_command(['cp', license_file_path, '/usr/local/foundry/RLM/xf_foundry.lic'])
            
            # Step 23-25: Start license server
            self.log("[STEP 23-25] Starting license server...")
            self.log("Checking license server status...")
            self.run_sudo_command(['/usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility', '-s', 'status', '-t', 'RLM'], check=False)
            
            self.log("Starting license server...")
            self.run_sudo_command(['/usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility', '-s', 'start', '-t', 'RLM'])
            
            self.log("Verifying license server status...")
            stdout, _, _ = self.run_sudo_command(['/usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility', '-s', 'status', '-t', 'RLM'], check=False)
            self.log(stdout)
            
            # Create alias
            self.log("[BONUS] Creating 'nukex' alias...")
            
            # Find actual Nuke executable
            nuke_base_path = f"{install_path}/Nuke{nuke_version}"
            nuke_exe = None
            if os.path.isdir(nuke_base_path):
                for file in os.listdir(nuke_base_path):
                    if file.startswith('Nuke') and os.access(os.path.join(nuke_base_path, file), os.X_OK):
                        nuke_exe = file
                        break
            
            if not nuke_exe:
                # Try to find any Nuke installation
                for item in os.listdir(install_path):
                    if item.startswith('Nuke'):
                        nuke_base_path = os.path.join(install_path, item)
                        for file in os.listdir(nuke_base_path):
                            if file.startswith('Nuke') and os.access(os.path.join(nuke_base_path, file), os.X_OK):
                                nuke_exe = file
                                break
                        if nuke_exe:
                            break
            
            if nuke_exe:
                # Create a function that starts license server first, waits for it, then starts Nuke
                alias_content = f'''
# Nuke launcher function - Starts license server first, then Nuke
nukex() {{
    echo "=========================================="
    echo "Starting Nuke License Server..."
    echo "=========================================="
    
    # Check current status
    echo "Checking license server status..."
    sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM
    
    # Start the license server
    echo ""
    echo "Starting license server..."
    sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s start -t RLM
    
    # Wait a moment for server to initialize
    sleep 3
    
    # Verify server is running
    echo ""
    echo "Verifying license server is running..."
    STATUS_OUTPUT=$(sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM 2>&1)
    echo "$STATUS_OUTPUT"
    
    # Check if server is actually running (look for "rlm" or "running" in output)
    if echo "$STATUS_OUTPUT" | grep -qi "rlm.*running\|server.*running\|started"; then
        echo ""
        echo "✓ License server is running successfully!"
        echo ""
        echo "=========================================="
        echo "Starting Nuke..."
        echo "=========================================="
        cd {nuke_base_path}
        ./{nuke_exe} &
        echo "✓ Nuke is starting in the background!"
        echo ""
    else
        echo ""
        echo "⚠ Warning: License server may not be running properly"
        echo "Attempting to start Nuke anyway..."
        echo ""
        cd {nuke_base_path}
        ./{nuke_exe} &
        echo "✓ Nuke is starting in the background!"
        echo ""
    fi
}}
'''
            else:
                # Fallback if we can't find the exact path
                alias_content = f'''
# Nuke launcher function - Starts license server first, then Nuke
nukex() {{
    echo "=========================================="
    echo "Starting Nuke License Server..."
    echo "=========================================="
    
    # Check current status
    echo "Checking license server status..."
    sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM
    
    # Start the license server
    echo ""
    echo "Starting license server..."
    sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s start -t RLM
    
    # Wait a moment for server to initialize
    sleep 3
    
    # Verify server is running
    echo ""
    echo "Verifying license server is running..."
    STATUS_OUTPUT=$(sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM 2>&1)
    echo "$STATUS_OUTPUT"
    
    # Check if server is actually running
    if echo "$STATUS_OUTPUT" | grep -qi "rlm.*running\|server.*running\|started"; then
        echo ""
        echo "✓ License server is running successfully!"
        echo ""
        echo "=========================================="
        echo "Starting Nuke..."
        echo "=========================================="
        NUKE_DIR=$(find {install_path} -maxdepth 1 -type d -name "Nuke*" 2>/dev/null | head -1)
        if [ -n "$NUKE_DIR" ]; then
            cd "$NUKE_DIR"
            NUKE_EXE=$(find . -maxdepth 1 -type f -name "Nuke*" -executable | head -1)
            if [ -n "$NUKE_EXE" ]; then
                ./"$(basename "$NUKE_EXE")" &
                echo "✓ Nuke is starting in the background!"
                echo ""
            else
                echo "✗ Error: Could not find Nuke executable"
                exit 1
            fi
        else
            echo "✗ Error: Could not find Nuke installation directory"
            exit 1
        fi
    else
        echo ""
        echo "⚠ Warning: License server may not be running properly"
        echo "Attempting to start Nuke anyway..."
        echo ""
        NUKE_DIR=$(find {install_path} -maxdepth 1 -type d -name "Nuke*" 2>/dev/null | head -1)
        if [ -n "$NUKE_DIR" ]; then
            cd "$NUKE_DIR"
            NUKE_EXE=$(find . -maxdepth 1 -type f -name "Nuke*" -executable | head -1)
            if [ -n "$NUKE_EXE" ]; then
                ./"$(basename "$NUKE_EXE")" &
                echo "✓ Nuke is starting in the background!"
                echo ""
            else
                echo "✗ Error: Could not find Nuke executable"
                exit 1
            fi
        else
            echo "✗ Error: Could not find Nuke installation directory"
            exit 1
        fi
    fi
}}
'''
            
            # Add to .bashrc
            bashrc_path = os.path.expanduser('~/.bashrc')
            if os.path.exists(bashrc_path):
                with open(bashrc_path, 'r') as f:
                    content = f.read()
                if 'nukex()' not in content:
                    with open(bashrc_path, 'a') as f:
                        f.write(alias_content)
                    self.log("Function 'nukex' added to ~/.bashrc")
                else:
                    self.log("Function 'nukex' already exists in ~/.bashrc")
            else:
                with open(bashrc_path, 'w') as f:
                    f.write(alias_content)
                self.log("Created ~/.bashrc and added function 'nukex'")
            
            # Also add to .bash_aliases if it exists
            bash_aliases_path = os.path.expanduser('~/.bash_aliases')
            if os.path.exists(bash_aliases_path):
                with open(bash_aliases_path, 'r') as f:
                    content = f.read()
                if 'nukex()' not in content:
                    with open(bash_aliases_path, 'a') as f:
                        f.write(alias_content)
                    self.log("Function 'nukex' also added to ~/.bash_aliases")
            
            # Step 28-29: Create startup script in /etc/init.d
            if self.create_startup_script.get():
                print("\n[STEP 28-29] Creating startup script in /etc/init.d...", flush=True)
                self.log("[STEP 28-29] Creating startup script in /etc/init.d...")
                
                startup_script_content = f'''#!/bin/bash

#Starting RLM.Foundry

clear
echo "Starting RLM License server"

sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM

P1=$!

sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s start -t RLM

P1=$!

sudo /usr/local/foundry/LicensingTools7.1/FoundryLicenseUtility -s status -t RLM


echo "Started RLM License server successfully"

exit 0
'''
                
                script_name = "rlm-foundry-startup"
                script_path = f"/etc/init.d/{script_name}"
                
                # Create script in temp location first
                temp_script = os.path.join(os.path.expanduser('~'), f'temp_{script_name}.sh')
                with open(temp_script, 'w') as f:
                    f.write(startup_script_content)
                
                # Make it executable
                os.chmod(temp_script, 0o755)
                
                # Copy to /etc/init.d
                self.log(f"Copying startup script to {script_path}...")
                self.run_sudo_command(['cp', temp_script, script_path])
                self.run_sudo_command(['chmod', '+x', script_path])
                
                # Clean up temp file
                os.remove(temp_script)
                
                # Enable the service (if systemd is available)
                try:
                    self.log("Enabling startup script...")
                    self.run_sudo_command(['update-rc.d', script_name, 'defaults'], check=False)
                    self.log("Startup script enabled successfully", "SUCCESS")
                except Exception as e:
                    self.log(f"Note: Could not auto-enable startup script: {str(e)}. You may need to enable it manually.", "WARNING")
                
                self.log(f"Startup script created at: {script_path}", "SUCCESS")
                self.log("License server will start automatically on system boot")
            
            # Step 32-33: Setup passwordless sudo (optional)
            if self.setup_passwordless_sudo.get():
                print("\n[STEP 32-33] Setting up passwordless sudo...", flush=True)
                self.log("[STEP 32-33] Setting up passwordless sudo...")
                
                try:
                    username = getpass.getuser()
                    self.log(f"Setting up passwordless sudo for user: {username}")
                    
                    # Create a backup of sudoers
                    self.log("Creating backup of sudoers file...")
                    self.run_sudo_command(['cp', '/etc/sudoers', '/etc/sudoers.backup'], check=False)
                    
                    # Check if entry already exists
                    result = subprocess.run(['sudo', '-S', 'grep', '-q', f'^{username}.*NOPASSWD', '/etc/sudoers'], 
                                          input=self.sudo_password + '\n',
                                          capture_output=True,
                                          text=True,
                                          timeout=5)
                    if result.returncode == 0:
                        self.log("Passwordless sudo already configured for this user", "WARNING")
                    else:
                        # Add entry to sudoers
                        self.log("Adding NOPASSWD entry to sudoers...")
                        sudoers_entry = f"\n{username} ALL=(ALL) NOPASSWD: ALL\n"
                        
                        # Use visudo -c to validate, but we'll use a safer method
                        # Create a temp file with the entry
                        temp_sudoers = os.path.join(os.path.expanduser('~'), 'temp_sudoers_entry')
                        with open(temp_sudoers, 'w') as f:
                            f.write(sudoers_entry)
                        
                        # Append to sudoers using sudo tee
                        cmd = f'echo "{sudoers_entry}" | sudo tee -a /etc/sudoers'
                        process = subprocess.Popen(
                            ['bash', '-c', cmd],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        stdout, stderr = process.communicate(input=self.sudo_password + '\n', timeout=10)
                        
                        if process.returncode == 0:
                            # Validate sudoers file
                            result = self.run_sudo_command(['visudo', '-c'], check=False)
                            if 'syntax OK' in result[0] or result[2] == 0:
                                self.log("Passwordless sudo configured successfully", "SUCCESS")
                                self.log("You can now run sudo commands without password", "SUCCESS")
                            else:
                                self.log("Warning: sudoers validation failed. Restoring backup...", "WARNING")
                                self.run_sudo_command(['cp', '/etc/sudoers.backup', '/etc/sudoers'], check=False)
                                raise Exception("Failed to validate sudoers file")
                        else:
                            raise Exception(f"Failed to add sudoers entry: {stderr}")
                        
                        # Clean up
                        if os.path.exists(temp_sudoers):
                            os.remove(temp_sudoers)
                    
                except Exception as e:
                    self.log(f"Warning: Could not setup passwordless sudo: {str(e)}", "WARNING")
                    self.log("You can set it up manually later using: sudo visudo", "WARNING")
                    # Restore backup if something went wrong
                    if os.path.exists('/etc/sudoers.backup'):
                        try:
                            self.run_sudo_command(['cp', '/etc/sudoers.backup', '/etc/sudoers'], check=False)
                        except:
                            pass
            
            self.log("")
            print("\n" + "=" * 70, flush=True)
            print("INSTALLATION COMPLETED SUCCESSFULLY!", flush=True)
            print("=" * 70 + "\n", flush=True)
            
            self.log("=" * 70)
            self.log("Installation completed successfully!", "SUCCESS")
            self.log("=" * 70)
            self.log("")
            self.log("You can now run Nuke using: nukex", "SUCCESS")
            self.log("(You may need to restart your terminal or run: source ~/.bashrc)")
            self.log("")
            self.log(f"Nuke is installed at: {install_path}/Nuke{nuke_version}/")
            
            if self.create_startup_script.get():
                self.log("License server will start automatically on system boot", "SUCCESS")
            
            if self.setup_passwordless_sudo.get():
                self.log("Passwordless sudo has been configured", "SUCCESS")
            
            print(f"\n✓ Installation completed successfully!", flush=True)
            print(f"✓ Nuke is installed at: {install_path}/Nuke{nuke_version}/", flush=True)
            print(f"✓ Use 'nukex' command to start Nuke", flush=True)
            if self.create_startup_script.get():
                print(f"✓ License server will auto-start on boot", flush=True)
            if self.setup_passwordless_sudo.get():
                print(f"✓ Passwordless sudo configured", flush=True)
            print(f"✓ Run 'source ~/.bashrc' or restart terminal to use nukex\n", flush=True)
            
            complete_msg = "Installation completed successfully!\n\n"
            complete_msg += "You can now run Nuke using the 'nukex' command.\n"
            if self.create_startup_script.get():
                complete_msg += "\nLicense server will start automatically on system boot.\n"
            if self.setup_passwordless_sudo.get():
                complete_msg += "\nPasswordless sudo has been configured.\n"
            complete_msg += "\nRestart your terminal or run: source ~/.bashrc"
            
            messagebox.showinfo("Installation Complete", complete_msg)
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ ERROR: {error_msg}", flush=True, file=sys.stderr)
            self.log(f"ERROR: {error_msg}", "ERROR")
            import traceback
            traceback_str = traceback.format_exc()
            print(traceback_str, flush=True, file=sys.stderr)
            self.log(traceback_str, "ERROR")
            messagebox.showerror("Error", f"Installation error: {error_msg}\n\nCheck the log for details.")
        finally:
            self.install_button.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    app = NukeInstallerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
