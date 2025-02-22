
import logging

logger= logging.getLogger("uvicorn")
logging.basicConfig(level=logging.INFO)
def print_number(lowest, highest):
    print("== job processing started ==")
    
    x = lowest
    while x <= highest:
        print(f"{str(x)}\n")
        x += 1
        # time.sleep(1)
    print("== End ==")