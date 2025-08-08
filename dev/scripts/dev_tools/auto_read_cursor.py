#!/usr/bin/env python3
"""
Auto-read Cursor chat responses
Monitors clipboard and auto-reads new content
"""

import time
import subprocess
import pyperclip
import threading
from datetime import datetime

class CursorAutoReader:
    def __init__(self):
        self.last_clipboard = ""
        self.is_reading = False
        self.voice = "Samantha"  # or "Alex", "Victoria"
        self.rate = 200  # words per minute
        
    def speak_text(self, text):
        """Speak text using macOS say command"""
        if self.is_reading:
            return  # Don't interrupt current speech
            
        self.is_reading = True
        try:
            # Text is already cleaned when passed to this method
            if not text or len(text.strip()) < 5:
                return
                
            # Use macOS say command
            subprocess.run([
                'say', 
                '-v', self.voice,
                '-r', str(self.rate),
                text
            ], check=True)
        except Exception as e:
            print(f"Speech error: {e}")
        finally:
            self.is_reading = False
    
    def clean_text_for_speech(self, text):
        """Clean text to sound better when spoken - focus on conversational content only"""
        
        # Skip if it looks like code, terminal output, or technical data
        if self.is_technical_content(text):
            return None
            
        # Remove code blocks entirely
        import re
        text = re.sub(r'```[\s\S]*?```', '', text)
        
        # Remove inline code
        text = re.sub(r'`[^`]+`', '', text)
        
        # Remove terminal-style output
        text = re.sub(r'^\s*[\$%#]\s+.*$', '', text, flags=re.MULTILINE)
        
        # Remove excessive formatting but keep structure
        text = text.replace('##', '')
        text = text.replace('**', '')
        text = text.replace('###', '')
        
        # Replace symbols with words (but less aggressively)
        text = text.replace('✅', 'yes')
        text = text.replace('❌', 'no')
        text = text.replace('🎯', '')
        text = text.replace('🔒', '')
        text = text.replace('⚠️', 'note:')
        
        # Remove empty lines and clean up
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = ' '.join(lines)
        
        # Only return if there's substantial conversational content
        if len(text.strip()) < 20:
            return None
            
        return text.strip()
    
    def is_technical_content(self, text):
        """Detect if text is primarily technical/code content that shouldn't be read"""
        # Check for high concentration of technical indicators
        technical_indicators = [
            'def ', 'import ', 'class ', 'function',
            'SELECT ', 'INSERT ', 'UPDATE ', 'CREATE ',
            'DB_CONFIG', 'psycopg2', 'cursor',
            '#!/', 'python3', 'pip install',
            'Exit code:', 'Command output:',
            '(venv)', 'MacBook-Air',
            'Exception:', 'Error:', 'Traceback',
            'Connected to database',
            'Security setup', 'RLS enabled'
        ]
        
        # Count technical indicators
        technical_count = sum(1 for indicator in technical_indicators if indicator in text)
        
        # If more than 3 technical indicators, probably code/output
        if technical_count > 3:
            return True
            
        # Check for code block patterns
        if '```' in text or text.count('`') > 5:
            return True
            
        # Check for terminal output patterns
        if any(pattern in text for pattern in ['$', '% ', 'Exit code:', '(venv)']):
            return True
            
        return False
    
    def monitor_clipboard(self):
        """Monitor clipboard for new content to read"""
        print("🎵 Auto-reader started. Copy text to hear it read aloud.")
        print("Press Ctrl+C to stop.")
        
        try:
            while True:
                try:
                    current_clipboard = pyperclip.paste()
                    
                    # Check if clipboard changed and has substantial content
                    if (current_clipboard != self.last_clipboard and 
                        len(current_clipboard.strip()) > 10 and
                        not self.is_reading):
                        
                        # Clean the text first to see if it's worth reading
                        cleaned_text = self.clean_text_for_speech(current_clipboard)
                        
                        if cleaned_text:  # Only read if we have conversational content
                            print(f"📢 Reading: {cleaned_text[:50]}...")
                            
                            # Read in background thread so monitoring continues
                            thread = threading.Thread(
                                target=self.speak_text, 
                                args=(cleaned_text,)
                            )
                            thread.daemon = True
                            thread.start()
                        else:
                            print(f"⏭️  Skipping technical content: {current_clipboard[:30]}...")
                        
                        self.last_clipboard = current_clipboard
                    
                    time.sleep(0.5)  # Check every 500ms
                    
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n🛑 Auto-reader stopped.")

if __name__ == "__main__":
    print("🎵 Cursor Auto-Reader")
    print("=" * 30)
    print("Usage:")
    print("1. Run this script")
    print("2. In Cursor, copy any chat response (Cmd+A, Cmd+C)")
    print("3. Text will be read aloud automatically")
    print("4. Press Ctrl+C to stop")
    print()
    
    reader = CursorAutoReader()
    reader.monitor_clipboard()
