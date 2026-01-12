
# Pirate Chatbot Using Gemini API

This is a fun Python project where you will create a **pirate-themed chatbot** that responds to user input in **pirate speak**, using **Google's Gemini API**.

The chatbot generates responses based on the **Gemini-1.5-flash** model from Google and is designed to be interactive. It allows users to chat and get creative pirate-style responses!

## Prerequisites

Before you start, you will need to:

1. **Create a Google Cloud Account** and set up access to the **Gemini API**.
2. **Install the required libraries** for Python.
3. **Set up your API key** and store it securely in a `.env` file.

## Setting Up Your Project

### 1. **Create a Gemini API Key**:
To use the **Gemini API**, you need to create an API key from **Google Cloud**. Follow these steps to create your API key:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new **project**.
3. Go to **APIs & Services** → **Credentials**.
4. Click **Create Credentials** → **API Key**.
5. Copy the API Key provided and store it securely. You will use this key in your project.

### 2. **Set Up Your Environment**:

1. Install Python (preferably **Python 3.x**).
2. Install the required Python packages (explained below).

### 3. **Create the `.env` File**:

Your **API Key** should not be hard-coded into the script for security reasons. Instead, we will use a `.env` file to store sensitive information like the API key. Here’s how you set it up:

1. In the root folder of the project, create a file named **`.env`**.
2. Add the following line to the `.env` file:

```env
API_KEY=your-gemini-api-key-here
```

Replace `your-gemini-api-key-here` with the API key you created earlier.

### 4. **Install Dependencies**:

You will need to install the following Python libraries:

- **google-generativeai**: The library to access the Gemini API.
- **python-dotenv**: To load environment variables from the `.env` file.

To install the required libraries, open a terminal and run:

```bash
pip install google-generativeai python-dotenv
```

Alternatively, you can create a **requirements.txt** (see below) and use the following command to install everything:

```bash
pip install -r requirements.txt
```

### 5. **Run the Project**:

1. Once you've installed the dependencies and set up the `.env` file, you can start the chatbot by running:

```bash
python gem.py
```

This will start an interactive loop where you can type your messages, and the chatbot will respond in pirate speak.

### 6. **Exit the Chat**:
To exit the chat, simply type `exit` and hit Enter.

---

## **requirements.txt**

```
google-generativeai
python-dotenv
```

---

## **Folder Structure Example**:

Your project folder should look like this:

```
/pirate-chatbot
    ├── gem.py              # Main Python script
    ├── .env                # Store the Gemini API key here
    ├── requirements.txt     # Python dependencies
    └── README.md           # Project documentation
```

---

## **Additional Notes**:

- The code uses the **Gemini API** to generate pirate responses. You can modify the **system message** if you want to adjust the style or personality of the chatbot.
- To experiment further, try integrating other APIs (e.g., weather, trivia, etc.) for even more creative outputs!
- This project is designed to practice basic Python skills, **API integration**, and understanding how **environment variables** work.

---

### 
