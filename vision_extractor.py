"""
AI Vision Extractor using Google Gemini 2.0 Flash / Vision AI.
Extracts expiry dates, bills, amounts, and medicine details from camera photos.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
from datetime import datetime, date

import config


class VisionExtractor:
    """Extracts structured item info from images using Gemini Vision."""

    @staticmethod
    def extract_from_image(image_path: Path) -> Dict[str, Any]:
        """Send image to Gemini Vision to detect bill/item name, category, and expiry date."""
        if not config.GEMINI_API_KEY:
            logger.warning("No GEMINI_API_KEY provided; using heuristic date parser fallback.")
            return VisionExtractor._fallback_parse(image_path)

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=config.GEMINI_API_KEY)
            with open(image_path, "rb") as f:
                img_bytes = f.read()

            image_part = types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")

            prompt = (
                "Analyze this photo of a bill, receipt, medicine package, or grocery product.\n"
                "Extract the following information in strict valid JSON format:\n"
                "{\n"
                '  "title": "Clear concise name of the item, utility company, or medication",\n'
                '  "category": "Bill" or "Medication" or "Food" or "Document",\n'
                '  "expiry_date": "YYYY-MM-DD format (The due date or expiry/best before date)",\n'
                '  "amount": Float amount if bill or 0.0,\n'
                '  "notes": "Short notes like dosage instructions, account number, or storage"\n'
                "}\n"
                "Rules: If no explicit year is shown, infer the nearest future year based on today's date ("
                + date.today().isoformat()
                + "). Return ONLY JSON."
            )

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[image_part, prompt]
            )

            raw_text = response.text or "{}"
            # Extract json block if wrapped in backticks
            raw_text = re.sub(r"```json|```", "", raw_text).strip()
            data = json.loads(raw_text)

            # Ensure valid expiry date format
            exp = data.get("expiry_date", "")
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", exp):
                data["expiry_date"] = (date.today() + datetime.timedelta(days=7)).isoformat()

            return {
                "title": data.get("title") or "Unknown Item",
                "category": data.get("category") or "General",
                "expiry_date": data.get("expiry_date"),
                "amount": float(data.get("amount") or 0.0),
                "notes": data.get("notes") or "",
            }

        except Exception as e:
            logger.error(f"Gemini Vision extraction error: {e}")
            return VisionExtractor._fallback_parse(image_path)

    @staticmethod
    def _fallback_parse(image_path: Path) -> Dict[str, Any]:
        """Simple fallback if Gemini key is missing or offline."""
        from datetime import date, timedelta
        return {
            "title": "Scanned Item",
            "category": "Bill",
            "expiry_date": (date.today() + timedelta(days=7)).isoformat(),
            "amount": 0.0,
            "notes": "Auto-scanned photo (Please verify details)",
        }
