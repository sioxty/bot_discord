# main.py
import multiprocessing

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")  # або "fork" на Linux
    from bot import run
    run()
