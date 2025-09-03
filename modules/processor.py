from modules.section_extractors import (
    extract_and_format_infobox,
    extract_introduction,
    extract_relationships,
    extract_general_section,
    extract_dialogue_section,
    extract_character_story,
)

section_headline_map = {
    "Appearance": "Appearance",
    "Personality": "Personality",
    "Background": "Background",
    "Relationships": "Relationships",
    "Relationship": "Relationship",
    "Abilities and Skills": "Abilities and Skills",
    "Abilities and Powers": "Abilities and Powers",
    "Character_Stories": "Character Stories",
    "Official_Introduction": "Official Introduction",
    "Open-World_Dialogue": "Open-World Dialogue",
    "Character_Synopsis": "Character Synopsis",
    "Character_Statistics": "Character Statistics",
    "Agent_Intel": "Agent Intel",
    "Chronology": "Chronology",
    "Abilities": "Abilities",
    "Equipment": "Equipment",
    "Weaknesses": "Weaknesses",
    "Profile": "Profile",
    "History": "History",
    "Fans": "Fans",
    "Quotes": "Quotes",
    "Etymology": "Etymology",
    "Trivia": "Trivia",
}

def process_fandom_page(main_soup, intro_soup, intro_link, char_name, link):
    """
    Orchestrates the process of extracting content from the Fandom page.
    """
    output = []

    # Initial imports
    for section_name in ["Expression", "Lore", "Dialogue", "Stats", "Emotionals", "Bio"]:
        output.append(f"import {{char}}.{section_name}\n")
    output.append(f"\nfrom '{char_name}' ")
    output.append("import {{char}}\n")
    output.append("from {{user}} import {{user}}\n\n")

    # Find content divs
    content_div = main_soup.find('div', class_='mw-content-ltr')
    if not content_div:
        print("Div dengan kelas 'mw-content-ltr' tidak ditemukan.")
        return []

    intro_content_div = content_div
    if intro_soup:
        temp_intro_content_div = intro_soup.find('div', class_='mw-content-ltr')
        if temp_intro_content_div:
            intro_content_div = temp_intro_content_div
        else:
            print("Warning: 'mw-content-ltr' div not found in intro URL, using main URL content for intro.")

    # Extract Infobox
    infobox_output_lines = extract_and_format_infobox(intro_content_div if intro_soup else content_div)
    output.extend(infobox_output_lines)

    # Extract Introduction
    intro_content = extract_introduction(intro_content_div if intro_soup else content_div, main_soup if intro_link != link else None)
    if intro_content:
        output.append("def {{char}}.Introduction():\n")
        output.append("    " + "\n    ".join(intro_content) + "\n\n")

    # Process each section
    for section_function_name, headline_text in section_headline_map.items():
        h2_section = content_div.find('h2', id=headline_text.replace(" ", "_"))
        if not h2_section:
            h2_span = content_div.find('span', class_='mw-headline', string=headline_text)
            if h2_span:
                h2_section = h2_span.find_parent('h2')

        if h2_section:
            output.append(f"def {{char}}.{section_function_name}():\n")
            if section_function_name in ["Relationships", "Relationship", "History", "Agent Intel", "Abilities", "Equipment", "Profile"]:
                section_content = extract_relationships(h2_section)
                output.extend(section_content)
            elif section_function_name == "Character_Stories":
                section_content = extract_character_story(h2_section)
                output.extend(section_content)
            elif section_function_name == "Open-World_Dialogue":
                section_content = extract_dialogue_section(h2_section)
                output.extend(section_content)
            elif section_function_name in ["Etymology", "Trivia", "Quotes", "Fans"]:
                section_content = extract_general_section(h2_section)
                for item in section_content:
                    output.append(f"    {item}\n" if item.startswith('-') else f"    {item}\n")
            else:
                section_content = extract_general_section(h2_section)
                output.append("    " + "\n    ".join(section_content) + "\n")
            output.append("\n")

    return output
