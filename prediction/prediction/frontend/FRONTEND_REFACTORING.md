# Frontend Refactoring - Professional Healthcare Web Application

## Overview
This document outlines the comprehensive refactoring of the React frontend for the AI Healthcare Decision Support System, transforming it into a professional-grade healthcare web application.

## Architecture & Component Structure

### Project Structure
```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   └── Navbar.js          # Navigation header with branding
│   │   └── ui/
│   │       ├── Button.js          # Reusable button component
│   │       ├── Card.js            # Reusable card container
│   │       └── InputField.js      # Form input with validation
│   ├── pages/
│   │   ├── Home.js                # Landing page
│   │   ├── Diagnosis.js           # Main prediction interface
│   │   └── [PatientProfile.js]    # Future enhancement
│   ├── services/
│   │   └── api.js                 # Backend API communication
│   ├── App.js                     # Root component with routing
│   ├── index.js                   # React entry point
│   └── index.css                  # Design system & all styles
├── package.json
├── tailwind.config.js
└── Dockerfile
```

## Key Improvements Made

### ✅ Issues Fixed

#### 1. **Backend Routing Connection** (CRITICAL)
- **Issue**: Flask blueprint not registered with `/api` prefix
- **Fixed**: Updated `backend/app.py` to register blueprint with `url_prefix='/api'`
- **Result**: Frontend now correctly connects to `http://127.0.0.1:5000/api/predict`

#### 2. **Form Validation Enhanced**
- Added numeric validation
- Added positive number validation
- Improved error message clarity
- Display all validation errors before submission

#### 3. **UI/UX Improvements**
- Professional healthcare color scheme (blue + white)
- Consistent spacing and typography
- Loading states with spinners
- Success feedback after predictions
- Better error display with contextual alerts
- Responsive design for all screen sizes

#### 4. **Code Quality**
- Added JSDoc comments for all components
- Improved component prop documentation
- Better error handling in API calls
- Proper accessibility attributes (aria-* labels)

### 📱 Component Details

#### **Navbar Component**
- Professional header with brand identity
- Heart icon indicating healthcare domain
- Navigation links with active state
- Sticky position for easy navigation
- Responsive mobile menu support

#### **Home Page**
- Engaging hero section with gradient backgrounds
- Feature cards explaining system benefits
- "How It Works" section with 4-step process
- Medical disclaimer banner
- Call-to-action button to diagnosis tool

#### **Diagnosis Page**
- Two-column layout (form + results)
- Patient Information section with all metrics
- Clinical metrics with units and hints:
  - Pregnancies (count)
  - Glucose (mg/dL)
  - Blood Pressure (mmHg)
  - Skin Thickness (mm)
  - Insulin (μU/ml)
  - BMI (kg/m²)
  - DPF (coefficient)
  - Age (years)
- Treatment section with prescription textarea
- Results display with risk indicators
- Confidence score with visual progress bar
- Medication recommendations as badges
- Clinical suggestions as checklist

#### **UI Components**

##### `InputField.js`
- Wraps native input with label
- Error message display
- Accessibility attributes (aria-invalid, aria-describedby)
- Required field indicator
- Customizable type, placeholder, and hints

##### `Button.js`
- Multiple variants (primary, secondary, danger)
- Loading state support with spinner animation
- Disabled state handling
- Accessibility attributes
- Customizable class names

##### `Card.js`
- Flexible container for grouped content
- Title and subtitle support
- CSS module class management
- Proper semantic HTML (section element)
- Content wrapper div

### 🎨 Design System

#### Color Palette
```
Primary Blue:        #1c7ed6
Primary Dark:        #1462ad
Primary Light:       #d9ebff
Success Green:       #1f9d55
Success Light:       #d4edda
Danger Red:          #d64545
Danger Light:        #f8d7da
Warning Amber:       #f59e0b
Background:          #f3f8ff
Surface:             #ffffff
Border:              #d8e7ff
Text:                #0f2942
Text Soft:           #486581
```

#### Typography
- Font Family: System UI stack (Segoe UI, Roboto, etc.)
- Heading Weight: 700-800
- Body Weight: 400-600
- Sizes: Responsive with `clamp()`

#### Spacing Scale
```
xs: 0.25rem   (4px)
sm: 0.5rem    (8px)
md: 1rem      (16px)
lg: 1.5rem    (24px)
xl: 2rem      (32px)
2xl: 3rem     (48px)
```

#### Border Radius
```
sm: 6px (inputs)
md: 10px (buttons)
lg: 16px (cards)
xl: 18px (hero card)
```

### 🔗 API Integration

#### Endpoint: `POST /api/predict`

**Request:**
```json
{
  "features": [
    0,      // pregnancies
    140,    // glucose (mg/dL)
    90,     // blood pressure (mmHg)
    0,      // skin thickness (mm)
    0,      // insulin (μU/ml)
    25.5,   // BMI (kg/m²)
    0.5,    // DPF coefficient
    45      // age (years)
  ],
  "prescription": "Metformin 500mg twice daily"
}
```

**Response:**
```json
{
  "risk": "high",           // "low" or "high"
  "confidence": 0.85,       // 0.0 - 1.0
  "matched_drugs": ["Metformin", "Insulin"],
  "suggestions": ["Monitor blood glucose regularly", "Increase physical activity"]
}
```

### 📋 Form Validation Rules

1. **All fields required** - Empty field check
2. **Numeric validation** - Must be valid numbers
3. **Positive numbers** - No negative values
4. **Prescription required** - Cannot be empty
5. **Real-time error clearing** - Errors disappear as user corrects
6. **Form-level validation** - All errors shown before submission

### 🎯 Responsive Design

#### Breakpoints
- **Mobile**: < 640px
- **Tablet**: 640px - 980px
- **Desktop**: > 980px

#### Adjustments
- Single-column layout on mobile
- Sticky form card only on desktop
- Stack buttons vertically on small screens
- Flexible grid with auto-fit
- Touch-friendly button sizes

### ♿ Accessibility Features

1. **Semantic HTML**
   - Proper heading hierarchy (h1, h2, h3, h4)
   - Section elements for logical grouping
   - Form labels with htmlFor associations

2. **ARIA Attributes**
   - `aria-invalid` for error states
   - `aria-describedby` for error descriptions
   - `aria-busy` for loading states
   - `aria-label` for navigation

3. **Keyboard Navigation**
   - Tab order follows visual flow
   - Focus states on all interactive elements
   - Enter key submit support

4. **Color Contrast**
   - WCAG AA compliant color combinations
   - Not relying on color alone for meaning
   - Red + green colorblind friendly patterns

5. **Reduced Motion**
   - Respects `prefers-reduced-motion` preference
   - Disables animations for users who request it

## File Connections & Data Flow

### Route Flow
```
App.js
├── / (Home page)
│   └── Home.js
│       ├── Button → navigates to /diagnosis
│       ├── Card × 3 (Features)
│       └── Card × 4 (How It Works)
└── /diagnosis (Prediction page)
    └── Diagnosis.js
        ├── Form Card (Left column)
        │   ├── InputField × 8 (Metrics)
        │   └── Button (Predict)
        └── Results Card (Right column)
            └── Results Display
```

### Data Flow: Form Submission
```
Diagnosis.js
  ↓ User enters data & clicks Predict
  ↓ validateForm() checks all rules
  ↓ If valid, predictAPI() called
  ↓ api.js sends POST to backend
  ↓ Backend: /api/predict endpoint
  ↓ Response with prediction data
  ↓ setResult() updates state
  ↓ Results render in Card
```

### Error Handling Flow
```
API Error
  ├── Network unreachable → "Service unreachable" message
  ├── Invalid response → Display error from backend
  ├── Form validation error → Show field-level errors
  └── Success → Display results in card
```

## State Management

### Diagnosis.js State
```javascript
features          // Object: patient metrics
prescription      // String: current medication
result            // Object: prediction response
errors            // Object: field validation errors
loading           // Boolean: API call in progress
apiError          // String: API error message
submitSuccess     // Boolean: successful prediction
```

### State Updates
- User input → `handleChange()` updates features
- Form submission → `validateForm()` & `handleSubmit()`
- API response → `setResult()` displays prediction
- Clear form → `handleClearForm()` resets all state

## Development & Building

### Prerequisites
```bash
node >= 14.0.0
npm >= 6.0.0
```

### Install Dependencies
```bash
npm install
```

### Start Development Server
```bash
npm start
# Starts on http://localhost:3000
# Auto-reloads on file changes
```

### Build for Production
```bash
npm run build
# Creates optimized build in /build directory
```

### Docker Build & Run
```bash
docker build -t healthcare-frontend .
docker run -p 3000:3000 healthcare-frontend
```

## Backend Requirements

The frontend requires the backend running on `http://127.0.0.1:5000`:

```bash
cd backend
python -m pip install -r requirements.txt
python app.py
# Backend will be available at http://127.0.0.1:5000/api
```

### Backend Fix Applied
File: `backend/app.py`
```python
# Before (INCORRECT)
app.register_blueprint(diagnosis_bp)

# After (CORRECT)
app.register_blueprint(diagnosis_bp, url_prefix='/api')
```

## Styling Approach

### CSS Organization
- Single `index.css` file with design system
- CSS custom properties (variables) for theming
- Mobile-first responsive approach
- Utility-like classes for common patterns

### CSS Structure
1. **Design System** - Color vars, spacing, typography
2. **Global Styles** - Base tags, resets
3. **Layout** - Container, app shell, main content
4. **Components** - Navbar, Card, Button, Form inputs
5. **Pages** - Home, Diagnosis specific styles
6. **Utilities** - Flexbox, grid helpers
7. **Responsive** - Media queries for breakpoints
8. **Accessibility** - Reduced motion, dark mode, print

## Future Enhancements

1. **Additional Pages**
   - PatientProfile.js - View patient history
   - Recommendations.js - Detailed drug info
   - Dashboard.js - Analytics overview

2. **Feature Additions**
   - Patient history tracking
   - Export predictions as PDF
   - Multi-language support
   - Dark mode toggle
   - User authentication

3. **Performance**
   - Code splitting by route
   - Image optimization
   - Lazy loading components
   - Service worker for offline support

4. **Testing**
   - Jest unit tests
   - React Testing Library integration tests
   - E2E tests with Cypress

## Troubleshooting

### Backend Not Connecting
- Ensure backend is running on `http://127.0.0.1:5000`
- Check CORS is enabled in Flask (already enabled)
- Verify `/api` prefix in Flask app registration
- Check network tab in browser DevTools

### Form Not Validating
- Check browser console for JavaScript errors
- Verify all InputField components receive error props
- Test with invalid input (empty fields, negative numbers)

### Styling Issues
- Clear browser cache (or hard refresh Ctrl+Shift+R)
- Verify all CSS variables are defined
- Check for conflicting CSS in build tools

## Production Deployment

### Environment Setup
1. Set `REACT_APP_API_URL` environment variable
2. Build optimized production bundle
3. Serve with appropriate headers (CORS, CSP)
4. Use HTTPS in production
5. Configure CORS to accept production backend URL

### Performance Checklist
- ✓ CSS minified
- ✓ JavaScript minified
- ✓ Images optimized
- ✓ Font files loaded efficiently
- ✓ No console errors/warnings
- ✓ Responsive design tested
- ✓ Accessibility tested with screen reader

## Support & Documentation

For backend API documentation, see `backend/README.md`
For deployment information, see main project `README.md`
For style customization, modify CSS custom properties in `index.css`
