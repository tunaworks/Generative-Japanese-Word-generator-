import os
import random

# Main configs
WORD_LENGTH = 4
WORDS_GENERATED = 10000
CHAR_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hira")
"""
If you wanted to specify a particular starting word/letter, its all in lowercase
e.g. STARTS_WITH = "K".lower(), ENDS_WITH = "N".lower()
"""

ENDS_WITH = ""
STARTS_WITH = ""
PROHIBITED_STARTS = ("dy", "z", "t", "di", "du", "-", "wo")

def load_chars():
    # Grab hira->en mapping
    hira = {}
    
    for file_name in os.listdir(CHAR_FOLDER):
        try:
            with open(os.path.join(CHAR_FOLDER, file_name), "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        hira.update(eval(line))
        except UnicodeDecodeError:
            # JIS/Shift-JIS/EUC-JP
            try:
                with open(os.path.join(CHAR_FOLDER, file_name), "r", encoding="shift-jis") as f:
                    for line in f:
                        if line.strip():
                            hira.update(eval(line))
            except Exception as e:
                print(f"Can't read {file_name}: {e}")
    
    return hira

def is_valid_start(romaji):
    return (romaji.lower().startswith(STARTS_WITH) and 
            not any(romaji.lower().startswith(p) for p in PROHIBITED_STARTS))

def is_valid_end(romaji):
    return romaji.lower().endswith(ENDS_WITH)

def make_word(chars):
    word_jp = ""
    word_romaji = ""
    position = 0
    
    while position < WORD_LENGTH:
        # Grab a random char
        letter_key = random.choice(list(chars))
        letter_val = chars[letter_key]
        
        # Hard-code positional rules, gg
        if position == 0:
            # First char needs to follow start rules
            if not is_valid_start(letter_val):
                continue
                
        elif position == 1:
            # Second char: if first was "う", next can't be "ん"
            if word_jp[-1] == "う" and letter_val.lower().startswith("n"):
                continue
                
        elif position > 1:
            # Later positions: "ち" followed by "う"
            if word_jp[-1] == "ち" and letter_val.lower().startswith("u"):
                continue
        
        # No double dashes (ー) - looks weird
        if word_jp and word_jp[-1] == "ー" and letter_key == "ー":
            continue
            
        # Last position needs proper ending
        if position == WORD_LENGTH - 1 and not is_valid_end(letter_val):
            continue
            
        # Handle the dash (ー) (vowel extension)
        if letter_key == "ー" and word_jp:
            if word_romaji[-1].startswith("o"):
                letter_val = "U"  # for long o sounds
            else:
                letter_val = word_romaji[-1]
        
        # Add to our word
        word_jp += letter_key
        word_romaji += letter_val
        
        # Move position tracker based on char length
        position += max(1, len(letter_key))
    
    return f"{word_jp} {word_romaji}"

def get_output_filename():
    # Create file if it doesn't exist, else create a new file_{number} instance
    base_dir = os.path.dirname(os.path.abspath(__file__))
    base = os.path.join(base_dir, "word_output")

    # Check for existing filenames with this structure until an available integer exists
    counter = 0
    while True:
        filename = f"{base}_{counter}.txt" if counter else f"{base}.txt"
        if not os.path.exists(filename):
            return filename
        counter += 1

def main():
    # Grab character set
    chars = load_chars()
    if not chars:
        print("No characters found. Check the hira folder.")
        return
        
    print(f"Got {len(chars)} characters")
    print(f"Generating {WORDS_GENERATED} words...")
    
    # Make a bunch of unique words
    unique_words = set()
    attempts = 0
    
    while len(unique_words) < WORDS_GENERATED:
        word = make_word(chars)
        
        if word not in unique_words:
            unique_words.add(word)
            
            # Progress updates
            if len(unique_words) % 1000 == 0:
                print(f"Got {len(unique_words)} words so far...")
        
        attempts += 1
        if attempts > WORDS_GENERATED * 10:
            print(f"Hit the attempt limit. Generated {len(unique_words)} words.")
            break
    
    # Save everything in random order
    output_file = get_output_filename()
    words_list = list(unique_words)
    random.shuffle(words_list) # randomize
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(words_list))
        print(f"Done! Generated {len(words_list)} words in {output_file}")
    except IOError as e:
        print(f"Failed to save the file: {str(e)}")

if __name__ == "__main__":
    main()