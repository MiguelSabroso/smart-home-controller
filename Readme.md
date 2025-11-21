**Smart Home Controller**

A Python-based Smart Home Dashboard application built with Flet. This app simulates a central control unit for a smart home, featuring real-time updates, asynchronous device simulation, and a modern interactive UI.

**Project Description**

This project demonstrates a responsive UI for managing smart devices (lights, doors, thermostats, fans). It uses an asynchronous background task to simulate environmental changes and user interactions (ghost touch), updating the interface in real-time using a Pub/Sub event architecture without requiring page reloads.

**Features**

- Overview Dashboard: * Interactive cards for different device types (Lights, Security, Temperature, Climate).

  - Color-coded UI for easy status recognition.
  - Real-time status updates via UI-driven events or background simulation.

- Real-Time Analytics:

  - Live Line Chart displaying simulated power consumption (kW).

  - Auto-updating Action Log table tracking all device changes.

- Device Details:

  - Dedicated view for each device with specific controls and history log.

- Technical Highlights:

  - Async/Await: Fully asynchronous core for non-blocking UI.

  - Pub/Sub System: Decoupled component communication.

  - Background Simulation: Random event generator running in a separate thread loop.

**Installation & Usage**

1. Clone the repository:

  git clone [https://github.com/your-username/smart-home-controller.git](https://github.com/your-username/smart-home-controller.git)
  cd smart-home-controller


2. Install dependencies:

  pip install flet


3. Run the application:

  python app.py or flet run app.py
