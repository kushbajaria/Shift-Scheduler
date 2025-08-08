# Deployment Guide

This guide covers how to deploy your Shift Scheduler application to various hosting platforms.

## Option 1: Heroku (Recommended)

Heroku is a popular platform-as-a-service that makes deployment easy.

### Step 1: Create a Heroku Account
1. Sign up at [heroku.com](https://signup.heroku.com/)
2. Install the Heroku CLI from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)

### Step 2: Deploy Your App
1. **Login to Heroku**
   ```bash
   heroku login
   ```

2. **Create a new Heroku app**
   ```bash
   heroku create your-shift-scheduler-app
   ```

3. **Set environment variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex())')
   ```

4. **Deploy your code**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push heroku main
   ```

5. **Initialize the database**
   ```bash
   heroku run python init_database.py
   ```

6. **Open your app**
   ```bash
   heroku open
   ```

### Step 3: Access Your App
- Your app will be available at `https://your-shift-scheduler-app.herokuapp.com`
- Login with username: `admin`, password: `admin123`

## Option 2: Render

Render is another excellent hosting platform with a free tier.

### Step 1: Create a Render Account
1. Sign up at [render.com](https://render.com)
2. Connect your GitHub account

### Step 2: Deploy Your App
1. Click "New +" and select "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `shift-scheduler`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### Step 3: Set Environment Variables
In the Render dashboard, add these environment variables:
- `FLASK_ENV`: `production`
- `SECRET_KEY`: Generate a secure secret key
- `PYTHON_VERSION`: `3.11.7`

### Step 4: Deploy
1. Click "Create Web Service"
2. Wait for the build to complete
3. Your app will be live at the provided URL

## Option 3: Railway

Railway offers easy deployment with a great developer experience.

### Step 1: Create a Railway Account
1. Sign up at [railway.app](https://railway.app)
2. Connect your GitHub account

### Step 2: Deploy Your App
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Railway will automatically detect it's a Python app

### Step 3: Set Environment Variables
In the Railway dashboard:
- `FLASK_ENV`: `production`
- `SECRET_KEY`: A secure secret key

### Step 4: Access Your App
Your app will be available at the provided Railway URL.

## Post-Deployment Steps

1. **Change Default Password**
   - Login with `admin`/`admin123`
   - Go to Profile > Change Password
   - Set a secure password

2. **Add Employees**
   - Use the "Manage Employees" section
   - Add your team members

3. **Generate Schedules**
   - Go to "View Schedules"
   - Set shift requirements
   - Click "Generate Schedule"

## Troubleshooting

### Database Issues
If you see database errors:
```bash
# For Heroku
heroku run python init_database.py

# For other platforms
# Access the platform's shell and run the same command
```

### Environment Variables
Make sure these are set correctly:
- `FLASK_ENV=production`
- `SECRET_KEY=your-secure-key`
- `DATABASE_URL` (usually auto-set by hosting platforms)

### Build Failures
If builds fail, check:
1. All files are committed to Git
2. `requirements.txt` is in the root directory
3. Python version compatibility (we support 3.11+)

## Security Notes

- Always change the default admin password in production
- Use a strong, unique secret key
- Consider setting up HTTPS (most platforms enable this by default)
- Regularly update dependencies for security patches

## Support

If you encounter issues:
1. Check the application logs on your hosting platform
2. Verify all environment variables are set correctly
3. Ensure the database is properly initialized
