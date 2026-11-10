import av


def main():
    print("Connecting to Mac video...")

    with av.open(
        "tcp://100.71.157.67:5000",
        format="h264",
        timeout=(5.0, 5.0),
    ) as container:
        for number, frame in enumerate(
            container.decode(video=0), start=1
        ):
            print(
                f"Frame {number}: "
                f"{frame.width}x{frame.height}, "
                f"format={frame.format.name}"
            )

            if number == 5:
                break

    print("Video decode check complete.")


if __name__ == "__main__":
    main()
