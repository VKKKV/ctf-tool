import re

text = """Once upon a time there was a creature She was found in 1969‌​‌​​
And again in the 1980s In the 90s, she popped up all over the place​‌​​​
And by the turn of the century, she belonged to the people​​‌​‌
She was beautiful, vulnerable, power and success​​​​​​
And she was terrifying Impossible to pin down​​​​‌
She was alive and maybe not​‌‌‌​
And I’d be a completely different person if she didn’t exist‌​​‌‌

In 2016, she made it to Beijing‌​‌‌‌
And in 2020, I met her in person​​‌​‌
And in 2025 she and I both stopped being able to tell the difference between real and pretend human beings online‌​​‌​

Do you think angels live in stories?​​​​​​
Do you think at a certain point anyone who’s ever crossed a certain threshold of vitality has to become hyper real?​‌​​‌
When the internet finishes dying And every comment section is a deep sea graveyard of Schroediger’s eyes‌​​‌‌
A big tangled mess of concentric interwoven biblically accurate angels​​​​​​
Will everyone have crossed that threshold?​‌‌​‌
Will we all be viral?​​‌​‌
Will we all be angels?​‌‌​‌
And will we all be contaminated?​​‌​‌"""

for line in text.split("\n"):
    s = ""
    for char in line:
        if char == "\u200b":
            s += "0"
        elif char == "\u200c":
            s += "1"
    print(f"{s}")
    if s == "":
        continue
    bin2int = int(s, 2)
    if bin2int == 0:
        continue
    print(bin2int)
    print(chr(96+bin2int))
