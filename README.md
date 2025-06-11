# Pushcrt

Pushcrt is a Python utility that allows you to **install custom CA certificates** (e.g., Burp Suite) into the **Android system trust store** via ADB, even when `adbd` cannot run as root. This script leverages `su` (Magisk) access and dynamically hashes certificates into the required `.0` filename format.

---

## 🔥 Features

- ✅ Supports `.crt`, `.cer`, `.der`, `.pem`
- ✅ Auto-converts to PEM format
- ✅ Calculates `.0` filename hash dynamically via OpenSSL
- ✅ Pushes cert to Android system store with proper permissions
- ✅ Works even if `adbd` is not running as root (uses `su`)
- ✅ Dry-run support to simulate actions
- ✅ Verbose logging for debugging
- ✅ Error handling for all common issues

---

## ⚙️ Requirements

- Python 3.x
- `adb` in your PATH
- `openssl` in your PATH
- Android device with:
  - Root access (via `su`, e.g. Magisk)
  - USB debugging enabled

---

## 🛠️ Installation

1. Clone the repository:

```bash
git clone https://github.com/7absec/Pushcrt.git
cd Pushcrt
```

### 🧩 Install Dependencies

No extra Python libraries are needed.

Just make sure the following are installed and added to your system `PATH`:

- [`adb`](https://developer.android.com/tools/releases/platform-tools)
- [`openssl`](https://slproweb.com/products/Win32OpenSSL.html)

#### 💡 For Windows Users

- Install **OpenSSL** using Chocolatey:

  ```bash
  choco install openssl -y
  ```

## 🚀 Usage

```bash
python pushcrt.py <certificate_file>
OR
python pushcrt.py burp.crt
OR
python pushcrt.py burp.crt --dry-run --verbose
```

## 🧩 Options

| Option       | Description                             |
|--------------|-----------------------------------------|
| `--dry-run`  | Show the commands that would be run without actually executing them. Useful for testing. |
| `--verbose`  | Enable detailed logging for debugging purposes. |


⚠️ **Note**  
> Do **not** restart your device after pushing the certificate, or the custom CA will be wiped from memory (since it's mounted on a tmpfs).
  
