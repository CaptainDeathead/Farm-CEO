#include <SDL2/SDL.h>
#include <SDL2/SDL_ttf.h>
#include <vector>

class Text {
    public:
        SDL_Renderer* renderer;
        int x;
        int y;
        const char* fontFile;
        char * text;
        int size;
        std::vector<int> color;

        Text(SDL_Renderer* sdl_renderer, int pos_x, int pos_y, const char* font_file, char* str_text, int text_size, std::vector<int> text_color) : renderer(sdl_renderer), x(pos_x), y(pos_y), fontFile(font_file), text(str_text), size(text_size), color(text_color) {}

        TTF_Font* Font = TTF_OpenFont(fontFile, size);

        SDL_Surface *TextSurface = TTF_RenderText_Blended_Wrapped(Font, text, (SDL_Color){color[0], color[1], color[2], color[3]}, 500);
        SDL_Texture *TextTexture = SDL_CreateTextureFromSurface(renderer, TextSurface);

        // Create a temporary SDL_Rect variable
        SDL_Rect dstRect = {
            x - TextSurface->w / 2,
            y - TextSurface->h / 2,
            TextSurface->w,
            TextSurface->h
        };

        void setup() {
            SDL_FreeSurface(TextSurface);
            SDL_DestroyTexture(TextTexture);

            TextSurface = TTF_RenderText_Blended_Wrapped(Font, text, (SDL_Color){color[0], color[1], color[2], color[3]}, 500);
            TextTexture = SDL_CreateTextureFromSurface(renderer, TextSurface);

            // Create a temporary SDL_Rect variable
            dstRect = {
                x - TextSurface->w / 2,
                y - TextSurface->h / 2,
                TextSurface->w,
                TextSurface->h
            };
        }

    void draw() {
        // Render using the temporary SDL_Rect variable
        SDL_RenderCopy(renderer, TextTexture, NULL, &dstRect);
    }
};