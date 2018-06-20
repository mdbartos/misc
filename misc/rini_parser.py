import re

filepath = 'experience.tex'
replacements = {'\\\\newline' : '',
                '  +' : ' ',
                '^ *' : ''}

def parse_cventries(filepath, replacements):
    section_header = '\\cventry'
    subsection_header = '\\begin{cvitems}'
    subsection_footer = '\\end{cvitems}'
    cv_list = []

    with open(filepath) as experience:
    r = experience.read()

    search_text = r

    for _ in range(100):
        cventry_list = []
        section = search_text.find(section_header)
        if (section == -1):
            break
        section_start = section + len(section_header)
        search_text = search_text[section_start:]

        for __ in range(4):
            start = search_text.find('{') + 1
            end = search_text.find('}')
            cventry_list.append(search_text[start:end])
            search_text = search_text[(end + 1):]

        subsection_start = search_text.find(subsection_header) + len(subsection_header)
        subsection_end = search_text.find(subsection_footer) + len(subsection_footer)
        subsection_text = search_text[subsection_start:subsection_end]

        for __ in range(100):
            item = subsection_text.find('\\item')
            if (item == -1):
                break
            else:
                start = subsection_text.find('{') + 1
                end = subsection_text.find('}')
                item_text = '- ' + subsection_text[start:end]
                cventry_list.append(item_text)
                subsection_text = subsection_text[(end + 1):]

        cventry = '\n'.join(cventry_list)
        cv_list.append(cventry)
        search_text = search_text[(subsection_end + 1):]

    cv = '\n\n'.join(cv_list)

    for string_to_replace, replacement in replacements.items():
        cv = re.sub(string_to_replace, replacement, cv)
    return cv

cv = parse_cventries(filepath, replacements)
print(cv)
