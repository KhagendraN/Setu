### Nepal Justice Weaver – Implementation Workflow 

1. Law Explanation (RAG-based)  
2. Bias-Free Letter Generation  
3. Bias Auditing (EquityLens)  

The goal is to allow users to enter via any door while enabling smart, conversational connections between features.

#### Phase 1: Preparation & Data Collection (3-4 hours)
- Collect and prepare core data assets:
  - Download 8-12 key Nepali legal documents in English: Constitution of Nepal, Citizenship Act 2006 (with amendments), Muluki Civil Code sections on citizenship/inheritance/property, sample government notifications.
  - Gather or create 4-6 standard official letter templates in editable format (e.g., citizenship application, affidavit for unidentified father, land-related complaint, general application to DAO or ward office). Ensure placeholders are neutral where possible.
  - Prepare a small set of Nepal-specific bias examples (e.g., paternal language in citizenship forms, urban-centric assumptions) to guide the bias model. Or we have alternative (pre-trained model)

#### Phase 2: Build Individual Modules Separately (10-12 hours total)
Work in parallel.

**Module A: Law Explanation (RAG Pipeline)**
- Extract and chunk text from collected legal PDFs.
- Create embeddings and build a local vector database.
- Set up retrieval chain with a local or API-based LLM (we may prefer API-based) for generating simple, plain-language explanations.
- Add bilingual capability (Future extension).

**Module B: Bias-Free Letter Generation**
- Load letter templates.
- Build a form-based or natural-language input system to collect user details.
- Create a filling mechanism that inserts user data into the selected template.
- Automatically route every generated letter through the bias auditor (Module C) before final output.

**Module C: Bias Auditing (EquityLens)**
- Load or fine-tune a lightweight bias detection model (using general fairness datasets + Nepal-specific examples).
- Develop sentence/document-level scanning for common bias types (gender, socioeconomic, paternal/maternal assumptions, urban-rural disparity).
- Generate highlighted reports, bias scores, explanations, and suggested neutral rewrites.
- Add an interactive option: “Apply fixes automatically to create a bias-reduced version?”

#### Phase 3: Create User Entry Points & Modes (4-5 hours)
Design three clear, independent access modes in the UI:

1. **Explain Law Mode**
   - Text input or chat box for describing a situation.
   - Outputs simple explanation of relevant laws.

2. **Generate Letter Mode**
   - Dropdown or keyword detection to select template type.
   - Guided questions or free-text input for personal details.
   - Always produces a bias-audited, bias-reduced letter.

3. **Audit Document Mode**
   - File upload (PDF/Word/Text) of existing letter or policy draft.
   - Displays bias report with highlights and suggestions.
   - Offers: “Generate a bias-free updated version?” → If accepted, rewrites using generation module.

#### Phase 4: Add Smart Interconnections (Conversational Flow) (4-6 hours)
- Implement a central chat-style interface that can handle natural user queries.
- Add intent detection logic to route queries to the correct starting module.
- Build proactive suggestions:
  - After a law explanation, check if the retrieved law typically requires a formal letter → Offer: “Would you like me to generate the required application letter?”
  - After bias auditing an uploaded document, offer automatic rewriting.
  - After letter generation, always show a summary of bias checks performed and fixes applied.
- Use session state to remember context (e.g., user details from explanation phase can pre-fill letter generation).

#### Phase 5: UI/UX & Demo Polish (4-5 hours)
- Create a clean main interface with:
  - Tabs or buttons for quick access to the three modes.
  - A prominent central chat box for natural, guided conversations.
- Add language toggle (English/Nepali - aaile lai dekhauna matra).
- Include clear disclaimers: “This tool provides information and templates for educational purposes; it is not legal advice.”
- Prepare 3 strong demo scenarios:
  1. Single mother seeking child citizenship (explanation → proactive letter offer → bias-free generation).
  2. User uploads biased existing letter → audit → accepts rewrite.
  3. Direct request for a neutral complaint letter.

#### Phase 6: Testing & Final Touches (2-3 hours)
- Test all independent modes thoroughly.
- Test full connected flows end-to-end.
- Ensure smooth handoffs between modules.
- Record a clear 2-3 minute demo video highlighting modularity and intelligent connections.
