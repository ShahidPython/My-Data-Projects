from .core import MadLibs

def mad_libs_cli():
    print("\033[1;36m" + "=" * 50)
    print("          MAD LIBS - CLI VERSION")
    print("=" * 50 + "\033[0m")
    
    madlibs = MadLibs()
    
    while True:
        # Select a random template
        template_data = madlibs.get_random_template()
        template = template_data["template"]
        title = template_data.get("title", "Untitled Story")
        
        print(f"\n\033[1;35m{title}\033[0m")
        print("\033[1mPlease provide the following words:\033[0m")
        
        # Get placeholders from template
        placeholders = madlibs.get_placeholders(template)
        words = {}
        
        for placeholder in placeholders:
            words[placeholder] = input(f"Enter a {placeholder}: ").strip()
        
        if all(words.values()):
            try:
                story = madlibs.generate_story(template, words)
                print("\n\033[1;32mHere is your story:\033[0m")
                print("\033[1;33m" + story + "\033[0m")
                
                play_again = input("\nPlay again? (y/n): ").lower()
                if play_again != 'y':
                    print("\033[1;36mThanks for playing Mad Libs!\033[0m")
                    break
            except ValueError as e:
                print(f"\033[1;31mError: {e}\033[0m")
        else:
            print("\033[1;31mPlease fill in all the words!\033[0m")

if __name__ == "__main__":
    mad_libs_cli()