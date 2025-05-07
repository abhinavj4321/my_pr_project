from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChatbotFAQ, ChatbotFeedback
import json
import re
import requests
import random

# Pre-defined responses for common IIITDMJ queries
IIITDMJ_INFO = {
    "about": "IIITDMJ (Indian Institute of Information Technology, Design and Manufacturing, Jabalpur) is an Institute of National Importance established by the Government of India in 2005. It focuses on education and research in IT, design, and manufacturing.",
    "location": "IIITDMJ is located in Jabalpur, Madhya Pradesh, India. The campus is situated at Dumna Airport Road, Jabalpur, Madhya Pradesh 482005.",
    "courses": "IIITDMJ offers B.Tech, M.Tech, and Ph.D. programs in Computer Science and Engineering, Electronics and Communication Engineering, Mechanical Engineering, and Design.",
    "facilities": "IIITDMJ campus offers various facilities including academic buildings, hostels, sports facilities, library, computer labs, cafeteria, medical center, and recreational areas.",
    "attendance": "The Student Attendance System uses QR codes for marking attendance. Students need to scan the QR code displayed by the faculty during class. A minimum of 75% attendance is required in each course.",
    "specific_course": "To view your attendance or marks for a specific course like DAA (Data Structures and Algorithms), please navigate to the 'View Attendance' section after logging in. Select the subject from the dropdown menu to see your attendance percentage and details.",
    "marks": "To view your marks or grades, please log in to the student portal and navigate to the 'Academic Performance' or 'Results' section. You can view your marks for individual subjects, assignments, and examinations there.",
    "default": "I'm an AI assistant for IIITDMJ. I can provide information about the campus, courses, facilities, and the attendance system. Please ask me specific questions about these topics."
}

# AI model context information about IIITDMJ
IIITDMJ_CONTEXT = """
IIITDMJ (Indian Institute of Information Technology, Design and Manufacturing, Jabalpur) is an Institute of National Importance established by the Government of India in 2005. It focuses on education and research in IT, design, and manufacturing.

Location: IIITDMJ is located in Jabalpur, Madhya Pradesh, India. The campus is situated at Dumna Airport Road, Jabalpur, Madhya Pradesh 482005.

Courses: IIITDMJ offers B.Tech, M.Tech, and Ph.D. programs in Computer Science and Engineering, Electronics and Communication Engineering, Mechanical Engineering, and Design.

Facilities: IIITDMJ campus offers various facilities including academic buildings, hostels, sports facilities, library, computer labs, cafeteria, medical center, and recreational areas.

Attendance System: The Student Attendance System uses QR codes for marking attendance. Students need to scan the QR code displayed by the faculty during class. A minimum of 75% attendance is required in each course.

Popular Courses:
- DAA (Data Structures and Algorithms): A core computer science course covering fundamental data structures and algorithm design techniques.
- DBMS (Database Management Systems): Covers database design, SQL, and database administration.
- OS (Operating Systems): Focuses on operating system principles, process management, and memory management.
- CN (Computer Networks): Covers network protocols, architecture, and security.
- AI (Artificial Intelligence): Introduces AI concepts, machine learning, and neural networks.
- ML (Machine Learning): Focuses on supervised and unsupervised learning algorithms.

Student Portal: Students can view their attendance, marks, and academic performance by logging into the student portal. For specific course information, navigate to the 'View Attendance' or 'Academic Performance' sections.
"""

# Function to get response from AI model
def get_ai_response(query, context=None):
    try:
        print(f"Processing query: {query}")
        query_lower = query.lower().strip()
        
        # Use context to provide more personalized responses
        if context and 'history' in context and len(context['history']) > 0:
            # Check if this is a follow-up question
            last_interaction = context['history'][-1]
            last_query = last_interaction['query'].lower()
            last_response = last_interaction['response']
            
            # Check for follow-up patterns
            follow_up_indicators = ['what about', 'how about', 'and', 'what else', 'tell me more']
            is_follow_up = any(indicator in query_lower for indicator in follow_up_indicators)
            
            if is_follow_up:
                # If it's about courses and the last query was also about courses
                if 'course' in last_query and any(course in last_query for course in ['daa', 'dbms', 'os', 'cn', 'ai', 'ml']):
                    # Extract the course from the last query
                    for course in ['daa', 'dbms', 'os', 'cn', 'ai', 'ml']:
                        if course in last_query:
                            # If the follow-up is about attendance or marks
                            if 'attendance' in query_lower:
                                return f"For {course.upper()} attendance, you can check the 'View Attendance' section in your student dashboard. The minimum required attendance is 75%."  
                            elif any(term in query_lower for term in ['mark', 'grade', 'score']):
                                return f"You can view your {course.upper()} marks in the 'Academic Performance' section of your student dashboard. The course includes continuous assessment through assignments, quizzes, and exams."
                            elif 'syllabus' in query_lower:
                                # Return course-specific syllabus information
                                course_info = {
                                    "daa": "DAA (Data Structures and Algorithms) is a core computer science course that covers fundamental data structures like arrays, linked lists, trees, graphs, and algorithm design techniques including divide and conquer, greedy algorithms, and dynamic programming. The course is typically offered in the 3rd semester.",
                                    "dbms": "DBMS (Database Management Systems) covers relational database design, SQL, normalization, transaction processing, and database administration. This course is usually offered in the 4th semester and includes practical sessions on SQL and database design.",
                                    "os": "Operating Systems (OS) is a course that focuses on process management, memory management, file systems, and security in modern operating systems. It's typically offered in the 5th semester and includes practical components on system programming.",
                                    "cn": "Computer Networks (CN) covers network protocols, architecture, routing algorithms, and network security. The course is usually offered in the 6th semester and includes lab sessions on network configuration and protocol analysis.",
                                    "ai": "Artificial Intelligence (AI) introduces concepts like search algorithms, knowledge representation, reasoning, and machine learning. This course is typically offered as an elective in the 7th semester.",
                                    "ml": "Machine Learning (ML) focuses on supervised and unsupervised learning algorithms, neural networks, and deep learning. It's usually offered as an elective in the 7th or 8th semester and includes practical implementation of ML algorithms."
                                }
                                return f"The syllabus for {course.upper()} includes: {course_info.get(course, 'detailed information about algorithms and data structures')}. You can find the complete syllabus on the student portal."
        
        # If not a follow-up or no context, proceed with regular response generation
        query_tokens = preprocess_text(query_lower)
        
        # Create a more sophisticated response system
        response_categories = {
            'greeting': ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening'],
            'farewell': ['bye', 'goodbye', 'see you', 'talk to you later', 'thanks'],
            'help': ['help', 'assist', 'support', 'guide', 'how to'],
            'about': ['about', 'what is', 'tell me about', 'information', 'details'],
            'location': ['where', 'location', 'address', 'place', 'situated', 'located'],
            'courses': ['course', 'program', 'degree', 'btech', 'mtech', 'phd', 'study'],
            'facilities': ['facility', 'amenity', 'hostel', 'library', 'lab', 'sports', 'canteen'],
            'attendance': ['attendance', 'present', 'absent', 'mark', 'scan', 'qr'],
            'marks': ['mark', 'grade', 'result', 'score', 'performance', 'cgpa', 'sgpa'],
        }
        
        # Determine the category of the query
        category_scores = {}
        for category, keywords in response_categories.items():
            category_tokens = []
            for keyword in keywords:
                category_tokens.extend(preprocess_text(keyword))
            similarity = calculate_similarity(query_tokens, category_tokens)
            category_scores[category] = similarity
        
        # Get the highest scoring category
        best_category = max(category_scores.items(), key=lambda x: x[1])
        category_name, score = best_category
        
        # If the score is too low, use a more general approach
        if score < 0.2:
            # Check for course-specific queries first
            course_info = {
                "daa": "DAA (Data Structures and Algorithms) is a core computer science course that covers fundamental data structures like arrays, linked lists, trees, graphs, and algorithm design techniques including divide and conquer, greedy algorithms, and dynamic programming. The course is typically offered in the 3rd semester.",
                "dbms": "DBMS (Database Management Systems) covers relational database design, SQL, normalization, transaction processing, and database administration. This course is usually offered in the 4th semester and includes practical sessions on SQL and database design.",
                "os": "Operating Systems (OS) is a course that focuses on process management, memory management, file systems, and security in modern operating systems. It's typically offered in the 5th semester and includes practical components on system programming.",
                "cn": "Computer Networks (CN) covers network protocols, architecture, routing algorithms, and network security. The course is usually offered in the 6th semester and includes lab sessions on network configuration and protocol analysis.",
                "ai": "Artificial Intelligence (AI) introduces concepts like search algorithms, knowledge representation, reasoning, and machine learning. This course is typically offered as an elective in the 7th semester.",
                "ml": "Machine Learning (ML) focuses on supervised and unsupervised learning algorithms, neural networks, and deep learning. It's usually offered as an elective in the 7th or 8th semester and includes practical implementation of ML algorithms."
            }
        
        # Check for course-specific queries
        for course_code, info in course_info.items():
            if course_code in query_lower:
                if "mark" in query_lower or "grade" in query_lower or "result" in query_lower or "score" in query_lower:
                    return f"To view your marks for {course_code.upper()}, please log in to the student portal and navigate to the 'Academic Performance' section. There you can see your scores for assignments, tests, and exams for this course. The grading system is typically based on a 10-point scale with continuous evaluation throughout the semester."
        
                elif "attendance" in query_lower or "present" in query_lower or "absent" in query_lower:
                    return f"To check your attendance for {course_code.upper()}, log in to the student portal and go to the 'View Attendance' section. Select {course_code.upper()} from the dropdown menu to see your attendance percentage and details of present/absent days. Remember that a minimum of 75% attendance is required to be eligible for the final examination."
        
                elif "syllabus" in query_lower or "content" in query_lower or "topic" in query_lower:
                    return f"The syllabus for {course_code.upper()} includes: {info} You can find the detailed syllabus in the course handbook available on the student portal."
        
                else:
                    return f"Information about {course_code.upper()}: {info} For more details about this course, including your attendance and performance, please check the student portal."
        
        # General queries about marks or attendance
        if "mark" in query_lower or "grade" in query_lower or "result" in query_lower or "score" in query_lower:
            return "To view your marks or grades for any course, please log in to the student portal and navigate to the 'Academic Performance' section. There you can select specific courses to view your scores for assignments, tests, and exams. The grading system is based on a 10-point scale with continuous evaluation throughout the semester."
        
        elif "attendance" in query_lower or "present" in query_lower or "absent" in query_lower:
            return "To check your attendance for any course, log in to the student portal and go to the 'View Attendance' section. You can select specific courses from the dropdown menu to see your attendance percentage and details of present/absent days. A minimum of 75% attendance is required for each course to be eligible for the final examination."
        
        # Generate responses for other types of queries using the context
        elif "location" in query_lower or "where" in query_lower or "address" in query_lower:
            return "IIITDMJ is located in Jabalpur, Madhya Pradesh, India. The campus is situated at Dumna Airport Road, Jabalpur, Madhya Pradesh 482005. The campus is approximately 10 km from Jabalpur railway station and 30 km from Jabalpur airport."
        
        elif "course" in query_lower or "program" in query_lower or "degree" in query_lower:
            return "IIITDMJ offers B.Tech programs in Computer Science and Engineering, Electronics and Communication Engineering, Mechanical Engineering, and Design. The institute also offers M.Tech and Ph.D. programs in these disciplines. The B.Tech program is a 4-year undergraduate program with a focus on both theoretical knowledge and practical skills."
        
        elif "facility" in query_lower or "amenity" in query_lower or "hostel" in query_lower:
            return "IIITDMJ campus offers various facilities including academic buildings, separate hostels for boys and girls, sports facilities (indoor and outdoor), a central library with digital resources, computer labs with high-speed internet, cafeteria and mess facilities, a medical center for healthcare, and recreational areas for student activities."
        
        elif "about" in query_lower or "iiitdmj" in query_lower:
            return "IIITDMJ (Indian Institute of Information Technology, Design and Manufacturing, Jabalpur) is an Institute of National Importance established by the Government of India in 2005. It focuses on education and research in IT, design, and manufacturing. The institute follows a credit-based system with continuous evaluation and offers various undergraduate, postgraduate, and doctoral programs."
        
        else:
            # Generate a more personalized default response
            responses = [
                "I'm an AI assistant for IIITDMJ. I can provide information about specific courses like DAA, DBMS, OS, CN, AI, ML, as well as general information about the campus, facilities, and the attendance system. How can I help you today?",
                "As an AI assistant for IIITDMJ, I can answer questions about courses, attendance, marks, campus facilities, and more. Feel free to ask about specific courses or any aspect of student life at IIITDMJ.",
                "I'm here to help with information about IIITDMJ. You can ask me about specific courses (like DAA, DBMS, OS), your attendance, marks, or general information about the campus and facilities."
            ]
            return random.choice(responses)

    except Exception as e:
        print(f"Error in AI response: {str(e)}")
        return "I'm sorry, I'm having trouble processing your request right now. Please try asking about IIITDMJ campus or the attendance system."

# Add these imports at the top
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string

# Download necessary NLTK resources (run once)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

def preprocess_text(text):
    """Preprocess text for better matching"""
    # Convert to lowercase and remove punctuation
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenize and remove stopwords
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # Lemmatize tokens
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    return tokens

def calculate_similarity(query_tokens, text_tokens):
    """Calculate similarity between two token sets"""
    # Simple Jaccard similarity
    query_set = set(query_tokens)
    text_set = set(text_tokens)
    
    if not query_set or not text_set:
        return 0.0
    
    intersection = query_set.intersection(text_set)
    union = query_set.union(text_set)
    
    return len(intersection) / len(union)

def improved_process_query(query):
    """Improved query processing with NLP techniques"""
    # Preprocess the query
    query_tokens = preprocess_text(query)
    
    # Get all FAQs
    faqs = ChatbotFAQ.objects.all()
    
    best_match = None
    highest_score = 0.3  # Threshold for minimum similarity
    
    for faq in faqs:
        # Preprocess question and keywords
        question_tokens = preprocess_text(faq.question)
        keyword_tokens = []
        for keyword in faq.keywords.split(','):
            keyword_tokens.extend(preprocess_text(keyword.strip()))
        
        # Calculate similarity scores
        question_similarity = calculate_similarity(query_tokens, question_tokens)
        keyword_similarity = calculate_similarity(query_tokens, keyword_tokens)
        
        # Combined score (weighted)
        score = 0.7 * question_similarity + 0.3 * keyword_similarity
        
        # Update best match if this score is higher
        if score > highest_score:
            highest_score = score
            best_match = faq
    
    return best_match

@csrf_exempt
def chatbot_query(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '')
            session_id = data.get('session_id', None)  # Get session ID from request
            
            if not query:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No query provided'
                })
            
            # Get or create session context
            session_context = {}
            if session_id and session_id in request.session:
                session_context = request.session[session_id]
            else:
                # Generate a new session ID if none provided
                if not session_id:
                    session_id = str(uuid.uuid4())
                session_context = {'history': []}
            
            print(f"Received query: {query} (Session: {session_id})")
            
            # Process the query with context
            faq = improved_process_query(query)
            
            response_data = {}
            
            if faq:
                print(f"Found FAQ match: {faq.question}")
                answer = faq.answer
                response_data = {
                    'status': 'success',
                    'answer': answer,
                    'faq_id': faq.id,
                    'session_id': session_id
                }
            else:
                print("No FAQ match found, using AI response")
                # Use AI model as fallback, passing the session context
                ai_response = get_ai_response(query, context=session_context)
                print(f"AI response: {ai_response}")
                response_data = {
                    'status': 'ai_response',
                    'answer': ai_response,
                    'session_id': session_id
                }
            
            # Update session context with this interaction
            session_context['history'].append({
                'query': query,
                'response': response_data['answer'],
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only the last 5 interactions to avoid session bloat
            if len(session_context['history']) > 5:
                session_context['history'] = session_context['history'][-5:]
            
            # Save updated context to session
            request.session[session_id] = session_context
            
            return JsonResponse(response_data)
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST requests are allowed'
    })

@csrf_exempt
def chatbot_feedback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            faq_id = data.get('faq_id')
            question = data.get('question', '')
            helpful = data.get('helpful', False)
            user_email = data.get('user_email', None)

            # Create feedback entry
            feedback = ChatbotFeedback()

            if faq_id:
                try:
                    faq = ChatbotFAQ.objects.get(id=faq_id)
                    feedback.faq = faq
                except ChatbotFAQ.DoesNotExist:
                    pass

            feedback.question = question
            feedback.helpful = helpful
            feedback.user_email = user_email
            feedback.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Feedback recorded successfully'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Only POST requests are allowed'
    })
