# Insulin Simulator App

This Insulin Simulator App is designed to assist both newly diagnosed diabetics and those looking for a more streamlined approach to insulin management. It leverages AI to provide personalized insulin dosage recommendations based on various inputs, offering a user-friendly interface to experiment with insulin to carb ratios, correction factors, and more.

## Features

- **Personalized Insulin Recommendations:** Input your Insulin to Carb Ratio (I:C), Correction Factor, and activity level to get tailored insulin dosage suggestions.
- **Real-Time Glucose Data Integration:** Fetch the most recent blood sugar readings from the Dexcom G6 using the pydexcom library.
- **Nutritional Analysis:** Enter your meal and get detailed nutritional information, including carbohydrates, protein, fat, calories, sodium, sugar, and fiber.
- **Practical Advice:** Receive personalized tips to avoid blood sugar spikes based on your current blood sugar level.
- **Prompt Engineering:** Uses OpenAI's powerful GPT-4 model for extracting nutritional information and providing insights.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/insulin-simulator-app.git
    cd insulin-simulator-app
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a `config.py` file with your API keys and credentials:

    ```python
    # config.py

    OPENAI_API_KEY = 'your_openai_api_key'
    DEXCOM_USERNAME = 'your_dexcom_username'
    DEXCOM_PASSWORD = 'your_dexcom_password'
    ```

5. Place your background image in the same directory as `app.py` and name it `background.jpg`.

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
