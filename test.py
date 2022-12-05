def gen_rx(lower: int = 1, upper: int = 9) -> str:
    for outer_start in range(lower, upper + 1):
        for outer_end in range(outer_start + 1, upper + 1):
            print(f"[{outer_start}-{outer_end}]")

            for x in range(outer_start, outer_end + 1):
                print(" - " f"[{inner_start}-{inner_end}]")



            inner_start, inner_end = outer_start, outer_end - 1
            print(" - " f"[{inner_start}-{inner_end}]")

            inner_start, inner_end = outer_start + 1, outer_end
            print(" - " f"[{inner_start}-{inner_end}]")

            # if outer_start == inner_start and outer_end == inner_end:
            #     continue
            # print(" - " f"[{inner_start}-{inner_end}]")

            input("Press Enter to continue... ")


if __name__ == "__main__":
    gen_rx()
