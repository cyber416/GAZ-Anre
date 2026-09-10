name: Construieste APK

on:
  push:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Ia fisierele
        uses: actions/checkout@v4

      - name: Compileaza cu Buildozer
        uses: ArtemSBulgakov/buildozer-action@v1
        id: buildozer
        with:
          command: buildozer android debug
          buildozer_version: stable

      - name: Publica APK-ul
        uses: actions/upload-artifact@v4
        with:
          name: ExamenANRE-APK
          path: ${{ steps.buildozer.outputs.filename }}
