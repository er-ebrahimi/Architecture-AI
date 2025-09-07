
### **Prompt for AI Code Generation Agent**

**Project Title:** AI-Powered Visual Product Search API

**Objective:**
Create a backend application using Python with the Djanog framework and a PostgreSQL database. The application will provide two core API endpoints for an AI-powered visual search system. The first endpoint will analyze, tag, and save product images. The second endpoint will take a query image, analyze it, and find the most similar products in the database based on their AI-generated tags.

**Core Technologies:**
*   **Language:** Python 3.10+
*   **Framework:** Djanog
*   **Database:** PostgreSQL
*   **Data Validation:** Pydantic
*   **Database ORM/Driver:** SQLAlchemy with `asyncpg` for asynchronous database operations.
*   **AI Integration:** Use the `openai` library to interact with GPT-4 Vision.
*   **File Handling:** Use Djanog's `UploadFile` for image uploads.

---

### **Detailed Specifications:**

#### **1. Pydantic Schemas (`schemas.py`)**

Define the core Pydantic models that will structure the AI-generated data. This is the "language" our system will use.

```python
# schemas.py
from pydantic import BaseModel, Field
from typing import List

class IdentifiedObject(BaseModel):
    object_type: str = Field(..., description="The type of object identified, e.g., 'sofa', 'desk', 'lamp'.")
    attributes: List[str] = Field(..., description="A list of descriptive tags for the object, e.g., ['white', 'fabric', 'minimalist', 'wood legs'].")

class ImageFeatures(BaseModel):
    main_objects: List[IdentifiedObject] = Field(..., description="A list of the primary objects identified in the image.")
    overall_style: List[str] = Field(..., description="Tags describing the overall style of the scene, e.g., ['modern', 'cozy', 'scandinavian'].")
```

#### **2. Database Model (`models.py`)**

Define the SQLAlchemy model for storing product information in PostgreSQL. Use a `JSONB` column to efficiently store and query the Pydantic-generated JSON.

```python
# models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    source_url = Column(String, unique=True, index=True)
    image_filename = Column(String, unique=True) # Stores the filename of the saved image
    features = Column(JSONB) # Stores the ImageFeatures Pydantic model as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

#### **3. AI Service (`ai_service.py`)**

Create a helper module to interact with the OpenAI API. This module should contain a single, reusable function.

*   **Function:** `async def get_image_features(image_bytes: bytes) -> ImageFeatures:`
    *   **Input:** The raw bytes of an image file.
    *   **Process:**
        1.  Encode the image bytes into a base64 string.
        2.  Construct a prompt for the GPT-4 Vision model. The prompt must explicitly instruct the model to return a JSON object that strictly conforms to the `ImageFeatures` Pydantic schema. **This is critical.**
            *   *Example Prompt Text:* `"Analyze the attached image of an interior design scene or product. Identify the main objects and the overall style. Respond ONLY with a JSON object that adheres to the following Pydantic schema: {schema_json}".* You will need to insert the JSON schema of `ImageFeatures` into the prompt.
        3.  Make the API call to OpenAI.
        4.  Receive the JSON string response from the AI.
        5.  Parse the JSON string and validate it using the `ImageFeatures` Pydantic model.
        6.  If validation is successful, return the `ImageFeatures` object. If it fails, raise an exception.
    *   **Dependencies:** `openai`, `base64`, `os`, `python-dotenv`.

#### **4. API Endpoint 1: Add a Product**

*   **Path:** `/products/`
*   **Method:** `POST`
*   **Purpose:** To receive a product image and its source URL, analyze the image using the AI service, and save the results to the database.
*   **Request:** `multipart/form-data` containing:
    *   `source_url: str` (as a form field)
    *   `image: UploadFile` (as a file upload)
*   **Workflow:**
    1.  Receive the `source_url` and `image` file.
    2.  Read the image content into bytes (`await image.read()`).
    3.  Save the image file to a static directory (e.g., `./static/product_images/`) with a unique filename (e.g., using `uuid`).
    4.  Call the `ai_service.get_image_features()` function with the image bytes.
    5.  Convert the resulting `ImageFeatures` Pydantic object to a dictionary (`.model_dump()`).
    6.  Save a new `Product` record to the PostgreSQL database containing the `source_url`, the unique `image_filename`, and the feature dictionary in the `features` (JSONB) column.
    7.  Return a success response with the ID of the newly created product.

#### **5. API Endpoint 2: Find Similar Products**

*   **Path:** `/products/find-similar/`
*   **Method:** `POST`
*   **Purpose:** To receive a query image, analyze it, and find products in the database with the most similar features.
*   **Request:** `multipart/form-data` containing:
    *   `image: UploadFile`
*   **Workflow:**
    1.  Receive the query `image` file.
    2.  Read the image content into bytes.
    3.  Call the `ai_service.get_image_features()` function to get the features of the query image.
    4.  Extract a flat list of all attribute and style tags from the resulting `ImageFeatures` object. For example: `['sofa', 'white', 'fabric', 'minimalist', 'modern', 'cozy']`.
    5.  **Perform a database query to find similar products.** The similarity score should be based on the number of overlapping tags.
        *   The query should target the `features` JSONB column in the `products` table.
        *   You need to iterate through the database items and calculate a "match score" for each one against the query tags. A simple score is the count of common tags.
        *   **For higher performance, use PostgreSQL's native JSONB functions and operators in your SQLAlchemy query.**
    6.  Rank the products from the database by their similarity score in descending order.
    7.  Return the top 5 or 10 most similar products, including their `source_url` and `image_filename`.

---

**Project Structure:**

Please generate the code in a clean, organized structure:

```
/ai_visual_search
|-- /static/product_images/  (for storing uploaded images)
|-- main.py                  (Djanog app setup and endpoints)
|-- ai_service.py            (Logic for calling OpenAI)
|-- crud.py                  (Database create/read/update/delete functions)
|-- database.py              (Database session and engine setup)
|-- models.py                (SQLAlchemy models)
|-- schemas.py               (Pydantic models)
|-- requirements.txt
|-- .env                     (for OPENAI_API_KEY)
```

Please generate the complete, runnable code for all the specified Python files. Include comments explaining the key parts of the logic, especially the AI prompt construction and the database query for similarity search.