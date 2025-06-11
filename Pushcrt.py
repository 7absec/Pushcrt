import os
import sys
import subprocess
import shutil
import argparse
import logging

DEVICE_TMP_DIR = "/sdcard/7absec"
SYSTEM_CERT_DIR = "/system/etc/security/cacerts"

def run(cmd, dry_run=False):
    logging.info(f"[+] Running: {cmd}")
    if dry_run:
        return
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(result.stderr.strip())
        sys.exit(1)
    if result.stdout.strip():
        logging.info(result.stdout.strip())

def check_dependency(name):
    if not shutil.which(name):
        logging.error(f"[-] {name} not found in PATH.")
        if name == "openssl":
            logging.info("Install using Chocolatey: choco install openssl -y")
            logging.info("Or from: https://slproweb.com/products/Win32OpenSSL.html")
        elif name == "adb":
            logging.info("Install via platform-tools or https://developer.android.com/tools/releases/platform-tools")
        sys.exit(1)

def check_device_connected():
    result = subprocess.run("adb get-state", shell=True, capture_output=True, text=True)
    if "device" not in result.stdout.strip():
        logging.error("[-] No Android device connected or unauthorized.")
        sys.exit(1)

def is_pem_format(file_path):
    with open(file_path, "rb") as f:
        header = f.read(30)
        return b"-----BEGIN CERTIFICATE-----" in header

def convert_to_pem(input_file, output_file):
    if is_pem_format(input_file):
        logging.info("[*] Certificate already in PEM format. Copying.")
        shutil.copy(input_file, output_file)
    else:
        logging.info("[*] Converting certificate from DER to PEM...")
        run(f'openssl x509 -inform DER -in "{input_file}" -out "{output_file}"')

def get_cert_hash(pem_file):
    result = subprocess.run(f'openssl x509 -inform PEM -subject_hash_old -in "{pem_file}"', shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error("[-] Failed to generate hash from PEM certificate.")
        sys.exit(1)
    hash_value = result.stdout.splitlines()[0].strip()
    return f"{hash_value}.0"

def main():
    parser = argparse.ArgumentParser(description="Push a certificate to Android system store via ADB.")
    parser.add_argument("certificate", help="Path to the certificate file (.crt/.cer/.der/.pem)")
    parser.add_argument("--dry-run", action="store_true", help="Only show commands, do not execute")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format='%(message)s')

    cert_path = args.certificate
    dry_run = args.dry_run

    if not os.path.exists(cert_path):
        logging.error(f"[-] File not found: {cert_path}")
        sys.exit(1)

    check_dependency("openssl")
    check_dependency("adb")
    check_device_connected()

    # Convert to PEM format
    temp_pem = "__temp__.pem"
    convert_to_pem(cert_path, temp_pem)

    # Generate filename as <hash>.0
    final_cert = get_cert_hash(temp_pem)
    os.rename(temp_pem, final_cert)
    logging.info(f"[*] Using hash filename: {final_cert}")

    # ADB & cert install
    run(f'adb shell su -c "mkdir -m 700 {DEVICE_TMP_DIR}"', dry_run)
    run(f'adb push {final_cert} {DEVICE_TMP_DIR}/', dry_run)
    run(f'adb shell su -c "mount -t tmpfs tmpfs {SYSTEM_CERT_DIR}"', dry_run)
    run(f'adb shell su -c "cp {DEVICE_TMP_DIR}/* {SYSTEM_CERT_DIR}/"', dry_run)
    run(f'adb shell su -c "chown root:root {SYSTEM_CERT_DIR}/*"', dry_run)
    run(f'adb shell su -c "chmod 644 {SYSTEM_CERT_DIR}/*"', dry_run)
    run(f'adb shell su -c "chcon u:object_r:system_file:s0 {SYSTEM_CERT_DIR}/*"', dry_run)

    logging.info("\n[+] Certificate installed successfully. DO NOT reboot the device.")
    if os.path.exists(final_cert):
        os.remove(final_cert)

if __name__ == "__main__":
    main()
