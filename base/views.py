from django.shortcuts import render, redirect, get_object_or_404
import _mysql_connector as sql
from django.contrib.auth.models import User, AbstractUser
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Departments, Records, Approvals, Actions, Documents, Employees, Criticality, Designations
from .forms import AddEmployeeForm
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from .forms import CustomPasswordResetForm
from django.db import transaction
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import FileUploadForm

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from django.conf import settings
from google.oauth2.credentials import Credentials

from django.contrib.auth.forms import SetPasswordForm
from datetime import datetime, timedelta

from django.utils import timezone



CLIENT_ID = settings.CLIENT_ID
CLIENT_SECRET = settings.CLIENT_SECRET
REDIRECT_URI = settings.REDIRECT_URI
REFRESH_TOKEN = settings.REFRESH_TOKEN

# Constants
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
PARENT_FOLDER_ID = "19LfkPcJoFdu-mvP_BTW1ZotkBAZmZViS"


    
    
def upload_to_drive(request):
    form = FileUploadForm(request.POST or None, request.FILES or None)
    documents = Documents.objects.all()  # Retrieve all documents from the database

    if request.method == 'POST':
        # Authenticate with Google Drive API using service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=credentials)

        if 'fileUpload' in request.FILES:
            file = request.FILES['fileUpload']
            try:
                # Upload file to Google Drive
                file_metadata = {'name': file.name, 'parents': [PARENT_FOLDER_ID]}
                media = MediaIoBaseUpload(file, mimetype=file.content_type)
                uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                file_id = uploaded_file.get('id')

                # Retrieve form data
                doc_name = request.POST.get('docName')
                doc_description = request.POST.get('docDescription')

                criticality_value = request.POST.get('criticality')
                department_name = request.POST.get('department')
                print("Department name from form:", department_name)
                owner_id = request.user.id
                criticality_instance = Criticality.objects.get(criticality_level=criticality_value)
                latest_version = 0 # Retrieve department_id from the form
                department_instance = Departments.objects.get(department_name=department_name)

                # Create document record in the database
                document = Documents.objects.create(
                    document_name=doc_name,
                    detail=doc_description,
                    department=department_instance,
                    criticality=criticality_instance,
                    owner_id=owner_id,
                    version=latest_version,
                    loc_id=file_id,
                )
                document.save()
                messages.success(request, 'Document uploaded successfully')
            except Exception as e:
                # Handle any errors that may occur during file upload or database operation
                print(f"Error occurred: {e}")
                messages.error(request, 'Failed to upload file')

    return render(request, 'base/upload.html', {
        'form': form,
        'documents': documents
    })


def generate_public_url(request):
    # Authenticate with Google Drive API using OAuth 2.0 credentials
    if request.method == 'POST':
        credentials = Credentials(
            None,
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            refresh_token=settings.REFRESH_TOKEN,
            token_uri='https://oauth2.googleapis.com/token'
        )

        # Build the Google Drive service
        service = build('drive', 'v3', credentials=credentials)
        doc_id= request.POST.get('doc_id')
        document = Documents.objects.get(document_id=doc_id)
        file_id = document.loc_id


            # Retrieve the file metadata to get the webViewLink
        file_metadata = service.files().get(fileId=file_id, fields='webViewLink').execute()
        public_url = file_metadata['webViewLink']
        return redirect(public_url)
    

def reset_password2(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            # Process form data and send email for password reset
            form.save(request=request)
            # Redirect to a success page or show a success message
    else:
        form = CustomPasswordResetForm()
    
    return render(request, 'base/recover2.html', {'form': form}) 

def reset_password(request):
    if request.method == 'POST':
        # Get the employee ID from the form
        id = request.POST.get('emp_id')
  
        try:
            # Get the user corresponding to the employee ID
            user = User.objects.get(username=id)
            

            # Generate a password reset token
            token_generator = default_token_generator
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)

            # Construct the password reset URL
            reset_url = request.build_absolute_uri(f'/reset/{uid}/{token}/')

            # Send the password reset email
            subject = 'Password Reset'
            message = f'Please click the following link to reset your password: {reset_url}'
            from_email = 'hashamshakeel13@gmail.com'  # Replace with your email address
            to_email = user.email
            send_mail(subject, message, from_email, [to_email])

            # Redirect to a page indicating that the email has been sent
            messages.success(request, 'Password reset email sent successfully')
            

        except User.DoesNotExist:
            print(f"User not found with ID: {id}")    
            # Handle case where user with given ID does not exist
            messages.error(request, 'User does not exist')

    return render(request, 'base/recover.html')
    


def signin(request):
    if request.method == "POST":
        id = request.POST.get('id')
        pwd = request.POST.get('pwd')

        try:
            user = User.objects.get(username=id)
            employee = Employees.objects.get(employee_id=id)

            # Check if employee's designation is 'Other Employee'
            print(employee.designation.designation_id)
            if employee.designation.designation_id == 4:
                request.session['redirect_to'] = 'documents'  # Store the redirection URL in session
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
            return render(request, 'base/sign in.html', {})

        user = authenticate(request, username=id, password=pwd)

        if user is not None:
            login(request, user)
            if 'redirect_to' in request.session:
                redirect_url = request.session.pop('redirect_to')
                return redirect(redirect_url)  # Redirect to the stored URL
            else:
                return redirect('dashboard')  # Default redirect if no specific redirection is set
        else:
            messages.error(request, 'Incorrect Password')

    return render(request, 'base/sign in.html', {})



class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password2'].error_messages = {'password_mismatch': 'This password is too short'}

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the form, which creates the User object
            user = form.save()

            # Access the saved user object
            username = form.cleaned_data.get('username')
            if Employees.objects.filter(employee_id=username).exists():
                employee = Employees.objects.get(employee_id=username)
                user.email = employee.email
                user.first_name = employee.first_name
                user.last_name = employee.last_name
                user.save()

                messages.success(request, 'Your account has been created successfully!')
                return redirect('signup')  # Redirect to login page after successful signup
            else:
                user.delete()  # Delete the user if employee ID does not exist
                messages.error(request, 'Employee ID does not exist.')
    else:
        form = UserCreationForm()
    return render(request, 'base/sign up.html', {'form': form})

def logoutUser(request):
    logout(request)
    return redirect('signin')


def reset(request):
    return render(request, 'base/recover.html',{})

def view_emp(request):
    users = User.objects.all()
    if request.method == 'POST':

        employee_id = request.POST.get('employeeId')
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        email = request.POST.get('email')
        designation_id= request.POST.get('designation') # Default value if not provided

        designation = get_object_or_404(Designations, pk=designation_id)
        new_employee = Employees.objects.create(employee_id=employee_id, email=email, first_name=first_name, last_name=last_name, designation=designation)
        new_employee.first_name = first_name
        new_employee.last_name = last_name

        new_employee.save()

        # Add success message
        messages.success(request, 'Employee added successfully.')
    context = {'users': users}
    return render(request, 'base/emp2.html', context)

def update_employee(request):
    users = User.objects.all()
    if request.method == 'POST':
        try:
            employee_id = request.POST.get('employeeId')
            first_name = request.POST.get('firstName')
            last_name = request.POST.get('lastName')
            email = request.POST.get('email')
            designation= request.POST.get('designation') # Default value if not provided

            # Create an instance of the Employees model
            new_employee = Employees.objects.create(employee_id=employee_id, email=email, first_name=first_name, last_name=last_name, designation=designation)
            print("Designation ID:", designation)
            # Add success message
            messages.success(request, 'Employee added successfully.')
        except Exception as e:
            # Add error message with details
            messages.error(request, f'Error adding employee: {str(e)}')

    context = {'users': users}
    return render(request, 'base/emp2.html', context)

def view_records(request):
    # Retrieve all records along with their associated actions
    all_records = Records.objects.select_related('action').all()

    context = {
        'records': all_records
    }

    return render(request, 'base/viewActions.html', context)


def approvals(request):
    # Assuming you have a model named Approval with data to be displayed
    approvals = Approvals.objects.all()
    context = {
        'approvals': approvals,
    }
    return render(request, 'base/viewApprovals.html', context)


'''@login_required'''
def dashb(request):
    current_year = timezone.now().year
    current_month = timezone.now().month
    # Retrieve counts of each action type
    deleted_count = Records.objects.filter(action__action_taken='Deleted').count()
    approved_count = Records.objects.filter(action__action_taken='Approved').count()
    rejected_count = Records.objects.filter(action__action_taken='Rejected').count()
    viewed_count = Records.objects.filter(action__action_taken='Viewed').count()
    updated_count = Records.objects.filter(action__action_taken='Updated').count()
    pending = Approvals.objects.all().count()
    last_two_approvals = Approvals.objects.order_by('-date')[:2]
    username = request.user.username
    
    # Filter Records objects for 'Deleted' actions in the current month
    deleted_count_monthly = Records.objects.filter(action__action_taken='Deleted', date_time__month=current_month).count()

# Filter Records objects for 'Approved' actions in the current month
    approved_count_monthly = Records.objects.filter(action__action_taken='Approved', date_time__month=current_month).count()

# Filter Records objects for 'Rejected' actions in the current month
    rejected_count_monthly = Records.objects.filter(action__action_taken='Rejected', date_time__month=current_month).count()

# Filter Records objects for 'Updated' actions in the current month
    updated_count_monthly = Records.objects.filter(action__action_taken='Updated', date_time__month=current_month).count()

# Filter Records objects for 'Deleted' actions in the current year
    deleted_count_yearly = Records.objects.filter(action__action_taken='Deleted', date_time__year=current_year).count()

# Filter Records objects for 'Approved' actions in the current year
    approved_count_yearly = Records.objects.filter(action__action_taken='Approved', date_time__year=current_year).count()

# Filter Records objects for 'Rejected' actions in the current year
    rejected_count_yearly = Records.objects.filter(action__action_taken='Rejected', date_time__year=current_year).count()

# Filter Records objects for 'Updated' actions in the current year
    updated_count_yearly = Records.objects.filter(action__action_taken='Updated', date_time__year=current_year).count()
    
    last_three_documents = Documents.objects.order_by('-upload_date_time')[:3]
    
    if request.method=='POST':
        return redirect('dashboard')
    if request.user.is_authenticated:
        employee_id = request.user.username
        try:
            employee = Employees.objects.get(employee_id=employee_id)
        except Employees.DoesNotExist:
            employee = None


    # Pass the counts to the template
    context = {
        'last_three_documents': last_three_documents,
        'deleted_count': deleted_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'viewed_count': viewed_count,
        'updated_count': updated_count,
        'pending': pending,
        'last_two_approvals': last_two_approvals,
        'username': username,
        'deleted_count_monthly': deleted_count_monthly,
        'approved_count_monthly': approved_count_monthly,
        'rejected_count_monthly': rejected_count_monthly,
        'updated_count_monthly': updated_count_monthly,
        'deleted_count_yearly': deleted_count_yearly,
        'approved_count_yearly': approved_count_yearly,
        'rejected_count_yearly': rejected_count_yearly,
        'updated_count_yearly': updated_count_yearly,
        'employee': employee
    }
    return render(request, 'base/dashb.html', context)

    # Pass the counts to the template
    context = {
        'last_three_documents': last_three_documents,
        'deleted_count': deleted_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'viewed_count': viewed_count,
        'updated_count': updated_count,
        'pending': pending,
        'last_two_approvals': last_two_approvals,
        'username': username,
        'deleted_count_monthly': deleted_count_monthly,
        'approved_count_monthly': approved_count_monthly,
        'rejected_count_monthly': rejected_count_monthly,
        'updated_count_monthly': updated_count_monthly,
        'deleted_count_yearly': deleted_count_yearly,
        'approved_count_yearly': approved_count_yearly,
        'rejected_count_yearly': rejected_count_yearly,
        'updated_count_yearly': updated_count_yearly,
    }
    return render(request, 'base/dashb.html', context)


def docs(request):
    if request.method == 'POST':
        doc_name = request.POST.get('docName')
        doc_description = request.POST.get('docDescription')
        is_private = request.POST.get('isPrivate')
        criticality_value = request.POST.get('criticality')  # Get the value from the form

        # Convert is_private to boolean
        is_private = True if is_private == 'on' else False

        # Get the owner ID from the logged-in user
        owner_id = request.user.id  

        # Retrieve the corresponding Criticality instance
        criticality_instance = Criticality.objects.get(criticality_level=criticality_value)

        # Get the latest version for the document
        latest_version = 0

        # Save the data to the database
        document = Documents.objects.create(
            document_name=doc_name,
            detail=doc_description,
            is_private=is_private,
            criticality=criticality_instance,
            owner_id=owner_id,
            version=latest_version
        )

        # Optionally, you can add some messages for success or error
        messages.success(request, 'Document uploaded successfully')

        # Redirect to a success page or any other appropriate view

    # Retrieve all documents from the database
    documents = Documents.objects.all()

    # Render the template and pass the documents queryset to it
    return render(request, 'base/upload.html', {'documents': documents})


def docsemp(request):
    return render(request, 'base/docs.html',{})

def docs2(request):
    documents = Documents.objects.all()
    context = {
        'documents': documents,
    }
    return render(request, 'base/docs2.html', context)


def request_access(request):
    if request.method == 'POST':
        document_id = request.POST.get('document_id')
        doc = Documents.objects.get(pk=document_id)
        user = request.user
       # id = request.POST.get('id')
        # Create a new patient entry in the database using the Patient model
        approval = Approvals(date=datetime.now(), sender_employee=user, document=doc)
        approval.save()
        messages.success(request, "Approval request submitted")
        return redirect("documents")

def check_approved(request):
    if request.method == 'POST':
        document_id = request.POST.get('document_id')
        doc = Documents.objects.get(pk=document_id)
        user = request.user
        if Records.objects.filter(employee=user, document=doc).exists():
            record = Records.objects.get(employee=user, document=doc)
            if record.action_id == 7:
                credentials = Credentials(
                    None,
                    client_id=settings.CLIENT_ID,
                    client_secret=settings.CLIENT_SECRET,
                    refresh_token=settings.REFRESH_TOKEN,
                    token_uri='https://oauth2.googleapis.com/token'
                )

                # Build the Google Drive service
                service = build('drive', 'v3', credentials=credentials)
                doc_id= request.POST.get('doc_id')
                file_id = doc.loc_id  
                 

                    # Retrieve the file metadata to get the webViewLink
                file_metadata = service.files().get(fileId=file_id, fields='webViewLink').execute()
                public_url = file_metadata['webViewLink']
                return redirect(public_url)
            else:
                messages.error(request, "You don't have approval to access this document")
                return redirect("documents")
        else:
            messages.error(request, "You don't have approval to access this document")
            return redirect("documents")

def approvedDocument(request):
    initial_values = {
        'employee': '1716',
        'document': '1',
        'action': '13',
    }
    form = ApproveDocument(initial=initial_values)
    if request.method == 'POST':
        form = ApproveDocument(request.POST)
        if form.is_valid():
            form.save()
            print(request.POST)
    print(form.errors)
    context = {'form': form}
    return render(request, 'base/viewApprovals.html', context)
#function to search documents
def search_doc(request):
    if request.method == 'POST':
        doc_name = request.POST.get('doc_name')
        docs = Documents.objects.filter(document_name=doc_name)
        context = {'documents': docs}
    return render(request, 'base/docs2.html', context)

def search_doc2(request):
    if request.method == 'POST':
        doc_name = request.POST.get('doc_name')
        docs = Documents.objects.filter(document_name=doc_name)
        context = {'documents': docs}
    return render(request, 'base/upload.html', context)

#Function to search employee
def search_emp(request):
    if request.method =="POST":
        search = request.POST.get('emp_search')
        if search == "":
            users = User.objects.all()
        else:
            users = User.objects.filter(pk=search)
        if users.exists():
            context ={'users' : users}
            return render(request, 'base/emp2.html', context)
        else:
            messages.error(request, "No employee found")
            return redirect("employees")

def remove_emp(request,user_id):
    '''emp = Employees.objects.get(pk=user_id)'''
    user = User.objects.get(pk=user_id)
    user.delete()
    '''emp.delete()'''
    messages.success(request, 'Employee deleted successfully.')
    return redirect('employees')
    

def view_employee(request):
    if request.method == 'POST':
        employee_id = request.POST.get('user_id')
        emp = User.objects.get(pk=employee_id)
        context = { 'employee': emp}
        return render(request, 'base/view_emp.html', context)

def update_employee(request):
    if request.method == 'POST':
        emp_id = request.POST.get('emp_ID')
        emp_fname = request.POST.get('first_name')
        emp_lname = request.POST.get('last_name')
        emp_email = request.POST.get('email')
        emp = User.objects.get(pk=emp_id)
        emp.first_name = emp_fname
        emp.last_name = emp_lname
        emp.email = emp_email
        emp.save()
        return redirect("employees")
    
    
def search_criticality(request):
    if request.method == 'POST':
        criticality = request.POST.get('criticality')
        department = request.Post.get('department')
        if criticality == "4" and department == "All":
            docs = Documents.objects.all()
            context = {'documents': docs}
        else:
            if criticality == "4" and department != "All":
                docs = Documents.objects.filter(department=department)
                context = {'documents': docs}
            if criticality != "4" and department == "All":
                docs = Documents.objects.filter(criticality_id=criticality)
                context = {'documents': docs}

            else:
                docs = Documents.objects.filter(criticality_id=criticality, department=department)
                context = {'documents': docs}
    return render(request, 'base/upload.html', context)

@transaction.atomic
def delete_document(request, doc_id):
    document = get_object_or_404(Documents, document_id=doc_id)

    # Create a new record indicating deletion action
    action_deleted = Actions.objects.get(action_id=8)  # Assuming 8 corresponds to 'Deleted' action
    record = Records.objects.create(employee=request.user, document=document, action=action_deleted)

    # Authenticate with Google Drive API
    credentials = service_account.Credentials.from_service_account_file(
        'service_account.json', scopes=['https://www.googleapis.com/auth/drive'])
    service = build('drive', 'v3', credentials=credentials)

    # Delete the document from Google Drive
    service.files().delete(fileId=document.loc_id).execute()

    # Delete the document record from the database
    document.delete()

    messages.success(request, 'Document deleted successfully.')
    return redirect('documents_admin')
def approvedDocument(request):
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        document_id = request.POST.get('document_id')
        action = Actions.objects.get(pk=7)
        request_id = request.POST.get('request_id')
        if emp_id:
            new_record = Records(employee_id=emp_id, document_id=document_id, action=action)
            new_record.save()
            new_record2 = Approvals(request_id=request_id)
            new_record2.delete()
        return redirect("approvals")  

def rejectedDocument(request):
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        document_id = request.POST.get('document_id')  
        action = Actions.objects.get(pk=6)
        request_id = request.POST.get('request_id')
        if emp_id:
            new_record = Records(employee_id=emp_id, document_id=document_id, action=action)
            new_record.save()
            new_record2 = Approvals(request_id=request_id)
            new_record2.delete()
        return redirect("approvals")
     
def filter_docs(request):
    if request.method == 'POST':
        criticality = request.POST.get('criticality')
        department = request.POST.get('department')
        if criticality == "4" and department == "All":
            docs = Documents.objects.all()
        else:
            if criticality == "4" and department != "All":
                department_id = Departments.objects.get(department_name=department).department_id
                docs = Documents.objects.filter(department=department_id)
            elif criticality != "4" and department == "All":
                docs = Documents.objects.filter(criticality=criticality)

            else:
                department_id = Departments.objects.get(department_name=department).department_id
                docs = Documents.objects.filter(criticality=criticality, department=department_id)
                
        if docs.exists():
            context ={'documents': docs}
            return render(request, 'base/upload.html', context)
        else:
            messages.error(request, "No documents found")
            return redirect("documents_admin")
        
def filter_docs2(request):
    if request.method == 'POST':
        criticality = request.POST.get('criticality')
        department = request.POST.get('department')
        if criticality == "4" and department == "All":
            docs = Documents.objects.all()
        else:
            if criticality == "4" and department != "All":
                department_id = Departments.objects.get(department_name=department).department_id
                docs = Documents.objects.filter(department=department_id)
            elif criticality != "4" and department == "All":
                docs = Documents.objects.filter(criticality=criticality)

            else:
                department_id = Departments.objects.get(department_name=department).department_id
                docs = Documents.objects.filter(criticality=criticality, department=department_id)
        if docs.exists():
            context ={'documents': docs}
            return render(request, 'base/docs2.html', context)
        else:
            messages.error(request, "No documents found")
            return redirect("documents")