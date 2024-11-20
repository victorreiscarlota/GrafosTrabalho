#!/bin/bash

FRAMES_DIR="dados/imagens_ppm"

if [ ! -d "dados" ]; then
  echo "A pasta 'dados' não foi encontrada."
  exit 1
fi

if [ ! -d "$FRAMES_DIR" ]; then
  echo "A pasta 'imagens_ppm' não foi encontrada dentro de 'dados'."
  exit 1
fi

if [ -z "$(ls -A $FRAMES_DIR/*.ppm 2>/dev/null)" ]; then
  echo "Não há imagens PPM na pasta $FRAMES_DIR."
  exit 1
fi

OUTPUT_GIF="dados/animacao.gif"

# Usa o FFmpeg para criar o GIF
ffmpeg -framerate 1 -i $FRAMES_DIR/frame_%d.ppm -vf "scale=800:-1:flags=lanczos" -loop 0 "$OUTPUT_GIF"

if [ -f "$OUTPUT_GIF" ]; then
  echo "GIF criado com sucesso em $OUTPUT_GIF"
else
  echo "Ocorreu um erro ao criar o GIF."
fi
