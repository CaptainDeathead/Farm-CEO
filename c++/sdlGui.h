#include <SDL2/SDL.h>
#include <vector>
#include <iostream>

using namespace std;

class Button {
    public:
        SDL_Renderer* renderer;
        int x;
        int y;
        int width;
        int height;
        vector<int> color;
        vector<int> selectedColor;
        vector<int> textColor;
        char* text = "";
        int radius;
        bool clicked = false;
        Text font;
        int size;
        RoundedRect rect = RoundedRect(0, 0, 10, 10, {255, 255, 255, 255}, 10);

        Button(SDL_Renderer* sdl_renderer, int button_x, int button_y, int button_width, int button_height, vector<int> button_color, vector<int> button_selected_color,
                vector<int> button_text_color, char* button_text, int text_size, int border_radius) : renderer(sdl_renderer), x(button_x), y(button_y), width(button_width),
                height(button_height), color(button_color), selectedColor(button_selected_color), textColor(button_text_color), text(button_text),
                size(text_size), radius(border_radius), font(Text(renderer, 0, 0, "Arial.ttf", "None", 20, {255, 255, 255, 255}))
                {
                    rect.x = x;
                    rect.y = y;
                    rect.width = width;
                    rect.height = height;
                    rect.color = color;
                    rect.radius = radius;
                    rect.setup();
                };

        void draw() {
            // TODO: finish/start this
            rect.draw(renderer);
            font.draw();
        }
};