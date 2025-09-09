# AI Visual Product Search - React Frontend (Vite)

A modern and fast React application built with Vite that connects to the Django backend to perform AI-powered visual product searches.

## ⚡ Why Vite?

This frontend uses **Vite** instead of Create React App for:

- **Lightning Fast**: Instant dev server startup and HMR
- **Modern Tooling**: Native ES modules and optimized builds
- **Better DX**: Superior developer experience with TypeScript support
- **Smaller Bundle**: More efficient production builds

## 🚀 Features

- 🖼️ **Image Upload**: Beautiful drag & drop interface with preview
- 🔍 **AI Search**: Find similar products using computer vision
- 🎨 **Modern UI**: Built with shadcn/ui and Tailwind CSS
- 📱 **Responsive**: Works perfectly on all devices
- ⚡ **Super Fast**: Vite's instant HMR for development
- 🔄 **Smart Caching**: React Query for optimal data management

## 🛠️ Getting Started

### Prerequisites

- Node.js 18+ installed
- The Django backend running on `http://localhost:9000`

### Installation

1. Navigate to the react-frontend directory:

```bash
cd react-frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

4. Open [http://localhost:5173](http://localhost:5173) to view it in the browser.

## 📦 Scripts

- `npm run dev` - Start development server with HMR
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## 🎯 Usage

1. **Upload an Image**: Click the upload area or drag an image file
2. **Search**: Click "Find Similar Products" to search for similar items
3. **Browse Results**: View beautiful product cards with similarity scores
4. **Explore Details**: See object types, attributes, and overall styles
5. **Visit Source**: Click "View Original" to see the source product

## 🔌 API Integration

The app connects to the Django backend API at:

- **Endpoint**: `POST /api/products/find-similar/`
- **Base URL**: `http://localhost:9000`
- **Expected Response**: JSON with similar products and AI analysis

## 🏗️ Tech Stack

- **Vite 5** - Next generation frontend tooling
- **React 18** - Latest React with concurrent features
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Beautiful and accessible UI components
- **React Query (TanStack Query)** - Powerful data synchronization
- **Axios** - Promise-based HTTP client
- **Lucide React** - Beautiful and consistent icons

## 📁 Project Structure

```
src/
├── components/
│   ├── ui/                    # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── input.tsx
│   ├── ImageUpload.tsx        # Drag & drop image upload
│   ├── ProductCard.tsx        # Product display card
│   └── ProductSearch.tsx      # Main search interface
├── hooks/
│   └── useProductSearch.ts    # React Query hook
├── services/
│   └── api.ts                # API service and types
├── lib/
│   └── utils.ts              # Utility functions
├── App.tsx                   # Main app component
├── main.tsx                  # Vite entry point
└── index.css                 # Global styles with Tailwind
```

## 🎨 Design System

The app uses a consistent design system with:

- **CSS Variables**: Easy theming and customization
- **Tailwind Utilities**: Rapid UI development
- **shadcn/ui Components**: Pre-built, accessible components
- **Responsive Grid**: Adaptive layout for all screen sizes
- **Smooth Animations**: Hover effects and transitions

## 🔧 Configuration

### Vite Config

The app is configured with:

- TypeScript support
- React plugin with Fast Refresh
- Tailwind CSS integration
- Optimized build settings

### Tailwind Config

Custom design tokens for:

- Color palette (primary, secondary, accent, etc.)
- Border radius variables
- Typography scale
- Spacing system

## 🌐 Environment Setup

Make sure your Django backend is running:

1. Navigate to the architecture-ai directory:

```bash
cd ../architecture-ai
```

2. Activate virtual environment:

```bash
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Start Django server:

```bash
python manage.py runserver
```

The React app expects the backend at `http://localhost:9000`.

## 🚀 Production Build

```bash
npm run build
```

This creates an optimized build in the `dist/` folder with:

- Minified JavaScript and CSS
- Optimized assets
- Code splitting for better performance
- Modern browser targeting

## 🔍 Development

### Hot Module Replacement

Vite provides instant HMR - changes reflect immediately without losing state.

### Type Checking

TypeScript provides compile-time type checking for better developer experience.

### Linting

ESLint ensures code quality and consistency.

## 🤝 Backend Communication

The frontend communicates with the Django backend using:

- **FormData**: For file uploads
- **Multipart requests**: Proper image handling
- **Error handling**: User-friendly error messages
- **Loading states**: Visual feedback during API calls

## 📱 Responsive Design

The app works perfectly on:

- 📱 Mobile phones (320px+)
- 📱 Tablets (768px+)
- 💻 Laptops (1024px+)
- 🖥️ Desktops (1280px+)

## 🎯 Performance

- **Fast Initial Load**: Vite's optimized bundling
- **Efficient Updates**: React Query caching
- **Image Optimization**: Proper sizing and lazy loading
- **Code Splitting**: Reduced bundle sizes

## 🛠️ Troubleshooting

### Common Issues

1. **Port 5173 in use**: Vite will automatically use the next available port
2. **Backend not running**: Ensure Django server is on port 9000
3. **CORS issues**: Django backend includes CORS headers
4. **Build errors**: Check TypeScript types and imports

### Development Tips

- Use the browser's developer tools for debugging
- React Query DevTools available in development
- Tailwind CSS IntelliSense for better DX
- Hot reload preserves component state

This Vite-powered frontend provides a modern, fast, and developer-friendly experience while maintaining all the functionality of the original application! 🚀
