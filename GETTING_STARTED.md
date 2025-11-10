# Getting Started Guide - Windows, macOS, Linux

## 🚀 Quick Start (3 Steps)

### **Step 1: Setup**

```bash
python setup.py
```

### **Step 2: Start Application**

Windows:

```cmd
start.bat
```

macOS/Linux:

```bash
python -m app.web
```

### **Step 3: Access Application**

Open your browser to: **http://localhost:5000**

## 📋 Detailed Setup Instructions

### **Prerequisites**

- Windows 10 or later / macOS / Linux
- Python 3.8 or higher
- Internet connection

### **Installation Steps**

1. **Open Command Prompt or PowerShell**

   - Press `Win + R`, type `cmd`, press Enter
   - Or press `Win + X`, select "Windows PowerShell"

2. **Navigate to project directory**

Windows (PowerShell/CMD):

```cmd
cd C:\path\to\CBA
```

macOS/Linux (Terminal):

```bash
cd /path/to/CBA
```

3. **Run automated setup**

```bash
python setup.py
```

4. **Start the application**
   Windows:

```cmd
start.bat
```

macOS/Linux:

```bash
python -m app.web
```

## 🎯 Using the Application

### **First Time Users**

1. **Click "Use sample"** on the main page
2. **Click "Run Investigation"**
3. **View the comprehensive report**
4. **Click on agents in the audit trail** to see detailed descriptions

### **Advanced Users**

1. **Upload your own files (optional)**:
   - PACS.004 (return message)
   - PACS.008 (original payment)
   - Note: The app always uses built-in customers.csv
2. **Configure parameters** (Index page toggles):
   - Channel Type (Non-branch)
   - Sanctions Status
3. **Run investigation** and analyze results

## 🔍 Understanding the Results

### **Transaction Details**

- UETR, End-to-End ID, Customer IBAN
- Return amount and currency
- Reason codes and descriptions

### **Eligibility Assessment**

- 20+ comprehensive checks
- Pass/Fail/Info status indicators
- Detailed verification results

### **Enhanced Refund Processing**

- Complete 8-step foreign currency flow
- Visual step-by-step progress
- Actual processing results

### **Agent Flow**

- Interactive SVG diagram
- Clickable agent nodes
- Visual processing flow

### **Audit Trail**

- Chronological event log
- Clickable agent descriptions
- Detailed verification values

## 🛠️ Troubleshooting

### **Common Issues**

#### **"Python not found"**

```bash
# Install Python
# Windows (Winget): winget install Python.Python.3.11
# macOS (Homebrew): brew install python
# Ubuntu/Debian:     sudo apt-get install -y python3 python3-venv
```

#### **"Port 5000 already in use"**

```cmd
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace <PID> with actual process ID)
taskkill /PID <PID> /F
```

#### **"Virtual environment issues"**

Windows:

```cmd
rmdir /s .venv
python setup.py
```

macOS/Linux:

```bash
rm -rf .venv
python setup.py
```

#### **"Missing dependencies"**

Windows:

```cmd
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### **Browser Issues**

- **Clear browser cache** (Ctrl + Shift + Delete)
- **Try different browser** (Chrome, Edge, Firefox)
- **Check browser console** (F12) for errors
- **Disable browser extensions**

### **Performance Issues**

- **Close other applications**
- **Check available memory** (Task Manager)
- **Restart the application**

## 📊 Sample Data

The application includes comprehensive sample data:

### **PACS.004 (Return Message)**

- **UETR**: e8b2f9c4-0e7d-4b8a-8c7c-4f5d6e7f8a9b
- **Amount**: EUR 970.00
- **Reason**: AC04 (Account Closed)
- **Customer**: DE89370400440532013000

### **PACS.008 (Original Payment)**

- **UETR**: e8b2f9c4-0e7d-4b8a-8c7c-4f5d6e7f8a9b
- **Amount**: EUR 1000.00
- **Customer**: DE89370400440532013000

### **Customer Registry**

- **Account Holder**: Original Creditor Name
- **IBAN**: DE89370400440532013000
- **Status**: ACTIVE
- **Currency**: EUR

## 🎓 Learning Path

### **Beginner**

1. Run sample investigation
2. Explore the main report sections
3. Click on audit trail agents
4. Understand eligibility assessment

### **Intermediate**

1. Upload custom PACS messages
2. Modify customer registry
3. Test different scenarios
4. Analyze agent flow diagram

### **Advanced**

1. Modify API mockup responses
2. Customize eligibility criteria
3. Extend agent functionality
4. Add new processing steps

## 🔧 Development

### **Project Structure**

```
CBA/
├── app/
│   ├── agents/           # Agent implementations
│   ├── utils/            # Utilities and mockups
│   ├── templates/        # Web UI templates
│   ├── graph.py          # LangGraph workflow
│   └── web.py            # Flask application
├── samples/              # Sample data
├── runs/                 # Generated reports
└── requirements.txt      # Dependencies
```

### **Key Files**

- **`app/agents/refund.py`**: Main refund processing with 8-step enhanced flow
- **`app/utils/api_mockups.py`**: API mockup services
- **`app/templates/report.html`**: Comprehensive report template
- **`app/graph.py`**: LangGraph workflow definition

### **Customization**

- **Modify eligibility criteria** in agent implementations
- **Update API mockup responses** in `api_mockups.py`
- **Customize UI templates** in `templates/`
- **Add new agents** by extending the workflow

## 📞 Support

### **Getting Help**

1. **Check this guide** for common issues
2. **Review the README.md** for detailed information
3. **Examine the audit trail** for processing details
4. **Check browser console** (F12) for frontend errors

### **Reporting Issues**

- **Describe the problem** clearly
- **Include error messages** if any
- **Specify your Windows version**
- **Provide steps to reproduce**

## 🎉 What's Next?

### **Explore Features**

- ✅ Complete 8-step enhanced refund flow
- ✅ Comprehensive eligibility assessment
- ✅ Visual agent flow diagram
- ✅ Detailed audit trail with agent descriptions
- ✅ API mockup system for testing
- ✅ Professional web interface

### **Try Different Scenarios**

- Test with different currencies
- Modify customer account status
- Change FX loss amounts
- Test various return reason codes

### **Extend Functionality**

- Add new eligibility checks
- Implement additional agents
- Create custom API integrations
- Enhance the user interface

---

**Ready to dive in? Run the setup and start exploring!** 🚀
