#include <iostream>
#include <vector>
#include <conio.h>
#include <thread>
#include <chrono>

using namespace std;

const int width = 10;
const int height = 20;
vector<vector<int>> board(height, vector<int>(width, 0));

int tetrominoes[7][4][4] = {
    {{1, 1, 1, 1},
     {0, 0, 0, 0},
     {0, 0, 0, 0},
     {0, 0, 0, 0}},

    {{1, 1, 1, 0},
     {1, 0, 0, 0},
     {0, 0, 0, 0},
     {0, 0, 0, 0}},

    {{1, 1, 1, 0},
     {0, 0, 1, 0},
     {0, 0, 0, 0},
     {0, 0, 0, 0}},

    {{1, 1, 0, 0},
     {1, 1, 0, 0},
     {0, 0, 0, 0},
     {0, 0, 0, 0}},

    {{1, 1, 0, 0},
     {0, 1, 1, 0},
     {0, 0, 0, 0},
     {0, 0, 0, 0}},

    {{0, 1, 1, 0},
     {1, 1, 0, 0},
     {0, 0, 0, 0},
     {0, 0, 0, 0}},

    {{1, 1, 1, 0},
     {0, 1, 0, 0},
     {0, 0, 0, 0},
     {0, 0, 0, 0}}
};

int currentPiece, x = width / 2 - 2, y = 0;

bool checkCollision(int xOffset, int yOffset, int rotation) {
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            if (tetrominoes[currentPiece][i][j]) {
                int newX = x + j + xOffset;
                int newY = y + i + yOffset;
                if (newX < 0 || newX >= width || newY >= height || (newY >= 0 && board[newY][newX])) {
                    return true;
                }
            }
        }
    }
    return false;
}

void placePiece() {
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            if (tetrominoes[currentPiece][i][j] && y + i >= 0) {
                board[y + i][x + j] = 1;
            }
        }
    }
}

void clearLines() {
    for (int i = 0; i < height; i++) {
        bool full = true;
        for (int j = 0; j < width; j++) {
            if (!board[i][j]) {
                full = false;
                break;
            }
        }
        if (full) {
            board.erase(board.begin() + i);
            board.insert(board.begin(), vector<int>(width, 0));
        }
    }
}

void drawBoard() {
    system("cls");
    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            if (board[i][j]) cout << "#";
            else cout << ".";
        }
        cout << endl;
    }
}

void spawnPiece() {
    currentPiece = rand() % 7;
    x = width / 2 - 2;
    y = 0;
    if (checkCollision(0, 0, 0)) {
        cout << "Game Over!" << endl;
        exit(0);
    }
}

int main() {
    spawnPiece();
    while (true) {
        drawBoard();
        this_thread::sleep_for(chrono::milliseconds(500));

        if (_kbhit()) {
            char key = _getch();
            if (key == 'a' && !checkCollision(-1, 0, 0)) x--;
            else if (key == 'd' && !checkCollision(1, 0, 0)) x++;
            else if (key == 's' && !checkCollision(0, 1, 0)) y++;
        }

        if (!checkCollision(0, 1, 0)) {
            y++;
        } else {
            placePiece();
            clearLines();
            spawnPiece();
        }
    }
}
