{
  pkgs ? import <nixpkgs> {
  },
}:

pkgs.mkShell {
  name = "python-shell";
  buildInputs = with pkgs; [
    (python313.withPackages (
      pythonPackages: with pythonPackages; [
        pip
        pillow
        kivy
      ]
    ))
    SDL2
    SDL2_image
    SDL2_ttf
    SDL2_mixer
    mesa
    libGL
    gcc
    freetype
    fontconfig
    xorg.libX11
    xorg.libXcursor
    xorg.libXrandr
    xorg.libXi
    xorg.libXinerama
  ];

  shellHook = ''
    export KIVY_WINDOW=sdl2
    export KIVY_TEXT=pil
  '';
}
