from datetime import datetime
import os
import re


class User:
    def __init__ (self, first_name, last_name, password, mobile,email):
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.mobile = mobile
        self.email = email
        # self.is_active = False



class Project:
    def __init__ (self, title, details, target, start_date, end_date, email_creator):
        self.title = title
        self.details = details
        self.target = target
        self.start_date = start_date
        self.end_date = end_date
        self.email_creator = email_creator



# ===========================================================
# Function to register a user
# ===========================================================
def register_user():
    first_name = input("Enter your first name: ")
    last_name = input("Enter your last name: ")
    password = input("Enter your password: ")
    mobile = input("Enter your mobile number: ")
    email = input("Enter your email address: ")

    # Validate
    validate_email(email)
    validate_mobile(mobile)
    validate_password(password)
    # create file if not exist
    if not os.path.exists("users.txt"):
        with open("users.txt", "w") as file:
            file.write("")
    # Check if user already exists
    with open("users.txt", "r") as file:
        for line in file:
            if email in line:
                print("User already exists")
                return None


    user = User(first_name, last_name, password, mobile, email)

    save_user_data_into_file(user)
    print(f"User {user.first_name} {user.last_name} registered successfully!")
    
    return user

# ===========================================================
# Function to create a project 
# ===========================================================
def create_project(logged_email):
    title = input("Enter project title: ")
    details = input("Enter project details: ")
    target = input("Enter funding target: ")
    start_date = input("Enter project start date (YYYY-MM-DD): ")
    end_date = input("Enter project end date (YYYY-MM-DD): ")
    email_creator = logged_email
    # Validate
    validate_date(start_date, end_date)
    

    project = Project(title, details, target, start_date, end_date, email_creator)
    save_project_data_into_file(project)
    print(f"Project '{project.title}' created successfully!")
    return project

# =========================================
# Function to view projects
# =========================================
# Logic:
#     if logged_email is passed show only the users projects
#     if there is no email show all projects
def view_projects(logged_email=None):
    try: 
        with open("projects.txt", "r") as file:
            projects = file.readlines()
            if not projects:
                print("No projects found")
                return
            for project in projects:
                title, details, target, start_date, end_date, email_creator = project.strip().split(",")
                if logged_email and email_creator != logged_email:
                    continue
                print(f"\n{'-'*30}")
                print(f"Title: {title}")
                print(f"Details: {details}")
                print(f"Target: {target} EGP")
                print(f"Start Date: {start_date}")
                print(f"End Date: {end_date}")
                print(f"Email Creator: {logged_email}")
                print(f"{'-'*30}")
    except FileNotFoundError:
        print("No projects found")
        return
# ================================================
# Edit project
# ================================================
def edit_project(logged_email):
    """
    Allows a user to edit their own project
    """
    print("=== Edit Project ===")
    title_to_edit = input("Enter the title of the project you want to edit: ")
    
    try:
        with open("projects.txt", "r") as file:
            projects = file.readlines()
        
        found = False
        updated_projects = []
        
        for line in projects:
            parts = line.strip().split(",")
            if len(parts) != 6:
                updated_projects.append(line)
                continue
                
            title, details, target, start_date, end_date, creator_email = parts
            
            if title == title_to_edit and creator_email == logged_email:
                found = True
                print("\nCurrent Project Details:")
                print(f"Title: {title}")
                print(f"Details: {details}")
                print(f"Target: {target} EGP")
                print(f"Start Date: {start_date}")
                print(f"End Date: {end_date}")
                
                # Get new values or keep old ones
                new_title = input(f"New title (press Enter to keep '{title}'): ") or title
                new_details = input(f"New details (press Enter to keep '{details}'): ") or details
                new_target = input(f"New target (press Enter to keep '{target}'): ") or target
                
                valid_date = False
                new_start = start_date
                new_end = end_date
                
                while not valid_date:
                    new_start = input(f"New start date (YYYY-MM-DD) (press Enter to keep '{start_date}'): ") or start_date
                    new_end = input(f"New end date (YYYY-MM-DD) (press Enter to keep '{end_date}'): ") or end_date
                    
                    if validate_date(new_start, new_end):
                        valid_date = True
                    else:
                        print("Please enter valid dates with start before end date")
                
                # Create updated project line
                updated_project = f"{new_title},{new_details},{new_target},{new_start},{new_end},{creator_email}\n"
                updated_projects.append(updated_project)
                print("Project updated successfully!")
            
            else:
                updated_projects.append(line)
        
        if not found:
            print("No matching project found. Make sure you own the project and entered the title correctly.")
            return
        
        # Write updated projects back to file
        with open("projects.txt", "w") as file:
            file.writelines(updated_projects)
            
    except FileNotFoundError:
        print("No projects file found. No projects have been created yet.")
# ================================================
# Delete project
# ================================================
def delete_project(logged_email):
 
    print("=== Delete Project ===")
    title_to_delete = input("Enter the title of the project to delete: ")
    
    try:
        with open("projects.txt", "r") as file:
            projects = file.readlines()
        
        found = False
        updated_projects = []
        
        for line in projects:
            parts = line.strip().split(",")
            if len(parts) != 6:
                updated_projects.append(line)
                continue
                
            title, details, target, start_date, end_date, creator_email = parts
            
            if title == title_to_delete and creator_email == logged_email:
                found = True
                confirm = input(f"Are you sure you want to delete '{title}'? (yes/no): ")
                if confirm.lower() == 'yes':
                    print(f"Project '{title}' has been deleted.")
                    continue  # Skip adding this project to the updated list
            
            updated_projects.append(line)
        
        if not found:
            print("No matching project found. Make sure you own the project and entered the title correctly.")
            return
        
        # Write updated projects back to file
        with open("projects.txt", "w") as file:
            file.writelines(updated_projects)
            
    except FileNotFoundError:
        print("No projects file found. No projects have been created yet.")
# ================================================
# Search projects by date
# ================================================
def search_projects_by_date():
    """
    Search projects that overlap with a specific date range
    """
    print("=== Search Projects by Date ===")
    start_range = input("Enter start of date range (YYYY-MM-DD): ")
    end_range = input("Enter end of date range (YYYY-MM-DD): ")
    
    if not validate_date(start_range, end_range):
        print("Invalid date range. Please try again.")
        return
    
    try:
        with open("projects.txt", "r") as file:
            projects = file.readlines()
        
        print("\n=== Projects Matching Date Range ===")
        found = False
        
        range_start = datetime.strptime(start_range, "%Y-%m-%d")
        range_end = datetime.strptime(end_range, "%Y-%m-%d")
        
        for line in projects:
            parts = line.strip().split(",")
            if len(parts) != 6:
                continue
                
            title, details, target, start_date, end_date, creator_email = parts
            
            try:
                project_start = datetime.strptime(start_date, "%Y-%m-%d")
                project_end = datetime.strptime(end_date, "%Y-%m-%d")
                
                
                if (project_start <= range_end) and (project_end >= range_start):
                    print(f"\n{'-'*30}")
                    print(f"Title: {title}")
                    print(f"Details: {details}")
                    print(f"Target: {target} EGP")
                    print(f"Start Date: {start_date}")
                    print(f"End Date: {end_date}")
                    print(f"Creator: {creator_email}")
                    print(f"{'-'*30}")
                    found = True
            except ValueError:
                continue
        
        if not found:
            print("No projects found in the specified date range.")
            
    except FileNotFoundError:
        print("No projects file found. No projects have been created yet.")
# ======================================
# login_user():
# ===============================
def login_user():
    email = input("Enter your email address: ")
    password = input("Enter your password: ")

    with open("users.txt", "r") as file:
        for line in file:
            if email in line and password in line:
                print("Login successful!")
                return email
    print("Invalid email or password")
    return False
# Validation 
# ===============================
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(pattern, email):
        return True
    else:
        print("Invalid email address")
        return False
def validate_mobile(mobile):
    if re.match(r'^01[0-2|5]\d{8}$', mobile):
        return True
    else:
        print("Invalid mobile number")
        return False
def validate_password(password):
    if len(password) >= 8 and any(char.isdigit() for char in password) and any(char.isalpha() for char in password):
        return True
    else:
        print("Password must be at least 8 characters long and contain both letters and numbers")
        return False
def validate_date(start_date, end_date):
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        if start < end:
            return True
        else:
            print("Start date must be before end date")
            return False
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return False
    
# =============================
# saving data to a file
# =============================
def save_user_data_into_file(user):
    with open ("users.txt", "a") as file:
        file.write(f"{user.first_name},{user.last_name},{user.password},{user.mobile},{user.email}\n")

def save_project_data_into_file(project):
    if not os.path.exists("projects.txt"):
         open("projects.txt", "w").close()
    with open ("projects.txt", "a") as file:
        file.write(f"{project.title},{project.details},{project.target},{project.start_date},{project.end_date},{project.email_creator}\n")
# =================================================
# Function to view project Menu
# =================================================
def project_menu(logged_email):
    while True:
        print("==== Welcome to the project page\n"
        "1. Create a project\n"
        "2. View projects\n"
        "3. Edit Project\n"
        "4. Delete Project\n"
        "5. Search projects by Date\n"
        "6. Logout")


        choice = input ("==== Please enter your choice: ")
        if (choice) == "1":
            create_project(logged_email)
        elif (choice) == "2":
            print ("View projects page")
            view_projects(logged_email);
        elif (choice) == "3":
            print ("Edit project page")
            edit_project(logged_email)
        elif (choice) == "4":
            print ("Delete project page")
            delete_project(logged_email)
        elif (choice) == "5":
            print ("Search projects by date page")
            search_projects_by_date()
        elif (choice) == "6":
            print ("Logout the program")
            register_main()
            break
        else:
            print ("Invalid choice, please try again")


# ==============================================================
# Main Registration menu 
# ==============================================================
# This function will be called when the program starts
def register_main ():
    while True:
        print ("******* Welcome to the registration page *******" \
        "\n" \
        "1. Register" \
        "\n" \
        "2. Login" \
        "\n" \
        "3. Exit")
        choice = input ("Please enter your choice: ")
        if (choice) == "1":
            user = register_user()
            if user : 
                project_menu(user.email)
        elif (choice) == "2":
            print ("Login page")
            logged_email = login_user()
            if logged_email:
                project_menu(logged_email)
        elif (choice) == "3":
            print ("Exiting the program")
            break
        else:
            print ("Invalid choice, please try again")
            


register_main()
