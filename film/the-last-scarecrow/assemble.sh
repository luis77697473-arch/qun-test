#!/usr/bin/env bash
# 粗剪拼装：按分镜表顺序把 shots/ 下的镜头裁成 2.39:1、统一 24fps、截到指定时长后拼接。
# 缺失的镜头会用带编号的黑色占位片代替，所以素材没齐也能先看动态分镜（animatic）。
# 用法：./assemble.sh            → out/rough_cut.mp4
#       放入 audio/mix.wav 会自动混入；subs.srt 会作为软字幕封装。
set -euo pipefail
cd "$(dirname "$0")"

W=1920; H=804; FPS=24
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf

# 镜头ID 时长(秒) —— 与 03_分镜与提示词_shotlist.md 一致
SHOTS="
S01 6    S02 8    S03 8    S04 8    S05 6    S06 6
S07 8    S08 8    S09 6    S10 8    S11 6    S12 6    S13 4    S13x 2
S14 8    S15 8    S16 6    S17 8    S18a 5   S18b 5   S19a 3   S19b 3
S20 8    S21 6    S22 6    S23 8    S24 6    S25 6    S26 8    S27a 5   S27b 5
S28 6    S29 6    S30 6
S31 8    S32 8    S33 8    S34 8    S35a 5   S35b 4.5 S16x 0.5 S36 6
S37 10   S38 6    S39 8
"

mkdir -p out/norm
: > out/list.txt
total=0
set -- $SHOTS
while [ $# -gt 0 ]; do
  id=$1; dur=$2; shift 2
  src=shots/$id.mp4
  dst=out/norm/$id.mp4
  if [ -f "$src" ]; then
    ffmpeg -loglevel error -y -i "$src" -t "$dur" -an \
      -vf "scale=$W:-2,crop=$W:$H,fps=$FPS,format=yuv420p" \
      -c:v libx264 -crf 16 -preset medium "$dst"
  else
    ffmpeg -loglevel error -y -f lavfi -i "color=c=0x101418:s=${W}x${H}:r=$FPS:d=$dur" \
      -vf "drawtext=fontfile=$FONT:text='$id  ($dur s)':fontcolor=0x5FF2E6:fontsize=48:x=(w-tw)/2:y=(h-th)/2,format=yuv420p" \
      -c:v libx264 -crf 16 -preset medium "$dst"
  fi
  echo "file 'norm/$id.mp4'" >> out/list.txt
  total=$(awk "BEGIN{print $total+$dur}")
done

ffmpeg -loglevel error -y -f concat -safe 0 -i out/list.txt -c copy out/video.mp4

args=(-i out/video.mp4)
maps=(-map 0:v)
if [ -f audio/mix.wav ]; then args+=(-i audio/mix.wav); maps+=(-map 1:a -c:a aac -b:a 320k -shortest); fi
if [ -f subs.srt ]; then
  args+=(-i subs.srt); n=$(( ${#args[@]} / 2 - 1 ))
  maps+=(-map "$n:s" -c:s mov_text -metadata:s:s:0 language=chi)
fi
ffmpeg -loglevel error -y "${args[@]}" "${maps[@]}" -c:v copy out/rough_cut.mp4

echo "完成：out/rough_cut.mp4  （分镜总时长 ${total}s）"
