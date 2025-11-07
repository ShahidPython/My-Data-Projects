import random
import string

def welcome():
    print("🔐 Welcome to the Password Generator!")
    print("------------------------------------------")

def get_password_length():
    while True:
        try:
            length = int(input("Enter desired password length (minimum 4): "))
            if length < 4:
                print("Password length should be at least 4 characters.")
            else:
                return length
        except ValueError:
            print("Please enter a valid number.")

def get_character_options():
    print("\nChoose character types to include in the password:")
    use_lowercase = input("Include lowercase letters? (y/n): ").lower() == "y"
    use_uppercase = input("Include uppercase letters? (y/n): ").lower() == "y"
    use_digits = input("Include digits? (y/n): ").lower() == "y"
    use_symbols = input("Include symbols? (y/n): ").lower() == "y"

    char_pool = ""

    if use_lowercase:
        char_pool += string.ascii_lowercase
    if use_uppercase:
        char_pool += string.ascii_uppercase
    if use_digits:
        char_pool += string.digits
    if use_symbols:
        char_pool += string.punctuation
    
    if not char_pool:
        print("⚠️  You must select at least one character type.")
        return get_character_options()
    
    return char_pool

def generate_password(length, characters):
    password = ''.join(random.choices(characters, k=length))
    return password

if __name__ == "__main__":
    welcome()
    password_length = get_password_length()
    char_pool = get_character_options()
    password = generate_password(password_length, char_pool)
    print("\n🔑 Your generated password is:")
    print(password)