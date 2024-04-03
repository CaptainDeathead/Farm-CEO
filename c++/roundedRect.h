#include <SDL2/SDL.h>
#include <vector>
#include "circle.h"

void DrawCircleOld(SDL_Renderer *renderer, int32_t centreX, int32_t centreY, int32_t radius)
{
    const int32_t diameter = (radius * 2);

    int32_t x = (radius - 1);
    int32_t y = 0;
    int32_t tx = 1;
    int32_t ty = 1;
    int32_t error = (tx - diameter);

    while (x >= y)
    {
        //  Each of the following renders an octant of the circle
        SDL_RenderDrawPoint(renderer, centreX + x, centreY - y);
        SDL_RenderDrawPoint(renderer, centreX + x, centreY + y);
        SDL_RenderDrawPoint(renderer, centreX - x, centreY - y);
        SDL_RenderDrawPoint(renderer, centreX - x, centreY + y);
        SDL_RenderDrawPoint(renderer, centreX + y, centreY - x);
        SDL_RenderDrawPoint(renderer, centreX + y, centreY + x);
        SDL_RenderDrawPoint(renderer, centreX - y, centreY - x);
        SDL_RenderDrawPoint(renderer, centreX - y, centreY + x);

        if (error <= 0)
        {
            ++y;
            error += ty;
            ty += 2;
        }

        if (error > 0)
        {
            --x;
            tx += 2;
            error += (tx - diameter);
        }
    }
}

void SDL_RenderFillRoundedRect(SDL_Renderer* renderer, int x, int y, int width, int height, std::vector<int> color, int radius) {
    SDL_Rect centerRect = {x, y+radius, width, height-radius*2};
    SDL_Rect topRect = {x+radius, y, width-radius*2, radius};
    SDL_Rect bottomRect = {x+radius, y+height-radius, width-radius*2, radius};

    SDL_SetRenderDrawColor(renderer, color[0], color[1], color[2], color[3]);
            
    SDL_RenderFillCircle(renderer, x+radius, y+radius, radius);
    SDL_RenderFillCircle(renderer, x+width-radius-1, y+radius, radius);
    SDL_RenderFillCircle(renderer, x+radius, y+height-radius-1, radius);
    SDL_RenderFillCircle(renderer, x+width-radius-1, y+height-radius-1, radius);

    SDL_RenderFillRect(renderer, &centerRect);
    SDL_RenderFillRect(renderer, &topRect);
    SDL_RenderFillRect(renderer, &bottomRect);
}

class RoundedRect {
    public:
        int x;
        int y;
        int width;
        int height;
        std::vector<int> color;
        int radius;

        SDL_Rect centerRect;
        SDL_Rect topRect;
        SDL_Rect bottomRect;

        RoundedRect(int pos_x, int pos_y, int rect_width, int rect_height, std::vector<int> rect_color, int border_radius) : x(pos_x), y(pos_y), width(rect_width), height(rect_height), color(rect_color), radius(border_radius) {
            centerRect = {x, y+radius, width, height-radius*2};
            topRect = {x+radius, y, width-radius*2, radius};
            bottomRect = {x+radius, y+height-radius, width-radius*2, radius};
        }

        void setup() {
            centerRect = {x, y+radius, width, height-radius*2};
            topRect = {x+radius, y, width-radius*2, radius};
            bottomRect = {x+radius, y+height-radius, width-radius*2, radius};
        }

        void draw(SDL_Renderer* renderer) {
            SDL_SetRenderDrawColor(renderer, color[0], color[1], color[2], color[3]);
            
            SDL_RenderFillCircle(renderer, x+radius, y+radius, radius);
            SDL_RenderFillCircle(renderer, x+width-radius-1, y+radius, radius);
            SDL_RenderFillCircle(renderer, x+radius, y+height-radius-1, radius);
            SDL_RenderFillCircle(renderer, x+width-radius-1, y+height-radius-1, radius);

            SDL_RenderFillRect(renderer, &centerRect);
            SDL_RenderFillRect(renderer, &topRect);
            SDL_RenderFillRect(renderer, &bottomRect);
        }
};