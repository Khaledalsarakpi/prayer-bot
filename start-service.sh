#!/bin/bash
SESSION="prayer-bot"

tmux kill-session -t $SESSION 2>/dev/null

tmux new-session -d -s $SESSION "cd /root/prayer_bot && bash run.sh"

echo "تم بدء البوت في tmux"
echo "للدخول: tmux attach -t prayer-bot"
echo "للخروج: Ctrl+B ثم D"
