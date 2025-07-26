import tkinter as tk
from tkinter import ttk, messagebox
import ssl
import socket
from datetime import datetime

THEME_BG = "#7f0909"
THEME_FG = "gold"
FONT = ("Georgia", 11)

class SSLCertInspector:
    def __init__(self, root):
        self.root = root
        self.root.title("CertScry - SSL Certificate Inspector")
        self.root.geometry("750x500")
        self.root.configure(bg=THEME_BG)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=THEME_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=THEME_BG, foreground=THEME_FG, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", THEME_FG)], foreground=[("selected", THEME_BG)])

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True)

        self.create_inspector_tab()
        self.create_help_tab()

    def create_inspector_tab(self):
        tab = tk.Frame(self.tabs, bg=THEME_BG)
        self.tabs.add(tab, text="🔍 Inspect Certificate")

        tk.Label(tab, text="🔐 Enter domain name (e.g., google.com)", fg=THEME_FG, bg=THEME_BG, font=("Georgia", 13)).pack(pady=15)
        self.domain_entry = tk.Entry(tab, font=("Georgia", 12), width=50)
        self.domain_entry.pack(pady=5)

        tk.Button(tab, text="Check SSL Certificate", command=self.inspect_cert, bg="gold").pack(pady=10)

        self.output_box = tk.Text(tab, width=85, height=20, bg="black", fg="lime", font=("Courier", 10))
        self.output_box.pack(pady=10)

    def create_help_tab(self):
        tab = tk.Frame(self.tabs, bg=THEME_BG)
        self.tabs.add(tab, text="📖 How to Use")

        help_text = """
🧙‍♂️ Welcome to CertScry - SSL Certificate Inspector

🔹 Step 1: Go to 'Inspect Certificate' tab
🔹 Step 2: Enter a domain (e.g., google.com)
🔹 Step 3: Click 'Check SSL Certificate'
🔹 Step 4: You'll see details like:
    - Issuer
    - Subject
    - Validity Period
    - SAN (Subject Alt Names)

🔒 Why use this?
- Check if a website's certificate is valid
- Look for certificate expiry
- Explore SANs (what domains the cert is valid for)
- Good for OSINT, DevSecOps, and curious minds

🔎 NOTE:
- Tool connects to port 443 (HTTPS)
- Ensure you have internet connectivity
"""
        tk.Label(tab, text=help_text, justify="left", fg=THEME_FG, bg=THEME_BG, font=FONT, wraplength=700).pack(padx=20, pady=20)

    def inspect_cert(self):
        domain = self.domain_entry.get().strip()
        if not domain:
            messagebox.showwarning("Input Error", "Please enter a valid domain name.")
            return

        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()

            output = []
            output.append(f"🔍 Certificate for: {domain}")
            output.append("")

            # Subject
            subject = dict(x[0] for x in cert.get("subject", []))
            output.append(f"👤 Subject: {subject.get('commonName', 'N/A')}")
            
            # Issuer
            issuer = dict(x[0] for x in cert.get("issuer", []))
            output.append(f"🏢 Issuer: {issuer.get('commonName', 'N/A')}")

            # Validity
            output.append(f"📅 Valid From: {cert.get('notBefore', 'N/A')}")
            output.append(f"📅 Valid To  : {cert.get('notAfter', 'N/A')}")

            # SANs
            san = cert.get("subjectAltName", [])
            if san:
                san_list = [entry[1] for entry in san]
                output.append(f"\n📜 Subject Alt Names ({len(san_list)}):")
                output.extend(f" - {item}" for item in san_list)

            else:
                output.append("No SANs listed.")

            self.output_box.delete(1.0, tk.END)
            self.output_box.insert(tk.END, "\n".join(output))

        except socket.gaierror:
            messagebox.showerror("Connection Error", f"Could not resolve domain: {domain}")
        except ssl.SSLError as e:
            messagebox.showerror("SSL Error", f"SSL error: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SSLCertInspector(root)
    root.mainloop()
