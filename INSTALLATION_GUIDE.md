# Visual Product Search - Installation Guide

This guide will help you set up and run the Visual Product Search application, which consists of a Django backend with AI-powered image analysis and a React frontend with a beautiful dashboard.

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn
- PostgreSQL (optional, SQLite works for development)

## Backend Setup (Django)

### 1. Navigate to the Django project

```bash
cd architecture-ai
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` file with your settings:

```env
# Database (for development, SQLite is fine)
DB_NAME=architectai_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# AI Service (OpenAI API key required)
OPENAI_API_KEY=your_openai_api_key

# Django settings
SECRET_KEY=your_secret_key
DEBUG=True
```

### 5. Database setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run the Django server

```bash
python manage.py runserver
```

The backend API will be available at `http://localhost:9000`

## Frontend Setup (React)

### 1. Navigate to the React project

```bash
cd architect-frontend
```

### 2. Install dependencies

```bash
npm install
```

### 3. Environment configuration

The `.env` file should already be created with:

```env
VITE_API_BASE_URL=http://localhost:9000
```

### 4. Run the development server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

1. **Access the Dashboard**: Open your browser and go to `http://localhost:5173`

2. **Navigate to Visual Search**: Click on the "Visual Search" tab in the dashboard

3. **Upload an Image**:

   - Drag and drop an image into the upload area, or
   - Click "Choose Image" to browse and select a file
   - Supported formats: JPEG, PNG, WebP (Max: 10MB)

4. **Search for Similar Products**: Click "Find Similar Products" to analyze your image

5. **View Results**: The system will:
   - Analyze your image using AI to identify objects, styles, and attributes
   - Search the database for similar products
   - Display results as beautiful product cards with similarity scores
   - Show detailed analysis of what was detected in your image

## API Endpoints

The backend provides these main endpoints:

- `POST /api/products/find-similar/` - Upload an image to find similar products
- `POST /api/products/` - Add a new product to the database
- `GET /api/health/` - Health check endpoint
- `GET /docs/` - Swagger API documentation

## Features

### Frontend Features

- ✨ Modern, responsive design with dark/light theme support
- 🖱️ Drag and drop image upload
- 🔍 Real-time search with beautiful loading states
- 📱 Mobile-friendly product cards
- 🎨 Rich visual feedback and error handling
- 📊 Detailed analysis results display

### Backend Features

- 🤖 AI-powered image analysis using OpenAI Vision API
- 🔍 Intelligent similarity matching algorithm
- 📝 RESTful API with Swagger documentation
- 🛡️ CORS enabled for frontend integration
- 🗃️ Flexible database storage (PostgreSQL/SQLite)

## Troubleshooting

### CORS Issues

If you encounter CORS errors, ensure:

- The Django server is running on `http://localhost:9000`
- The React server is running on `http://localhost:5173`
- CORS settings in Django are properly configured

### Image Upload Issues

- Check file size (must be under 10MB)
- Ensure file is a valid image format
- Verify the backend media directory has write permissions

### API Connection Issues

- Confirm both servers are running
- Check the `VITE_API_BASE_URL` in the frontend `.env` file
- Verify network connectivity between frontend and backend

### AI Analysis Issues

- Ensure your OpenAI API key is valid and has sufficient credits
- Check the API key is properly set in the backend `.env` file
- Monitor the Django server logs for AI service errors

## Development Notes

- The project follows SOLID principles and clean architecture
- Components are modular and reusable
- API responses follow consistent JSON structure
- Error handling is comprehensive throughout both frontend and backend
- The UI is built with shadcn/ui components for consistency and beauty

For additional help, check the Django and React server logs for detailed error messages.
