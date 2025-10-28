from .whatsapp_backup_ocr import analyze_whatsapp_backup_screenshot
from .whatsapp_chat_ocr import analyze_whatsapp_chat_screenshot

def run_full_whatsapp_analysis(backup_path, chat_path):
    backup_result = analyze_whatsapp_backup_screenshot(backup_path)
    chat_result = analyze_whatsapp_chat_screenshot(chat_path)

    # Merge both results in one dictionary
    return {
        "backup": backup_result,
        "chat": chat_result
    }
