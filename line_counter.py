import os

total = 0
for f in os.listdir():
    try:
        if f.split('.')[1] == 'py' and f != os.path.basename(__file__):
            with open(f) as file:
                line_amount = len(file.readlines())
                total += line_amount
                print(f"{f:<20}: {line_amount}")
    except:
        pass
    
print(f"\n{'TOTAL':<20}: {total}")