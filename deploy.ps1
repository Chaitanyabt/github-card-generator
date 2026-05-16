# Deployment script for GitHub Dev Card Generator
# Ensure you have gcloud installed and are logged in: gcloud auth login

$PROJECT_ID = "gfg-496514"
$REGION = "us-central1"
$GEMINI_KEY = "AIzaSyCLcBQe_I78Fr9e_CI7EooA4LUo8d_5mkU"

Write-Host "Starting deployment to Project: $PROJECT_ID..."

# 1. Deploy Backend
Write-Host "Deploying Backend (github-card-backend)..."
gcloud run deploy github-card-backend `
  --source ./backend `
  --region $REGION `
  --allow-unauthenticated `
  --port 8080 `
  --memory 512Mi `
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GEMINI_API_KEY=$GEMINI_KEY" `
  --project $PROJECT_ID

if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend deployment failed."
    exit $LASTEXITCODE
}

# 2. Get Backend URL
$BACKEND_URL = gcloud run services describe github-card-backend --region $REGION --format "value(status.url)" --project $PROJECT_ID
Write-Host "Backend live at: $BACKEND_URL"

# 3. Deploy Frontend
Write-Host "Deploying Frontend (github-card-frontend)..."
gcloud run deploy github-card-frontend `
  --source ./frontend `
  --region $REGION `
  --allow-unauthenticated `
  --port 80 `
  --memory 256Mi `
  --set-env-vars "BACKEND_URL=$BACKEND_URL" `
  --project $PROJECT_ID

if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend deployment failed."
    exit $LASTEXITCODE
}

$FRONTEND_URL = gcloud run services describe github-card-frontend --region $REGION --format "value(status.url)" --project $PROJECT_ID

Write-Host "Deployment Complete!"
Write-Host "Frontend URL: $FRONTEND_URL"
Write-Host "Backend URL:  $BACKEND_URL"
