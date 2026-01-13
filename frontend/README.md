# AI Job Matcher - Frontend

Modern Next.js frontend for the AI-powered job recommendation platform.

## Features

- 📤 **Resume Upload** - Drag & drop PDF upload with validation
- 🎯 **Smart Matching** - Real-time job matching with AI explanations
- 📊 **Match Analytics** - Visual breakdown of match quality and scores
- 💡 **Skill Analysis** - See matching skills and areas to improve
- 🎨 **Modern UI** - Clean, responsive design with Tailwind CSS

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm installed
- Backend API running on `http://localhost:8000`

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create `.env.local` file:

```bash
cp .env.local.example .env.local
```

Update the API URL if needed:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx        # Root layout
│   ├── page.tsx          # Home page
│   └── globals.css       # Global styles
├── components/
│   ├── ResumeUpload.tsx  # Resume upload component
│   ├── JobMatches.tsx    # Job matches list
│   └── JobCard.tsx       # Individual job card
├── lib/
│   ├── api.ts           # API client
│   └── types.ts         # TypeScript types
├── public/              # Static assets
├── package.json         # Dependencies
├── tailwind.config.js   # Tailwind configuration
└── tsconfig.json        # TypeScript configuration
```

## Technology Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API requests
- **React Hooks** - Modern state management

## Key Features Explained

### Resume Upload Component
- PDF validation (type & size)
- Real-time upload progress
- Extracted skills preview
- Error handling

### Job Matching Dashboard
- Top 10 job recommendations
- Match quality indicators
- Similarity scores (0-100%)
- Skill gap analysis

### Job Cards
- Expandable details
- Visual skill matching
- Company information
- Detailed explanations

## API Integration

The frontend communicates with the FastAPI backend:

```typescript
// Upload resume
POST /resumes/upload

// Get job matches
GET /matches/{resume_id}?top_n=10
```

See [lib/api.ts](lib/api.ts) for complete API client implementation.

## Deployment

### Deploy to Vercel (Recommended)

1. Push code to GitHub
2. Import repository in Vercel
3. Set environment variable:
   - `NEXT_PUBLIC_API_URL`: Your backend API URL
4. Deploy!

### Manual Deployment

```bash
npm run build
npm start
```

## Customization

### Colors
Edit [tailwind.config.js](tailwind.config.js) to change the color scheme.

### API Endpoint
Update `.env.local` to point to your backend.

### Features
Add new components in the `components/` directory.

## Troubleshooting

**Issue**: API requests fail
- Ensure backend is running on correct port
- Check CORS configuration in backend
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`

**Issue**: Styling not working
- Run `npm install` to ensure Tailwind is installed
- Check `tailwind.config.js` content paths

## Screenshots

### Home Page
- Clean, modern landing page
- Resume upload interface
- Feature highlights

### Job Matches
- Ranked job recommendations
- Match quality scores
- Detailed explanations

### Job Details
- Full job descriptions
- Skill breakdown
- Gap analysis
