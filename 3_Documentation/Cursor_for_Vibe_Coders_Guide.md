# CURSOR FOR VIBE CODERS
## (Dan's Non-Technical Reference)

---

## WHAT IS VIBE CODING?

You focus on **WHAT** you want to build, not **HOW** to code it.  
Claude (AI) handles the syntax, the debugging, and the technical details.  
You stay in "architect mode" - describing intent, making decisions, approving changes.

---

## THE 3 CURSOR FEATURES YOU ACTUALLY NEED

### **1. COMPOSER MODE** (Your Primary Tool)
**What it does:** Multi-file editing with natural language  
**How to use:** Press `Ctrl+I` → Describe what you want → Accept changes

**Examples:**
- "Add error handling to the reactivation script"
- "Update both launch and preview scripts to use the new Calendly URL"
- "Create a new script that pulls customer data from Odoo and exports to CSV"

**Why it's powerful:** You never copy-paste. You never manually edit code. You just describe and approve.

---

### **2. CODEBASE SEARCH** (@Codebase)
**What it does:** Finds code by meaning, not just filename  
**How to use:** Type `@Codebase` in chat → Ask your question

**Examples:**
- `@Codebase where do we update the last reactivation date?`
- `@Codebase show me all code that calls the Workiz API`
- `@Codebase do we have any code that formats dates?`

**Why it's powerful:** You don't need to remember where you put things. Just ask.

---

### **3. CHAT WITH CONTEXT** (File References)
**What it does:** Reference specific files in conversation  
**How to use:** Type `#filename` in chat

**Examples:**
- "Look at #odoo_reactivation_launch.py and explain what line 191 does"
- "Compare #odoo_reactivation_launch.py and #odoo_reactivation_preview.py - what's different?"

**Why it's powerful:** Claude knows exactly what you're talking about. No ambiguity.

---

## FEATURES YOU DON'T NEED (As a Non-Coder)

### ❌ **Terminal Commands**
- You don't need to learn command-line syntax
- If you need to run Python scripts, just ask Claude: "Run this script for me"

### ❌ **Git Version Control**
- Advanced feature for professional developers
- Your Odoo scripts are backed up in your folder structure

### ❌ **Debugging Tools**
- Breakpoints, stack traces, etc. are for hardcore coders
- When something breaks, just tell Claude: "This isn't working, fix it"

### ❌ **Multi-Cursor Editing**
- Manual text manipulation
- Let Composer do it for you with natural language

### ❌ **Extensions/Plugins**
- You don't need to customize Cursor
- The default setup is perfect for vibe coding

---

## YOUR TYPICAL WORKFLOW

### **PLANNING PHASE:**
1. Discuss idea with Claude in Chat
2. Ask questions, explore options
3. Get Claude's architectural recommendations

### **BUILD PHASE:**
1. Press `Ctrl+I` (Composer)
2. Describe what you want built
3. Review the changes Claude made
4. Click "Accept" or "Reject"
5. Test it

### **DEBUG PHASE:**
1. Copy error message into Chat
2. Claude explains what went wrong
3. Press `Ctrl+I`: "Fix this error"
4. Accept changes
5. Test again

### **MAINTENANCE PHASE:**
1. `@Codebase where did we handle X?`
2. Press `Ctrl+I`: "Update this to do Y instead"
3. Accept changes

---

## THE ONLY KEYBOARD SHORTCUTS YOU NEED

| Shortcut | What It Does | When to Use |
|----------|-------------|-------------|
| **Ctrl+I** | Open Composer | When you want to build/edit code |
| **Ctrl+L** | New Chat | When you want to start fresh topic |
| **Ctrl+P** | Find File | When you need to open a specific file |
| **Ctrl+Shift+F** | Search All Files | When you need to find specific text |

---

## THE ODOO WORKFLOW (Your Specific Use Case)

### **1. Edit Odoo Server Action Scripts:**
- Open `1_Active_Odoo_Scripts/odoo_reactivation_launch.py` in Cursor
- Press `Ctrl+I`: "Add a check to prevent sending reactivations more than once per month"
- Accept changes
- Copy the updated code → Paste into Odoo UI

### **2. Build New Automation:**
- Press `Ctrl+I`: "Create a new script that finds customers who haven't booked in 6 months"
- Accept changes
- Test it
- Deploy to Odoo

### **3. Debug Zapier Issues:**
- Paste error message in Chat
- Claude explains the problem
- Press `Ctrl+I`: "Fix the JSON formatting for Zapier"
- Accept changes
- Test in Zapier

---

## THE VALUE PROPOSITION

**What you're paying $20/month for:**
- Multi-file editing without copy-paste
- Intelligent code search
- Context-aware AI that remembers your project
- 200K token conversations (hours of work without losing track)

**What you're NOT paying for:**
- A text editor (VS Code is free)
- Git hosting (GitHub is free)
- Terminal access (PowerShell is free)

**The real product:** A vibe coding workflow where you describe intent and Claude handles implementation.

---

## WHEN TO USE CURSOR VS. GEMINI

### **Use Cursor (Claude) for:**
- Writing/editing Python code
- Building Odoo Server Actions
- Multi-file projects
- Complex debugging

### **Use Gemini for:**
- Google Sheets/Docs automation
- Gmail integration
- Google Calendar workflows
- Research and learning

### **Use Gemini Side Panel for:**
- Watching you work in other apps (Cal.com, Calendly)
- Duplicating configurations between apps

---

## FINAL TIP: THE "PLANNING SESSION" RITUAL

**Once a week (or before major features):**
1. Open Chat with Claude
2. Say: "Let's do a planning session"
3. Describe your goal at high level
4. Claude asks clarifying questions
5. Claude proposes architecture
6. You approve or iterate
7. **THEN** start building with Composer

**Why this matters:** Vibe coding is fast, but messy if you don't plan. Spend 20 minutes planning to save 2 hours of rework.

---

## YOUR NEXT STEPS

1. ✓ Workspace organized into folders
2. ⏳ Test Composer mode (`Ctrl+I`)
3. ⏳ Test Codebase Search (`@Codebase`)
4. ⏳ Do Phase 3 planning session
5. ⏳ Build Phase 3 with Composer

---

**Remember:** You're not learning to code. You're learning to architect systems and let AI handle the implementation. That's vibe coding.

---
*Last Updated: February 3, 2026*
