import streamlit as st
import streamlit.components.v1 as components

def snake_game():
    # CSS for the game canvas
    st.markdown("""
        <style>
            canvas {
                border: 2px solid #333;
                background: #f0f0f0;
            }
            .game-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin: 20px 0;
            }
        </style>
    """, unsafe_allow_html=True)

    # JavaScript code for the Snake game
    game_code = """
    <div class="game-container">
        <canvas id="snakeCanvas" width="400" height="400"></canvas>
        <p id="score">Score: 0</p>
        <button onclick="startGame()">Start New Game</button>
    </div>

    <script>
        const canvas = document.getElementById('snakeCanvas');
        const ctx = canvas.getContext('2d');
        const scoreElement = document.getElementById('score');
        const gridSize = 20;
        const tileCount = canvas.width / gridSize;
        
        let snake = [];
        let food = {};
        let dx = gridSize;
        let dy = 0;
        let score = 0;
        let gameInterval;
        let isGameActive = false;

        function startGame() {
            // Reset game state
            snake = [{x: 200, y: 200}];
            score = 0;
            dx = gridSize;
            dy = 0;
            placeFood();
            
            // Clear previous interval if exists
            if (gameInterval) clearInterval(gameInterval);
            
            // Start game loop
            isGameActive = true;
            gameInterval = setInterval(gameLoop, 100);
            
            // Update score display
            scoreElement.textContent = `Score: ${score}`;
            
            // Focus canvas for key events
            canvas.focus();
        }

        function placeFood() {
            food = {
                x: Math.floor(Math.random() * tileCount) * gridSize,
                y: Math.floor(Math.random() * tileCount) * gridSize
            };
        }

        function gameLoop() {
            if (!isGameActive) return;

            // Move snake
            const head = {x: snake[0].x + dx, y: snake[0].y + dy};
            
            // Check wall collision
            if (head.x < 0 || head.x >= canvas.width || 
                head.y < 0 || head.y >= canvas.height) {
                gameOver();
                return;
            }
            
            // Check self collision
            for (let i = 0; i < snake.length; i++) {
                if (head.x === snake[i].x && head.y === snake[i].y) {
                    gameOver();
                    return;
                }
            }
            
            // Add new head
            snake.unshift(head);
            
            // Check food collision
            if (head.x === food.x && head.y === food.y) {
                score += 10;
                scoreElement.textContent = `Score: ${score}`;
                placeFood();
            } else {
                snake.pop();
            }
            
            // Draw game
            draw();
        }

        function draw() {
            // Clear canvas
            ctx.fillStyle = '#f0f0f0';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Draw snake
            ctx.fillStyle = '#4CAF50';
            snake.forEach(segment => {
                ctx.fillRect(segment.x, segment.y, gridSize - 2, gridSize - 2);
            });
            
            // Draw food
            ctx.fillStyle = '#FF5722';
            ctx.fillRect(food.x, food.y, gridSize - 2, gridSize - 2);
        }

        function gameOver() {
            isGameActive = false;
            clearInterval(gameInterval);
            alert(`Game Over! Score: ${score}`);
        }

        // Handle keyboard input
        document.addEventListener('keydown', (e) => {
            if (!isGameActive) return;
            
            // Prevent default arrow key behavior only when game is active
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
                e.preventDefault();
            }
            
            switch(e.key) {
                case 'ArrowUp':
                    if (dy === 0) { dx = 0; dy = -gridSize; }
                    break;
                case 'ArrowDown':
                    if (dy === 0) { dx = 0; dy = gridSize; }
                    break;
                case 'ArrowLeft':
                    if (dx === 0) { dx = -gridSize; dy = 0; }
                    break;
                case 'ArrowRight':
                    if (dx === 0) { dx = gridSize; dy = 0; }
                    break;
            }
        });

        // Initial setup
        draw();
    </script>
    """
    
    # Render the game
    components.html(game_code, height=500) 