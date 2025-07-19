
# 🏎️ Modular Multiplayer Car Game with AI

A Python-based car racing game that supports both **multiplayer over sockets** and **AI-controlled cars**. Designed with a modular architecture to separate rendering, networking, collision detection, game logic, and AI subsystems.

---

## 📦 Features

- 🚗 **Multiplayer Mode**: Players can race in real time over a network using Python sockets.
- 🧠 **AI Car**: AI-controlled car uses waypoints and angle adjustments to navigate the track intelligently.
- 🔄 **Modular Design**: Code is organized into subsystems for easier development and testing:
  - `cars/`: Car mechanics and movement
  - `network/`: Multiplayer socket communication
  - `game/`: Game loop and logic (lap counting, state tracking)
  - `collision/`: Collision detection system
  - `ai/`: AI car controller logic

---

## 🎮 How to Play

### 🧑‍🤝‍🧑 Multiplayer Mode
1. Start the server:
   ```bash
   python server.py
   ```
2. Start the client:
   ```bash
   python client.py
   ```
3. Players join and race with keyboard controls.

### 🤖 AI Mode
- The AI car is activated automatically and follows waypoints on the track.
- You can test it by starting the game in single-player mode and watching the AI navigate.

---

## 🧠 AI Logic

- AI selects the next waypoint and adjusts its angle toward it.
- Uses trigonometric functions and vector math to steer smoothly.
- Stops at collisions and resets if stuck.

---

## 🛠️ Tech Stack

- **Python 3**
- **Pygame** for rendering and game mechanics
- **Socket** library for networking
- **NumPy** for AI calculations

---

## 🚧 To-Do / Future Improvements

- Add obstacle avoidance for AI cars
- Implement power-ups or turbo boosts
- Add UI for player stats and lap time
- Add AI difficulty settings

---


## 👨‍💻 Author

**Lakshmish R. Kanchan**  


