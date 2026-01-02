### **Nepal Justice Weaver** 
---
Making the **three core features** (Law Explanation via RAG, Bias-Free Letter Generation, and Bias Auditing via EquityLens) **independent yet interconnected** creates a flexible, user-friendly platform. Users can access any feature alone or let the AI guide them through a seamless flow (e.g., explanation → detect need for letter → generate bias-free version).

This modular approach strengthens the hackathon MVP: It's easier to build/test separately, but the connections make it feel intelligent and impactful.

**Key Real-World Context (for Authentic Demo):**
- Nepal's citizenship laws (Constitution Article 11, Citizenship Act 2006 with amendments) still have subtle gender biases: Easier via father's lineage; mothers often need extra declarations if father is "unidentified."
- Common bureaucratic need: Formal applications/letters to District Administration Offices (DAO) for citizenship certificates.
- Templates: Often include placeholders for "father's name," which can be biased—our tool can flag and rewrite to "parent's name" or neutral alternatives.

#### Three Independent Modes + Smart Connections

1. **Mode 1: Bias Auditing Only**
   - User uploads an existing document (PDF/Word/Docx, e.g., a drafted letter or policy).
   - AI scans for biases (gender, socioeconomic, etc.—tuned for Nepal contexts like paternal assumptions).
   - Outputs: Highlighted report, bias score, explanations, and suggested rewrites.
   - **Interactive Twist**: "Bias detected! Do you want a bias-free updated version?" → If yes → Generate revised document (using generation module).

2. **Mode 2: Letter Generation Only**
   - User selects a template (e.g., "Citizenship Application," "Complaint to DAO") or describes need.
   - Inputs personal details (name, situation).
   - AI fills template → **Automatically runs bias audit** → Outputs a **guaranteed bias-free letter** (with fixes applied).
   - Download as Docx/PDF.

3. **Mode 3: Law Explanation Only (RAG Standalone)**
   - User describes situation in natural language (e.g., "I need citizenship for my child but no father" in English (for now)).
   - AI retrieves relevant laws (from our vector DB of Constitution, Citizenship Act, Muluki Civil Code snippets).
   - Explains in simple, plain language.
   - **No proactive linking here** unless needed.

**Smart Connections (Conversational Flow):**
- The app uses a **chat-like interface** to detect intent and offer cross-feature help.
- Example Full Flow (Citizenship Scenario):
  1. User: "I need citizenship but no father" → Mode 3: Explains law (e.g., "Per Nepal Constitution Article 11 and recent amendments, a child can get citizenship via mother's lineage with declarations if father unidentified. You may need to submit an application to DAO with birth certificate and affidavit.").
  2. AI proactively: "This often requires a formal application letter to the District Administration Office. Would you like me to generate one for you?"
  3. If yes → Switch to Mode 2: Ask for details (child's name, mother's details, district) → Generate letter using template.
  4. Auto-run Mode 1: Audit for biases (e.g., flag any "father required" fields) → Apply fixes → "Here's your bias-free letter, rewritten to use neutral language."

This makes it feel like a helpful AI assistant, not just separate tools!
