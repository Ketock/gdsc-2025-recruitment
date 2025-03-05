#include "Chip8.h"
#include <fstream>
#include <iostream>

Chip8::Chip8() {
    // Clear memory, registers, and stack
    memory.fill(0);
    V.fill(0);
    stack.fill(0);
}

void Chip8::LoadProgram(const char* filename) {
    std::ifstream file(filename, std::ios::binary | std::ios::ate);
    
    if (!file) {
        std::cerr << "Failed to open file: " << filename << std::endl;
        return;
    }

    std::streamsize size = file.tellg();
    if (size > 3584) {  // Max program size (4096 - 512)
        std::cerr << "Program too large!" << std::endl;
        return;
    }

    file.seekg(0, std::ios::beg);
    file.read(reinterpret_cast<char*>(&memory[0x200]), size);
    file.close();
}

void Chip8::EmulateCycle() {
    // Fetch: Read two bytes from memory at PC
    opcode = (memory[PC] << 8) | memory[PC + 1];

    // Decode: Identify the opcode structure
    switch (opcode & 0xF000) {  // Check first hex digit
        case 0x0000:
            if (opcode == 0x00E0) {
                // 00E0: Clear screen
                std::cout << "Clearing screen\n";
            } else if (opcode == 0x00EE) {
                // 00EE: Return from subroutine
                PC = stack[--SP];
                std::cout << "Returning from subroutine\n";
            }
            break;

        case 0x1000:
            // 1NNN: Jump to address NNN
            PC = opcode & 0x0FFF;
            std::cout << "Jump to " << std::hex << PC << std::endl;
            return;

        case 0x6000:
            // 6XNN: Set register VX = NN
            {
                uint8_t X = (opcode & 0x0F00) >> 8;
                uint8_t NN = opcode & 0x00FF;
                V[X] = NN;
                std::cout << "Set V" << (int)X << " = " << (int)NN << std::endl;
            }
            break;

        case 0x7000:
            // 7XNN: Add NN to VX
            {
                uint8_t X = (opcode & 0x0F00) >> 8;
                uint8_t NN = opcode & 0x00FF;
                V[X] += NN;
                std::cout << "Add " << (int)NN << " to V" << (int)X << std::endl;
            }
            break;

        default:
            std::cout << "Unknown opcode: " << std::hex << opcode << std::endl;
    }

    // Increment PC by 2 (since each instruction is 2 bytes)
    PC += 2;
}

