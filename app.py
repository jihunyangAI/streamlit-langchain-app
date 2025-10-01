import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="테트리스", page_icon="🧱", layout="centered")

st.title("🧱 테트리스")
st.markdown(
    """
### 조작 방법
- ⬅️ ➡️ : 블록 이동
- ⬆️ : 블록 회전
- ⬇️ : 빠른 하강
- Space : 즉시 하강

아래 캔버스에서 고전 테트리스 게임을 즐겨보세요!
    """
)

tetris_html = """
<style>
body {background-color: #0f172a;}
canvas {background: #0f172a; border: 2px solid #38bdf8; border-radius: 8px;}
#stats {font-family: 'Pretendard', 'Noto Sans KR', sans-serif; color: #e2e8f0;}
button {margin-top: 10px;}
</style>
<div id="stats">
  <p>점수: <span id="score">0</span></p>
  <p>레벨: <span id="level">1</span></p>
  <p>줄: <span id="lines">0</span></p>
</div>
<canvas id="board" width="300" height="600"></canvas>
<button id="restart">다시 시작</button>
<script>
const canvas = document.getElementById('board');
const context = canvas.getContext('2d');
context.scale(30, 30);

const colors = [
  null,
  '#38bdf8',
  '#f97316',
  '#a855f7',
  '#f59e0b',
  '#22c55e',
  '#ef4444',
  '#c084fc'
];

const SHAPES = {
  I: [
    [0, 0, 0, 0],
    [1, 1, 1, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
  ],
  J: [
    [2, 0, 0],
    [2, 2, 2],
    [0, 0, 0]
  ],
  L: [
    [0, 0, 3],
    [3, 3, 3],
    [0, 0, 0]
  ],
  O: [
    [4, 4],
    [4, 4]
  ],
  S: [
    [0, 5, 5],
    [5, 5, 0],
    [0, 0, 0]
  ],
  T: [
    [0, 6, 0],
    [6, 6, 6],
    [0, 0, 0]
  ],
  Z: [
    [7, 7, 0],
    [0, 7, 7],
    [0, 0, 0]
  ]
};

const arena = createMatrix(10, 20);

function createMatrix(width, height) {
  const matrix = [];
  while (height--) {
    matrix.push(new Array(width).fill(0));
  }
  return matrix;
}

function createPiece(type) {
  return SHAPES[type].map(row => row.slice());
}

function collide(arena, player) {
  const [m, o] = [player.matrix, player.pos];
  for (let y = 0; y < m.length; ++y) {
    for (let x = 0; x < m[y].length; ++x) {
      if (m[y][x] !== 0 && (arena[y + o.y] && arena[y + o.y][x + o.x]) !== 0) {
        return true;
      }
    }
  }
  return false;
}

function merge(arena, player) {
  player.matrix.forEach((row, y) => {
    row.forEach((value, x) => {
      if (value !== 0) {
        arena[y + player.pos.y][x + player.pos.x] = value;
      }
    });
  });
}

function rotate(matrix, dir) {
  for (let y = 0; y < matrix.length; ++y) {
    for (let x = 0; x < y; ++x) {
      [matrix[x][y], matrix[y][x]] = [matrix[y][x], matrix[x][y]];
    }
  }

  if (dir > 0) {
    matrix.forEach(row => row.reverse());
  } else {
    matrix.reverse();
  }
}

function playerDrop() {
  player.pos.y++;
  if (collide(arena, player)) {
    player.pos.y--;
    merge(arena, player);
    playerReset();
    arenaSweep();
    updateScore();
  }
  dropCounter = 0;
}

function playerMove(offset) {
  player.pos.x += offset;
  if (collide(arena, player)) {
    player.pos.x -= offset;
  }
}

function playerRotate(dir) {
  const pos = player.pos.x;
  let offset = 1;
  rotate(player.matrix, dir);
  while (collide(arena, player)) {
    player.pos.x += offset;
    offset = -(offset + (offset > 0 ? 1 : -1));
    if (offset > player.matrix[0].length) {
      rotate(player.matrix, -dir);
      player.pos.x = pos;
      return;
    }
  }
}

function arenaSweep() {
  let rowCount = 0;
  outer: for (let y = arena.length - 1; y >= 0; --y) {
    for (let x = 0; x < arena[y].length; ++x) {
      if (arena[y][x] === 0) {
        continue outer;
      }
    }
    const row = arena.splice(y, 1)[0].fill(0);
    arena.unshift(row);
    ++y;
    rowCount++;
  }
  if (rowCount > 0) {
    player.score += rowCount * 100;
    player.lines += rowCount;
    player.level = Math.floor(player.lines / 10) + 1;
  }
}

function drawMatrix(matrix, offset) {
  matrix.forEach((row, y) => {
    row.forEach((value, x) => {
      if (value !== 0) {
        context.fillStyle = colors[value];
        context.fillRect(x + offset.x, y + offset.y, 1, 1);
        context.strokeStyle = '#0f172a';
        context.strokeRect(x + offset.x, y + offset.y, 1, 1);
      }
    });
  });
}

function draw() {
  context.fillStyle = '#0f172a';
  context.fillRect(0, 0, canvas.width, canvas.height);
  drawMatrix(arena, {x: 0, y: 0});
  drawMatrix(player.matrix, player.pos);
}

function playerReset() {
  const pieces = 'TJLOSZI';
  player.matrix = createPiece(pieces[(pieces.length * Math.random()) | 0]);
  player.pos.y = 0;
  player.pos.x = ((arena[0].length / 2) | 0) - ((player.matrix[0].length / 2) | 0);
  if (collide(arena, player)) {
    arena.forEach(row => row.fill(0));
    player.score = 0;
    player.lines = 0;
    player.level = 1;
    updateScore();
  }
}

function hardDrop() {
  while (!collide(arena, player)) {
    player.pos.y++;
  }
  player.pos.y--;
  merge(arena, player);
  playerReset();
  arenaSweep();
  updateScore();
  dropCounter = 0;
}

let dropCounter = 0;
let dropInterval = 1000;
let lastTime = 0;

const player = {
  pos: {x: 0, y: 0},
  matrix: null,
  score: 0,
  level: 1,
  lines: 0,
};

function update(time = 0) {
  const deltaTime = time - lastTime;
  lastTime = time;
  dropCounter += deltaTime;
  dropInterval = Math.max(100, 1000 - (player.level - 1) * 75);

  if (dropCounter > dropInterval) {
    playerDrop();
  }
  draw();
  requestAnimationFrame(update);
}

function updateScore() {
  document.getElementById('score').innerText = player.score;
  document.getElementById('level').innerText = player.level;
  document.getElementById('lines').innerText = player.lines;
}

document.addEventListener('keydown', event => {
  if (event.keyCode === 37) {
    playerMove(-1);
  } else if (event.keyCode === 39) {
    playerMove(1);
  } else if (event.keyCode === 40) {
    playerDrop();
  } else if (event.keyCode === 81) {
    playerRotate(-1);
  } else if (event.keyCode === 87 || event.keyCode === 38) {
    playerRotate(1);
  } else if (event.keyCode === 32) {
    hardDrop();
  }
});

document.getElementById('restart').addEventListener('click', () => {
  arena.forEach(row => row.fill(0));
  player.score = 0;
  player.lines = 0;
  player.level = 1;
  updateScore();
  playerReset();
});

playerReset();
updateScore();
update();
</script>
"""

components.html(tetris_html, height=700)
