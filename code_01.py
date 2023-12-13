import fitz  # PyMuPDF
import re

months_dict = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
    'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
}

pdf_path = "C:\\Users\\LENOVO\\Downloads\\resume (2).pdf"

def extract_information_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    linkedin_profile = None
    experience = []
    education = []

    edu_start_pattern = re.compile(r'Education', re.IGNORECASE)
    exp_start_pattern = re.compile(r'Experience', re.IGNORECASE)

    
    all_text = ''
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        all_text += page.get_text()  

    capturing_edu = False
    capturing_exp = False
    for line in all_text.split('\n'):
        
        if re.search(r'Page \d+ of \d+', line):
            continue  
        if not line.strip():
            continue

        linkedin_pattern = re.compile(r'(www.linkedin.com/in/[a-zA-Z0-9-\n]+)', re.MULTILINE)
        match = linkedin_pattern.search(all_text)
        if match:
            linkedin_profile = match.group(0).replace('\n', '')
            
        if edu_start_pattern.search(line):
            capturing_edu = True
            education_content = ""
            continue

        if capturing_edu:
            if not line.strip():
                continue

            education_content += line.strip() + " "

            if line.strip().endswith(")"):
                capturing_edu = False
                education.append(re.sub('\s+', ' ', education_content).strip())

        if exp_start_pattern.search(line):
            capturing_exp = True
            experience_content = ""
            continue

        if capturing_exp:
            if not line.strip():
                continue

            experience_content += line.strip() + " "

            if line.strip().endswith(")"):
                capturing_exp = False
                experience.append(re.sub('\s+', ' ', experience_content).strip())

    pdf_document.close()
    output = {
        "Experience": experience,
        "Education": education,
        "linkedin_profile": linkedin_profile
    }
    return output

result = extract_information_from_pdf(pdf_path)

if 'Experience' in result:
    parsed_experience = []
    for exp_string in result['Experience']:
        match = re.search(r'(?P<organization>The[\w\s]+) (?P<designation>COO[\w\s&]+) (?P<dates>(?:\w+\s+\d+ - \w+ \(\d+ months\)|Present))', exp_string)
        if match:
            organization = match.group('organization').strip()
            designation = match.group('designation').strip()
            dates = match.group('dates').strip()

            date_matches = re.findall(r'\b(\w+)\s+(\d+)\b', dates)

            if date_matches:
                start_date = [months_dict[date_matches[0][0]], int(date_matches[0][1])]
                end_date = [months_dict[date_matches[1][0]], int(date_matches[1][1])] if len(date_matches) > 1 else [None, None]

                parsed_experience.append({
                    "organization": organization,
                    "designation": designation,
                    "from": start_date,
                    "to": end_date
                })

    result['Experience'] = parsed_experience
    
if 'Education' in result:
    parsed_education = []
    for edu_string in result['Education']:
        
        match = re.search(r'(?P<school>[\w\s]+) (?P<degree>Master[\w\s,]+) ', edu_string)
        match2= re.search(r' \((?P<from>\d+) - (?P<to>\d+)\)', edu_string)
        if match:
            if match2:
                school = match.group('school').strip()
                degree = match.group('degree').strip()
                from1 = match2.group('from').strip()
                to1 = match2.group('to').strip()
                parsed_education.append({
                    "school": school,
                    "degree": degree,
                    "from": from1,
                    "to": to1
                })
        result['Education'] = parsed_education

for key, value in result.items():
    print(f"{key}:")
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                for sub_key, sub_value in item.items():
                    print(f"  {sub_key}: {sub_value}")
    else:
        print(f"  {value}")
    print()
