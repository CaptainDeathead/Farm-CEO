#include <SDL2/SDL.h>
#include <vector>
#include <map>
#include <iostream>
#include <string>
#include "data.h"
#include "roundedRect.h"
#include "text.h"
#include "sdlGui.h"

class Menu {
    public:
        SDL_Renderer* renderer;
        int x = 0;
        int y = 0;
        int width = 0;
        int height = 0;
        SDL_Rect backgroundRect = {x, y, width, height};
        Button butt;

        Menu(SDL_Renderer* sdl_renderer, int c_width, int c_height) : renderer(sdl_renderer), width(c_width), height(c_height), butt(Button(sdl_renderer, 10, 10, 100, 100, {0, 0, 0, 255}, {255, 0, 0, 255}, {255, 255, 255, 255}, "uwu", 20, 20)) {}

        //Button butt = Button(renderer, 10, 10, 100, 100, {0, 0, 0, 255}, {255, 0, 0, 255}, {255, 255, 255, 255}, "uwu", 20, 20);

    void draw() {
        cout << butt.renderer << endl;
        SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
        SDL_RenderFillRect(renderer, &backgroundRect);
        butt.draw();
    }
};

class Window {
    public:
        SDL_Window* window = nullptr;
        SDL_Renderer* renderer = nullptr;
        SDL_Event event;
        
        SDL_Surface* mapSurface;
        SDL_Texture* map;
        float mapScale = 1080/ZOOM/609;
        SDL_Rect mapRect = {static_cast<int>(WIDTH/ZOOM-969*mapScale), 0, static_cast<int>(969*mapScale), static_cast<int>(609*mapScale)};

        Menu menu = Menu(renderer, 2340/ZOOM-969*mapScale, 1080/ZOOM);

        bool keys[SDL_NUM_SCANCODES] = {false};

    void main() {
        SDL_Init(SDL_INIT_EVERYTHING);
        SDL_CreateWindowAndRenderer((int)WIDTH/ZOOM, (int)HEIGHT/ZOOM, 0, &this->window, &this->renderer);
        SDL_SetRenderTarget(this->renderer, nullptr);
        SDL_SetWindowTitle(this->window, "Farm CEO");

        mapSurface = SDL_LoadBMP("./Data/map.bmp");
        map = SDL_CreateTextureFromSurface(renderer, mapSurface);

        SDL_FreeSurface(this->mapSurface);

        while (true) {
            while (SDL_PollEvent(&event)) {
                if (event.type == SDL_QUIT) {
                    return;
                } else if (event.type == SDL_KEYDOWN) {
                    keys[event.key.keysym.scancode] = true;
                } else if (event.type == SDL_KEYUP) {
                    keys[event.key.keysym.scancode] = false;
                }
            }

            // fill screen to black
            //SDL_SetRenderDrawColor(this->renderer, 0, 0, 0, 255);
            //SDL_RenderClear(this->renderer);

            // draw map
            SDL_RenderCopy(renderer, this->map, nullptr, &this->mapRect);

            menu.draw();

            SDL_RenderPresent(this->renderer);
            SDL_Delay(10);
        }
    }
};

int main(int argv, char** args) {
    Window window;
    window.main();

    return 0;
}
