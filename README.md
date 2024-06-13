# Room Reservation App

Room Reservation App is a desktop application designed for managing room reservations. It includes features to create, delete, and view reservations with priority handling to ensure important bookings are never missed.

## Features

- Create and manage buildings and rooms
- Make room reservations with priority levels
- Prevent double booking based on priority
- View and delete reservations
- User-friendly interface with real-time updates

## Installation

### Prerequisites

- Python 3.10 or later (for development and running from source)
- `PyQt5` library

### Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/room-reservation-app.git
    cd room-reservation-app
    ```

2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:

    ```bash
    python main.py
    ```

## Packaging the Application

### macOS

To create a standalone macOS application, you can use `PyInstaller`:

1. Install `pyinstaller`:

    ```bash
    pip install pyinstaller
    ```

2. Create the standalone application:

    ```bash
    pyinstaller --onefile --windowed main.py
    ```

3. The standalone application bundle will be located in the `dist` directory.

### Linux

To create a standalone Linux application, you can use `PyInstaller`:

1. Install `pyinstaller`:

    ```bash
    pip install pyinstaller
    ```

2. Create the standalone application:

    ```bash
    pyinstaller --onefile main.py
    ```

3. The standalone executable will be located in the `dist` directory.

### Windows

To create a standalone Windows application, you can use `PyInstaller`:

1. Install `pyinstaller`:

    ```bash
    pip install pyinstaller
    ```

2. Create the standalone application:

    ```bash
    pyinstaller --onefile --windowed main.py
    ```

3. The standalone executable will be located in the `dist` directory.

## Running the Application on Different Operating Systems

### macOS

1. Follow the steps in the "Packaging for macOS" section to create a standalone application bundle.
2. The standalone application bundle will be located in the `dist` directory.

### Linux

1. Follow the steps in the "Packaging for Linux" section to create a standalone executable.
2. The standalone executable will be located in the `dist` directory.

### Windows

1. Follow the steps in the "Packaging for Windows" section to create a standalone executable.
2. The standalone executable will be located in the `dist` directory.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
