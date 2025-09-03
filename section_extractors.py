from bs4 import Tag, NavigableString
import re
from utils import is_stop_tag

def extract_and_format_infobox(target_content_div):
    """Extracts and formats the content of a portable-infobox."""
    infobox_lines = []
    infobox_element = target_content_div.find('aside', class_='portable-infobox')
    if not infobox_element:
        return infobox_lines

    infobox_lines.append("def {{char}}.Infobox():\n")
    title = infobox_element.find(class_='pi-title') or infobox_element.find(class_='pi-header')
    if title:
        infobox_lines.append(f"    # Title: {title.get_text(strip=True)}\n    ")

    for item in infobox_element.find_all(class_=['pi-item', 'pi-group', 'pi-data']):
        item_text = []
        item_label = item.find(class_='pi-data-label')
        if item_label:
            label_text = item_label.get_text(strip=True)
            item_text.append(f"     # {label_text}: ")
            item_value = item.find(class_='pi-data-value')
            if item_value:
                item_text.append(item_value.get_text(separator=' ', strip=True))
            infobox_lines.append("".join(item_text).strip() + "\n    ")
        elif item.name in ['ul', 'ol']:
            for li in item.find_all('li'):
                infobox_lines.append(f"    - {li.get_text(strip=True)}\n")
        else:
            stripped_item_text = item.get_text(separator=' ', strip=True)
            if stripped_item_text:
                infobox_lines.append(f"{stripped_item_text}\n    ")

    infobox_lines.append("\n")
    infobox_element.extract()
    return infobox_lines

def extract_introduction(target_content_div, main_page_soup_for_specific_div=None, link=None):
    """Extracts and formats the introduction section of the page."""
    introduction_content = []
    unwanted_classes = [
        ['custom-tabs-default', 'custom-tabs'],
        ['mbox', 'notice', 'hidden', 'plainlinks'],
        ['mbox', 'upcoming'],
        ['toc'],
        ['mbox', 'stub'],
        ['reference']
    ]

    def extract_from_div(content_div):
        extracted_content = []
        for element in content_div.children:
            if element.name in ['h1', 'h2']:
                break
            if element.name == 'p':
                text = element.get_text(separator=' ', strip=True)
                if text:
                    extracted_content.append(text)
            elif element.name == 'div':
                element_classes = element.get('class', [])
                if any(all(c in element_classes for c in classes_to_skip) for classes_to_skip in unwanted_classes):
                    continue
                text = element.get_text(separator=' ', strip=True)
                if text:
                    extracted_content.append(text)
            elif isinstance(element, NavigableString) and element.strip():
                extracted_content.append(element.strip())
        return extracted_content

    introduction_content.extend(extract_from_div(target_content_div))

    if main_page_soup_for_specific_div and link and link.endswith("/Lore"):
        intro_h2 = main_page_soup_for_specific_div.find('h2', string=lambda x: x and "Introduction" in x)
        if intro_h2:
            current = intro_h2.find_next_sibling()
            while current and not is_stop_tag(current):
                if current.name == 'p':
                    text = current.get_text(separator=' ', strip=True)
                    if text and text not in introduction_content:
                        introduction_content.append(text)
                current = current.find_next_sibling()

    if main_page_soup_for_specific_div:
        specific_div = main_page_soup_for_specific_div.find('div', class_='description standard-border')
        if specific_div:
            text = specific_div.get_text(separator='\n    ', strip=True)
            if text and text not in introduction_content:
                introduction_content.append(text)
            print(f"Successfully extracted 'description standard-border' div from main_page_soup.")

    return introduction_content

def extract_relationships(h2_section):
    """Extracts and formats the relationships section."""
    relationships_content = []
    current = h2_section.find_next_sibling()
    while current and not is_stop_tag(current):
        if current.name in ['h3', 'h4']:
            heading_text = current.get_text(strip=True)
            relationships_content.append(f"    # {heading_text}\n")
            next_elem = current.find_next_sibling()
            while next_elem and next_elem.name not in ['h3', 'h4'] and not is_stop_tag(next_elem):
                if next_elem.name == 'p':
                    text = next_elem.get_text(strip=True)
                    if text:
                        relationships_content.append(f"    {text}\n")
                elif next_elem.name == 'ul':
                    for li in next_elem.find_all('li'):
                        text = li.get_text(strip=True)
                        if text:
                            relationships_content.append(f"    - {text}\n")
                elif next_elem.name == 'div':
                    for p_or_li in next_elem.find_all(['p', 'li']):
                        text = p_or_li.get_text(strip=True)
                        if text:
                            relationships_content.append(f"    {'- ' if p_or_li.name == 'li' else ''}{text}\n")
                next_elem = next_elem.find_next_sibling()
            current = next_elem
            continue
        if current.name == 'p':
            text = current.get_text(strip=True)
            if text:
                relationships_content.append(f"    {text}\n")
        elif current.name == 'ul':
            for li in current.find_all('li'):
                text = li.get_text(strip=True)
                if text:
                    relationships_content.append(f"    - {text}\n")
        elif current.name == 'div':
            for p_or_li in current.find_all(['p', 'li']):
                text = p_or_li.get_text(strip=True)
                if text:
                    relationships_content.append(f"    {'- ' if p_or_li.name == 'li' else ''}{text}\n")
        current = current.find_next_sibling()
    return relationships_content

def extract_general_section(h2_section):
    """Extracts and formats a general section without subheadings."""
    section_content = []
    current = h2_section.find_next_sibling()
    while current and not is_stop_tag(current):
        if current.name == 'p':
            text = current.get_text(strip=True)
            if text:
                section_content.append(text)
        elif current.name == 'blockquote':
            block_items = []
            for child in current.children:
                if isinstance(child, Tag):
                    text = child.get_text(separator=' ', strip=True)
                    if text:
                        block_items.append(text)
                elif isinstance(child, NavigableString) and child.strip():
                    block_items.append(child.strip())
            if block_items:
                section_content.append(" ".join(block_items))
        elif current.name in ['ul', 'ol']:
            for li in current.find_all('li'):
                text = li.get_text(strip=True)
                if text:
                    section_content.append(f"- {text}")
        elif current.name == 'div':
            for p_or_li in current.find_all(['p', 'li']):
                text = p_or_li.get_text(strip=True)
                if text:
                    section_content.append(f"{'- ' if p_or_li.name == 'li' else ''}{text}")
        current = current.find_next_sibling()
    return section_content

def extract_dialogue_section(h2_section):
    """Extracts and formats a dialogue section."""
    dialogue_content = []
    current = h2_section.find_next_sibling()
    while current and not is_stop_tag(current):
        if current.name == 'h3':
            current_location = current.get_text(strip=True)
            dialogue_content.append(f"    # Lokasi: {current_location}\n")
        elif current.name == 'div' and 'dialogue' in current.get('class', []):
            for dl_tag in current.find_all('dl'):
                dt_tag = dl_tag.find('dt')
                all_dd_tags = dl_tag.find_all('dd')
                if dt_tag:
                    dialogue_content.append(f"    {dt_tag.get_text(strip=True)}\n")
                for dd_tag in all_dd_tags:
                    speaker_name, dialogue_text = "", ""
                    b_tag = dd_tag.find('b')
                    if b_tag:
                        speaker_name = b_tag.get_text(strip=True).replace(':', '')
                        dialogue_parts = [p.strip() for p in b_tag.next_siblings if isinstance(p, NavigableString) and p.strip()]
                        dialogue_parts.extend([t.get_text(separator=' ', strip=True) for t in b_tag.next_siblings if isinstance(t, Tag)])
                        dialogue_text = " ".join(dialogue_parts).strip().strip('"')
                    else:
                        dialogue_text = dd_tag.get_text(separator=' ', strip=True).strip('"')
                    if speaker_name and dialogue_text:
                        dialogue_content.append(f"        {speaker_name}: \"{dialogue_text}\"\n")
                    elif dialogue_text and dd_tag.find('span'):
                        dialogue_content.append(f"        => {dialogue_text}\n")
                    elif dialogue_text:
                        dialogue_content.append(f"        \"{dialogue_text}\"\n")
        current = current.find_next_sibling()
    return dialogue_content

def extract_character_story(h2_section):
    """Extracts and formats character story sections from h3 subheadings."""
    story_content = []
    current_h3 = h2_section.find_next('h3')
    while current_h3 and current_h3.find_parent('h2') == h2_section:
        heading_text = current_h3.get_text(strip=True)
        story_content.append(f"    # {heading_text}\n")
        next_boundary = current_h3.find_next(['h3', 'h2'])
        current_p = current_h3.find_next('p')
        while current_p and (not next_boundary or current_p != next_boundary):
            if current_p and current_p.find_previous('h3') == current_h3:
                text = current_p.get_text(strip=True)
                if text:
                    story_content.append(f"    {text}\n")
            current_p = current_p.find_next('p')
            if current_p and next_boundary and current_p == next_boundary:
                break
        current_h3 = current_h3.find_next('h3')
    return story_content
