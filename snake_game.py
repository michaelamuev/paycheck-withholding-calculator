import streamlit as st
import streamlit.components.v1 as components

def snake_game():
    try:
        # Initialize session state for high score if it doesn't exist
        if 'high_score' not in st.session_state:
            st.session_state.high_score = 0
        if 'high_score_player' not in st.session_state:
            st.session_state.high_score_player = 'This Session'

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
                .high-score {
                    margin-top: 10px;
                    font-size: 18px;
                    font-weight: bold;
                    color: #2196F3;
                }
            </style>
        """, unsafe_allow_html=True)

        # JavaScript code for the Snake game
        game_code = f"""
        <div class="game-container">
            <canvas id="snakeCanvas" width="400" height="400"></canvas>
            <p id="score">Score: 0</p>
            <p id="highScore" class="high-score">High Score: {st.session_state.high_score} (This Session Only)</p>
            <button onclick="startGame()">Start New Game</button>
        </div>

        <script>
            try {{
                const canvas = document.getElementById('snakeCanvas');
                const ctx = canvas.getContext('2d');
                const scoreElement = document.getElementById('score');
                const highScoreElement = document.getElementById('highScore');
                const gridSize = 20;
                const tileCount = canvas.width / gridSize;
                
                let snake = [];
                let food = {{}};
                let dx = gridSize;
                let dy = 0;
                let score = 0;
                let gameInterval;
                let isGameActive = false;
                let currentHighScore = {st.session_state.high_score};

                function startGame() {{
                    try {{
                        // Reset game state
                        snake = [{{x: 200, y: 200}}];
                        score = 0;
                        dx = gridSize;
                        dy = 0;
                        placeFood();
                        
                        // Clear previous interval if exists
                        if (gameInterval) clearInterval(gameInterval);
                        
                        // Create countdown overlay
                        const overlay = document.createElement('div');
                        overlay.style.cssText = `
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            transform: translate(-50%, -50%);
                            font-size: 48px;
                            font-weight: bold;
                            color: #2196F3;
                            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                            z-index: 1000;
                        `;
                        canvas.parentElement.style.position = 'relative';
                        canvas.parentElement.appendChild(overlay);
                        
                        // Start countdown
                        let count = 3;
                        overlay.textContent = count;
                        
                        const countdownInterval = setInterval(() => {{
                            count--;
                            if (count > 0) {{
                                overlay.textContent = count;
                            }} else if (count === 0) {{
                                overlay.textContent = 'GO!';
                            }} else {{
                                clearInterval(countdownInterval);
                                overlay.remove();
                                
                                // Start game loop
                                isGameActive = true;
                                gameInterval = setInterval(gameLoop, 100);
                                
                                // Update score display
                                scoreElement.textContent = `Score: ${{score}}`;
                            }}
                        }}, 1000);
                        
                    }} catch (error) {{
                        console.error('Error in startGame:', error);
                    }}
                }}

                function placeFood() {{
                    food = {{
                        x: Math.floor(Math.random() * tileCount) * gridSize,
                        y: Math.floor(Math.random() * tileCount) * gridSize
                    }};
                }}

                function gameLoop() {{
                    try {{
                        if (!isGameActive) return;

                        // Move snake
                        const head = {{x: snake[0].x + dx, y: snake[0].y + dy}};
                        
                        // Check wall collision
                        if (head.x < 0 || head.x >= canvas.width || 
                            head.y < 0 || head.y >= canvas.height) {{
                            gameOver();
                            return;
                        }}
                        
                        // Check self collision
                        for (let i = 0; i < snake.length; i++) {{
                            if (head.x === snake[i].x && head.y === snake[i].y) {{
                                gameOver();
                                return;
                            }}
                        }}
                        
                        // Add new head
                        snake.unshift(head);
                        
                        // Check food collision
                        if (head.x === food.x && head.y === food.y) {{
                            score += 10;
                            scoreElement.textContent = `Score: ${{score}}`;
                            placeFood();
                        }} else {{
                            snake.pop();
                        }}
                        
                        // Draw game
                        draw();
                    }} catch (error) {{
                        console.error('Error in gameLoop:', error);
                        gameOver();
                    }}
                }}

                function draw() {{
                    try {{
                        // Clear canvas
                        ctx.fillStyle = '#f0f0f0';
                        ctx.fillRect(0, 0, canvas.width, canvas.height);
                        
                        // Draw snake
                        ctx.fillStyle = '#4CAF50';
                        snake.forEach(segment => {{
                            ctx.fillRect(segment.x, segment.y, gridSize - 2, gridSize - 2);
                        }});
                        
                        // Draw food
                        ctx.fillStyle = '#FF5722';
                        ctx.fillRect(food.x, food.y, gridSize - 2, gridSize - 2);
                    }} catch (error) {{
                        console.error('Error in draw:', error);
                    }}
                }}

                function gameOver() {{
                    isGameActive = false;
                    clearInterval(gameInterval);
                    
                    if (score > currentHighScore) {{
                        const playerName = prompt(
                            `🎮 BOOM! You just crushed the high score with ${{score}} points!\n\n` + 
                            `Want to immortalize your victory *just for this session*? Drop your gamer tag, nickname, or any cool name below.\n` + 
                            `(It won't be saved beyond this game — no cookies or browser data here!)`
                        );
                        const finalName = playerName || 'Anonymous';
                        
                        // Update the high score display
                        currentHighScore = score;
                        highScoreElement.textContent = `High Score: ${{score}} by ${{finalName}} (This Session Only)`;
                    }} else {{
                        alert(`Game Over! Score: ${{score}}`);
                    }}
                }}

                // Handle keyboard input with error handling
                document.addEventListener('keydown', (e) => {{
                    try {{
                        if (!isGameActive) return;
                        
                        // Prevent default arrow key behavior only when game is active
                        if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {{
                            e.preventDefault();
                        }}
                        
                        switch(e.key) {{
                            case 'ArrowUp':
                                if (dy === 0) {{ dx = 0; dy = -gridSize; }}
                                break;
                            case 'ArrowDown':
                                if (dy === 0) {{ dx = 0; dy = gridSize; }}
                                break;
                            case 'ArrowLeft':
                                if (dx === 0) {{ dx = -gridSize; dy = 0; }}
                                break;
                            case 'ArrowRight':
                                if (dx === 0) {{ dx = gridSize; dy = 0; }}
                                break;
                        }}
                    }} catch (error) {{
                        console.error('Error in keydown handler:', error);
                    }}
                }});

                // Initial setup
                draw();
            }} catch (error) {{
                console.error('Error in game initialization:', error);
                document.querySelector('.game-container').innerHTML = '<p style="color: red;">Unable to load game. Please refresh the page.</p>';
            }}
        </script>
        """
        
        # Render the game without the key parameter
        components.html(game_code, height=600, width=450)
        
        # Handle high score updates
        if st.session_state.get('streamlit_message'):
            data = st.session_state.streamlit_message
            if data.get('score', 0) > st.session_state.high_score:
                st.session_state.high_score = data['score']
                st.session_state.high_score_player = data['player']
            del st.session_state.streamlit_message
        
    except Exception as e:
        st.error(f"Error loading snake game: {str(e)}")
        st.warning("Please try refreshing the page if the game doesn't load properly.") 
