---
name: user-profile
description: CORE SKILL. Always active. Contains the user's (Miguel Ferreira de Araujo) professional profile, technical preferences, and background (Python, Django, Education, Maker). Consult this skill to align all code, explanations, and architectural decisions with his specific expertise and style.
---

# User Profile: Miguel Ferreira de Araujo

## 👤 About
**Software Engineer in Training** with a strong focus on Back-end development, Automation, Tech Education, and Practical Impact.
- **Role**: Educator & Developer (ex-Professor at Softex FAP).
- **Community**: Member of "Hackers do Bem" (Ethical Hacking, Maker Culture).
- **Style**: Combines technical depth with educational clarity. Values robust, applicable code.

## 🛠️ Technical Stack & Expertise

### 🐍 Back-End (Strongest)
- **Languages**: Python (Primary).
- **Frameworks**: Django (Deep expertise - taught from basic to deploy), Flask.
- **Skills**: API Construction, Authentication, Database Integration, Cloud Deployment.

### 🌐 Front-End & Full-Stack
- **Languages**: HTML, CSS, JavaScript, TypeScript.
- **Frameworks**: Modern Web Libraries (e.g., React/Next.js context implied by "modern web"), Responsive Design.
- **Experience**: Functional interfaces, integration with back-end.

### 🤖 Maker & Automation
- **Hardware**: Arduino, C++, Sensors, Actuators.
- **Tools**: Tinkercad (Simulation), Physical Circuitry.
- **Focus**: Robotics, Physical Control, IoT, Educational Simulators.

## 📂 Portfolio Highlights (Context)
- **GitHub**: [github.com/MiguelFAraujo](https://github.com/MiguelFAraujo)
- **Key Projects**:
    - `Softex_BackEnd_Python`: Backend proficiency, APIs.
    - `spacex-launches`: TypeScript/Modern Web.
    - C++/Arduino Repos: Electronics & Automation logic.

## 🎓 Preferences for AI Interaction
1.  **Educational Tone**: When explaining concepts, keep the "Teacher" persona in mind—clear, structured, and didactically sound.
2.  **Code Quality**: Prioritize "robust and applicable" code. Miguel values ethics and best practices.
3.  **Context Awareness**: If a task involves Python/Django, assume a high level of proficiency. If it involves Front-end, provide more scaffolding if needed, but respect his Full-Stack capability.
4.  **Maker/IoT**: Be ready to switch contexts to C++/Hardware logic if the task relates to physical computing.

## 🚨 Current Project Status (Jan 2026)
- **Project**: RoboTutor (Django + Google AI).
- **SDK Migration**: Migrated from `google-generativeai` to `google-genai` (v1.0+) to fix deprecation warnings.
- **Database**:
    - **Local**: Using SQLite (`db.sqlite3`). `DATABASE_URL` in `.env` is commented out.
    - **Production**: Uses Neon PostgreSQL (requires uncommenting `.env`).
- **Auth & Ports**:
    - **Port**: Fixed to `8095` (`http://localhost:8095`) to avoid Chrome HSTS redirect loops on 8000/8080.
    - **Google Login**: Configured globally in `settings.py` (deleted specific DB `SocialApp` entries).
    - **Callback URI**: `http://localhost:8095/accounts/google/login/callback/`.
- **Theme**: "I, Robot" Asimov Theme (Industrial Metals, Gear Animations) implemented.
