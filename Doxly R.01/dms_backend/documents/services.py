import os
import requests
from datetime import datetime, timedelta

API_BASE_URL = "http://127.0.0.1:8000/api/documents/"

# Document Endpoints
def get_documents():
    return requests.get(API_BASE_URL).json()

def create_document(data):
    return requests.post(API_BASE_URL, json=data).json()

def get_document(doc_id):
    return requests.get(f"{API_BASE_URL}{doc_id}/").json()

def update_document(doc_id, data):
    return requests.put(f"{API_BASE_URL}{doc_id}/", json=data).json()

def delete_document(doc_id):
    return requests.delete(f"{API_BASE_URL}{doc_id}/").status_code

# Version Endpoints
def get_versions():
    return requests.get(API_BASE_URL + "versions/").json()

def create_version(data):
    return requests.post(API_BASE_URL + "versions/", json=data).json()

def get_version(ver_id):
    return requests.get(f"{API_BASE_URL}versions/{ver_id}/").json()

def update_version(ver_id, data):
    return requests.put(f"{API_BASE_URL}versions/{ver_id}/", json=data).json()

def delete_version(ver_id):
    return requests.delete(f"{API_BASE_URL}versions/{ver_id}/").status_code

# DMS Utility Logic
def generate_document_code(b, c, d, e, f, g, h_number):
    return f"{b}-{c}-{d}-{e}-{f}-{g}-{int(h_number):06}"

def is_latest_revision(doc, revisions):
    if not revisions:
        return True
    latest = sorted(revisions, key=lambda r: r.get('created_date', ''), reverse=True)[0]
    return latest.get('revision_number') == doc.get('revision')

def is_latest_drawing(drawing_code, rev_num, drawing_list):
    max_rev = max((d.get('rev') for d in drawing_list if d.get('code') == drawing_code), default=None)
    return rev_num == max_rev

def get_references_for_document(doc, all_docs):
    code = f"{doc['document_code']}_R{doc['revision']}" if doc.get('revision') else doc['document_code']
    return [
        f"{d['document_code']}_R{d['revision']}" if d.get('revision') else d['document_code']
        for d in all_docs if code in d.get('references', '')
    ]

def get_reference_dates(doc, all_docs):
    related_dates = []
    for d in all_docs:
        if doc['document_code'] in d.get('references', ''):
            try:
                related_dates.append(datetime.strptime(d['created_date'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d/%m/%Y'))
            except:
                pass
    return ', '.join(set(related_dates))

def categorize_invoice(doc):
    code = doc.get('document_type', {}).get('code', '')
    if code == "INV":
        return "Client Invoice"
    elif code == "SNV":
        return "Sub Contractor Invoice"
    return ""

# Date/Time Calculations
def calculate_due_date(start_date: datetime, days: int, holidays: list, weekends=(5, 6)) -> datetime:
    """Moved from Document.calculate_due_date"""
    date = start_date
    count = 0
    while count < days:
        date += timedelta(days=1)
        if date.weekday() not in weekends and date not in holidays:
            count += 1
    return date


def count_vacation_overlap(start: datetime, end: datetime, vacations: list) -> int:
    """Moved from Document.count_vacation_overlap"""
    days = 0
    for vac in vacations:
        if vac.end_date >= start and vac.start_date <= end:
            overlap_start = max(start, vac.start_date)
            overlap_end = min(end, vac.end_date)
            days += (overlap_end - overlap_start).days + 1
    return days

# Document Paths
def build_document_folder_path(project_name: str, doc_code: str, revision: int, sender: str) -> str:
    """Moved from Document.build_document_folder_path"""
    return os.path.join(
        "doxly", "projects", project_name.replace(" ", "_"),
        f"{doc_code}_R{revision}", sender
    )

# Status Checks
def determine_document_status(status_code: str, is_latest_revision: bool) -> str:
    """Moved from Document.determine_document_status"""
    if status_code == "URE":
        return "URE"
    if status_code in ["A", "B", "D", "E"]:
        return "Closed"
    if status_code == "C":
        return "Open need Revision" if not is_latest_revision else "Closed"
    return "Status code is empty"

def get_final_close_date(doc):
    dates = [doc.get("completed_date"), doc.get("due_date"), doc.get("modified_date")]
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in dates if d]
    return max(dates).strftime("%Y-%m-%d") if dates else None

def check_document_files(base_path, doc_code, revision):
    result = {}
    for ext in ["pdf", "docx", "xlsx"]:
        full_path = os.path.join(base_path, f"{doc_code}_R{revision}.{ext}")
        result[ext] = os.path.exists(full_path)
    return result

def get_overdue_days(doc):
    if doc.get("due_date") and not doc.get("completed_date"):
        delta = (datetime.now() - datetime.strptime(doc['due_date'], "%Y-%m-%d")).days
        return max(delta, 0)
    return 0

def get_delay_status(doc):
    due = doc.get("due_date")
    completed = doc.get("completed_date")
    if not completed and due:
        return "Overdue" if datetime.now().date() > datetime.strptime(due, "%Y-%m-%d").date() else "URE"
    if completed and due:
        return "Delay" if datetime.strptime(completed, "%Y-%m-%d") > datetime.strptime(due, "%Y-%m-%d") else "On Date"
    return "Unknown"
def search_documents(self, query: str, filters: dict = None):
    params = {'search': query}
    if filters:
        params.update(filters)
    try:
        response = requests.get(
            f"{self.base_url}search/",
            params=params,
            headers=self.get_headers()
        )
        return self.handle_response(response)
    except Exception as e:
        raise Exception(f"Search failed: {str(e)}")


class DocumentAPI(BaseAPI):
    def __init__(self, token: str = None, refresh_token: str = None):
        super().__init__()
        self.base_url = f"{BACKEND_API_URL.rstrip('/')}/documents/"
        self.token = token
        self.refresh_token = refresh_token
        self.token_expiration = datetime.now() + timedelta(minutes=14)  # Set 1 min before actual expiration

    def refresh_access_token(self):
        """Refresh the access token using the refresh token"""
        try:
            response = requests.post(
                f"{BACKEND_API_URL.rstrip('/')}/token/refresh/",
                data={'refresh': self.refresh_token}
            )
            response.raise_for_status()
            token_data = response.json()
            self.token = token_data['access']
            self.token_expiration = datetime.now() + timedelta(minutes=14)
            return True
        except Exception as e:
            print(f"Token refresh failed: {str(e)}")
            return False

    def make_authenticated_request(self, method, endpoint, **kwargs):
        """Handle token refresh automatically before making requests"""
        if datetime.now() >= self.token_expiration:
            if not self.refresh_access_token():
                raise Exception("Authentication failed - could not refresh token")
        
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {self.token}'
        kwargs['headers'] = headers
        
        return getattr(requests, method)(
            f"{self.base_url}{endpoint}",
            **kwargs
        )

    def get_documents(self):
        """Example method using the authenticated request handler"""
        try:
            response = self.make_authenticated_request(
                'get',
                '',
                params={'page': 1, 'page_size': 20}
            )
            return self.handle_response(response)
        except Exception as e:
            raise Exception(f"Failed to fetch documents: {str(e)}")

    def upload_document(self, document_data):
        """Upload a document with the given data"""
        try:
            response = self.make_authenticated_request(
                'post',
                'upload/',
                files=document_data
            )
            response_data = self.handle_response(response)
            # Ensure the response includes file name and unique ID
            print(f"Uploaded document: {response_data['file_name']} with ID: {response_data['unique_id']}")
            return response_data
        except Exception as e:
            raise Exception(f"Failed to upload document: {str(e)}")
            