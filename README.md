AI-Powered Adaptive Chessboard

Overview

This project is an AI-powered chessboard that allows users to play against a Leela Chess Zero (Lc0) engine with adaptive difficulty. The chessboard uses an electromagnet on a coreXY plane to move pieces, creating an interactive and automated playing experience. The adaptive difficulty mode adjusts based on user performance, ensuring a personalized challenge.

Features

AI-Powered Gameplay: Users play against a bot powered by Lc0.

Piece Movement Automation: The system moves pieces via an electromagnet.

Adaptive Difficulty: The bot adjusts its Elo rating dynamically based on user performance.

Game Metrics Tracking: Tracks win/loss ratio, blunder rate, and game duration.

Installation & Setup

Requirements

Python 3.8+

python-chess

subprocess (for handling Lc0 commands)

A CUDA-compatible GPU (optional, for faster inference)

Installation

# Clone the repository
git clone https://github.com/yourusername/capstone-chessboard.git
cd capstone-chessboard


Running the Project


Contributors
Syed Moiz, Liam Ault, Peter Mcewen, Mohammed Aziz
License

