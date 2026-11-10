import queue

import pygame

from input_sender import InputSender

from video_feed import VideoFeed


def make_picture(frame):
    rgb = frame.reformat(format="rgb24")
    plane = rgb.planes[0]
    raw = bytes(plane)
    row_bytes = rgb.width * 3

    pixels = b"".join(
        raw[y * plane.line_size:y * plane.line_size + row_bytes]
        for y in range(rgb.height)
    )

    return pygame.image.frombytes(
        pixels, (rgb.width, rgb.height), "RGB"
    )


def main():
    pygame.display.init()
    screen = pygame.display.set_mode((960, 600))
    pygame.display.set_caption("WindowBridge — connecting")
    clock = pygame.time.Clock()

    feed = VideoFeed("tcp://100.71.157.67:5000")
    picture = None
    running = True
    left_pressed = False
    last_position = (0.5, 0.5)
    sender = InputSender()
    feed.start()

    try:
        while running:
            for event in pygame.event.get():
                try:
                    if event.type == pygame.QUIT:
                        running = False

                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False

                    elif event.type in (
                        pygame.WINDOWFOCUSLOST,
                        pygame.WINDOWLEAVE,
                    ):
                        if left_pressed:
                            sender.set_left_button(
                                False, *last_position
                            )
                            left_pressed = False

                    elif event.type in (
                        pygame.MOUSEMOTION,
                        pygame.MOUSEBUTTONDOWN,
                        pygame.MOUSEBUTTONUP,
                    ):
                        if picture is None:
                            continue

                        if event.type != pygame.MOUSEMOTION:
                            if event.button != 1:
                                continue

                        width, height = screen.get_size()
                        mouse_x, mouse_y = event.pos

                        inside_window = (
                            0 <= mouse_x < width
                            and 0 <= mouse_y < height
                        )

                        if not inside_window:
                            if left_pressed:
                                sender.set_left_button(
                                    False, *last_position
                                )
                                left_pressed = False
                                print("Released button at window boundary")
                            continue
                        normalized_x = min(
                            1.0, max(0.0, mouse_x / max(width - 1, 1))
                        )
                        normalized_y = min(
                            1.0, max(0.0, mouse_y / max(height - 1, 1))
                        )
                        last_position = (normalized_x, normalized_y)

                        if event.type == pygame.MOUSEMOTION:
                            sender.move_mouse(*last_position)

                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if not left_pressed:
                                sender.set_left_button(
                                    True, *last_position
                                )
                                left_pressed = True

                        elif event.type == pygame.MOUSEBUTTONUP:
                            if left_pressed:
                                sender.set_left_button(
                                    False, *last_position
                                )
                                left_pressed = False

                except OSError as error:
                    print(f"Input connection failed: {error}")
                    running = False

                if not running:
                       break

            if not running:
                break

            try:
                frame = feed.frames.get_nowait()
            except queue.Empty:
                pass
            else:
                picture = make_picture(frame)
                if screen.get_size() != picture.get_size():
                    print("VIDEO RESIZE:",
                        screen.get_size(),
                        "->",
                        picture.get_size(),
                        )
                    screen = pygame.display.set_mode(
                        picture.get_size()
                    )
                pygame.display.set_caption("WindowBridge — live")

            try:
                message = feed.messages.get_nowait()
            except queue.Empty:
                pass
            else:
                print(message)
                pygame.display.set_caption(message)

            screen.fill((24, 26, 30))
            if picture is not None:
                screen.blit(picture, (0, 0))

            pygame.display.flip()
            clock.tick(60)
    finally:
        sender.close()
        feed.stop()
        pygame.quit()


if __name__ == "__main__":
    main()
