import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

# Now we can import Django models
from chatbot.models import ChatbotCategory, ChatbotFAQ

def create_initial_categories():
    # Create categories
    campus_info, created = ChatbotCategory.objects.get_or_create(
        name="Campus Information",
        defaults={"description": "Information about IIITDMJ campus, facilities, and locations"}
    )
    
    academic_info, created = ChatbotCategory.objects.get_or_create(
        name="Academic Information",
        defaults={"description": "Information about courses, programs, and academic policies"}
    )
    
    website_info, created = ChatbotCategory.objects.get_or_create(
        name="Website Help",
        defaults={"description": "Help with navigating and using the student attendance system"}
    )
    
    general_info, created = ChatbotCategory.objects.get_or_create(
        name="General Information",
        defaults={"description": "General information about IIITDMJ"}
    )
    
    return {
        'campus_info': campus_info,
        'academic_info': academic_info,
        'website_info': website_info,
        'general_info': general_info
    }

def create_initial_faqs(categories):
    # Create FAQs
    faqs = [
        # Campus Information
        {
            'question': "Where is IIITDMJ located?",
            'answer': "IIITDMJ (Indian Institute of Information Technology, Design and Manufacturing, Jabalpur) is located in Jabalpur, Madhya Pradesh, India. The campus is situated at Dumna Airport Road, Jabalpur, Madhya Pradesh 482005.",
            'category': categories['campus_info'],
            'keywords': "location, address, where, campus, situated, place, find, reach, jabalpur"
        },
        {
            'question': "What facilities are available on campus?",
            'answer': "IIITDMJ campus offers various facilities including academic buildings, hostels, sports facilities (indoor and outdoor), library, computer labs, cafeteria, medical center, and recreational areas.",
            'category': categories['campus_info'],
            'keywords': "facilities, amenities, available, campus, hostel, sports, library, lab, cafeteria, medical"
        },
        {
            'question': "How many hostels are there in IIITDMJ?",
            'answer': "IIITDMJ has separate hostels for boys and girls. There are multiple hostel blocks to accommodate students from different years and programs.",
            'category': categories['campus_info'],
            'keywords': "hostel, accommodation, stay, living, residence, dormitory"
        },
        
        # Academic Information
        {
            'question': "What courses are offered at IIITDMJ?",
            'answer': "IIITDMJ offers B.Tech, M.Tech, and Ph.D. programs in Computer Science and Engineering, Electronics and Communication Engineering, Mechanical Engineering, and Design. The institute also offers dual degree programs.",
            'category': categories['academic_info'],
            'keywords': "courses, programs, degrees, btech, mtech, phd, offered, study, academic"
        },
        {
            'question': "What is the attendance policy?",
            'answer': "Students are required to maintain a minimum of 75% attendance in each course. Attendance is recorded through the QR code attendance system. Students with attendance below the required minimum may not be allowed to appear for the end-semester examination.",
            'category': categories['academic_info'],
            'keywords': "attendance, policy, required, minimum, percentage, class, present, absent"
        },
        {
            'question': "How is attendance marked in the system?",
            'answer': "Attendance is marked using QR codes. Students need to scan the QR code displayed by the faculty during class using the attendance system. The system records the attendance automatically.",
            'category': categories['academic_info'],
            'keywords': "attendance, mark, record, scan, qr, code, system, how"
        },
        
        # Website Help
        {
            'question': "How do I log in to the attendance system?",
            'answer': "You can log in to the attendance system using your registered email and password. If you're a new user, your default credentials would have been provided by the administrator. For students, the default email format is usually your roll number followed by @iiitdmj.ac.in.",
            'category': categories['website_info'],
            'keywords': "login, sign in, access, credentials, password, email, account, system"
        },
        {
            'question': "I forgot my password. How can I reset it?",
            'answer': "If you've forgotten your password, please contact your administrator or the IT department to reset your password. Currently, the system doesn't have an automated password reset feature.",
            'category': categories['website_info'],
            'keywords': "forgot, password, reset, recover, change, unable, login, access"
        },
        {
            'question': "How can I view my attendance record?",
            'answer': "After logging in as a student, you can view your attendance record by navigating to the 'View Attendance' section. Here, you can select the subject and see your attendance percentage and details of present/absent days.",
            'category': categories['website_info'],
            'keywords': "view, check, see, attendance, record, history, percentage, report"
        },
        
        # General Information
        {
            'question': "What is IIITDMJ?",
            'answer': "IIITDMJ (Indian Institute of Information Technology, Design and Manufacturing, Jabalpur) is an Institute of National Importance established by the Government of India. It focuses on education and research in IT, design, and manufacturing.",
            'category': categories['general_info'],
            'keywords': "what, iiitdmj, about, institute, college, university"
        },
        {
            'question': "When was IIITDMJ established?",
            'answer': "IIITDMJ was established in 2005 by the Government of India. It was declared an Institute of National Importance in 2014.",
            'category': categories['general_info'],
            'keywords': "when, established, founded, started, history, year, date"
        },
        {
            'question': "Who is the current director of IIITDMJ?",
            'answer': "For the most current information about the Director of IIITDMJ, please visit the official IIITDMJ website as this information may change over time.",
            'category': categories['general_info'],
            'keywords': "director, head, who, current, present, lead"
        }
    ]
    
    # Create FAQ objects
    for faq_data in faqs:
        # Check if FAQ already exists
        existing_faqs = ChatbotFAQ.objects.filter(question=faq_data['question'])
        if not existing_faqs.exists():
            ChatbotFAQ.objects.create(
                question=faq_data['question'],
                answer=faq_data['answer'],
                category=faq_data['category'],
                keywords=faq_data['keywords']
            )
            print(f"Created FAQ: {faq_data['question']}")
        else:
            print(f"FAQ already exists: {faq_data['question']}")

if __name__ == "__main__":
    print("Populating chatbot data...")
    categories = create_initial_categories()
    create_initial_faqs(categories)
    print("Chatbot data population complete.")
