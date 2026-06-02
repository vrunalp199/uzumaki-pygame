<p align="center">
  <img src="images/banner.png" width="100%">
</p>

<h1 align="center">🌀 Uzumaki Pygame</h1>

<p align="center">
  Raspberry Pi • Pygame • Multi-threading • System Management
</p>

Uzumaki Pygame is a Raspberry Pi–based cybersecurity demonstration platform disguised as a simple game interface. While users interact with a retro-style game environment, the system can execute authorized security testing modules in the background, showcasing concepts such as process management, multi-threading, remote administration, and system automation.

The project was developed as an educational and research-oriented platform for studying Raspberry Pi performance, background task execution, remote device management, and cybersecurity tool integration. It demonstrates how multiple security-related services can operate concurrently while maintaining a responsive user interface.

Key Features
Retro-style Pygame interface
Multi-threaded background task execution
Raspberry Pi optimized architecture
Remote administration support
Process and resource management
Modular cybersecurity testing framework
Educational demonstration of concurrent system operations
Educational Objectives

This project helps students understand:

Multi-threading and multiprocessing
Raspberry Pi system administration
Background service management
Remote device operation

## 🚀 Features

- Interactive game interface
- Multi-threaded architecture
- Resource monitoring
- Lightweight design
- Raspberry Pi compatible

## 🔧 Hardware Configuration

This project is designed around a Raspberry Pi CM4 embedded platform.

### Main Components

* Raspberry Pi Compute Module 4 (CM4)
* Waveshare PoE UPS Base Board
* 4-inch HDMI Display
* ESP8266 NodeMCU
* USB Wi-Fi Adapter
* AMS1117 Voltage Regulation Circuit

### Software Stack

* Raspberry Pi OS
* Python 3
* Pygame
* Multi-threaded task execution
* Network management modules

### System Overview

The Pygame interface serves as the primary user interaction layer while the Raspberry Pi CM4 executes background services and system management tasks. An ESP8266 module provides auxiliary wireless control functionality, and a USB Wi-Fi adapter is used for network-related research and testing activities.

This architecture demonstrates embedded Linux development, user-interface design, hardware integration, concurrent processing, and Raspberry Pi system administration.
```bash

                          ┌───────────────────┐
                          │     Mobile Phone  │
                          │    VNC Viewer     │
                          └─────────┬─────────┘
                                    │
                                    │ Wi-Fi
                                    ▼
┌──────────────────────────────────────────────────────┐
│                Raspberry Pi CM4                      │
│          Raspberry Pi OS (Bookworm)                  │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │              Uzumaki Pygame                  │    │
│  │                                              │    │
│  │  Main Menu                                   │    │
│  │  Packet Scanner                              │    │
│  │  ESP8266 Control                             │    │
│  │  System Dashboard                            │    │
│  └────────────────┬─────────────────────────────┘    │
│                   │                                  │
│                   │ Launches & Controls              │
│                   ▼                                  │
│  ┌──────────────────────────────────────────────┐    │
│  │          Background Services                 │    │
│  │                                              │    │
│  │  Thread 1 → WiFi Scanner                     │    │
│  │  Thread 2 → Packet Monitor                   │    │
│  │  Thread 3 → ESP8266 Communication            │    │
│  │  Thread 4 → System Monitoring                │    │
│  │  Thread 5 → Log Collection                   │    │
│  └───────────────┬──────────────────────────────┘    │
└──────────────────┼───────────────────────────────────┘
                   │ UART / Serial
                   ▼
          ┌──────────────────────┐
          │    ESP8266 NodeMCU   │
          │                      │
          │  Wi-Fi Controller    │
          │  Remote Commands     │
          │  External Interface  │
          └──────────────────────┘
                   ▲
                   │
                   │ USB
                   ▼
          ┌──────────────────────┐
          │  USB WiFi Adapter    │
          │                      │
          │  Network Interface   │
          │  Monitoring Module   │
          └──────────────────────┘
```
## 📸 Screenshots

### Main Interface

![Interface](images/interface.png)

### Packet Scanner

![Packet Scanner](images/packetscan.png)

### Deauth Tool

![Deauth Tool](images/deauth-tool.png)

## 🛠 Requirements

```bash
pip3 install -r requirements.txt
```

Install dependencies:
Run
python main.py

## 📂 Project Structure

```text
uzumaki-pygame/
│
├── assets/
├── images/
├── sounds/
├── src/
│   └── main.py
└── README.md
```
#Future Improvements
Leaderboard
Sound effects
Animations
Multiplayer support

```bash
pip install pygame
```
## 👨‍💻 Author

<p align="center">
  <img src="https://github.com/vrunalp199.png" width="150">
</p>

<p align="center">
  <b>Vrunal Patil</b><br>
  Computer Science Student<br>
  Raspberry Pi & Cyber Security Enthusiast
</p>
