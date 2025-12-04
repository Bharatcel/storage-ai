# File Upload Implementation - Azure Blob Storage

## ✅ What's Been Implemented:

### 1. **File Validation**
- ✅ Allowed file types: `.png`, `.txt`, `.jpg`, `.jpeg`, `.pdf`
- ✅ Maximum file size: 10MB
- ✅ Automatic error on invalid file types
- ✅ Automatic error on oversized files

### 2. **Azure Blob Storage Integration**
- ✅ Files uploaded to Azure Blob Storage container
- ✅ Organized by project and question: `project_{id}/question_{id}/{uuid}{ext}`
- ✅ Returns blob URL to store in database
- ✅ Content-Type set automatically based on file extension

### 3. **New API Endpoints**

#### **Upload File**
```
POST /api/files/upload
```

**Form Data:**
- `project_id` (integer) - The project ID
- `question_id` (string) - The question ID (e.g., "67", "68")
- `file` (file) - The file to upload

**Response:**
```json
{
  "success": true,
  "blob_url": "https://<account>.blob.core.windows.net/assessment-uploads/project_1/question_67/uuid.pdf",
  "filename": "document.pdf",
  "project_id": 1,
  "question_id": "67"
}
```

**Errors:**
- 400: Invalid file type or file too large
- 503: Blob storage not configured
- 500: Upload failed

#### **Delete File**
```
DELETE /api/files/upload?blob_url=<url>
```

---

## 🔧 Configuration Required:

### Step 1: Get Azure Storage Connection String

You need to add your Azure Storage account connection string to `.env`:

1. Go to Azure Portal
2. Navigate to your Storage Account
3. Go to **Access keys**
4. Copy **Connection string**

### Step 2: Update `.env` File

Replace this line in your `.env`:
```env
AZURE_STORAGE_CONNECTION_STRING=your_connection_string_here
```

With your actual connection string:
```env
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net
```

The container `assessment-uploads` will be created automatically on first upload.

---

## 📝 How to Use in Your Assessment Flow:

### Workflow for File Upload Questions:

For questions with `"type": "MCQ_WITH_FILE"` or `"type": "FILE_UPLOAD"`:

**Step 1: User uploads file**
```javascript
// Frontend: Upload file first
const formData = new FormData();
formData.append('project_id', projectId);
formData.append('question_id', '67');
formData.append('file', selectedFile);

const response = await fetch('http://localhost:8000/api/files/upload', {
  method: 'POST',
  body: formData
});

const result = await response.json();
// result.blob_url = "https://...blob URL..."
```

**Step 2: Submit assessment with blob URL**
```javascript
// Include the blob_url in the response_value
{
  "project": { ... },
  "responses": [
    {
      "question_id": "67",
      "question_text": "Do you have KPIs?",
      "response_value": result.blob_url,  // Store the blob URL
      "comments": "Uploaded file: document.pdf"
    }
  ]
}
```

**Step 3: Response saved in database**
The `response_value` column in `dbo.tpsm_responses` will contain:
```
https://youraccount.blob.core.windows.net/assessment-uploads/project_1/question_67/uuid.pdf
```

---

## 🧪 Testing File Upload:

### Using Swagger UI (http://localhost:8000/docs):

1. **Go to POST `/api/files/upload`**
2. Click **"Try it out"**
3. Fill in:
   - `project_id`: 1
   - `question_id`: "67"
   - `file`: Click "Choose File" and select a PDF
4. Click **"Execute"**

**Expected Success Response:**
```json
{
  "success": true,
  "blob_url": "https://...",
  "filename": "test.pdf",
  "project_id": 1,
  "question_id": "67"
}
```

**Test Invalid File Type:**
- Upload a `.exe` or `.zip` file
- Expected: 400 error with message about allowed types

---

## 🎯 Questions That Support File Upload:

From your `questions.py`, these questions have file upload:

- **Question 11**: Architecture diagram (FILE_UPLOAD)
- **Question 67**: KPIs tracking document (MCQ_WITH_FILE)
- **Question 68**: On-premises inventory (MCQ_WITH_FILE)
- **Question 69**: Architecture documentation (MCQ_WITH_FILE)
- **Question 70**: Storage utilization report (MCQ_WITH_FILE)

---

## 🔐 Security Features:

✅ Only allowed file types can be uploaded
✅ File size limited to 10MB
✅ Files organized by project/question (prevents conflicts)
✅ UUID in filename prevents overwriting
✅ Content-Type headers set correctly
✅ Connection to Azure uses secure connection string

---

## 📊 Database Storage:

Files are NOT stored in the database. Only the blob URL is stored:

**Table:** `dbo.tpsm_responses`
**Column:** `response_value` (TEXT)
**Value:** `https://storageaccount.blob.core.windows.net/assessment-uploads/project_1/question_67/abc123.pdf`

This keeps your database lightweight and fast!

---

## ⚠️ Important Notes:

1. **Container Creation**: The `assessment-uploads` container is created automatically on first upload
2. **Blob Storage Required**: Set `AZURE_STORAGE_CONNECTION_STRING` in `.env` before testing
3. **File Persistence**: Files remain in blob storage even if you delete the database record
4. **Cost**: Azure Blob Storage has minimal costs for storage and bandwidth

---

## 🚀 Next Steps:

1. ✅ Add your Azure Storage connection string to `.env`
2. ✅ Restart the server: `uvicorn main:app --reload`
3. ✅ Test file upload via Swagger UI
4. ✅ Update frontend to handle file uploads for file upload questions
