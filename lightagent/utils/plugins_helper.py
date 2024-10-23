import string

class PluginsHelper:
    
    @staticmethod
    def is_chinese(query: str) -> bool:
        chinese_char_count = 0
        total_char_count = 0

        for char in query:
            # Check if character is Chinese (CJK Unified Ideographs)
            if '\u4e00' <= char <= '\u9fff':
                chinese_char_count += 1
            # Check if character is Chinese punctuation (CJK Symbols and Fullwidth Forms)
            elif '\u3000' <= char <= '\u303F' or '\uFF00' <= char <= '\uFFEF':
                chinese_char_count += 1
            # Skip English punctuation
            elif char in string.punctuation:
                continue
            
            total_char_count += 1

        # Return True if majority of characters are Chinese
        if total_char_count > 0:
            return chinese_char_count / total_char_count > 0.333  # e.g., more than 50% are Chinese
        else:
            return False