
import os
import re

def update_content():
    """
    Reads the vindkraftsersattning_guide.md file, identifies the main sections,
    and generates a new article based on the identified sections.
    """
    try:
        with open("projects/vindkollen/vindkraftsersattning_guide.md", "r", encoding="utf-8") as f:
            content = f.read()

        # Identify the main sections of the guide
        sections = re.findall(r"## (.*)", content)

        if not sections:
            return "No sections found in the guide."

        # Generate a new article based on the sections
        new_article = "# New Article Based on Vindkraftsersättning Guide\n\n"
        new_article += "This article is an overview of the main topics discussed in our comprehensive guide on wind power compensation.\n\n"

        for section in sections:
            new_article += f"## {section}\n"
            new_article += f"Read more about {section.lower()} in our full guide.\n\n"

        with open("projects/vindkollen/new_article.md", "w", encoding="utf-8") as f:
            f.write(new_article)

        return "New article has been created successfully."

    except FileNotFoundError:
        return "Error: vindkraftsersattning_guide.md not found."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == "__main__":
    result = update_content()
    print(result)
