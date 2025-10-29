from .whatsapp_backup_ocr import analyze_whatsapp_backup_screenshot
from .whatsapp_chat_ocr import analyze_whatsapp_chat_screenshot

def run_full_whatsapp_analysis(backup_path, chat_path):
    """
    Runs full OCR analysis on both backup & chat screenshots
    and merges the results.
    """
    backup_result = analyze_whatsapp_backup_screenshot(backup_path)
    chat_result = analyze_whatsapp_chat_screenshot(chat_path)

    # Merge both results into a single dictionary (flat structure)
    combined = {**backup_result, **chat_result}
    return combined
