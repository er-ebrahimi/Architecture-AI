# ArchitectAI - AI-Powered Visual Product Search API

A Django-based REST API that uses AI to analyze product images and find similar products through visual similarity matching. Built with Django, PostgreSQL, and OpenAI's vision capabilities.

## 🚀 Features

- **AI-Powered Image Analysis**: Uses OpenAI's vision models to extract detailed features from product images
- **Visual Similarity Search**: Find similar products based on visual characteristics and style
- **RESTful API**: Clean, well-documented API endpoints
- **PostgreSQL Database**: Robust data storage with optimized queries
- **File Management**: Secure image upload and storage
- **Environment Configuration**: Easy setup with environment variables

## 🏗️ Architecture

### Core Components

1. **Django Backend**: REST API framework
2. **PostgreSQL Database**: Primary data storage
3. **OpenAI Integration**: AI-powered image analysis
4. **File Storage**: Product image management
5. **Pydantic Models**: Type-safe data validation

### API Endpoints

- `POST /api/products/` - Add a new product with image analysis
- `POST /api/products/find-similar/` - Find similar products by image
- `GET /api/health/` - Health check endpoint
- `GET /admin/` - Django admin interface

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL 17+
- OpenAI API Key
- Git

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd ArchitecuterAI
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Install PostgreSQL

- Download and install PostgreSQL 17+ from [postgresql.org](https://www.postgresql.org/download/)
- Create a database named `architectai_db`
- Set up a user with appropriate permissions

#### Configure Database

```bash
# Create database
createdb architectai_db

# Or using psql
psql -U postgres -c "CREATE DATABASE architectai_db;"
```

### 5. Environment Configuration

Create a `.env` file in the project root:

```env
# Database Configuration
DB_NAME=architectai_db
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Django Configuration
SECRET_KEY=your_secret_key_here
DEBUG=True
```

### 6. Run Migrations

```bash
python manage.py migrate
```

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

## 🚀 Running the Application

### Start Development Server

```bash
python manage.py runserver
```

The API will be available at:

- **API Base URL**: `http://localhost:9000/api/`
- **Admin Panel**: `http://localhost:9000/admin/`
- **Health Check**: `http://localhost:9000/api/health/`
- **Swagger UI**: `http://localhost:9000/swagger/` - Interactive API documentation
- **ReDoc**: `http://localhost:9000/redoc/` - Alternative API documentation
- **OpenAPI Schema**: `http://localhost:9000/swagger.json` - Machine-readable API specification

## 📖 API Documentation

### Interactive Documentation

The API includes comprehensive interactive documentation powered by Swagger/OpenAPI:

- **Swagger UI**: Visit `http://localhost:9000/swagger/` for an interactive interface where you can:

  - Explore all available endpoints
  - View detailed request/response schemas
  - Test API calls directly from the browser
  - Download the OpenAPI specification

- **ReDoc**: Visit `http://localhost:9000/redoc/` for an alternative documentation interface with:
  - Clean, readable documentation
  - Detailed schema information
  - Better mobile experience

### API Schema

The API follows OpenAPI 3.0 specification and can be accessed at:

- **JSON Schema**: `http://localhost:9000/swagger.json`
- **YAML Schema**: `http://localhost:9000/swagger.yaml`

## 📖 API Usage

### 1. Add a Product

```bash
curl -X POST http://localhost:9000/api/products/ \
  -F "source_url=https://example.com/product" \
  -F "image=@/path/to/image.jpg"
```

**Response:**

```json
{
  "success": true,
  "product_id": 1,
  "image_filename": "uuid.jpg",
  "features": {
    "main_objects": [...],
    "overall_style": [...],
    "color_palette": [...]
  },
  "message": "Product successfully analyzed and saved"
}
```

### 2. Find Similar Products

```bash
curl -X POST http://localhost:9000/api/products/find-similar/ \
  -F "image=@/path/to/query_image.jpg"
```

**Response:**

```json
{
  "success": true,
  "query_features": {...},
  "query_tags": ["modern", "minimalist", "wood"],
  "total_products_checked": 50,
  "similar_products": [
    {
      "id": 1,
      "source_url": "https://example.com/product",
      "image_filename": "uuid.jpg",
      "image_url": "/media/uuid.jpg",
      "similarity_score": 8,
      "features": {...},
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "message": "Found 5 similar products"
}
```

### 3. Health Check

```bash
curl http://localhost:9000/api/health/
```

## 🗄️ Database Schema

### Products Table

| Field          | Type          | Description           |
| -------------- | ------------- | --------------------- |
| id             | BigAutoField  | Primary key           |
| source_url     | URLField      | Original product URL  |
| image_filename | CharField     | Unique image filename |
| features       | JSONField     | AI-generated features |
| created_at     | DateTimeField | Creation timestamp    |
| updated_at     | DateTimeField | Last update timestamp |

### Features JSON Structure

```json
{
  "main_objects": [
    {
      "object_type": "chair",
      "attributes": ["wooden", "modern", "minimalist"]
    }
  ],
  "overall_style": ["scandinavian", "contemporary"],
  "color_palette": ["#ffffff", "#8B4513", "#000000"],
  "materials": ["wood", "metal"],
  "textures": ["smooth", "matte"]
}
```

## 🔧 Development

### Project Structure

```
ArchitecuterAI/
├── api/                    # Main API app
│   ├── models.py          # Database models
│   ├── views.py           # API endpoints
│   ├── urls.py            # URL routing
│   ├── ai_service.py      # OpenAI integration
│   └── schemas.py         # Pydantic models
├── config/                # Django settings
│   ├── settings.py        # Main settings
│   ├── urls.py           # Root URL config
│   └── wsgi.py           # WSGI config
├── media/                 # Uploaded files
├── static/                # Static files
├── .env                   # Environment variables
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
├── manage.py             # Django management
└── README.md             # This file
```

### Adding New Features

1. **Models**: Add new models in `api/models.py`
2. **Views**: Create new API endpoints in `api/views.py`
3. **URLs**: Register new routes in `api/urls.py`
4. **Migrations**: Run `python manage.py makemigrations` and `python manage.py migrate`

### Code Quality

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Follow Django best practices

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test api

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 🚀 Deployment

### Production Settings

1. Set `DEBUG=False` in environment
2. Configure production database
3. Set up static file serving
4. Configure media file storage
5. Set up proper logging
6. Use environment variables for secrets

### Docker Deployment (Optional)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:9000"]
```

## 📝 Environment Variables

| Variable         | Description              | Default          |
| ---------------- | ------------------------ | ---------------- |
| `DB_NAME`        | PostgreSQL database name | `architectai_db` |
| `DB_USER`        | Database username        | `postgres`       |
| `DB_PASSWORD`    | Database password        | -                |
| `DB_HOST`        | Database host            | `localhost`      |
| `DB_PORT`        | Database port            | `5432`           |
| `OPENAI_API_KEY` | OpenAI API key           | -                |
| `SECRET_KEY`     | Django secret key        | -                |
| `DEBUG`          | Debug mode               | `True`           |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed information
3. Contact the development team

## 🔄 Changelog

### Version 1.0.0

- Initial release
- AI-powered image analysis
- Visual similarity search
- PostgreSQL integration
- RESTful API endpoints

---

**Built with ❤️ using Django, PostgreSQL, and OpenAI**
