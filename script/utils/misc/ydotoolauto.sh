sleep 5
for i in {1..100}; do
    ydotool click 0xc0
    ydotool type "wrong answer"
    ydotool key 28:1 28:0
    sleep 5
done
