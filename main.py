import json
from turtle import RawTurtle, Turtle

from cairosvg import svg2png
from svg_turtle import SvgTurtle

W = 1920
H = 1024
SCREEN_SCALE = 1
WORLD_SCALE = 5e-8
JUPITER_SCALE = 2
MOON_SCALE = 10


def get_angle(angle: float):
    if angle < 0:
        return 360 + angle

    return angle


def draw_circle_arc(t: RawTurtle, radius: float):
    t.penup()
    t.right(90)
    t.forward(radius)
    t.left(90)

    t.pendown()
    t.circle(radius, 4)

    t.penup()
    t.right(-90)
    t.forward(radius)
    t.left(-90)


def draw_circle_spacer(t: RawTurtle, radius: float):
    t.penup()
    t.right(90)
    t.forward(radius)
    t.left(90)
    t.circle(radius, 2)
    t.right(-90)
    t.forward(radius)
    t.left(-90)


def draw_vertical_line(t: RawTurtle):
    t.penup()
    t.right(90)
    t.forward(SCREEN_SCALE * 0.25)
    t.right(180)

    t.pendown()
    t.forward(SCREEN_SCALE * 0.5)

    t.penup()
    t.right(180)
    t.forward(SCREEN_SCALE * 0.25)
    t.left(90)


def draw_binary(t: RawTurtle, radius: float, angle: float, period: str):
    pos = t.pos()

    t.penup()
    t.setheading(angle)

    t.forward(radius + SCREEN_SCALE)

    for integer in period:
        if int(integer):
            draw_vertical_line(t)
            t.forward(SCREEN_SCALE * 0.25)

            continue

        t.pensize(1)
        t.pendown()
        t.forward(SCREEN_SCALE * 0.25)

        t.penup()
        t.forward(SCREEN_SCALE * 0.25)

    t.teleport(*pos)


def draw_binary_round(t: RawTurtle, radius: float, angle: float, period: str):
    radius = radius + 1.5 * SCREEN_SCALE
    t.penup()
    t.setheading(angle)

    for integer in period:
        if int(integer):
            t.penup()
            t.right(90)
            t.forward(radius)
            t.left(90)

            draw_vertical_line(t)

            t.penup()
            t.right(-90)
            t.forward(radius)
            t.left(-90)

            draw_circle_spacer(t, radius)

            continue

        draw_circle_arc(t, radius)

        draw_circle_spacer(t, radius)


def draw_moon(t: RawTurtle, moon: dict):
    orbit = SCREEN_SCALE * WORLD_SCALE * moon["orbit"]
    radius = MOON_SCALE * SCREEN_SCALE * WORLD_SCALE * moon["diameter"] / 2

    t.penup()
    if moon["direction"] == 1:
        t.forward(orbit)
    else:
        t.back(orbit)

    t.pendown()
    draw_circle_in_center(t, radius)


def draw_circle_in_center(t: RawTurtle, radius: float):
    t.penup()
    t.right(90)
    t.forward(radius)
    t.left(90)
    t.pendown()

    t.circle(radius)

    t.penup()
    t.right(-90)
    t.forward(radius)
    t.left(-90)
    t.pendown()


def config(jupiter: dict[str, int], moons: list[dict[str, int]]):
    global SCREEN_SCALE

    neg_x = pos_x = 0

    y = jupiter["diameter"] * 0.5 * JUPITER_SCALE * WORLD_SCALE

    for moon in moons:
        d = (moon["orbit"] + moon["diameter"] * MOON_SCALE) * WORLD_SCALE
        o = moon["direction"]

        x = o * d
        neg_x = min(x, neg_x)
        pos_x = max(x, pos_x)

    SCREEN_SCALE = min(W / (pos_x - neg_x + 16), H / (2 * y))

    start_x = -(pos_x + neg_x) * SCREEN_SCALE * 0.5  # (abs(neg_x) - max_x) * SCALE
    start_y = 0

    return start_x, start_y


def to_binary(number: int) -> str:
    return bin(number)[2:]


def main():
    with open("data/jupiter.json", "r") as f:
        jupiter_sys: list = json.load(f)

    t = SvgTurtle(W, H)

    jupiter: dict = jupiter_sys.pop(0)

    start_x, start_y = config(jupiter, jupiter_sys)

    radius = SCREEN_SCALE * JUPITER_SCALE * WORLD_SCALE * jupiter["diameter"] / 2

    t.teleport(start_x, start_y)

    draw_circle_in_center(t, radius)

    draw_binary_round(t, radius, -45, to_binary(jupiter["rotation"]))

    draw_binary_round(t, radius, 90, to_binary(jupiter["orbit"] // 1000))
    # draw_binary(t, radius, 90, to_binary(jupiter["orbit"] // 1000))

    draw_binary(t, radius, 180, to_binary(jupiter["period"]))

    for moon in jupiter_sys:
        t.teleport(start_x, start_y)
        t.setheading(0)

        draw_moon(t, moon)

        radius = SCREEN_SCALE * MOON_SCALE * WORLD_SCALE * moon["diameter"] / 2

        angle = 0 if moon["direction"] == -1 else 180

        draw_binary(t, radius, angle, to_binary(moon["period"])[:: moon["direction"]])
        draw_binary_round(t, 40, angle - 90, to_binary(moon["orbit"] // 1000))
        # draw_binary(t, radius, 90, to_binary(moon["orbit"] // 1000))

    t.save_as("jupiter.svg")

    svg2png(url="jupiter.svg", write_to="jupiter_transparent.png", dpi=300)
    svg2png(
        url="jupiter.svg",
        write_to="jupiter.png",
        dpi=300,
        background_color="white",
    )


if __name__ == "__main__":
    main()
    main()
    main()
