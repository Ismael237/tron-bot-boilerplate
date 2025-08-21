from typing import List, Dict
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

class KeyboardBuilder:
    """Dynamic keyboard construction"""
    
    @staticmethod
    def build_inline_keyboard(buttons_config: List[Dict]) -> InlineKeyboardMarkup:
        """Builds an inline keyboard from a configuration"""
        keyboard = []
        for row_config in buttons_config:
            row = []
            for button_config in row_config:
                button = InlineKeyboardButton(
                    text=button_config['text'],
                    callback_data=button_config.get('callback_data'),
                    url=button_config.get('url')
                )
                row.append(button)
            keyboard.append(row)
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def build_navigation_keyboard(
        current_page: int,
        total_pages: int,
        prefix: str = "page"
    ) -> InlineKeyboardMarkup:
        """Generic pagination keyboard"""
        buttons = []
        if current_page > 1:
            buttons.append({
                "text": "⬅️ Previous", 
                "callback_data": f"{prefix}_{current_page-1}"
            })
        if current_page < total_pages:
            buttons.append({
                "text": "Next ➡️", 
                "callback_data": f"{prefix}_{current_page+1}"
            })
        
        return KeyboardBuilder.build_inline_keyboard([buttons])