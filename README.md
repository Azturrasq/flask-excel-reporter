# Large Size Product Analysis

This project is a Flask application designed for analyzing sales data of large size products. It provides functionalities for uploading sales and stock data, processing the data, and generating reports.

## Project Structure

```
large-size-product-analysis
├── app
│   ├── __init__.py          # Initializes the Flask application
│   ├── routes.py            # Defines application routes
│   ├── models.py            # Contains data models
│   ├── forms.py             # Defines forms for user input
│   ├── utils                 # Utility functions for data handling
│   │   ├── __init__.py
│   │   ├── data_loader.py    # Functions for loading data from Excel
│   │   ├── data_processor.py  # Functions for processing data
│   │   └── report_generator.py # Functions for generating reports
│   ├── static                # Static files (CSS, JS)
│   │   ├── css
│   │   │   └── style.css
│   │   └── js
│   │       └── main.js
│   └── templates             # HTML templates for rendering views
│       ├── base.html
│       ├── index.html
│       ├── upload.html
│       └── report.html
├── data                      # Data directories
│   ├── sales
│   │   └── .gitkeep
│   ├── stock
│   │   └── .gitkeep
│   └── images
│       └── .gitkeep
├── results                   # Directory for storing results
│   └── .gitkeep
├── config.py                # Configuration settings for the application
├── run.py                   # Entry point for running the application
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd large-size-product-analysis
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```
   python run.py
   ```

5. **Access the application:**
   Open your web browser and go to `http://127.0.0.1:5000`.

## Usage

- Upload your sales and stock data in Excel format through the upload page.
- After uploading, the application will process the data and generate a report.
- You can download the report in Excel format.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.