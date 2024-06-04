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
