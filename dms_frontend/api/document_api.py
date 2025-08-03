def upload_document(self, file_path: str, progress_callback: Optional[Callable[[int], None]] = None) -> dict:
    print(f"Uploading document: {file_path}")
    
    # Prepare the file for upload
    with open(file_path, 'rb') as file:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        files = {'file': (file_name, file)}
        
        headers = {
            'Authorization': f'Token {self.token}'
        }
        
        print(f"Sending request to {self.base_url}documents/upload/")
        response = requests.post(
            f"{self.base_url}documents/upload/",
            files=files,
            headers=headers,
            stream=True,
            data={'total_size': file_size}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
    result = self.handle_response(response)
    print(f"Processed response: {result}")
    return result