# WhatsAppPentest Tool (Prototype)

A simple Python-based utility to help security testers work with WhatsApp exported chat and images.

## Features

- Modify exported WhatsApp chat text with search/replace
- Change image references in chat text (`old.jpg` -> `new.jpg`)
- Modify image binary data (append hidden payload)
- Add basic PNG metadata for embedded notes

## Usage

1. Install dependencies

```bash
python3 -m pip install Pillow
python3 -m pip install transformers sentencepiece
```

2. Run chat text modifications

```bash
python3 whatsapppentest.py --chat chat.txt --chat-out chat-modified.txt --search "old text" --replace "new text"
```

3. Replace image reference in chat

```bash
python3 whatsapppentest.py --chat chat.txt --chat-out chat-modified.txt --replace-img-ref "IMG-20250101-WA0001.jpg" "new-image.jpg"
```

4. Modify an image by embedding extra data

```bash
python3 whatsapppentest.py --image whatsapp.jpg --image-out whatsapp-modified.jpg --embed-data "INVISIBLE_PAYLOAD"
```

5. Add PNG metadata note (prototype)

```bash
python3 whatsapppentest.py --image whatsapp.png --image-out whatsapp-modified.png --metadata "pentest note"
```

6. AI-enhanced chat paraphrase (optional)

```bash
python3 whatsapppentest.py --chat chat.txt --chat-out chat-ai.txt --ai-paraphrase --ai-model t5-small
```

7. AI-generated sample chat (optional)

```bash
python3 whatsapppentest.py --chat-out chat-generated.txt --ai-generate "friendly security team discussing updates" --ai-model t5-small
```

## Minimum system requirements

- CPU: Intel Core i5 (or equivalent)
- RAM: 16GB
- GPU: NVIDIA RTX 3050 (for optional local image processing acceleration)
- Storage: 512GB SSD minimum
- OS: Linux, macOS, Windows

## Security and ethics

This tool is for authorized security testing only. Do not use it to compromise any system or data without explicit permission.

## Notes

- Make sure to use exported WhatsApp chat text (`.txt`) from WhatsApp's built-in export feature.
- This is a prototype; customize it for your workflow and targets.
