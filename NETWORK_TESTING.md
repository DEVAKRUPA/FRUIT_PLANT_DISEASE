# Network Device Testing

Use these commands when testing the app from another phone or computer on the same Wi-Fi.

## Backend

```powershell
cd "F:\FP 2\backend"
..\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

## Frontend

Create `F:\FP 2\frontend\.env` with your laptop IP:

```env
REACT_APP_API_BASE_URL=http://YOUR_LAPTOP_IP:8000
```

Then start React:

```powershell
cd "F:\FP 2\frontend"
npm start
```

Open this URL from your phone:

```text
http://YOUR_LAPTOP_IP:3000
```

Manual image upload works over HTTP. Live camera access may not work from another device over HTTP because browsers require HTTPS or localhost for camera permissions. For camera testing on a phone, use an HTTPS tunnel or deploy the frontend with HTTPS.
