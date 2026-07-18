# start_adi_music.ps1
Write-Host "Starting Adi Music Player Servers..." -ForegroundColor Green

# Start Backend
Write-Host "Starting Python Backend on port 8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit -Command `"cd backend; .\venv\Scripts\Activate.ps1; uvicorn main:app --host 0.0.0.0 --port 8000`""

# Start Frontend
Write-Host "Starting React Frontend on port 5173..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit -Command `"cd frontend; npm run dev -- --open`""

Write-Host "Both servers are running in separate windows. Do not close those windows while listening to music!" -ForegroundColor Yellow
