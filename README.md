# **FineTuned AI Chatbot with API Key Management and Rate Limiting**

## **Overview**
This project is a FastAPI-based application that provides an FinedTuned AI-powered chatbot. It includes robust features such as API key management, rate-limiting, error handling, and secure storage of sensitive data. Designed for developers, this project enables easy integration of AI chatbot functionality into applications while maintaining strict access control. It uses **Qwen3.2**, which use Architecture of transformers with RoPE, SwiGLU, RMSNorm, and Attention QKV bias with **38 Billion** Parametric Tokenization and support Context Length of Full **131,072** tokens.

---

## **Features**

### **1. AI-Powered Chatbot**
- Utilizes Fine Tuned HuggingFace Inference API to deliver AI-generated responses.
- Pre-configured with a **system prompt** to act as a knowledgeable assistant, specializing in data science, AI, and general knowledge.

### **2. API Key Management**
- Generates unique, one-time API keys for each user.
- Tracks and prevents the reuse of API keys.
- Restricts multiple API key generation requests from the same IP address.

### **3. Rate Limiting**
- Limits the number of requests per IP address using `slowapi`.
- Configured limits:
  - **100 requests/day** per IP.
  - **20 requests/minute** per IP.

### **4. Error Handling and Logging**
- Captures and logs:
  - HTTP request errors.
  - Invalid API key usage.
  - Unexpected server exceptions.
- Logs are stored in `app.log` for debugging and monitoring.

### **5. Secure Environment**
- Sensitive information, such as API keys, is stored in a `.env` file.
- `.gitignore` ensures `.env` and other sensitive files are excluded from version control.

---

## **API Endpoints**

### **1. Generate API Key**
- **URL:** `/generate_api`
- **Method:** `GET`
- **Description:** Generates a one-time API key for the requesting user based on their IP address.

### **2. Generate Response**
- **URL:** `/response
- **Method:** `GET`
- **Description:** Generates Response as Per systemprompt and Systemprompt context.


#### **Response Example for API key Generation**
```json
{
    "One Time API key": "1a2b3C4d5E6f7G8h9I0J1K2L3M4N5O6",
    "Generation Time": "2024-11-23 15:45:00",
    "!": "Don't share this secret API key."
}

#### **Input Format**
```json
{
    "system_prompt": "You are Machine learning Engineer, write your response in 100 words.",
    "message": "What is Linear Regression?",
    "tokens": 200
}
