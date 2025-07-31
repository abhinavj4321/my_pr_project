# 🔧 Fix Data Reset Issue - Complete Guide

## 🚨 **Problem: Data Gets Reset Every Few Minutes**

Your deployed application loses data because:
- **SQLite database** is stored on ephemeral file system
- **Containers restart** every 15-30 minutes on free tiers
- **Fresh deployments** reset the database

## ✅ **Solution: Switch to PostgreSQL**

### **Step 1: Update Your Repository**

The files have been updated with PostgreSQL support. Commit and push:

```bash
git add .
git commit -m "Fix data reset: Add PostgreSQL support and production database setup"
git push origin main
```

### **Step 2: Add PostgreSQL Database**

#### **For Render.com:**
1. Go to your Render dashboard
2. Click "New" → "PostgreSQL"
3. Create database (free tier available)
4. Copy the **External Database URL**

#### **For Railway:**
1. Go to your project dashboard
2. Click "New" → "Database" → "PostgreSQL"
3. Copy the **DATABASE_URL**

#### **For Heroku:**
1. Go to your app dashboard
2. Click "Resources" tab
3. Add "Heroku Postgres" (free tier)
4. Copy the **DATABASE_URL** from config vars

### **Step 3: Set Environment Variables**

Add these environment variables to your deployment:

```env
# Required for PostgreSQL
DATABASE_URL=postgresql://username:password@host:port/database_name

# Security (generate a new secret key)
SECRET_KEY=your-new-secret-key-here

# Production settings
DEBUG=False
ALLOWED_HOSTS=your-app-domain.com,your-app-domain.onrender.com
```

#### **How to Add Environment Variables:**

**Render.com:**
1. Go to your web service
2. Click "Environment"
3. Add the variables above

**Railway:**
1. Go to your project
2. Click "Variables" tab
3. Add the variables

**Heroku:**
1. Go to app dashboard
2. Click "Settings" → "Config Vars"
3. Add the variables

### **Step 4: Redeploy**

After adding environment variables:
1. **Trigger a new deployment** (push to GitHub or manual deploy)
2. **Check deployment logs** for success messages
3. **Test your application** - data should now persist!

## 🔧 **Alternative Quick Fix (Temporary)**

If you can't set up PostgreSQL immediately, here's a temporary workaround:

### **Option A: Use a Persistent Volume (Platform Dependent)**

Some platforms offer persistent storage:
- Check if your platform supports persistent volumes
- Mount the volume to store the SQLite database

### **Option B: Database Backup/Restore**

Create a script to backup/restore data:

```python
# backup_data.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from student_management_app.models import *
import json

def backup_data():
    # Export data to JSON
    data = {
        'users': list(CustomUser.objects.values()),
        'students': list(Students.objects.values()),
        'staff': list(Staffs.objects.values()),
        # Add other models as needed
    }
    
    with open('backup.json', 'w') as f:
        json.dump(data, f, default=str)
    
    print("Data backed up successfully!")

if __name__ == "__main__":
    backup_data()
```

## 🎯 **Recommended Solution: PostgreSQL**

### **Why PostgreSQL?**
- ✅ **Persistent storage** - data never gets lost
- ✅ **Production ready** - designed for web applications
- ✅ **Free tiers available** on all major platforms
- ✅ **Better performance** than SQLite for web apps
- ✅ **Concurrent access** - multiple users can access simultaneously

### **Migration Steps:**
1. ✅ **Updated settings.py** - Now supports PostgreSQL via DATABASE_URL
2. ✅ **Updated build.sh** - Includes database setup
3. ✅ **Added setup script** - Creates admin user automatically
4. 🔄 **Add DATABASE_URL** - Set environment variable
5. 🔄 **Redeploy** - Push changes and redeploy

## 🚀 **After Fix - What to Expect**

### **✅ Data Will Persist:**
- Student records stay saved
- Staff information remains
- Attendance data is preserved
- QR codes and settings persist
- Admin accounts don't reset

### **✅ Better Performance:**
- Faster database queries
- Better concurrent user support
- More reliable for production use

## 🔍 **Troubleshooting**

### **If PostgreSQL Connection Fails:**
1. **Check DATABASE_URL format:**
   ```
   postgresql://username:password@host:port/database_name
   ```

2. **Verify database exists** on your platform

3. **Check deployment logs** for connection errors

### **If Data Still Resets:**
1. **Verify environment variables** are set correctly
2. **Check if DATABASE_URL** is being used (not SQLite)
3. **Look at deployment logs** for database errors

### **Test Database Connection:**
```python
# In Django shell
from django.db import connection
print(connection.settings_dict)
# Should show PostgreSQL, not SQLite
```

## 🎉 **Success Indicators**

You'll know it's fixed when:
- ✅ Data persists after app restarts
- ✅ Students/staff you add stay in the system
- ✅ Attendance records don't disappear
- ✅ Admin settings remain saved
- ✅ No more "fresh database" after deployments

---

**🚀 Follow these steps and your data will persist permanently!**
