#include "Chip8.h"
#include <iostream>

int main() {
    Chip8 chip8;
    chip8.LoadProgram("roms/test.ch8");

    while (true) {
        chip8.EmulateCycle();
        // Add delay or timing logic later
    }

    return 0;
}

