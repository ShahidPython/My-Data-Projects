import random
import json
import os
import re

class MadLibs:
    def __init__(self, templates_file=None):
        self.templates = self.load_templates(templates_file)
    
    def load_templates(self, templates_file):
        default_templates = [
            {
                "title": "Summer Adventure",
                "template": """Last summer, I went to {place} and saw a very {adjective} {noun}. 
I {verb} it {adverb} and then ran away laughing!"""
            },
            {
                "title": "Fantasy Tale",
                "template": """Once upon a time, a {adjective} {noun} {verb} {adverb} 
in the middle of {place}. Everyone was amazed!"""
            },
            {
                "title": "Space Odyssey",
                "template": """Captain {name} stared at the {adjective} {noun} through the spaceship window. 
"We need to {verb} {adverb}!" they shouted, as the ship approached {place}."""
            },
            {
                "title": "Mystery Story",
                "template": """It was a {adjective} night when the {noun} disappeared. 
I had to {verb} {adverb} to find it before reaching {place}."""
            },
            {
                "title": "Food Adventure",
                "template": """The {adjective} {noun} made me {verb} {adverb} 
when I tasted it at {place}. What an experience!"""
            },
            {
                "title": "Animal Encounter",
                "template": """While hiking in {place}, I encountered a {adjective} {animal}. 
It {verb} {adverb} and then disappeared into the woods."""
            },
            {
                "title": "Dream Story",
                "template": """Last night, I had a dream about a {adjective} {noun} that could {verb}. 
It was so {emotion} that I woke up {adverb}!"""
            }
        ]
        
        if templates_file and os.path.exists(templates_file):
            try:
                with open(templates_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return default_templates
        return default_templates
    
    def get_placeholders(self, template):
        """Extract placeholders from a template string"""
        return re.findall(r'\{(\w+)\}', template)
    
    def generate_story(self, template, words):
        """Generate a story by replacing placeholders with provided words"""
        try:
            return template.format(**words)
        except KeyError as e:
            raise ValueError(f"Missing value for placeholder: {e}")
    
    def get_random_template(self):
        """Return a random template from available templates"""
        return random.choice(self.templates)
    
    def get_all_templates(self):
        """Return all available templates"""
        return self.templates
    
    def get_template_by_index(self, index):
        """Get a specific template by index"""
        if 0 <= index < len(self.templates):
            return self.templates[index]
        return None