# Step-by-Step Guide: Creating Your .env File

## What is a .env File and Why Do We Need It?

A `.env` file is a configuration file that stores **environment variables** - sensitive settings and credentials that your application needs to run. 

### Why We Use .env Files:

1. **Security**: Keeps passwords, API keys, and secrets out of your code
2. **Flexibility**: Different values for local development vs. production
3. **Version Control Safety**: `.env` is in `.gitignore` - it never gets committed to GitHub
4. **Easy Configuration**: One place to change settings without editing code

### The Problem We Solved:

Before this change, your code had **hardcoded credentials**:
- Database password: `"Naruto6767momo"` in `app/database.py`
- Session secret: `"CHANGE_THIS_SECRET_KEY"` in `app/main.py`

These were visible to anyone who saw your code! Now they're safely stored in `.env` which is never committed.

---

## Step-by-Step Instructions

### Step 1: Copy the Template File

**What to do:**
```bash
cp .env.example .env
```

**Why:**
- `.env.example` is a **template** with placeholder values
- It's safe to commit to Git (no real secrets)
- `.env` is your **actual** file with real values
- `.env` is in `.gitignore` so it won't be committed

**On Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**On Windows (Command Prompt):**
```cmd
copy .env.example .env
```

---

### Step 2: Open .env in Your Text Editor

Open the `.env` file you just created. You should see:

```env
# Drum Dungeon Environment Variables
# Copy this file to .env and fill in your values
# NEVER commit .env to version control

# Data directory for practice data (JSON files as backup)
PRACTICE_DATA_DIR=/srv/practice-data

# Environment: local, staging, or production
ENV=local

# Database connection URL
# Format: mysql+pymysql://user:password@host:port/database
# For local development:
DATABASE_URL=mysql+pymysql://root:your_password@localhost/drum_dungeon
# For Docker/production:
# DATABASE_URL=mysql+pymysql://drum_dungeon_user:secure_password@db:3306/drum_dungeon

# Session secret key (REQUIRED)
# Generate a secure random key: python -c "import secrets; print(secrets.token_urlsafe(32))"
SESSION_SECRET_KEY=generate-a-secure-random-key-here-minimum-32-bytes

# Database root password (for initial setup only, used by create_db.py)
# Only needed for local development
DB_ROOT_PASSWORD=your_root_password_here
```

---

### Step 3: Fill in PRACTICE_DATA_DIR

**What it is:**
The directory where your application stores student data (JSON files as backup).

**What to set:**
- **Windows**: Use a path like `C:\Users\momch\drum-dungeon-devops\practice_data`
- **Linux/Mac**: Use a path like `/home/yourname/practice_data` or `/srv/practice-data`

**Example for Windows:**
```env
PRACTICE_DATA_DIR=C:\Users\momch\drum-dungeon-devops\practice_data
```

**Example for Linux:**
```env
PRACTICE_DATA_DIR=/srv/practice-data
```

**Why:**
- Your app needs to know where to store/read student data files
- This path is used throughout the application (see `app/config.py`)
- The directory will be created automatically if it doesn't exist

---

### Step 4: Set ENV

**What it is:**
Tells the application which environment it's running in.

**What to set:**
- `local` - For development on your computer
- `staging` - For testing before production
- `production` - For the live application

**For now, use:**
```env
ENV=local
```

**Why:**
- Different environments may have different behaviors
- Currently used to determine database connection settings
- Helps with debugging (you know which environment you're in)

---

### Step 5: Set DATABASE_URL (Most Important!)

**What it is:**
The connection string to your MariaDB/MySQL database.

**Format:**
```
mysql+pymysql://username:password@host:port/database_name
```

**For Local Development (if MariaDB is installed locally):**

1. **Check if MariaDB/MySQL is running:**
   ```bash
   # Windows (if MySQL is a service)
   # Check Services app or:
   mysql --version
   ```

2. **Set the URL:**
   ```env
   DATABASE_URL=mysql+pymysql://root:YOUR_ACTUAL_PASSWORD@localhost/drum_dungeon
   ```
   
   Replace `YOUR_ACTUAL_PASSWORD` with your MariaDB root password.

**Example:**
```env
DATABASE_URL=mysql+pymysql://root:MySecurePassword123@localhost/drum_dungeon
```

**If you don't have MariaDB installed yet:**
- You can leave this commented out for now
- The app will run in "JSON-only mode" (no database)
- Install MariaDB later and then set this

**Why:**
- Your application needs to connect to the database
- This is how SQLAlchemy knows where to connect
- Without this, the app falls back to JSON-only mode

---

### Step 6: Generate and Set SESSION_SECRET_KEY (Critical!)

**What it is:**
A secret key used to encrypt user sessions (login cookies). **This MUST be random and secret!**

**Why it's critical:**
- If someone knows this key, they can forge login sessions
- Must be different for each environment
- Must be long and random

**How to generate:**

1. **Open a terminal/command prompt**

2. **Run this Python command:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   
   **Or if you have Python 3:**
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Copy the output** (it will look like: `xK9mP2qR5vW8yZ1aB4cD7eF0gH3jK6lM9nP2qR5vW8yZ1aB4cD7eF0gH3jK6lM`)

4. **Paste it in .env:**
   ```env
   SESSION_SECRET_KEY=xK9mP2qR5vW8yZ1aB4cD7eF0gH3jK6lM9nP2qR5vW8yZ1aB4cD7eF0gH3jK6lM
   ```

**Important:**
- Generate a NEW key for each environment (local, staging, production)
- Never share this key
- If compromised, generate a new one immediately

---

### Step 7: Set DB_ROOT_PASSWORD (Optional for Local)

**What it is:**
The root password for MariaDB/MySQL. Only needed if you're running `create_db.py` locally.

**What to set:**
```env
DB_ROOT_PASSWORD=your_actual_root_password
```

**If you don't have MariaDB installed:**
- You can leave this as-is or remove it
- Only needed when creating the database for the first time

**Why:**
- Used by `create_db.py` to create the database
- Only needed once during initial setup
- Not used by the application itself (uses DATABASE_URL instead)

---

## Complete Example .env File

Here's what a complete `.env` file might look like for **local Windows development**:

```env
# Drum Dungeon Environment Variables
PRACTICE_DATA_DIR=C:\Users\momch\drum-dungeon-devops\practice_data

ENV=local

# Local MariaDB connection
DATABASE_URL=mysql+pymysql://root:MySecurePassword123@localhost/drum_dungeon

# Generated secure session key
SESSION_SECRET_KEY=xK9mP2qR5vW8yZ1aB4cD7eF0gH3jK6lM9nP2qR5vW8yZ1aB4cD7eF0gH3jK6lM

# MariaDB root password (for create_db.py)
DB_ROOT_PASSWORD=MySecurePassword123
```

---

## How Your Application Uses These Variables

### PRACTICE_DATA_DIR
- Used in `app/config.py` to set where data files are stored
- Used throughout the app to read/write student data
- **Required** - app will crash without it

### ENV
- Used in `app/config.py` to determine environment
- Currently used for database connection logic
- Defaults to `"local"` if not set

### DATABASE_URL
- Used in `app/database.py` to connect to MariaDB
- **Optional** - app runs in JSON-only mode without it
- Format must be exact: `mysql+pymysql://user:pass@host/db`

### SESSION_SECRET_KEY
- Used in `app/main.py` for session encryption
- **Required** - app will crash without it
- Must be at least 32 bytes (the generator creates 44 characters)

### DB_ROOT_PASSWORD
- Used in `create_db.py` to create the database
- **Optional** - only needed for initial setup

---

## Verification Steps

After creating your `.env` file:

1. **Check that .env is in .gitignore:**
   ```bash
   cat .gitignore | grep .env
   ```
   Should show: `.env`

2. **Test that variables are loaded:**
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('PRACTICE_DATA_DIR:', os.getenv('PRACTICE_DATA_DIR'))"
   ```
   
   **Note:** If you get an error about `dotenv`, you may need to install it:
   ```bash
   pip install python-dotenv
   ```
   
   Or the app loads them directly via `os.environ` (which is what we're using).

3. **Try running your app:**
   ```bash
   cd app
   python main.py
   ```
   
   Check for any errors about missing environment variables.

---

## Common Issues and Solutions

### Issue: "PRACTICE_DATA_DIR environment variable is not set"
**Solution:** Make sure `.env` file exists and `PRACTICE_DATA_DIR` is set correctly

### Issue: "SESSION_SECRET_KEY environment variable is required"
**Solution:** Generate a key using the Python command and add it to `.env`

### Issue: Database connection fails
**Solution:** 
- Check DATABASE_URL format is correct
- Verify MariaDB is running
- Check username/password are correct
- Make sure database exists (run `create_db.py`)

### Issue: .env file not being read
**Solution:**
- Make sure file is named exactly `.env` (not `.env.txt`)
- Check you're in the project root directory
- Some IDEs need to be restarted to pick up new .env files

---

## Security Reminders

1. ✅ **NEVER commit .env to Git** (it's in .gitignore)
2. ✅ **Use different values for each environment** (local, staging, production)
3. ✅ **Generate new SESSION_SECRET_KEY for each environment**
4. ✅ **Use strong passwords** for database
5. ✅ **Don't share .env files** via email, Slack, etc.
6. ✅ **Rotate secrets periodically** (especially if compromised)

---

## Next Steps

Once your `.env` file is set up:

1. Test the application locally
2. Set up MariaDB if you haven't already
3. Run `create_db.py` to create the database
4. Test database connectivity
5. Move on to Docker setup (which will use different .env values)

---

## Summary

**What you did:**
- Created `.env` from `.env.example`
- Filled in all required values
- Secured your application credentials

**Why it matters:**
- No more hardcoded passwords in code
- Easy to change settings without editing code
- Safe for version control
- Different configs for different environments

**What's next:**
- Test your application with the new .env file
- Set up MariaDB if needed
- Continue with Docker setup
