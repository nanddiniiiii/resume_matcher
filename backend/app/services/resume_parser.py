import pdfplumber
from typing import Dict, List
import re


class ResumeParser:
    """Service to extract and parse resume content from PDF files."""
    
    def __init__(self):
        # Common skill keywords (can be expanded)
        self.skill_keywords = {
            'python', 'java', 'javascript', 'typescript', 'react', 'node.js', 'nodejs',
            'fastapi', 'django', 'flask', 'spring', 'sql', 'postgresql', 'mongodb',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'machine learning', 'ml',
            'deep learning', 'nlp', 'computer vision', 'data analysis', 'pandas',
            'numpy', 'tensorflow', 'pytorch', 'scikit-learn', 'git', 'html', 'css',
            'tailwind', 'bootstrap', 'rest api', 'graphql', 'microservices',
            'agile', 'scrum', 'ci/cd', 'jenkins', 'github actions', 'c++', 'c#',
            'go', 'rust', 'php', 'ruby', 'swift', 'kotlin', 'flutter', 'dart',
            'angular', 'vue.js', 'vuejs', 'next.js', 'nextjs', 'express',
            'redis', 'elasticsearch', 'kafka', 'rabbitmq', 'linux', 'bash'
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract raw text from PDF file."""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text using keyword matching."""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skill_keywords:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates
    
    def extract_education(self, text: str) -> List[Dict]:
        """Extract education information from resume text."""
        education = []
        
        # Look for degree patterns
        degree_patterns = [
            r'(B\.?Tech|Bachelor|B\.?E\.?|B\.?Sc\.?|M\.?Tech|Master|M\.?E\.?|M\.?Sc\.?|PhD|Ph\.?D\.?)',
            r'(Computer Science|Information Technology|Electronics|Mechanical|Civil|Software Engineering)',
        ]
        
        # Simple extraction - can be enhanced with spaCy
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(word in line_lower for word in ['university', 'college', 'institute', 'school']):
                # Check surrounding lines for degree
                context = ' '.join(lines[max(0, i-2):min(len(lines), i+3)])
                for pattern in degree_patterns:
                    if re.search(pattern, context, re.IGNORECASE):
                        education.append({
                            "institution": line.strip(),
                            "context": context[:200]  # First 200 chars
                        })
                        break
        
        return education[:3]  # Return top 3 matches
    
    def extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience from resume text."""
        experience = []
        
        # Look for experience indicators
        exp_keywords = ['intern', 'developer', 'engineer', 'analyst', 'manager', 
                       'consultant', 'designer', 'programmer', 'specialist']
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            # Check if line contains experience keywords
            if any(keyword in line_lower for keyword in exp_keywords):
                # Look for dates (simple pattern)
                date_pattern = r'\b(20\d{2}|19\d{2})\b'
                context = ' '.join(lines[i:min(len(lines), i+3)])
                if re.search(date_pattern, context):
                    experience.append({
                        "role": line.strip()[:100],
                        "context": context[:200]
                    })
        
        return experience[:5]  # Return top 5 matches
    
    def parse_resume(self, pdf_path: str) -> Dict:
        """
        Parse resume and extract all information.
        
        Returns:
            Dict with raw_text, skills, education, experience
        """
        # Extract raw text
        raw_text = self.extract_text_from_pdf(pdf_path)
        
        # Parse components
        skills = self.extract_skills(raw_text)
        education = self.extract_education(raw_text)
        experience = self.extract_experience(raw_text)
        
        return {
            "raw_text": raw_text,
            "skills": skills,
            "education": education,
            "experience": experience
        }
