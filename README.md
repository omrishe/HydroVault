# HydroVault - Barrel Storage Simulation

HydroVault is an IoT simulation project that simulates a barrel storage system with various components, including sensor data, panic control, and relay feedback.
It utilizes a message broker for communication between components.

## Features

* **Barrel Simulation (DHT):**
    * Simulates sensor data (barrel contents) and publishes it continuously to the message broker.
    * Represents different types of simulated barrels.
* **Panic Control:**
    * Provides a panic button interface.
    * When activated, sends a "drain" message to the message broker, simulating an emergency.
* **Relay Feedback:**
    * Listens for confirmation messages from the simulated barrels (DHT) after a panic event.
    * Provides a GUI to display these confirmation messages.
* **Main GUI:**
    * Acts as a central control panel.
    * Allows users to launch the DHT, Panic Button, and Relay GUIs.
    * Subscribes to the message broker to display all published messages.
    * Maintains a database to store information about created barrels.
    * Adds barrels to the database and publishes their content only once.
* **Message Broker Integration:**
    * Uses a message broker (MQTT) for communication between all components.
* **Database Integration:**
    * Stores barrel information in a database.

## Technologies Used

* Python
* PyQt (for GUIs)
* MQTT
* SQLite (for database)

## Getting Started

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/omrishe/HydroVault.git](https://github.com/omrishe/HydroVault.git)
    ```

2.  **Navigate to the project directory:**

    ```bash
    cd HydroVault
    ```


3.  **Start the application:**
    * Start the message broker.
    * Start the database.
    * Run the main python script.

    ```bash
    python GUI.py
    ```

## Usage

* **Main GUI:**
    * Use the buttons to launch the DHT, Panic Button, and Relay GUIs.
    * Observe published messages in the message display area.
    * Use the add barrel buttons to add barrels to the database without continuous messages being sent about the barrel.
* **DHT GUI:**
    * Simulates barrel sensor data and publishes it to the broker.
* **Panic Button GUI:**
    * Click the panic button to trigger a "drain" event.
* **Relay GUI:**
    * Monitors and displays confirmation messages from the DHT barrels.
* **DataBase Gui:**
  * shows the stored database barrels,their contents,id and amount

## Future Improvements

* **Advanced Simulation:** Implement more realistic barrel behavior.
* **Data Visualization:** Visualize sensor data and event logs.
* **User Authentication:** Implement user authentication for control access.
* **Scalability:** Design for handling a larger number of simulated barrels.

## Author

* Omri She - [https://github.com/omrishe](https://github.com/omrishe)
