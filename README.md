# 🔐 WhatsApp Forensics & Pentest Utility v2.0

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-informational?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-Research%20Only-red?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Price-%24230%20(was%20%24530)-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Author-redrecon-blueviolet?style=for-the-badge" />
</p>

---

> ⚠️ **LEGAL NOTICE**: This tool is intended **solely for authorized security research, digital forensics investigations, and penetration testing with explicit written permission**. Any unauthorized use is illegal and strictly prohibited. You bear full legal responsibility for how you use this software.

---

## 💰 Pricing

| Plan | Price | Details |
|------|-------|---------|
| ~~Original Price~~ | ~~$800~~ | — |
| **Special Offer Price** | **$400** | ✅ Save **$400** — Lifetime updates + Email support included |

> 🎯 **Limited-time offer.** Single-user, non-commercial research license. Purchase includes access to all future v2.x updates and dedicated email support.

---

## 🧰 What Is This Tool?

**WhatsApp Forensics & Pentest Utility v2.0** is a professional-grade Python-based command-line tool designed for:

- **Digital forensics investigators** working with exported WhatsApp chat data
- **Penetration testers** performing authorized testing on mobile messaging applications
- **Security researchers** studying WhatsApp chat file structures and image steganography

The tool provides both an **interactive menu-driven interface** (no command memorization needed) and a **traditional CLI mode** for scripting and automation.

---

## ✨ Features

### 🗨️ Chat Analysis & Modification
| Feature | Description |
|---------|-------------|
| **Chat Text Modifier** | Find and replace any keyword or phrase inside a `.txt` exported chat |
| **Image Reference Replacer** | Swap out image filenames referenced within a chat log |
| **Chat Metadata Analyser** | Parse participants, message counts, media count from a chat export |
| **Word Frequency Analyser** | Visualize the top N most-used words in a chat (with bar graph) |

### 🖼️ Image Forensics
| Feature | Description |
|---------|-------------|
| **Image Payload Embedder** | Append hidden payload bytes into JPEG/PNG image files (steganography testing) |
| **Image Metadata Editor** | Embed pentest notes directly into PNG metadata fields |

### 🤖 AI-Powered Features *(optional)*
| Feature | Description |
|---------|-------------|
| **AI Chat Paraphraser** | Paraphrase an entire exported chat using a local T5 AI model |
| **AI Chat Generator** | Generate a realistic synthetic WhatsApp chat from a text prompt |

---

## 🖥️ Interactive Mode (Recommended)

Launch with no arguments to enter the full interactive menu:

```bash
python3 whatsapppentest.py
```

You'll see a **professional banner** with pricing info and a numbered menu:

```
╔══════════════════════════════════════════════════════════════════╗
║       WhatsApp Forensics & Pentest Utility  v2.0                ║
║  Original Price : $530  │  Special Offer : $230  │  Save $300!  ║
╚══════════════════════════════════════════════════════════════════╝

   1.  Chat Text Modifier          Replace keywords/phrases inside a chat
   2.  Image Reference Replacer    Update image filenames in a chat .txt
   3.  Image Payload Embedder      Append hidden payload bytes into JPG/PNG
   4.  Image Metadata Editor       Embed a pentest note into PNG metadata
   5.  AI Chat Paraphraser         Re-phrase chat using a local AI model
   6.  AI Chat Generator           Generate synthetic chat from a prompt
   7.  Chat Metadata Analyser      Parse chat statistics & participant list
   8.  Word Frequency Analyser     Show most-used words in a chat
   9.  About / Pricing             Tool info and license details
  10.  Exit
```

Simply type a number and press **Enter**. The tool guides you step-by-step with prompts for all required inputs.

---

## ⌨️ CLI (Script) Mode

For automation or CI/CD pipelines, use command-line flags directly:

### 1. Install Dependencies

```bash
pip install Pillow
pip install transformers sentencepiece    # Optional – only for AI features
```

### 2. Chat Text Search & Replace

```bash
python3 whatsapppentest.py \
  --chat chat.txt \
  --chat-out chat-modified.txt \
  --search "original phrase" \
  --replace "replacement phrase"
```

### 3. Replace an Image Reference in Chat

```bash
python3 whatsapppentest.py \
  --chat chat.txt \
  --chat-out chat-with-new-ref.txt \
  --replace-img-ref "IMG-20250101-WA0001.jpg" "evidence-photo.jpg"
```

### 4. Embed Hidden Payload into an Image

```bash
python3 whatsapppentest.py \
  --image whatsapp.jpg \
  --image-out whatsapp-modified.jpg \
  --embed-data "HIDDEN_TEST_PAYLOAD"
```

### 5. Add Metadata Note to PNG

```bash
python3 whatsapppentest.py \
  --image screenshot.png \
  --image-out screenshot-tagged.png \
  --metadata "Forensic case #2025-001"
```

### 6. Analyse Chat Metadata

```bash
python3 whatsapppentest.py --chat chat.txt --analyse
```

### 7. Word Frequency Report

```bash
python3 whatsapppentest.py --chat chat.txt --word-freq
```

### 8. AI Paraphrase Chat *(requires transformers)*

```bash
python3 whatsapppentest.py \
  --chat chat.txt \
  --chat-out chat-paraphrased.txt \
  --ai-paraphrase \
  --ai-model t5-small
```

### 9. AI Generate Synthetic Chat *(requires transformers)*

```bash
python3 whatsapppentest.py \
  --chat-out synthetic-chat.txt \
  --ai-generate "two friends discussing a weekend trip" \
  --ai-model t5-small
```

---

## 🖥️ System Requirements

### Main Host Machine

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | Intel Core i5 (8th gen+) | Intel Core i7 / AMD Ryzen 7 |
| **RAM** | 16 GB | 32 GB |
| **GPU** | NVIDIA RTX 3050 (for AI features) | NVIDIA RTX 3060+ |
| **Storage** | 512 GB SSD | 1 TB NVMe SSD |
| **OS** | Linux, macOS, Windows 10+ | Kali Linux / Ubuntu 22.04 |
| **Python** | 3.8+ | 3.11+ |

### Encryption Analysis Module — Dedicated Hardware

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **Device** | Raspberry Pi Zero 2W | Required for the offline encryption key analysis module |
| **OS** | Raspberry Pi OS Lite (64-bit) | Headless setup recommended |
| **RAM** | 512 MB (on-board) | Sufficient for key schedule analysis tasks |
| **Storage** | 16 GB microSD (Class 10 / UHS-I) | Stores wordlists and key fragments |
| **Connectivity** | Wi-Fi 802.11 b/g/n | Used to sync results back to the host machine |
| **Power** | 5V / 2.5A micro-USB | Stable power supply recommended for long-running jobs |

> [!IMPORTANT]
> The **Raspberry Pi Zero 2W** is used as a dedicated offline co-processor for the encryption breaking module. Its low power draw (~0.4W idle) makes it ideal for running extended key-cracking dictionary attacks without burdening the main host machine. Connect it to the host via Wi-Fi or USB-OTG and run the encryption module in headless mode.

> The GPU is **only required** for AI-powered features (paraphrase/generate). All other features run on CPU.

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/your-org/whatsapp-pentest-tool.git
cd whatsapp-pentest-tool

# Install core dependency
pip install Pillow

# (Optional) Install AI dependencies
pip install transformers sentencepiece torch
```

---

## 📁 Input File Format

This tool works with **WhatsApp's native export format**. To export a chat:

1. Open WhatsApp → go to a chat
2. Tap the **⋮ menu** → **More** → **Export Chat**
3. Choose **Without Media** (exports a `.txt` file)
4. Transfer the `.txt` file to your analysis machine

The exported file follows this pattern:
```
01/15/2025, 10:32 AM - Alice: Hey, are you there?
01/15/2025, 10:33 AM - Bob: Yes, give me a moment.
01/15/2025, 10:35 AM - Alice: IMG-20250115-WA0001.jpg (file attached)
```

---

## 🛡️ Ethics & Legal Disclaimer

- ✅ **Authorized use**: Forensics investigations with lawful access, penetration tests with written permission, academic research in controlled environments.
- ❌ **Prohibited use**: Accessing another person's data without consent, distributing modified chat logs as genuine, any activity that violates local laws.

The developers of this tool **accept no liability** for misuse. By using this software you agree to comply with all applicable laws and regulations.

---

## 📧 Support & License

- **License**: Single-User Non-Commercial Research License
- **Support**: Email support included with purchase
- **Updates**: Lifetime v2.x updates included

---

*WhatsApp Forensics & Pentest Utility v2.0 — Professional Security Research Platform*
