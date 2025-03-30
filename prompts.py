
from utils.constants import category_emojis

templates_by_category = {
    "Work": {
        "Email Draft": {
            "goal": "Write a professional email about [topic]",
            "tone": "Professional",
            "output_type": "Text",
            "audience": "Colleagues or business partners"
        },
        "Meeting Summary": {
            "goal": "Summarize the key points from a meeting about [topic]",
            "tone": "Clear and helpful",
            "output_type": "Bullet List",
            "audience": "Team members"
        }
    },
    "Creative": {
        "Story Idea": {
            "goal": "Generate a creative story idea about [theme]",
            "tone": "Creative",
            "output_type": "Text",
            "audience": "Writers"
        },
        "Blog Post": {
            "goal": "Write a blog post about [topic]",
            "tone": "Professional",
            "output_type": "Markdown",
            "audience": "General readers"
        }
    },
    "Technical": {
        "Code Explanation": {
            "goal": "Explain how [code/algorithm] works",
            "tone": "Clear and helpful",
            "output_type": "Text",
            "audience": "Developers"
        },
        "Documentation": {
            "goal": "Create documentation for [project/feature]",
            "tone": "Professional",
            "output_type": "Markdown",
            "audience": "Technical users"
        }
    },
    "Personal": {
        "Journal Prompt": {
            "goal": "Create a reflective journal prompt about [topic]",
            "tone": "Reflective",
            "output_type": "Text",
            "audience": "Personal use"
        },
        "Congratulations Message": {
            "goal": "Write a congratulatory message for [occasion]",
            "tone": "Motivational",
            "output_type": "Text",
            "audience": "Friends or family"
        }
    },
    "Social Media": {
        "Tweet Thread": {
            "goal": "Create a thread of tweets about [topic]",
            "tone": "Casual",
            "output_type": "Conversation",
            "audience": "Twitter followers"
        },
        "LinkedIn Post": {
            "goal": "Write a professional LinkedIn post about [topic]",
            "tone": "Professional",
            "output_type": "Text",
            "audience": "Professional network"
        }
    }
}

def get_flat_templates():
    templates = {}
    template_categories = {}
    for category, entries in templates_by_category.items():
        for name, data in entries.items():
            templates[name] = data
            template_categories[name] = category
    return templates, template_categories
